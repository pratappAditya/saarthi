import React from 'react';

interface CardProps {
  children: React.ReactNode;
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
  bodyClassName?: string;
  footer?: React.ReactNode;
  orientation?: string;
}

export const Card: React.FC<CardProps> = ({
  children,
  title,
  subtitle,
  action,
  className = '',
  bodyClassName = '',
  footer
}) => {
  return (
    <div className={`bg-[#0d1118] border border-white/8 rounded-xl overflow-hidden shadow-lg shadow-black/20 ${className}`}>
      {(title || action) && (
        <div className="px-5 py-4 border-b border-white/6 flex items-center justify-between gap-4 bg-slate-900/40">
          <div>
            {title && <h3 className="text-sm font-semibold text-slate-100">{title}</h3>}
            {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
          </div>
          {action && <div className="shrink-0">{action}</div>}
        </div>
      )}
      <div className={`p-5 ${bodyClassName}`}>{children}</div>
      {footer && (
        <div className="px-5 py-3 border-t border-white/6 bg-slate-900/60 text-xs text-slate-400">
          {footer}
        </div>
      )}
    </div>
  );
};
