import { useState } from 'react';
import { LocalStorage } from '@/lib/storage';
import { isBrowser } from '@/lib/utils';

/**
 * Hook to get or generate user ID from localStorage
 */
export function useUserId() {
  const [userId] = useState<string>(() => {
    // Initialize on client side only
    if (!isBrowser()) return '';
    return LocalStorage.getUserId();
  });

  // No async loading needed since we use lazy initialization
  const isLoading = false;

  return { userId, isLoading };
}
