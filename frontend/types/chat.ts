/**
 * Message role types matching backend schema
 */
export type MessageRole = 'user' | 'assistant';

/**
 * Message structure from backend
 */
export interface Message {
  id: string;
  conversation_id: string;
  role: MessageRole;
  content: string;
  metadata?: Record<string, any>;
  created_at: string;
}

/**
 * Conversation structure from backend
 */
export interface Conversation {
  id: string;
  user_id: string;
  title?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Retrieved context from RAG pipeline
 */
export interface RetrievedContext {
  content: string;
  document_id: string;
  chunk_id: string;
  similarity_score: number;
  metadata?: Record<string, any>;
}

/**
 * Chat response from POST /api/v1/chat
 */
export interface ChatResponse {
  conversation_id: string;
  user_message: Message;
  assistant_message: Message;
  retrieved_contexts: RetrievedContext[];
}

/**
 * Conversation with messages from GET /api/v1/conversations/{id}
 */
export interface ConversationWithMessages {
  conversation: Conversation;
  messages: Message[];
}

/**
 * Local conversation metadata stored in localStorage
 */
export interface LocalConversation {
  id: string;
  title: string;
  updated_at: string;
}

/**
 * Optimistic message for immediate UI updates
 */
export interface OptimisticMessage extends Omit<Message, 'id' | 'created_at'> {
  id: string; // Temporary ID
  created_at: string;
  isOptimistic: true;
  error?: string;
}
