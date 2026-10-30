import { forwardRef, type HTMLAttributes, type ReactNode } from 'react';
import { cn } from '@/utils/cn';
import { Inbox } from 'lucide-react';

export interface EmptyStateProps extends HTMLAttributes<HTMLDivElement> {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
}

export const EmptyState = forwardRef<HTMLDivElement, EmptyStateProps>(
  (
    {
      className,
      icon = <Inbox className="w-8 h-8 text-industrial-400" />,
      title,
      description,
      action,
      ...props
    },
    ref
  ) => {
    return (
      <div
        ref={ref}
        className={cn(
          'flex flex-col items-center justify-center p-10 bg-white border border-dashed border-industrial-300 rounded-sm text-center',
          className
        )}
        {...props}
      >
        <div className="p-3 bg-industrial-100 rounded-sm mb-3">
          {icon}
        </div>
        <h4 className="text-sm font-semibold text-industrial-900 tracking-tight">
          {title}
        </h4>
        {description && (
          <p className="mt-1 text-xs text-industrial-500 max-w-sm">
            {description}
          </p>
        )}
        {action && <div className="mt-4">{action}</div>}
      </div>
    );
  }
);
EmptyState.displayName = 'EmptyState';
