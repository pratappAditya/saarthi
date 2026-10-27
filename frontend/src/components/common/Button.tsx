import React from 'react';
import type { LucideIcon } from 'lucide-react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'ai';
  size?: 'xs' | 'sm' | 'md' | 'lg';
  icon?: LucideIcon;
  iconPosition?: 'left' | 'right';
  isLoading?: boolean;
  shortcut?: string;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  icon: Icon,
  iconPosition = 'left',
  isLoading = false,
  shortcut,
  className = '',
  disabled,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-medium transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-blue-500/50 disabled:opacity-50 disabled:cursor-not-allowed select-none cursor-pointer whitespace-nowrap';

  const sizeStyles = {
    xs: 'text-xs px-2.5 py-1 gap-1.5 rounded-[var(--radius-sm)]',
    sm: 'text-xs px-3 py-1.5 gap-2 rounded-[var(--radius-sm)]',
    md: 'text-sm px-4 py-2 gap-2.5 rounded-[var(--radius-md)]',
    lg: 'text-base px-5 py-2.5 gap-3 rounded-[var(--radius-md)]'
  };

  const variantStyles = {
    primary: 'bg-[var(--accent-primary)] hover:bg-[var(--accent-primary-hover)] text-white shadow-sm active:scale-[0.98]',
    secondary: 'bg-[var(--bg-surface-elevated)] hover:bg-[var(--bg-surface-active)] text-[var(--text-primary)] border border-[var(--border-subtle)] active:scale-[0.98]',
    outline: 'bg-transparent hover:bg-[var(--bg-surface-elevated)] text-[var(--text-primary)] border border-[var(--border-strong)] active:scale-[0.98]',
    ghost: 'bg-transparent hover:bg-[var(--bg-surface-elevated)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] active:scale-[0.98]',
    danger: 'bg-rose-600/10 hover:bg-rose-600/20 text-rose-400 border border-rose-500/30 active:scale-[0.98]',
    ai: 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-md shadow-blue-900/30 border border-blue-400/30 active:scale-[0.98]'
  };

  return (
    <button
      className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      ) : (
        Icon && iconPosition === 'left' && <Icon className="w-4 h-4 shrink-0" />
      )}
      <span>{children}</span>
      {!isLoading && Icon && iconPosition === 'right' && <Icon className="w-4 h-4 shrink-0" />}
      {shortcut && (
        <kbd className="ml-1 px-1.5 py-0.5 text-[10px] uppercase font-mono tracking-wider bg-black/20 rounded border border-white/10 text-neutral-300">
          {shortcut}
        </kbd>
      )}
    </button>
  );
};
