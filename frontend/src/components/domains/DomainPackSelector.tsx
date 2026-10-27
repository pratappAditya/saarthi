import React, { useState, useEffect } from 'react';
import { Layers, ChevronDown, Lock, RefreshCw, Check, Sparkles } from 'lucide-react';

export interface DomainPackItem {
  id: string;
  name: string;
  category: string;
  description: string;
}

interface SelectorProps {
  currentDomainId?: string;
  isLocked?: boolean;
  onSelectDomain: (domainId: string, lock: boolean) => void;
}

export const DomainPackSelector: React.FC<SelectorProps> = ({
  currentDomainId = 'general',
  isLocked = false,
  onSelectDomain
}) => {
  const [domains, setDomains] = useState<DomainPackItem[]>([]);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    fetch('/api/domains')
      .then(res => res.json())
      .then(data => {
        if (data.domains) setDomains(data.domains);
      })
      .catch(console.error);
  }, []);

  const activePack = domains.find(d => d.id === currentDomainId) || { name: 'General Companion', id: 'general' };

  return (
    <div className="relative font-mono text-xs">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 text-purple-300 transition-all cursor-pointer shadow-sm"
      >
        <Layers className="w-3.5 h-3.5 text-purple-400" />
        <span className="font-bold">Saarthi ● {activePack.name}</span>
        {isLocked ? <Lock className="w-3 h-3 text-amber-400 ml-1" /> : <RefreshCw className="w-3 h-3 text-blue-400 ml-1" />}
        <ChevronDown className="w-3.5 h-3.5 text-purple-400" />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-72 max-h-80 overflow-y-auto bg-[#0b0f19] border border-purple-500/30 rounded-2xl p-2 z-50 shadow-2xl space-y-1 backdrop-blur-md">
          <div className="px-2 py-1 flex items-center justify-between border-b border-white/10 text-[10px] text-gray-400">
            <span>SELECT DOMAIN INTELLIGENCE</span>
            <button
              onClick={() => { onSelectDomain('auto', false); setIsOpen(false); }}
              className="text-blue-400 hover:underline cursor-pointer"
            >
              Auto-Route
            </button>
          </div>

          {domains.map((d) => (
            <button
              key={d.id}
              onClick={() => { onSelectDomain(d.id, true); setIsOpen(false); }}
              className={`w-full text-left px-2.5 py-1.5 rounded-xl flex items-center justify-between transition-all cursor-pointer ${
                d.id === currentDomainId ? 'bg-purple-500/20 text-purple-200 font-bold border border-purple-500/30' : 'text-gray-300 hover:bg-white/5'
              }`}
            >
              <div>
                <div className="text-xs">{d.name}</div>
                <div className="text-[9px] text-gray-400 capitalize">{d.category}</div>
              </div>
              {d.id === currentDomainId && <Check className="w-3.5 h-3.5 text-purple-400" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
