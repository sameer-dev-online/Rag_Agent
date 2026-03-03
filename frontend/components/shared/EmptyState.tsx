import { cn } from '@/lib/utils';

interface EmptyStateProps {
  icon?: React.ReactNode;
  message: string;
  description?: string;
  className?: string;
}

/**
 * Empty state component for empty conversations/messages
 */
export function EmptyState({ icon, message, description, className }: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center gap-3 sm:gap-4 p-6 sm:p-8 text-center max-w-md mx-auto',
        className
      )}
    >
      {icon && <div className="text-gray-600 text-3xl sm:text-4xl">{icon}</div>}
      <div className="space-y-1.5 sm:space-y-2 px-4">
        <p className="text-base sm:text-lg font-medium text-gray-300">{message}</p>
        {description && <p className="text-xs sm:text-sm text-gray-500">{description}</p>}
      </div>
    </div>
  );
}
