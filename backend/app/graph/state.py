"""Agent state definition for LangGraph"""

from typing import TypedDict, Annotated, List, Literal, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from langgraph.graph import add_messages


class AgentState(TypedDict):
    """State for the RAG agent workflow"""

    # Messages in the conversation
    messages: Annotated[List[BaseMessage], add_messages]

    # Retrieval results
    retrieved_docs: List[dict]

    # Web search results
    search_results: List[dict]

    # Route decision
    route: Literal["rag", "web_search", "direct"]

    # Query rewrite state
    query_rewrite_count: int
    rewritten_query: Optional[str]

    # Reflection state
    reflection_score: Optional[float]
    reflection_decision: Optional[Literal["relevant", "not_relevant", "uncertain"]]

    # Generation state
    answer: Optional[str]
    references: List[dict]

    # Error state
    error: Optional[str]


def create_initial_state(user_message: str) -> AgentState:
    """Create initial state from user message"""
    return AgentState(
        messages=[HumanMessage(content=user_message)],
        retrieved_docs=[],
        search_results=[],
        route="rag",  # Default to RAG
        query_rewrite_count=0,
        rewritten_query=None,
        reflection_score=None,
        reflection_decision=None,
        answer=None,
        references=[],
        error=None,
    )
