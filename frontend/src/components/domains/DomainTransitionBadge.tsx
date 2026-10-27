import React, { useState } from 'react';

interface DomainTransitionBadgeProps {
  activeDomain: string;
  subdomains?: string[];
  isLocked?: boolean;
  onToggleLock?: (locked: boolean) => void;
  reason?: string;
}

export const DomainTransitionBadge: React.FC<DomainTransitionBadgeProps> = ({
  activeDomain,
  subdomains = [],
  isLocked = false,
  onToggleLock,
  reason = "Cross-domain intelligence routing active."
}) => {
  const [showTooltip, setShowTooltip] = useState(false);

  const displayList = subdomains.length > 0 ? subdomains : [activeDomain];

  return (
    <div className="relative inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/80 border border-indigo-500/30 text-xs font-mono text-slate-200 shadow-sm backdrop-blur-md">
      <span className="flex items-center gap-1.5 text-indigo-400 font-semibold">
        <svg className="w-3.5 h-3.5 animate-pulse text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        Saarthi:
      </span>

      <div className="flex items-center gap-1">
        {displayList.map((dom, idx) => (
          <React.Fragment key={idx}>
            {idx > 0 && <span className="text-slate-500 font-bold">→</span>}
            <span className={`px-2 py-0.5 rounded text-[11px] font-medium capitalize ${
              dom.toLowerCase() === activeDomain.toLowerCase()
                ? "bg-indigo-600/40 text-indigo-200 border border-indigo-400/40"
                : "bg-slate-700/50 text-slate-400"
            }`}>
              {dom}
            </span>
          </React.Fragment>
        ))}
      </div>

      <button
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        onClick={() => onToggleLock && onToggleLock(!isLocked)}
        className={`p-1 rounded transition-colors ${
          isLocked
            ? "text-amber-400 hover:bg-amber-500/20"
            : "text-slate-400 hover:text-slate-200 hover:bg-slate-700/50"
        }`}
        title={isLocked ? "Domain Locked (Click to unlock)" : "Auto-Domain Switching Active (Click to lock)"}
      >
        {isLocked ? (
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        ) : (
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" />
          </svg>
        )}
      </button>

      {showTooltip && (
        <div className="absolute top-full left-0 mt-2 w-64 p-2.5 rounded-lg bg-slate-900 border border-slate-700 text-[11px] text-slate-300 shadow-xl z-50">
          <div className="font-semibold text-indigo-400 mb-1">Automatic Domain Transition</div>
          <div>{reason}</div>
          <div className="mt-1.5 pt-1.5 border-t border-slate-800 text-[10px] text-slate-400">
            {isLocked ? "Explicitly locked to current domain." : "Saarthi will automatically transition domains based on step requirements."}
          </div>
        </div>
      )}
    </div>
  );
};
