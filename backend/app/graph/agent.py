"""LangGraph agent workflow for RAG intelligent assistant"""

import json
from typing import Dict, List, Literal, Optional

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from app.graph.state import AgentState, create_initial_state
from app.core.config import settings
from app.services.llm.base import get_llm
from app.services.rag.retrieval import RetrievalService
from tavily import TavilyClient


class RAGAgent:
    """RAG Agent with LangGraph workflow"""

    def __init__(self, kb_id: Optional[int] = None):
        """
        Initialize RAG agent

        Args:
            kb_id: Knowledge base ID to use (None = web search only)
        """
        self.kb_id = kb_id
        self.llm = get_llm()
        self.retrieval_service = RetrievalService() if kb_id else None
        self.tavily_client = TavilyClient(api_key=settings.tavily_api_key) if settings.tavily_api_key else None

        # Build the workflow graph
        self.workflow = self._build_workflow()

        # Create checkpointer for state persistence
        checkpointer = SqliteSaver.from_conn_string(":memory:")

        # Create the compiled graph
        self.graph = self.workflow.compile(checkpointer=checkpointer)

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""

        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("route_query", self._route_query)
        workflow.add_node("retrieve", self._retrieve)
        workflow.add_node("rewrite_query", self._rewrite_query)
        workflow.add_node("search_web", self._search_web)
        workflow.add_node("reflect", self._reflect)
        workflow.add_node("generate", self._generate)

        # Define edges
        # Start -> route_query
        workflow.set_entry_point("route_query")

        # route_query -> retrieve (if rag) OR search_web (if web_search) OR direct (if direct)
        workflow.add_conditional_edges(
            "route_query",
            self._router_condition,
            {
                "rag": "retrieve",
                "web_search": "search_web",
                "direct": "generate",
            },
        )

        # retrieve -> reflect
        workflow.add_edge("retrieve", "reflect")

        # reflect -> (relevant) generate OR (not_relevant) rewrite_query OR (uncertain) search_web
        workflow.add_conditional_edges(
            "reflect",
            self._reflect_condition,
            {
                "relevant": "generate",
                "not_relevant": "rewrite_query",
                "uncertain": "search_web",
            },
        )

        # rewrite_query -> retrieve (if haven't exceeded max attempts) OR search_web
        workflow.add_conditional_edges(
            "rewrite_query",
            self._rewrite_condition,
            {
                "retrieve": "retrieve",
                "search_web": "search_web",
            },
        )

        # search_web -> generate
        workflow.add_edge("search_web", "generate")

        # generate -> END
        workflow.add_edge("generate", END)

        return workflow

    # Node implementations

    def _route_query(self, state: AgentState) -> AgentState:
        """
        Route query based on keywords and context

        Determines if RAG, web search, or direct answer is needed
        """
        user_message = state["messages"][-1]

        # Check for web search keywords
        text = user_message.content.lower()
        for keyword in settings.web_search_keywords_list:
            if keyword in text:
                state["route"] = "web_search"
                return state

        # Check if we have a knowledge base
        if self.kb_id is None or not self.retrieval_service:
            state["route"] = "web_search"
        else:
            # Default to RAG
            state["route"] = "rag"

        return state

    def _router_condition(
        self,
        state: AgentState,
    ) -> Literal["rag", "web_search", "direct"]:
        """Determine next step from route_query"""
        return state["route"]

    def _retrieve(self, state: AgentState) -> AgentState:
        """Retrieve relevant documents from knowledge base"""
        if not self.kb_id or not self.retrieval_service:
            state["retrieved_docs"] = []
            return state

        user_message = state["messages"][-1]
        query = state.get("rewritten_query") or user_message.content

        try:
            docs = self.retrieval_service.retrieve(query, self.kb_id)
            state["retrieved_docs"] = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                }
                for doc in docs
            ]
        except Exception as e:
            state["error"] = f"Retrieval failed: {str(e)}"
            state["retrieved_docs"] = []

        return state

    def _reflect(self, state: AgentState) -> AgentState:
        """
        Reflect on retrieval results to determine relevance

        Uses LLM to evaluate if retrieved documents are relevant to the query
        """
        if not state["retrieved_docs"]:
            state["reflection_decision"] = "uncertain"
            state["reflection_score"] = 0.0
            return state

        user_message = state["messages"][-1]

        # Simple reflection: check if we have relevant docs
        # In a more advanced version, we'd use LLM for this
        if state["retrieved_docs"]:
            # Check similarity scores if available
            scores = [
                doc.get("metadata", {}).get("score", 0.5)
                for doc in state["retrieved_docs"]
                if doc.get("metadata", {}).get("score") is not None
            ]

            if scores:
                avg_score = sum(scores) / len(scores)
                state["reflection_score"] = avg_score

                if avg_score >= settings.rewrite_threshold:
                    state["reflection_decision"] = "relevant"
                else:
                    state["reflection_decision"] = "not_relevant"
            else:
                # No scores available, assume relevant (can always try web search later)
                state["reflection_decision"] = "relevant"
                state["reflection_score"] = 0.6
        else:
            state["reflection_decision"] = "not_relevant"
            state["reflection_score"] = 0.0

        return state

    def _reflect_condition(
        self,
        state: AgentState,
    ) -> Literal["relevant", "not_relevant", "uncertain"]:
        """Determine next step from reflect."""
        return state["reflection_decision"] or "uncertain"

    def _rewrite_query(self, state: AgentState) -> AgentState:
        """
        Rewrite query for better retrieval

        Uses LLM to rewrite the query into more specific terms
        """
        state["query_rewrite_count"] += 1

        user_message = state["messages"][-1]
        query = user_message.content

        # Simple rewrite for MVP
        # In production, use LLM to intelligently rewrite
        original_query = query

        # Simple heuristics for query rewriting
        if "?" in query:
            rewritten = query.replace("?", "").strip()
        elif "如何" in query or "怎么" in query or "how" in query.lower():
            # Add relevant context words
            rewritten = query + " 方法 步骤"
        else:
            rewritten = query

        state["rewritten_query"] = rewritten
        return state

    def _rewrite_condition(
        self,
        state: AgentState,
    ) -> Literal["retrieve", "search_web"]:
        """Determine next step from rewrite_query"""
        if state["query_rewrite_count"] >= settings.max_rewrite_attempts:
            return "search_web"
        return "retrieve"

    def _search_web(self, state: AgentState) -> AgentState:
        """Search the web using Tavily"""
        user_message = state["messages"][-1]
        query = state.get("rewritten_query") or user_message.content

        if not self.tavily_client:
            state["search_results"] = []
            state["error"] = "Tavily API not configured"
            return state

        try:
            results = self.tavily_client.search(
                query=query,
                search_depth="basic",
                max_results=settings.top_k_results,
                include_domains=[],
                exclude_domains=[],
            )

            state["search_results"] = results.get("results", [])
        except Exception as e:
            state["error"] = f"Web search failed: {str(e)}"
            state["search_results"] = []

        return state

    def _generate(self, state: AgentState) -> AgentState:
        """
        Generate answer based on retrieved documents or web search results

        This is the final step in the workflow
        """
        user_message = state["messages"][-1]

        # Prepare context for generation
        if state["retrieved_docs"]:
            # RAG response
            context = "\n\n".join([
                f"[Document {i}]\n{doc['content']}"
                for i, doc in enumerate(state["retrieved_docs"])
            ])
            prompt = f"""Based on the following documents, answer the user's question.

User Question: {user_message.content}

Documents:
{context}

Please provide a clear and accurate answer based on the documents above. If the documents don't contain relevant information, please mention that.
"""
            state["references"] = [
                {
                    "id": i,
                    "doc_name": doc.get("metadata", {}).get("doc_name", "Unknown"),
                    "content": doc["content"][:200],
                }
                for i, doc in enumerate(state["retrieved_docs"])
            ]
        elif state["search_results"]:
            # Web search response
            context = "\n\n".join([
                f"[Source {i+1}] {result.get('title', 'Untitled')}\n{result.get('content', '')[:300]}"
                for i, result in enumerate(state["search_results"])
            ])
            prompt = f"""Based on the following search results, answer the user's question.

User Question: {user_message.content}

Search Results:
{context}

Please provide a clear and accurate answer based on the search results above.
"""
            state["references"] = [
                {
                    "id": i,
                    "doc_name": result.get("title", "Web Source"),
                    "content": result.get("content", "")[:200],
                    "url": result.get("url", ""),
                }
                for i, result in enumerate(state["search_results"])
            ]
        else:
            # Direct answer
            prompt = f"""User Question: {user_message.content}

Please provide a helpful answer to the user's question."""
            state["references"] = []

        # Generate response
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            state["answer"] = response.content

            # Add references to answer
            if state["references"]:
                ref_text = "\n\n**References:**\n" + "\n".join([
                    f"[{ref['id']}] {ref['doc_name']}"
                    for ref in state["references"]
                ])
                state["answer"] += ref_text

        except Exception as e:
            state["error"] = f"Generation failed: {str(e)}"
            state["answer"] = "I apologize, but I encountered an error while generating the response."

        return state

    async def stream(
        self,
        user_message: str,
        kb_id: Optional[int] = None,
    ):
        """
        Stream the agent response

        Args:
            user_message: User's message
            kb_id: Knowledge base ID (optional)

        Yields:
            Streaming response chunks
        """
        # Update KB if provided
        if kb_id is not None:
            self.kb_id = kb_id
            self.retrieval_service = RetrievalService() if kb_id else None

        # Create initial state
        initial_state = create_initial_state(user_message)

        # Run the workflow
        async for event in self.graph.astream(initial_state):
            # Output streamable content
            if isinstance(event, dict):
                for node_name, node_state in event.items():
                    if node_name == "generate" and node_state.get("answer"):
                        # Stream the answer
                        import asyncio

                        answer = node_state["answer"]
                        chunk_size = 10

                        for i in range(0, len(answer), chunk_size):
                            yield {
                                "type": "content",
                                "content": answer[i:i+chunk_size],
                            }
                            await asyncio.sleep(0.01)

                        # Yield references
                        if node_state.get("references"):
                            yield {
                                "type": "references",
                                "references": node_state["references"],
                            }

                        yield {"type": "done"}

        # If no answer was generated, yield error
        if not event.get("generate", {}).get("answer"):
            yield {
                "type": "error",
                "error": state.event.get("generate", {}).get("error", "Unknown error"),
            }

    async def invoke(
        self,
        user_message: str,
        kb_id: Optional[int] = None,
    ) -> Dict:
        """
        Invoke the agent and return final response

        Args:
            user_message: User's message
            kb_id: Knowledge base ID (optional)

        Returns:
            Final response with answer and references
        """
        # Update KB if provided
        if kb_id is not None:
            self.kb_id = kb_id
            self.retrieval_service = RetrievalService() if kb_id else None

        # Create initial state
        initial_state = create_initial_state(user_message)

        # Run the workflow
        final_state = await self.graph.ainvoke(initial_state)

        return {
            "answer": final_state.get("answer"),
            "references": final_state.get("references", []),
            "route": final_state.get("route"),
            "used_web_search": bool(final_state.get("search_results")),
            "error": final_state.get("error"),
        }


def create_agent(kb_id: Optional[int] = None) -> RAGAgent:
    """Factory function to create an RAG agent"""
    return RAGAgent(kb_id=kb_id)
