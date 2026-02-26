/**
 * LocalStorage keys
 */
export const STORAGE_KEYS = {
  USER_ID: 'rag_user_id',
  CONVERSATIONS: 'rag_conversations',
  ACTIVE_CONVERSATION_ID: 'rag_active_conversation_id',
} as const;

/**
 * API endpoint paths
 */
export const API_ENDPOINTS = {
  HEALTH: '/health',
  CHAT: '/chat',
  CONVERSATIONS: '/conversations',
  DOCUMENTS: '/documents',
} as const;

/**
 * File upload validation
 */
export const FILE_VALIDATION = {
  ACCEPTED_TYPES: {
    'application/pdf': ['.pdf'],
    'text/plain': ['.txt'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  },
  MAX_SIZE: 10 * 1024 * 1024, // 10MB in bytes
  MAX_SIZE_MB: 10,
} as const;

/**
 * UI constants
 */
export const UI_CONSTANTS = {
  TOAST_DURATION: 5000, // 5 seconds
  AUTO_SCROLL_DELAY: 100, // ms delay before auto-scroll
  TYPING_INDICATOR_DELAY: 300, // ms before showing typing indicator
  MESSAGE_ANIMATION_DURATION: 0.3, // seconds for framer-motion
  SIDEBAR_WIDTH: 280, // px
} as const;

/**
 * Default values
 */
export const DEFAULTS = {
  CONVERSATION_TITLE: 'New Conversation',
  ERROR_MESSAGE: 'Something went wrong. Please try again.',
  NETWORK_ERROR: 'Network error. Please check your connection.',
  AUTH_ERROR: 'Authentication failed. Please check your API key.',
} as const;
