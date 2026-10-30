import type { FC, ReactNode } from 'react';
import { ToastProvider } from '@/components/ui/Toast';
import { AppProvider } from './AppContext';

export * from './AppContext';

interface AppProvidersProps {
  children: ReactNode;
}

/**
 * Root providers wrapper for application-level contexts.
 */
export const AppProviders: FC<AppProvidersProps> = ({ children }) => {
  return (
    <ToastProvider>
      <AppProvider>{children}</AppProvider>
    </ToastProvider>
  );
};
