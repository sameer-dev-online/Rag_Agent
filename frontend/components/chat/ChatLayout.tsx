'use client';

import { useEffect } from 'react';
import { useChat } from '@/hooks/useChat';
import { LocalStorage } from '@/lib/storage';
import { ConversationSidebar } from './ConversationSidebar';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';

interface ChatLayoutProps {
  userId: string;
}

/**
 * Main chat layout orchestrator
 */
export function ChatLayout({ userId }: ChatLayoutProps) {
  const {
    conversationId,
    messages,
    isLoading,
    isTyping,
    sendMessage,
    loadConversation,
    startNewConversation,
    deleteConversation,
  } = useChat(userId);

  // Load active conversation on mount
  useEffect(() => {
    const activeId = LocalStorage.getActiveConversationId();
    if (activeId) {
      loadConversation(activeId);
    }
  }, [loadConversation]);

  const handleSelectConversation = (convId: string) => {
    if (convId !== conversationId) {
      loadConversation(convId);
    }
  };

  return (
    <div className="flex h-screen bg-gray-950">
      {/* Sidebar */}
      <ConversationSidebar
        activeConversationId={conversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={startNewConversation}
        onDeleteConversation={deleteConversation}
      />

      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        <MessageList messages={messages} isTyping={isTyping} />
        <ChatInput onSend={sendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}
