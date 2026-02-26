import { useState, useEffect } from 'react';
import { isBrowser } from '@/lib/utils';

/**
 * Generic hook for SSR-safe localStorage access
 */
export function useLocalStorage<T>(key: string, initialValue: T): [T, (value: T) => void] {
  // State to store our value
  const [storedValue, setStoredValue] = useState<T>(initialValue);

  // Initialize from localStorage on mount
  useEffect(() => {
    if (!isBrowser()) return;

    try {
      const item = localStorage.getItem(key);
      if (item) {
        setStoredValue(JSON.parse(item));
      }
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
    }
  }, [key]);

  // Wrapped setValue function that persists to localStorage
  const setValue = (value: T) => {
    try {
      setStoredValue(value);

      if (isBrowser()) {
        localStorage.setItem(key, JSON.stringify(value));
      }
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue];
}
