import React from 'react';

export type BadgeVariant =
  | 'emerald'
  | 'blue'
  | 'amber'
  | 'rose'
  | 'purple'
  | 'slate'
  | 'cyan'
  | 'indigo'
  | 'success'
  | 'warning'
  | 'danger'
  | 'neutral';

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  size?: 'xs' | 'sm';
  className?: string;
}

const variantStyles: Record<string, string> = {
  emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  success: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  indigo: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
  amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  warning: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  rose: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
  danger: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
  purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  slate: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
  neutral: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
  cyan: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'
};

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'slate',
  size = 'xs',
  className = ''
}) => {
  const sizeStyle = size === 'xs' ? 'px-2 py-0.5 text-[10px]' : 'px-2.5 py-1 text-xs';
  const colorStyle = variantStyles[variant] || variantStyles.slate;

  return (
    <span
      className={`inline-flex items-center font-medium font-mono uppercase tracking-wider rounded-md border ${sizeStyle} ${colorStyle} ${className}`}
    >
      {children}
    </span>
  );
};
