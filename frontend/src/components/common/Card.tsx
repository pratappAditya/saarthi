import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'subtle' | 'interactive' | 'ai';
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'default',
  padding = 'md',
  className = '',
  ...props
}) => {
  const paddingStyles = {
    none: 'p-0',
    sm: 'p-3',
    md: 'p-5',
    lg: 'p-7'
  };

  const variantStyles = {
    default: 'bg-[var(--bg-surface)] border border-[var(--border-subtle)] shadow-[var(--shadow-card)]',
    elevated: 'bg-[var(--bg-surface-elevated)] border border-[var(--border-strong)] shadow-[var(--shadow-elevated)]',
    subtle: 'bg-[var(--bg-subtle)] border border-[var(--border-subtle)]',
    interactive: 'bg-[var(--bg-surface)] hover:bg-[var(--bg-surface-elevated)] border border-[var(--border-subtle)] hover:border-[var(--border-strong)] shadow-[var(--shadow-card)] transition-all duration-200 cursor-pointer',
    ai: 'bg-gradient-to-b from-[var(--bg-surface-elevated)] to-[var(--bg-surface)] border border-blue-500/25 shadow-[0_4px_24px_rgba(59,130,246,0.08)]'
  };

  return (
    <div
      className={`rounded-[var(--radius-lg)] transition-all ${paddingStyles[padding]} ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
