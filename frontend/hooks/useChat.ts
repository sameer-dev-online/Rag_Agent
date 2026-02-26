import { useState, useCallback } from 'react';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api';
import { LocalStorage } from '@/lib/storage';
import { generateTempId, generateConversationTitle } from '@/lib/utils';
import { DEFAULTS } from '@/lib/constants';
import type { Message, OptimisticMessage, APIError } from '@/types';

/**
 * Core chat logic with optimistic updates
 */
export function useChat(userId: string) {
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);

  /**
   * Send a message
   */
  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || !userId) return;

      // Create optimistic user message
      const optimisticMessage: Message = {
        id: generateTempId(),
        conversation_id: conversationId || '',
        role: 'user',
        content: content.trim(),
        created_at: new Date().toISOString(),
      };

      // Add optimistic message immediately
      setMessages((prev) => [...prev, optimisticMessage]);
      setIsLoading(true);
      setIsTyping(true);

      try {
        // Call API
        const response = await apiClient.sendMessage(content.trim(), userId, conversationId);

        // Replace optimistic message with real messages from backend
        setMessages((prev) => {
          // Remove the optimistic message
          const filtered = prev.filter((msg) => msg.id !== optimisticMessage.id);
          // Add real messages
          return [...filtered, response.user_message, response.assistant_message];
        });

        // If first message, save conversation_id
        if (!conversationId) {
          setConversationId(response.conversation_id);
          LocalStorage.setActiveConversationId(response.conversation_id);

          // Generate and save conversation metadata
          const title = generateConversationTitle(content.trim());
          LocalStorage.saveConversation({
            id: response.conversation_id,
            title,
            updated_at: new Date().toISOString(),
          });
        } else {
          // Update existing conversation timestamp
          const conversations = LocalStorage.getConversations();
          const existing = conversations.find((c) => c.id === conversationId);
          if (existing) {
            LocalStorage.saveConversation({
              ...existing,
              updated_at: new Date().toISOString(),
            });
          }
        }
      } catch (error) {
        const apiError = error as APIError;
        console.error('Error sending message:', apiError);

        // Rollback optimistic update
        setMessages((prev) => prev.filter((msg) => msg.id !== optimisticMessage.id));

        // Show error toast
        toast.error(apiError.message || DEFAULTS.ERROR_MESSAGE, {
          description: 'Click to retry',
          action: {
            label: 'Retry',
            onClick: () => sendMessage(content),
          },
        });
      } finally {
        setIsLoading(false);
        setIsTyping(false);
      }
    },
    [userId, conversationId]
  );

  /**
   * Load a conversation from backend
   */
  const loadConversation = useCallback(
    async (convId: string) => {
      if (!userId) return;

      setIsLoading(true);
      try {
        const data = await apiClient.getConversation(convId, userId);
        setConversationId(convId);
        setMessages(data.messages);
        LocalStorage.setActiveConversationId(convId);
      } catch (error) {
        const apiError = error as APIError;
        console.error('Error loading conversation:', apiError);
        toast.error(apiError.message || 'Failed to load conversation');
      } finally {
        setIsLoading(false);
      }
    },
    [userId]
  );

  /**
   * Start a new conversation
   */
  const startNewConversation = useCallback(() => {
    setConversationId(undefined);
    setMessages([]);
    LocalStorage.setActiveConversationId(null);
  }, []);

  /**
   * Delete a conversation
   */
  const deleteConversation = useCallback(
    (convId: string) => {
      LocalStorage.deleteConversation(convId);

      // If deleting active conversation, start new one
      if (convId === conversationId) {
        startNewConversation();
      }

      toast.success('Conversation deleted');
    },
    [conversationId, startNewConversation]
  );

  return {
    conversationId,
    messages,
    isLoading,
    isTyping,
    sendMessage,
    loadConversation,
    startNewConversation,
    deleteConversation,
  };
}
