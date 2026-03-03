/**
 * Typing indicator with bouncing dots animation
 */
export function TypingIndicator() {
  return (
    <div className="flex items-center gap-2 p-3 sm:p-4 rounded-lg bg-gray-800 w-fit">
      <div className="flex gap-1">
        <div
          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
          style={{ animationDelay: '0ms' }}
        />
        <div
          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
          style={{ animationDelay: '150ms' }}
        />
        <div
          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
          style={{ animationDelay: '300ms' }}
        />
      </div>
      <span className="text-xs sm:text-sm text-gray-400">AI is typing...</span>
    </div>
  );
}
