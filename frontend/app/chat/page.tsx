'use client';

import { ChatLayout } from '@/components/chat/ChatLayout';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { useUserId } from '@/hooks/useUserId';

/**
 * Chat page
 */
export default function ChatPage() {
  const { userId, isLoading } = useUserId();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner text="Loading..." />
      </div>
    );
  }

  return <ChatLayout userId={userId} />;
}
