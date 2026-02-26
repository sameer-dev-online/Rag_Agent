'use client';

import { UploadCard } from '@/components/upload/UploadCard';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { useUserId } from '@/hooks/useUserId';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

/**
 * Upload page
 */
export default function UploadPage() {
  const { userId, isLoading } = useUserId();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner text="Loading..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-white">Upload Documents</h1>
          <Link href="/chat">
            <Button variant="outline">Back to Chat</Button>
          </Link>
        </div>

        {/* Upload card */}
        <UploadCard userId={userId} />
      </div>
    </div>
  );
}
