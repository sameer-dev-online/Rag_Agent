'use client';

import { useEffect, useState } from 'react';
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
  const [sidebarOpen, setSidebarOpen] = useState(false);
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
    // Close sidebar on mobile after selection
    setSidebarOpen(false);
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="flex h-screen bg-gray-950 overflow-hidden">
      {/* Sidebar */}
      <ConversationSidebar
        activeConversationId={conversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={startNewConversation}
        onDeleteConversation={deleteConversation}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header with navigation */}
        <div className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm px-3 sm:px-4 md:px-6 py-3 md:py-4">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 md:gap-3 min-w-0">
              {/* Mobile menu button */}
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleSidebar}
                className="md:hidden shrink-0"
                aria-label="Toggle sidebar"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                  className="w-5 h-5"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"
                  />
                </svg>
              </Button>
              <h1 className="text-lg sm:text-xl font-semibold text-white truncate">RAG Assistant</h1>
            </div>
            <Link href="/upload" className="shrink-0">
              <Button variant="outline" size="sm" className="gap-1.5 sm:gap-2">
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
                  className="shrink-0"
                >
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
                <span className="hidden sm:inline">Upload</span>
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
