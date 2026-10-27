import React, { useState } from 'react';
import { Terminal, Cpu, Database, Layers, Shield, Sparkles, ChevronDown, ChevronUp } from 'lucide-react';

interface IntelligenceDebugPanelProps {
  debugData?: any;
}

export const IntelligenceDebugPanel: React.FC<IntelligenceDebugPanelProps> = ({ debugData }) => {
  const [isOpen, setIsOpen] = useState(false);

  // Render in development mode

  return (
    <div className="fixed bottom-3 left-3 z-40 font-mono text-[10px]">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="px-3 py-1.5 rounded-lg bg-[#101524] border border-blue-500/40 text-blue-300 hover:bg-blue-950/40 transition-all flex items-center gap-2 shadow-2xl cursor-pointer"
      >
        <Cpu className="w-3.5 h-3.5 text-blue-400" />
        <span>Intelligence Debug Panel</span>
        {isOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
      </button>

      {isOpen && (
        <div className="mt-2 w-96 p-3 rounded-xl bg-[#0b0f19] border border-blue-500/30 text-gray-300 space-y-2 shadow-2xl animate-in fade-in duration-200">
          <div className="flex items-center justify-between border-b border-white/10 pb-1.5 text-white font-bold">
            <span>Orchestration Diagnostics</span>
            <span className="text-emerald-400">DEV MODE</span>
          </div>

          <div className="space-y-1 text-[10px]">
            <p><strong>Selected Model:</strong> <span className="text-blue-400">{debugData?.selected_model || 'nemotron-3-nano:4b (Local)'}</span></p>
            <p><strong>Domain Classification:</strong> <span className="text-purple-400">{debugData?.domain || 'career'}</span></p>
            <p><strong>Plan Entitlement:</strong> <span className="text-emerald-400">{debugData?.context?.user_context?.plan_id?.toUpperCase() || 'POWER'}</span></p>
          </div>

          <div className="p-2 rounded bg-white/5 border border-white/10 space-y-1">
            <span className="text-gray-400 font-bold">Retrieved Context & Memories:</span>
            <ul className="list-disc list-inside text-gray-300 space-y-0.5 max-h-24 overflow-y-auto">
              {debugData?.context?.memory_context?.relevant_memories?.length > 0 ? (
                debugData.context.memory_context.relevant_memories.map((m: string, i: number) => (
                  <li key={i} className="truncate">{m}</li>
                ))
              ) : (
                <li>No memories retrieved for active query.</li>
              )}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
