import { useState, useEffect } from 'react';
import { LocalStorage } from '@/lib/storage';

/**
 * Hook to get or generate user ID from localStorage
 */
export function useUserId() {
  const [userId, setUserId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Get user ID on mount
    const id = LocalStorage.getUserId();
    setUserId(id);
    setIsLoading(false);
  }, []);

  return { userId, isLoading };
}
