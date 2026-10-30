import { forwardRef, type HTMLAttributes } from 'react';
import { cn } from '@/utils/cn';

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'brand' | 'healthy' | 'warning' | 'critical' | 'outline';
  isMono?: boolean;
}

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = 'default', isMono = false, children, ...props }, ref) => {
    const base =
      'inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-sm border select-none uppercase tracking-wider';

    const variants = {
      default: 'bg-industrial-100 text-industrial-800 border-industrial-200',
      brand: 'bg-brand-orange-light text-brand-orange border-brand-orange-border',
      healthy: 'bg-status-healthy-bg text-status-healthy border-status-healthy-border',
      warning: 'bg-status-warning-bg text-status-warning border-status-warning-border',
      critical: 'bg-status-critical-bg text-status-critical border-status-critical-border',
      outline: 'bg-transparent text-industrial-700 border-industrial-300',
    };

    return (
      <span
        ref={ref}
        className={cn(base, variants[variant], isMono && 'font-mono text-[11px]', className)}
        {...props}
      >
        {children}
      </span>
    );
  }
);
Badge.displayName = 'Badge';
