import { cn } from '@/lib/utils';

interface LoadingSpinnerProps {
  text?: string;
  className?: string;
}

/**
 * Reusable loading spinner with optional text
 */
export function LoadingSpinner({ text, className }: LoadingSpinnerProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-3 sm:gap-4 p-4', className)}>
      <div className="animate-spin rounded-full h-10 w-10 sm:h-12 sm:w-12 border-b-2 border-blue-600" />
      {text && <p className="text-xs sm:text-sm text-gray-400">{text}</p>}
    </div>
  );
}
