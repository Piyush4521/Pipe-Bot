import { forwardRef, type SelectHTMLAttributes } from 'react';
import { cn } from '@/utils/cn';
import { ChevronDown } from 'lucide-react';

export interface SelectOption {
  label: string;
  value: string;
  disabled?: boolean;
}

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  helperText?: string;
  options?: SelectOption[];
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  (
    {
      className,
      label,
      error,
      helperText,
      options,
      children,
      id,
      disabled,
      ...props
    },
    ref
  ) => {
    const selectId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

    return (
      <div className="w-full space-y-1.5">
        {label && (
          <label
            htmlFor={selectId}
            className="block text-xs font-semibold uppercase tracking-wider text-industrial-700"
          >
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          <select
            id={selectId}
            ref={ref}
            disabled={disabled}
            className={cn(
              'w-full bg-white border border-industrial-300 rounded-sm text-sm text-industrial-900 px-3 py-2 pr-9 appearance-none transition-colors focus:border-brand-orange focus:ring-1 focus:ring-brand-orange outline-none disabled:bg-industrial-100 disabled:cursor-not-allowed',
              error && 'border-status-critical focus:border-status-critical',
              className
            )}
            {...props}
          >
            {options
              ? options.map((opt) => (
                  <option key={opt.value} value={opt.value} disabled={opt.disabled}>
                    {opt.label}
                  </option>
                ))
              : children}
          </select>
          <ChevronDown className="absolute right-3 w-4 h-4 text-industrial-400 pointer-events-none" />
        </div>
        {error && <p className="text-xs text-status-critical">{error}</p>}
        {!error && helperText && (
          <p className="text-xs text-industrial-500">{helperText}</p>
        )}
      </div>
    );
  }
);
Select.displayName = 'Select';
