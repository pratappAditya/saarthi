import React from 'react';
import type { LucideIcon } from 'lucide-react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  icon?: LucideIcon;
  rightElement?: React.ReactNode;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  hint,
  icon: Icon,
  rightElement,
  className = '',
  id,
  ...props
}) => {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className="w-full flex flex-col gap-1.5">
      {label && (
        <label htmlFor={inputId} className="text-xs font-medium text-[var(--text-secondary)] tracking-wide">
          {label}
        </label>
      )}
      <div className="relative flex items-center w-full">
        {Icon && (
          <div className="absolute left-3 text-[var(--text-muted)] pointer-events-none">
            <Icon className="w-4 h-4" />
          </div>
        )}
        <input
          id={inputId}
          className={`w-full bg-[var(--bg-subtle)] text-[var(--text-primary)] border border-[var(--border-subtle)] focus:border-[var(--border-focus)] focus:bg-[var(--bg-surface)] rounded-[var(--radius-md)] px-3.5 py-2 text-sm transition-all placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-blue-500/20 disabled:opacity-50 ${
            Icon ? 'pl-9' : ''
          } ${rightElement ? 'pr-10' : ''} ${error ? 'border-rose-500/80 focus:border-rose-500' : ''} ${className}`}
          {...props}
        />
        {rightElement && (
          <div className="absolute right-3 text-[var(--text-muted)]">
            {rightElement}
          </div>
        )}
      </div>
      {error && <span className="text-xs text-rose-400 font-medium">{error}</span>}
      {hint && !error && <span className="text-[11px] text-[var(--text-muted)]">{hint}</span>}
    </div>
  );
};

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export const Textarea: React.FC<TextareaProps> = ({
  label,
  error,
  hint,
  className = '',
  id,
  ...props
}) => {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className="w-full flex flex-col gap-1.5">
      {label && (
        <label htmlFor={inputId} className="text-xs font-medium text-[var(--text-secondary)] tracking-wide">
          {label}
        </label>
      )}
      <textarea
        id={inputId}
        className={`w-full bg-[var(--bg-subtle)] text-[var(--text-primary)] border border-[var(--border-subtle)] focus:border-[var(--border-focus)] focus:bg-[var(--bg-surface)] rounded-[var(--radius-md)] p-3 text-sm transition-all placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-blue-500/20 disabled:opacity-50 min-h-[100px] resize-y ${
          error ? 'border-rose-500/80 focus:border-rose-500' : ''
        } ${className}`}
        {...props}
      />
      {error && <span className="text-xs text-rose-400 font-medium">{error}</span>}
      {hint && !error && <span className="text-[11px] text-[var(--text-muted)]">{hint}</span>}
    </div>
  );
};
