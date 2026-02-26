'use client';

import { useEffect, useState } from 'react';
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
}

/**
 * Sidebar with conversation list
 */
export function ConversationSidebar({
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
}: ConversationSidebarProps) {
  const [conversations, setConversations] = useState<LocalConversation[]>([]);

  // Load conversations on mount and when active conversation changes
  useEffect(() => {
    loadConversations();
  }, [activeConversationId]);

  const loadConversations = () => {
    const convs = LocalStorage.getConversations();
    // Sort by updated_at descending
    const sorted = convs.sort(
      (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    );
    setConversations(sorted);
  };

  const handleDelete = (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    onDeleteConversation(conversationId);
    loadConversations();
  };

  return (
    <div className="w-[280px] border-r border-gray-800 bg-gray-950 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-800">
        <Button onClick={onNewConversation} className="w-full" size="lg">
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
                      className="opacity-0 group-hover:opacity-100 transition-opacity"
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
  );
}
