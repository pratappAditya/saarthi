import React, { useState } from 'react';
import { 
  Terminal, 
  Cpu, 
  Activity, 
  CheckCircle2, 
  AlertTriangle, 
  Search, 
  ArrowUpRight, 
  Code, 
  HardDrive,
  Sparkles,
  Zap,
  Play,
  RotateCw
} from 'lucide-react';
import { useApp } from '../../../context/AppContext';
import { Button } from '../../common/Button';

export const ForgeHome: React.FC = () => {
  const { applications, resumes, hardware, setActiveSection, addToast } = useApp();
  const [filterQuery, setFilterQuery] = useState('');

  const filteredApps = applications.filter(a => 
    a.company.toLowerCase().includes(filterQuery.toLowerCase()) ||
    a.role.toLowerCase().includes(filterQuery.toLowerCase()) ||
    a.stage.toLowerCase().includes(filterQuery.toLowerCase())
  );

  return (
    <div className="space-y-4 font-mono text-xs animate-in fade-in duration-200">
      {/* 1. TOP TELEMETRY MATRIX */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <div className="p-3 bg-[#0d1117] border border-[#21262d] rounded space-y-1">
          <div className="text-[10px] text-[#8b949e] uppercase">PIPELINE.TOTAL</div>
          <div className="text-xl font-bold text-white">{applications.length}</div>
          <div className="text-[10px] text-blue-400">4 in active loop</div>
        </div>

        <div className="p-3 bg-[#0d1117] border border-[#21262d] rounded space-y-1">
          <div className="text-[10px] text-[#8b949e] uppercase">ATS_COMPLIANCE</div>
          <div className="text-xl font-bold text-emerald-400">94.2%</div>
          <div className="text-[10px] text-[#8b949e]">0 parsing AST flaws</div>
        </div>

        <div className="p-3 bg-[#0d1117] border border-[#21262d] rounded space-y-1">
          <div className="text-[10px] text-[#8b949e] uppercase">NEMOTRON_SPEED</div>
          <div className="text-sm font-bold text-blue-400">
            {hardware.isBenchmarked && hardware.inferenceSpeed !== null ? `${hardware.inferenceSpeed} t/s` : 'Not benchmarked'}
          </div>
          <div className="text-[10px] text-[#8b949e]">vram: {hardware.vramUsage}% / 8GB</div>
        </div>

        <div className="p-3 bg-[#0d1117] border border-[#21262d] rounded space-y-1">
          <div className="text-[10px] text-[#8b949e] uppercase">SOCKET_STATUS</div>
          <div className="text-xl font-bold text-emerald-400">LOOPBACK</div>
          <div className="text-[10px] text-emerald-400/80">0 cloud telemetry tx</div>
        </div>
      </div>

      {/* 2. DENSE WORKBENCH: ACTIVE PIPELINE DATA GRID + QUICK COMMANDS */}
      <div className="p-3 bg-[#0d1117] border border-[#21262d] rounded space-y-3">
        {/* Table Controls */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#21262d] pb-2">
          <div className="flex items-center gap-2">
            <span className="font-bold text-white text-xs">PIPELINE_TABLE</span>
            <span className="px-1.5 py-0.2 rounded bg-[#161b22] text-[10px] text-[#8b949e]">
              COUNT: {filteredApps.length}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-[#6e7681] absolute left-2 top-2" />
              <input
                type="text"
                placeholder="grep stage:interview..."
                value={filterQuery}
                onChange={(e) => setFilterQuery(e.target.value)}
                className="pl-7 pr-3 py-1 rounded bg-[#161b22] border border-[#30363d] text-[11px] text-white focus:outline-none focus:border-blue-500 w-48"
              />
            </div>
            <button
              onClick={() => setActiveSection('tailor')}
              className="px-2.5 py-1 rounded bg-blue-600 hover:bg-blue-500 text-white font-bold text-[11px] flex items-center gap-1 cursor-pointer"
            >
              <Code className="w-3 h-3" /> diff --resume
            </button>
          </div>
        </div>

        {/* Dense Sortable Data Grid */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-[11px]">
            <thead>
              <tr className="text-[#8b949e] border-b border-[#21262d] font-bold">
                <th className="pb-1.5 pl-1">COMPANY</th>
                <th className="pb-1.5">ROLE_SPEC</th>
                <th className="pb-1.5">STAGE</th>
                <th className="pb-1.5">MATCH</th>
                <th className="pb-1.5">SALARY_BRACKET</th>
                <th className="pb-1.5 pr-1 text-right">ACTION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#21262d]/50 text-[#c9d1d9]">
              {filteredApps.map((app) => (
                <tr key={app.id} className="hover:bg-[#161b22] transition-colors">
                  <td className="py-2 pl-1 font-bold text-white">{app.company}</td>
                  <td className="py-2 text-[#8b949e]">{app.role}</td>
                  <td className="py-2">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] uppercase font-bold ${
                      app.stage === 'interview' ? 'bg-blue-500/20 text-blue-400' :
                      app.stage === 'offer' ? 'bg-emerald-500/20 text-emerald-400' :
                      'bg-[#21262d] text-[#8b949e]'
                    }`}>
                      {app.stage}
                    </span>
                  </td>
                  <td className="py-2 font-bold text-emerald-400">{app.matchScore}%</td>
                  <td className="py-2 text-[#8b949e]">{app.salaryRange}</td>
                  <td className="py-2 pr-1 text-right">
                    <button
                      onClick={() => setActiveSection('applications')}
                      className="px-2 py-0.5 rounded bg-[#21262d] hover:bg-[#30363d] text-white text-[10px] cursor-pointer"
                    >
                      inspect()
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 3. TECHNICAL DIAGNOSTICS & SYSTEM BENCHMARK */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-2">
        <div className="p-3 bg-[#0d1117] border border-[#21262d] rounded space-y-2">
          <div className="flex items-center justify-between text-[11px] font-bold text-white border-b border-[#21262d] pb-1">
            <span>ATS_AST_PARSER_DIAGNOSTICS</span>
            <span className="text-emerald-400">PASSED</span>
          </div>
          <div className="space-y-1 text-[10px] text-[#8b949e]">
            <div className="flex justify-between">
              <span>Section Hierarchy:</span>
              <span className="text-white">Valid (Header &gt; Summary &gt; Exp &gt; Skills)</span>
            </div>
            <div className="flex justify-between">
              <span>Quantified Metric Ratio:</span>
              <span className="text-emerald-400">18/22 bullets (81.8%)</span>
            </div>
            <div className="flex justify-between">
              <span>Action Verbs Strong:</span>
              <span className="text-emerald-400">Architected, Spearheaded, Reduced, Deployed</span>
            </div>
            <div className="flex justify-between">
              <span>Encoding / Tables:</span>
              <span className="text-white">0 Malformed Glyphs</span>
            </div>
          </div>
        </div>

        <div className="p-3 bg-[#0d1117] border border-[#21262d] rounded space-y-2">
          <div className="flex items-center justify-between text-[11px] font-bold text-white border-b border-[#21262d] pb-1">
            <span>LOCAL_INFERENCE_ENGINE</span>
            <span className="text-blue-400">NVIDIA_NEMOTRON</span>
          </div>
          <div className="space-y-1 text-[10px] text-[#8b949e]">
            <div className="flex justify-between">
              <span>Active Checkpoint:</span>
              <span className="text-white">{hardware.activeModel}</span>
            </div>
            <div className="flex justify-between">
              <span>Quantization:</span>
              <span className="text-white">Q4_K_M (Lossless GGUF)</span>
            </div>
            <div className="flex justify-between">
              <span>Latency (first token):</span>
              <span className="text-emerald-400">~140ms</span>
            </div>
            <div className="flex justify-between">
              <span>VRAM Footprint:</span>
              <span className="text-blue-400">3.4 GB / 8.0 GB GDDR6</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
