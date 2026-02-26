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
        'flex flex-col items-center justify-center gap-4 p-8 text-center',
        className
      )}
    >
      {icon && <div className="text-gray-600 text-4xl">{icon}</div>}
      <div className="space-y-2">
        <p className="text-lg font-medium text-gray-300">{message}</p>
        {description && <p className="text-sm text-gray-500">{description}</p>}
      </div>
    </div>
  );
}
