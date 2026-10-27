import React, { useState, useEffect } from 'react';
import { Activity, AlertTriangle } from 'lucide-react';

export function SystemStatusBadge() {
  const [healthy, setHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch('/api/health');
        const data = await res.json();
        setHealthy(data.status === 'healthy');
      } catch {
        setHealthy(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  if (healthy === null) return null;

  return (
    <div 
      className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono font-bold border transition ${
        healthy 
          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' 
          : 'bg-rose-500/10 text-rose-400 border-rose-500/30 animate-pulse'
      }`}
      title={healthy ? 'All Operational Systems Operational' : 'System Degraded'}
    >
      {healthy ? <Activity className="w-3 h-3 text-emerald-400" /> : <AlertTriangle className="w-3 h-3 text-rose-400" />}
      <span>{healthy ? 'SYSTEM OPERATIONAL' : 'DEGRADED'}</span>
    </div>
  );
}
