// Conversation types
export interface Message {
  id: number
  conversation_id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  metadata?: MessageMetadata
  created_at: string
}

export interface MessageMetadata {
  references?: Reference[]
}

export interface Reference {
  id: number
  doc_name?: string
  content: string
  url?: string
}

export interface Conversation {
  id: number
  title: string
  created_at: string
  updated_at: string
  messages?: Message[]
}

// Knowledge Base types
export interface KnowledgeBase {
  id: number
  name: string
  description: string
  document_count: number
  created_at: string
  updated_at: string
}

export interface Document {
  id: number
  kb_id: number
  doc_id: string
  doc_name: string
  file_type: string
  file_size: number
  status: 'uploading' | 'parsing' | 'chunking' | 'embedding' | 'completed' | 'failed'
  progress?: Progress
  metadata?: DocumentMetadata
  created_at: string
}

export interface Progress {
  stage: string
  progress: number
  message: string
}

export interface DocumentMetadata {
  total_chunks: number
  chunk_size: number
  parse_time: number
  file_type: string
  file_size: number
}

// Config types
export interface LLMConfig {
  vendor: 'openai' | 'vllm' | 'ollama'
  model: string
  api_key?: string
  base_url?: string
  temperature: number
  max_tokens?: number
}

export interface EmbeddingConfig {
  vendor: 'openai' | 'local'
  model: string
  dimension: number
  api_key?: string
  base_url?: string
}

export interface RerankerConfig {
  enabled: boolean
  model: string
  top_k: number
}

// SSE stream types
export interface StreamChunk {
  type: 'content' | 'references' | 'conversation_id' | 'done' | 'error'
  content?: string
  references?: Reference[]
  conversation_id?: number
  error?: string
}
