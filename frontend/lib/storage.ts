import { v4 as uuidv4 } from 'uuid';
import { STORAGE_KEYS } from './constants';
import { LocalConversation } from '@/types/chat';
import { isBrowser } from './utils';

/**
 * LocalStorage management class for persisting user data
 * All methods are SSR-safe
 */
export class LocalStorage {
  /**
   * Get or generate user ID
   */
  static getUserId(): string {
    if (!isBrowser()) return '';

    try {
      let userId = localStorage.getItem(STORAGE_KEYS.USER_ID);

      if (!userId) {
        userId = uuidv4();
        localStorage.setItem(STORAGE_KEYS.USER_ID, userId);
      }

      return userId;
    } catch (error) {
      console.error('Error accessing localStorage for user ID:', error);
      return '';
    }
  }

  /**
   * Get all conversations from localStorage
   */
  static getConversations(): LocalConversation[] {
    if (!isBrowser()) return [];

    try {
      const stored = localStorage.getItem(STORAGE_KEYS.CONVERSATIONS);
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('Error reading conversations from localStorage:', error);
      return [];
    }
  }

  /**
   * Save a conversation to localStorage
   */
  static saveConversation(conversation: LocalConversation): void {
    if (!isBrowser()) return;

    try {
      const conversations = this.getConversations();
      const existingIndex = conversations.findIndex((c) => c.id === conversation.id);

      if (existingIndex >= 0) {
        // Update existing conversation
        conversations[existingIndex] = conversation;
      } else {
        // Add new conversation
        conversations.push(conversation);
      }

      localStorage.setItem(STORAGE_KEYS.CONVERSATIONS, JSON.stringify(conversations));
    } catch (error) {
      console.error('Error saving conversation to localStorage:', error);
    }
  }

  /**
   * Delete a conversation from localStorage
   */
  static deleteConversation(conversationId: string): void {
    if (!isBrowser()) return;

    try {
      const conversations = this.getConversations();
      const filtered = conversations.filter((c) => c.id !== conversationId);
      localStorage.setItem(STORAGE_KEYS.CONVERSATIONS, JSON.stringify(filtered));
    } catch (error) {
      console.error('Error deleting conversation from localStorage:', error);
    }
  }

  /**
   * Get active conversation ID
   */
  static getActiveConversationId(): string | null {
    if (!isBrowser()) return null;

    try {
      return localStorage.getItem(STORAGE_KEYS.ACTIVE_CONVERSATION_ID);
    } catch (error) {
      console.error('Error reading active conversation ID:', error);
      return null;
    }
  }

  /**
   * Set active conversation ID
   */
  static setActiveConversationId(conversationId: string | null): void {
    if (!isBrowser()) return;

    try {
      if (conversationId) {
        localStorage.setItem(STORAGE_KEYS.ACTIVE_CONVERSATION_ID, conversationId);
      } else {
        localStorage.removeItem(STORAGE_KEYS.ACTIVE_CONVERSATION_ID);
      }
    } catch (error) {
      console.error('Error setting active conversation ID:', error);
    }
  }

  /**
   * Clear all storage (useful for testing/debugging)
   */
  static clear(): void {
    if (!isBrowser()) return;

    try {
      Object.values(STORAGE_KEYS).forEach((key) => {
        localStorage.removeItem(key);
      });
    } catch (error) {
      console.error('Error clearing localStorage:', error);
    }
  }
}
