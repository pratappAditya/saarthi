import React from 'react';

interface StatCardProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  subtext?: string;
  badge?: {
    text: string;
    variant: 'emerald' | 'blue' | 'amber' | 'rose' | 'slate' | 'cyan' | 'purple';
  };
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  icon,
  subtext,
  badge,
  className = ''
}) => {
  return (
    <div className={`p-4 bg-[#0d1118] border border-white/8 rounded-xl relative overflow-hidden shadow-md shadow-black/20 ${className}`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-slate-400">{label}</span>
        {icon && <div className="text-slate-400 p-1.5 bg-slate-800/60 rounded-lg">{icon}</div>}
      </div>
      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-xl font-bold font-mono tracking-tight text-slate-100">{value}</span>
        {badge && (
          <span
            className={`text-[10px] font-mono font-medium px-1.5 py-0.5 rounded border ${
              badge.variant === 'emerald'
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                : badge.variant === 'rose'
                ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                : badge.variant === 'amber'
                ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                : badge.variant === 'cyan'
                ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'
                : badge.variant === 'purple'
                ? 'bg-purple-500/10 text-purple-400 border-purple-500/20'
                : 'bg-blue-500/10 text-blue-400 border-blue-500/20'
            }`}
          >
            {badge.text}
          </span>
        )}
      </div>
      {subtext && <p className="text-[11px] text-slate-400 mt-1">{subtext}</p>}
    </div>
  );
};
