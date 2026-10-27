import React from 'react';

interface ProgressProps {
  value: number; // 0 - 100
  max?: number;
  label?: string;
  sublabel?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg';
  variant?: 'default' | 'accent' | 'success' | 'warning' | 'danger' | 'ai';
  showPercentage?: boolean;
  className?: string;
}

export const Progress: React.FC<ProgressProps> = ({
  value,
  max = 100,
  label,
  sublabel,
  size = 'md',
  variant = 'accent',
  showPercentage = true,
  className = ''
}) => {
  const percentage = Math.min(100, Math.max(0, Math.round((value / max) * 100)));

  const sizeStyles = {
    xs: 'h-1',
    sm: 'h-1.5',
    md: 'h-2',
    lg: 'h-3'
  };

  const fillStyles = {
    default: 'bg-neutral-400',
    accent: 'bg-[var(--accent-primary)]',
    success: 'bg-emerald-500',
    warning: 'bg-amber-500',
    danger: 'bg-rose-500',
    ai: 'bg-gradient-to-r from-blue-500 via-indigo-500 to-cyan-400'
  };

  return (
    <div className={`w-full flex flex-col gap-1.5 ${className}`}>
      {(label || showPercentage) && (
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            {label && <span className="font-medium text-[var(--text-primary)]">{label}</span>}
            {sublabel && <span className="text-[11px] text-[var(--text-muted)] font-mono-code">{sublabel}</span>}
          </div>
          {showPercentage && (
            <span className="font-mono text-[11px] font-semibold text-[var(--text-secondary)]">{percentage}%</span>
          )}
        </div>
      )}
      <div className={`w-full bg-[var(--bg-surface-elevated)] border border-[var(--border-subtle)] rounded-full overflow-hidden ${sizeStyles[size]}`}>
        <div
          className={`h-full rounded-full transition-all duration-300 ${fillStyles[variant]}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
