import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merges Tailwind and utility class names cleanly without collision.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

