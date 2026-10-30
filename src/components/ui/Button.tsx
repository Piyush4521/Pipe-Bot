import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from 'react';
import { cn } from '@/utils/cn';
import { Loader2 } from 'lucide-react';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      leftIcon,
      rightIcon,
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    const baseStyles =
      'inline-flex items-center justify-center font-medium transition-colors select-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-orange focus-visible:ring-offset-1 disabled:opacity-50 disabled:pointer-events-none rounded-sm border';

    const variants = {
      primary:
        'bg-brand-orange border-brand-orange text-white hover:bg-brand-orange-hover active:bg-brand-orange-hover shadow-industrial-sm',
      secondary:
        'bg-industrial-900 border-industrial-900 text-white hover:bg-industrial-800 active:bg-industrial-950 shadow-industrial-sm',
      outline:
        'bg-white border-industrial-300 text-industrial-800 hover:bg-industrial-100 active:bg-industrial-200 shadow-industrial-sm',
      ghost:
        'bg-transparent border-transparent text-industrial-700 hover:bg-industrial-100 active:bg-industrial-200',
      danger:
        'bg-status-critical border-status-critical text-white hover:bg-red-700 active:bg-red-800 shadow-industrial-sm',
    };

    const sizes = {
      sm: 'h-8 px-3 text-xs gap-1.5',
      md: 'h-9 px-4 text-sm gap-2',
      lg: 'h-11 px-5 text-base gap-2.5',
    };

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      >
        {isLoading ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          leftIcon && <span className="inline-flex shrink-0">{leftIcon}</span>
        )}
        {children}
        {!isLoading && rightIcon && (
          <span className="inline-flex shrink-0">{rightIcon}</span>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';
