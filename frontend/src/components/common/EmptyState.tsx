import React from 'react';
import type { LucideIcon } from 'lucide-react';
import { ShieldCheck, Cpu } from 'lucide-react';
import { Button } from './Button';

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  secondaryLabel?: string;
  onSecondaryAction?: () => void;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon: Icon,
  title,
  description,
  actionLabel,
  onAction,
  secondaryLabel,
  onSecondaryAction,
  className = ''
}) => {
  return (
    <div className={`flex flex-col items-center justify-center text-center p-8 sm:p-12 border border-dashed border-[var(--border-strong)] rounded-[var(--radius-xl)] bg-[var(--bg-subtle)]/50 ${className}`}>
      <div className="w-12 h-12 rounded-2xl bg-[var(--bg-surface-elevated)] border border-[var(--border-subtle)] flex items-center justify-center text-[var(--text-secondary)] mb-4 shadow-sm">
        <Icon className="w-6 h-6" />
      </div>
      <h4 className="text-base font-semibold text-[var(--text-primary)] font-display-title mb-1.5">{title}</h4>
      <p className="text-xs text-[var(--text-secondary)] max-w-md mb-6 leading-relaxed">{description}</p>
      <div className="flex items-center gap-3">
        {actionLabel && onAction && (
          <Button variant="primary" size="sm" onClick={onAction}>
            {actionLabel}
          </Button>
        )}
        {secondaryLabel && onSecondaryAction && (
          <Button variant="secondary" size="sm" onClick={onSecondaryAction}>
            {secondaryLabel}
          </Button>
        )}
      </div>
    </div>
  );
};

interface ErrorStateProps {
  title: string;
  description: string;
  errorCode?: string;
  onRetry?: () => void;
  onDiagnose?: () => void;
  actionLabel?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title,
  description,
  errorCode,
  onRetry,
  onDiagnose,
  actionLabel = 'Retry Local Connection'
}) => {
  return (
    <div className="p-6 rounded-[var(--radius-lg)] border border-rose-500/30 bg-rose-950/20 flex flex-col sm:flex-row items-start gap-4">
      <div className="p-2.5 rounded-[var(--radius-md)] bg-rose-500/10 border border-rose-500/20 text-rose-400 shrink-0">
        <Cpu className="w-5 h-5" />
      </div>
      <div className="flex-1">
        <div className="flex items-center gap-2 mb-1">
          <h4 className="text-sm font-semibold text-rose-200">{title}</h4>
          {errorCode && (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-900/50 text-rose-300 border border-rose-700/40">
              {errorCode}
            </span>
          )}
        </div>
        <p className="text-xs text-rose-200/80 mb-3 leading-relaxed">{description}</p>
        <div className="flex items-center gap-2.5">
          {onRetry && (
            <Button variant="danger" size="xs" onClick={onRetry}>
              {actionLabel}
            </Button>
          )}
          {onDiagnose && (
            <Button variant="outline" size="xs" onClick={onDiagnose}>
              Run Local Diagnostics
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export const LocalAIBadge: React.FC<{ modelName?: string; tokensPerSec?: number; className?: string }> = ({
  modelName = 'Nemotron 4B',
  tokensPerSec = 64,
  className = ''
}) => {
  return (
    <div className={`inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-[var(--bg-surface-elevated)] border border-[var(--border-subtle)] text-[11px] font-mono select-none ${className}`}>
      <span className="flex items-center gap-1 text-emerald-400 font-medium">
        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
        <span>100% PRIVATE</span>
      </span>
      <span className="text-[var(--text-muted)]">•</span>
      <span className="text-[var(--text-secondary)] font-medium">{modelName}</span>
      {tokensPerSec > 0 && (
        <>
          <span className="text-[var(--text-muted)]">•</span>
          <span className="text-blue-400">{tokensPerSec} tok/s</span>
        </>
      )}
    </div>
  );
};
