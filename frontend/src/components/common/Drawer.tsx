import React, { useEffect } from 'react';
import { X } from 'lucide-react';

interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title?: React.ReactNode;
  subtitle?: string;
  children: React.ReactNode;
  width?: 'sm' | 'md' | 'lg' | 'xl';
  position?: 'right' | 'left';
}

export const Drawer: React.FC<DrawerProps> = ({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  width = 'md',
  position = 'right'
}) => {
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      window.addEventListener('keydown', handleEsc);
    }
    return () => {
      window.removeEventListener('keydown', handleEsc);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const widthStyles = {
    sm: 'w-80',
    md: 'w-[440px]',
    lg: 'w-[560px]',
    xl: 'w-[720px]'
  };

  const posStyles = position === 'right' 
    ? 'right-0 top-0 bottom-0 border-l animate-in slide-in-from-right duration-200' 
    : 'left-0 top-0 bottom-0 border-r animate-in slide-in-from-left duration-200';

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      <div 
        className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity"
        onClick={onClose}
      />
      <div 
        className={`fixed ${posStyles} ${widthStyles[width]} max-w-full bg-[var(--bg-surface)] border-[var(--border-strong)] shadow-2xl flex flex-col z-10`}
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--border-subtle)] shrink-0 bg-[var(--bg-surface-elevated)]/50">
          <div>
            {typeof title === 'string' ? (
              <h3 className="text-sm font-semibold text-[var(--text-primary)] font-display-title">{title}</h3>
            ) : (
              title
            )}
            {subtitle && <p className="text-[11px] text-[var(--text-secondary)] mt-0.5">{subtitle}</p>}
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-[var(--text-muted)] hover:text-[var(--text-primary)] rounded-[var(--radius-sm)] hover:bg-[var(--bg-surface-elevated)] transition-all cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
        <div className="p-5 overflow-y-auto flex-1 flex flex-col gap-4">
          {children}
        </div>
      </div>
    </div>
  );
};
