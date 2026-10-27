import React, { useState } from 'react';
import { 
  Table, 
  Search, 
  Download, 
  Filter, 
  ArrowUpDown, 
  ExternalLink, 
  Terminal, 
  CheckSquare, 
  Square,
  Plus
} from 'lucide-react';
import { useApp } from '../../../context/AppContext';
import type { ApplicationItem } from '../../../types';

export const ForgeApplications: React.FC = () => {
  const { applications, setApplications, addToast, setActiveSection } = useApp();
  const [query, setQuery] = useState('');
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [sortField, setSortField] = useState<keyof ApplicationItem>('matchScore');
  const [sortAsc, setSortAsc] = useState(false);

  const filtered = applications.filter(a => 
    a.company.toLowerCase().includes(query.toLowerCase()) ||
    a.role.toLowerCase().includes(query.toLowerCase()) ||
    a.stage.toLowerCase().includes(query.toLowerCase())
  ).sort((a, b) => {
    const valA = a[sortField] ?? '';
    const valB = b[sortField] ?? '';
    if (valA < valB) return sortAsc ? -1 : 1;
    if (valA > valB) return sortAsc ? 1 : -1;
    return 0;
  });

  const handleExportJSON = () => {
    const blob = new Blob([JSON.stringify(applications, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `pipeline-forge-export-${Date.now()}.json`;
    a.click();
    addToast({ type: 'success', title: 'Pipeline JSON Dump Generated' });
  };

  const toggleSelect = (id: string) => {
    setSelectedIds(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  };

  return (
    <div className="space-y-3 font-mono text-xs animate-in fade-in duration-200">
      {/* Top Query & Action Toolbar */}
      <div className="p-2.5 bg-[#0d1117] border border-[#21262d] rounded flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Table className="w-4 h-4 text-blue-400" />
          <span className="font-bold text-white">DATA_GRID: PIPELINE.DB</span>
          <span className="text-[10px] text-[#8b949e]">({filtered.length} records)</span>
        </div>

        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-[#6e7681] absolute left-2 top-2" />
            <input
              type="text"
              placeholder="query: select * where..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="pl-7 pr-3 py-1 rounded bg-[#161b22] border border-[#30363d] text-[11px] text-white focus:outline-none focus:border-blue-500 w-56 font-mono"
            />
          </div>

          <button
            onClick={handleExportJSON}
            className="px-2.5 py-1 rounded bg-[#21262d] hover:bg-[#30363d] text-white text-[11px] flex items-center gap-1 cursor-pointer"
          >
            <Download className="w-3 h-3" /> dump_json()
          </button>
        </div>
      </div>

      {/* Main Dense Table */}
      <div className="bg-[#0d1117] border border-[#21262d] rounded overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-[11px]">
            <thead>
              <tr className="bg-[#161b22] text-[#8b949e] border-b border-[#21262d] font-bold">
                <th className="py-2 px-3 w-8">#</th>
                <th className="py-2 px-2 cursor-pointer hover:text-white" onClick={() => { setSortField('company'); setSortAsc(!sortAsc); }}>
                  COMPANY {sortField === 'company' && (sortAsc ? '▲' : '▼')}
                </th>
                <th className="py-2 px-2">ROLE_SPEC</th>
                <th className="py-2 px-2 cursor-pointer hover:text-white" onClick={() => { setSortField('stage'); setSortAsc(!sortAsc); }}>
                  STAGE {sortField === 'stage' && (sortAsc ? '▲' : '▼')}
                </th>
                <th className="py-2 px-2 cursor-pointer hover:text-white" onClick={() => { setSortField('matchScore'); setSortAsc(!sortAsc); }}>
                  MATCH_SCORE {sortField === 'matchScore' && (sortAsc ? '▲' : '▼')}
                </th>
                <th className="py-2 px-2">COMPENSATION</th>
                <th className="py-2 px-2">LOCATION</th>
                <th className="py-2 px-3 text-right">OPERATIONS</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#21262d]/60 text-[#c9d1d9]">
              {filtered.map((app) => {
                const isChecked = selectedIds.includes(app.id);
                return (
                  <tr key={app.id} className="hover:bg-[#161b22]/70 transition-colors">
                    <td className="py-2 px-3">
                      <button onClick={() => toggleSelect(app.id)} className="text-[#8b949e] cursor-pointer">
                        {isChecked ? <CheckSquare className="w-3.5 h-3.5 text-blue-400" /> : <Square className="w-3.5 h-3.5" />}
                      </button>
                    </td>
                    <td className="py-2 px-2 font-bold text-white">{app.company}</td>
                    <td className="py-2 px-2 text-[#8b949e]">{app.role}</td>
                    <td className="py-2 px-2">
                      <span className={`px-1.5 py-0.5 rounded text-[10px] uppercase font-bold ${
                        app.stage === 'interview' ? 'bg-blue-500/20 text-blue-400' :
                        app.stage === 'offer' ? 'bg-emerald-500/20 text-emerald-400' :
                        app.stage === 'screening' ? 'bg-amber-500/20 text-amber-400' :
                        'bg-[#21262d] text-[#8b949e]'
                      }`}>
                        {app.stage}
                      </span>
                    </td>
                    <td className="py-2 px-2 font-bold text-emerald-400">{app.matchScore}%</td>
                    <td className="py-2 px-2 text-[#8b949e]">{app.salaryRange}</td>
                    <td className="py-2 px-2 text-[#6e7681]">{app.location}</td>
                    <td className="py-2 px-3 text-right space-x-1.5">
                      <button
                        onClick={() => setActiveSection('interviews')}
                        className="px-2 py-0.5 rounded bg-blue-600/20 hover:bg-blue-600/40 text-blue-300 text-[10px] cursor-pointer"
                      >
                        eval_prep()
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
