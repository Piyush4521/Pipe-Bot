import { forwardRef, type HTMLAttributes } from 'react';
import { cn } from '@/utils/cn';

export interface PageContainerProps extends HTMLAttributes<HTMLDivElement> {
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
}

export const PageContainer = forwardRef<HTMLDivElement, PageContainerProps>(
  ({ className, maxWidth = 'xl', children, ...props }, ref) => {
    const maxWidths = {
      sm: 'max-w-screen-sm',
      md: 'max-w-screen-md',
      lg: 'max-w-screen-lg',
      xl: 'max-w-screen-xl',
      '2xl': 'max-w-screen-2xl',
      full: 'max-w-full',
    };

    return (
      <main
        ref={ref}
        className={cn('w-full mx-auto px-4 sm:px-6 lg:px-8 py-6', maxWidths[maxWidth], className)}
        {...props}
      >
        {children}
      </main>
    );
  }
);
PageContainer.displayName = 'PageContainer';
