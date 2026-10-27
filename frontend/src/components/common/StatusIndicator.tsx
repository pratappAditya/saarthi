import React from 'react';
import type { AIStatusType } from '../../types';

interface StatusIndicatorProps {
  status: AIStatusType | 'active' | 'inactive' | 'warning' | 'idle';
  label?: string;
  size?: 'xs' | 'sm' | 'md';
  pulse?: boolean;
  className?: string;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  label,
  size = 'sm',
  pulse = true,
  className = ''
}) => {
  const dotSizes = {
    xs: 'w-1.5 h-1.5',
    sm: 'w-2 h-2',
    md: 'w-2.5 h-2.5'
  };

  const getStatusConfig = () => {
    switch (status) {
      case 'ready':
      case 'active':
        return {
          dotClass: 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)]',
          textClass: 'text-emerald-400',
          defaultLabel: 'AI Ready (Local)'
        };
      case 'setting_up':
      case 'downloading':
        return {
          dotClass: 'bg-blue-400 shadow-[0_0_8px_rgba(96,165,250,0.6)]',
          textClass: 'text-blue-400',
          defaultLabel: status === 'downloading' ? 'Downloading Model...' : 'Setting Up Ollama...'
        };
      case 'model_update_available':
      case 'warning':
      case 'insufficient_resources':
        return {
          dotClass: 'bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.6)]',
          textClass: 'text-amber-400',
          defaultLabel: 'Resource Warning'
        };
      case 'offline':
      case 'inactive':
      case 'idle':
        return {
          dotClass: 'bg-neutral-500',
          textClass: 'text-neutral-400',
          defaultLabel: 'Engine Offline'
        };
      case 'error':
        return {
          dotClass: 'bg-rose-400 shadow-[0_0_8px_rgba(251,113,133,0.6)]',
          textClass: 'text-rose-400',
          defaultLabel: 'Engine Error'
        };
      default:
        return {
          dotClass: 'bg-neutral-400',
          textClass: 'text-neutral-300',
          defaultLabel: 'Unknown'
        };
    }
  };

  const config = getStatusConfig();
  const displayLabel = label || config.defaultLabel;

  return (
    <div className={`inline-flex items-center gap-2 select-none ${className}`}>
      <span className="relative flex items-center justify-center">
        {pulse && (status === 'ready' || status === 'downloading' || status === 'active') && (
          <span className={`absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping ${config.dotClass}`} />
        )}
        <span className={`relative inline-flex rounded-full ${dotSizes[size]} ${config.dotClass}`} />
      </span>
      {displayLabel && (
        <span className={`text-xs font-mono font-medium tracking-wide ${config.textClass}`}>
          {displayLabel}
        </span>
      )}
    </div>
  );
};
