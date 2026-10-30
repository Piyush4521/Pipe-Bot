import { forwardRef, type InputHTMLAttributes, type ReactNode } from 'react';
import { cn } from '@/utils/cn';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftAddon?: ReactNode;
  rightAddon?: ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      label,
      error,
      helperText,
      leftAddon,
      rightAddon,
      id,
      disabled,
      ...props
    },
    ref
  ) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

    return (
      <div className="w-full space-y-1.5">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-xs font-semibold uppercase tracking-wider text-industrial-700"
          >
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          {leftAddon && (
            <div className="absolute left-3 flex items-center pointer-events-none text-industrial-400">
              {leftAddon}
            </div>
          )}
          <input
            id={inputId}
            ref={ref}
            disabled={disabled}
            className={cn(
              'w-full bg-white border border-industrial-300 rounded-sm text-sm text-industrial-900 placeholder:text-industrial-400 px-3 py-2 transition-colors focus:border-brand-orange focus:ring-1 focus:ring-brand-orange outline-none disabled:bg-industrial-100 disabled:cursor-not-allowed',
              leftAddon && 'pl-9',
              rightAddon && 'pr-9',
              error && 'border-status-critical focus:border-status-critical focus:ring-status-critical',
              className
            )}
            {...props}
          />
          {rightAddon && (
            <div className="absolute right-3 flex items-center pointer-events-none text-industrial-400">
              {rightAddon}
            </div>
          )}
        </div>
        {error && <p className="text-xs text-status-critical">{error}</p>}
        {!error && helperText && (
          <p className="text-xs text-industrial-500">{helperText}</p>
        )}
      </div>
    );
  }
);
Input.displayName = 'Input';
