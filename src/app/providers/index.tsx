import type { FC, ReactNode } from 'react';
import { AppProvider } from './AppContext';

export * from './AppContext';

interface AppProvidersProps {
  children: ReactNode;
}

/**
 * Root providers wrapper for application-level contexts.
 */
export const AppProviders: FC<AppProvidersProps> = ({ children }) => {
  return <AppProvider>{children}</AppProvider>;
};
