'use client';

import { useEffect } from 'react';
import { useChat } from '@/hooks/useChat';
import { LocalStorage } from '@/lib/storage';
import { ConversationSidebar } from './ConversationSidebar';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

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
        {/* Header with navigation */}
        <div className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-semibold text-white">RAG Assistant</h1>
            <Link href="/upload">
              <Button variant="outline" size="sm">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="mr-2"
                >
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
                Upload Documents
              </Button>
            </Link>
          </div>
        </div>

        <MessageList messages={messages} isTyping={isTyping} />
        <ChatInput onSend={sendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}
