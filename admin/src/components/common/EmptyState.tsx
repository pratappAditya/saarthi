import React from 'react';
import { Inbox } from 'lucide-react';
import { Button } from './Button';

interface EmptyStateProps {
  icon?: React.ReactNode | React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
  action?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  actionText,
  onAction,
  action,
  className = ''
}) => {
  const renderIcon = () => {
    if (!icon) return <Inbox className="w-5 h-5" />;
    if (React.isValidElement(icon)) return icon;
    if (typeof icon === 'function') {
      const IconComponent = icon as React.ComponentType<{ className?: string }>;
      return <IconComponent className="w-5 h-5" />;
    }
    return <Inbox className="w-5 h-5" />;
  };

  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center rounded-xl border border-dashed border-white/10 bg-slate-900/20 ${className}`}>
      <div className="w-10 h-10 rounded-xl bg-slate-800/80 border border-white/5 flex items-center justify-center text-slate-400 mb-3">
        {renderIcon()}
      </div>
      <h4 className="text-sm font-semibold text-slate-200">{title}</h4>
      <p className="text-xs text-slate-400 max-w-sm mt-1 mb-4 leading-relaxed">{description}</p>
      {action}
      {actionText && onAction && !action && (
        <Button variant="secondary" size="sm" onClick={onAction}>
          {actionText}
        </Button>
      )}
    </div>
  );
};
