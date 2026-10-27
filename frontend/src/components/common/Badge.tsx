import React from 'react';
import type { LucideIcon } from 'lucide-react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'accent' | 'success' | 'warning' | 'danger' | 'ai' | 'purple' | 'outline';
  size?: 'xs' | 'sm' | 'md';
  icon?: LucideIcon;
  dot?: boolean;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'sm',
  icon: Icon,
  dot = false,
  className = ''
}) => {
  const sizeStyles = {
    xs: 'text-[10px] px-1.5 py-0.5 gap-1 font-medium',
    sm: 'text-xs px-2.5 py-0.5 gap-1.5 font-medium',
    md: 'text-sm px-3 py-1 gap-2 font-medium'
  };

  const variantStyles = {
    default: 'bg-[var(--bg-surface-elevated)] text-[var(--text-secondary)] border border-[var(--border-subtle)]',
    accent: 'bg-[var(--accent-subtle)] text-[var(--accent-text)] border border-[var(--accent-primary)]/20',
    success: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
    warning: 'bg-amber-500/10 text-amber-400 border border-amber-500/20',
    danger: 'bg-rose-500/10 text-rose-400 border border-rose-500/20',
    purple: 'bg-purple-500/10 text-purple-400 border border-purple-500/20',
    ai: 'bg-blue-500/15 text-blue-300 border border-blue-400/30 shadow-[0_0_12px_rgba(59,130,246,0.15)]',
    outline: 'bg-transparent text-[var(--text-secondary)] border border-[var(--border-strong)]'
  };

  return (
    <span className={`inline-flex items-center rounded-full tracking-wide shrink-0 select-none ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}>
      {dot && (
        <span className="w-1.5 h-1.5 rounded-full bg-current shrink-0 animate-pulse" />
      )}
      {Icon && <Icon className="w-3.5 h-3.5 shrink-0" />}
      <span className="truncate">{children}</span>
    </span>
  );
};
