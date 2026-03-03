'use client';

import { useEffect, useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { LocalStorage } from '@/lib/storage';
import { cn } from '@/lib/utils';
import type { LocalConversation } from '@/types';

interface ConversationSidebarProps {
  activeConversationId?: string;
  onSelectConversation: (conversationId: string) => void;
  onNewConversation: () => void;
  onDeleteConversation: (conversationId: string) => void;
  isOpen?: boolean;
  onClose?: () => void;
}

/**
 * Sidebar with conversation list
 */
export function ConversationSidebar({
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  isOpen = true,
  onClose,
}: ConversationSidebarProps) {
  const [conversations, setConversations] = useState<LocalConversation[]>([]);

  const loadConversations = useCallback(() => {
    const convs = LocalStorage.getConversations();
    // Sort by updated_at descending
    const sorted = convs.sort(
      (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    );
    setConversations(sorted);
  }, []);

  // Load conversations on mount and when active conversation changes
  useEffect(() => {
    (()=>{
      loadConversations();
    }) ();
  }, [activeConversationId, loadConversations]);

  const handleDelete = (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    onDeleteConversation(conversationId);
    loadConversations();
  };

  const handleNewConversation = () => {
    onNewConversation();
    onClose?.();
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <div
        className={cn(
          'fixed md:relative inset-y-0 left-0 z-50 w-[280px] border-r border-gray-800 bg-gray-950 flex flex-col transition-transform duration-300 ease-in-out md:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Header */}
        <div className="p-3 sm:p-4 border-b border-gray-800">
          <div className="flex items-center justify-between gap-2 mb-3 md:hidden">
            <h2 className="text-sm font-semibold text-white">Conversations</h2>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="shrink-0"
              aria-label="Close sidebar"
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
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </Button>
          </div>
          <Button onClick={handleNewConversation} className="w-full" size="lg">
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
                d="M12 4.5v15m7.5-7.5h-15"
              />
            </svg>
            New Chat
          </Button>
        </div>

        {/* Conversation list */}
        <ScrollArea className="flex-1">
          <div className="p-2 space-y-1">
            {conversations.length === 0 ? (
              <div className="p-4 text-center text-sm text-gray-500">
                No conversations yet
              </div>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.id}
                  className={cn(
                    'flex items-center gap-2 p-3 rounded-lg cursor-pointer transition-all hover:bg-gray-800 group',
                    activeConversationId === conv.id && 'bg-gray-800'
                  )}
                  onClick={() => onSelectConversation(conv.id)}
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white truncate">{conv.title}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(conv.updated_at).toLocaleDateString()}
                    </p>
                  </div>

                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          fill="none"
                          viewBox="0 0 24 24"
                          strokeWidth={1.5}
                          stroke="currentColor"
                          className="w-4 h-4"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            d="M12 6.75a.75.75 0 110-1.5.75.75 0 010 1.5zM12 12.75a.75.75 0 110-1.5.75.75 0 010 1.5zM12 18.75a.75.75 0 110-1.5.75.75 0 010 1.5z"
                          />
                        </svg>
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent>
                      <DropdownMenuItem
                        onClick={(e) => handleDelete(conv.id, e)}
                        className="text-red-500"
                      >
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              ))
            )}
          </div>
        </ScrollArea>
      </div>
    </>
  );
}
