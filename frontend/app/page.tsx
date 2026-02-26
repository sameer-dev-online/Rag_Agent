'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';

/**
 * Home page - redirects to chat
 */
export default function Home() {
  const router = useRouter();

  useEffect(() => {
    router.push('/chat');
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <LoadingSpinner />
    </div>
  );
}
