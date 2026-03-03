import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import type { UploadProgress as UploadProgressType } from '@/types';

interface UploadProgressProps {
  upload: UploadProgressType;
  onRetry?: () => void;
}

/**
 * Upload progress indicator
 */
export function UploadProgress({ upload, onRetry }: UploadProgressProps) {
  const getStatusColor = () => {
    switch (upload.status) {
      case 'success':
        return 'text-green-500';
      case 'error':
        return 'text-red-500';
      case 'uploading':
        return 'text-blue-500';
      default:
        return 'text-gray-400';
    }
  };

  const getStatusText = () => {
    switch (upload.status) {
      case 'success':
        return 'Upload complete';
      case 'error':
        return upload.error || 'Upload failed';
      case 'uploading':
        return `Uploading... ${upload.progress}%`;
      default:
        return 'Pending';
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex items-start sm:items-center justify-between gap-2">
        <span className="text-xs sm:text-sm font-medium text-white truncate flex-1">{upload.file.name}</span>
        <span className={`text-xs ${getStatusColor()} shrink-0`}>{getStatusText()}</span>
      </div>

      {upload.status === 'uploading' && <Progress value={upload.progress} />}

      {upload.status === 'success' && upload.document && (
        <div className="flex items-center gap-3 sm:gap-4 text-xs text-gray-400">
          <span>{upload.document.num_chunks} chunks</span>
          <span>{Math.round(upload.document.content_length / 1024)} KB</span>
        </div>
      )}

      {upload.status === 'error' && onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry} className="w-full sm:w-auto">
          Retry
        </Button>
      )}
    </div>
  );
}
