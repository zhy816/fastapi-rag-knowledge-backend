export interface User {
  id: number
  username: string
  create_time: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

export interface Document {
  id: number
  user_id: number
  filename: string
  file_path: string
  file_type: string
  status: string
  create_time: string
  update_time: string
}

export interface DocumentProcessResult {
  document_id: number
  status: string
  chunk_count?: number
  vector_count?: number
}

export interface ChatSession {
  id: number
  user_id: number
  document_id: number
  title: string
  create_time: string
  update_time: string
}

export interface ChatMessage {
  id: number
  session_id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  create_time: string
}

export interface SearchSource {
  chunk_id: number
  content: string
  distance: number
}

export interface ChatAskResult {
  session_id: number
  question: string
  answer: string
  sources: SearchSource[]
}