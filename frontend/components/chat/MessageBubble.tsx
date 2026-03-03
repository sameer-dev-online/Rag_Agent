'use client';

import { motion } from 'framer-motion';
import { formatTimestamp, cn } from '@/lib/utils';
import { UI_CONSTANTS } from '@/lib/constants';
import { MessageActions } from './MessageActions';
import type { Message } from '@/types';

interface MessageBubbleProps {
  message: Message;
  onRegenerate?: () => void;
}

/**
 * Message bubble with animation and actions
 */
export function MessageBubble({ message, onRegenerate }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: UI_CONSTANTS.MESSAGE_ANIMATION_DURATION }}
      className={cn('flex w-full group', isUser ? 'justify-end' : 'justify-start')}
    >
      <div className={cn('flex flex-col gap-1.5 sm:gap-2 max-w-[90%] sm:max-w-[85%] md:max-w-[80%]', isUser ? 'items-end' : 'items-start')}>
        <div
          className={cn(
            'rounded-2xl px-3 py-2.5 sm:px-4 sm:py-3 shadow-md',
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-gray-800 text-white border border-gray-700'
          )}
        >
          <p className="text-sm sm:text-base whitespace-pre-wrap break-words">{message.content}</p>
        </div>

        <div className="flex items-center gap-2 px-2">
          <span className="text-xs text-gray-500">{formatTimestamp(message.created_at)}</span>
          <MessageActions
            content={message.content}
            role={message.role}
            onRegenerate={onRegenerate}
          />
        </div>
      </div>
    </motion.div>
  );
}
