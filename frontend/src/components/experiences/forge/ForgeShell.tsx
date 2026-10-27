import React from 'react';
import { 
  Terminal, 
  Cpu, 
  Layers, 
  GitBranch, 
  FolderTree, 
  Code, 
  Play, 
  Settings, 
  ShieldCheck, 
  CreditCard, 
  Palette,
  Activity,
  FileCode,
  Table,
  CheckCircle2,
  Sliders,
  HardDrive
} from 'lucide-react';
import { useApp } from '../../../context/AppContext';
import type { NavSection } from '../../../types';
import { WindowsTitleBar } from '../../layout/WindowsTitleBar';

interface ForgeShellProps {
  children: React.ReactNode;
}

export const ForgeShell: React.FC<ForgeShellProps> = ({ children }) => {
  const { activeSection, setActiveSection, hardware } = useApp();

  const workspaceTree: { id: NavSection; label: string; path: string; icon: React.FC<{ className?: string }> }[] = [
    { id: 'home', label: 'telemetry.log', path: '~/workspace/status', icon: Activity },
    { id: 'career', label: 'roadmap.spec', path: '~/workspace/career', icon: GitBranch },
    { id: 'resumes', label: 'resume_v4.2.diff', path: '~/workspace/resumes', icon: FileCode },
    { id: 'tailor', label: 'ats_compiler.rs', path: '~/workspace/tailor', icon: Code },
    { id: 'applications', label: 'pipeline.db', path: '~/workspace/pipeline', icon: Table },
    { id: 'interviews', label: 'eval_runner.py', path: '~/workspace/interview-lab', icon: Terminal },
    { id: 'assistant', label: 'nemotron_cli.sh', path: '~/workspace/assistant', icon: Sliders },
  ];

  const systemTree: { id: NavSection; label: string; icon: React.FC<{ className?: string }> }[] = [
    { id: 'ai-models', label: 'models.gguf', icon: Cpu },
    { id: 'privacy', label: 'sandbox.rules', icon: ShieldCheck },
    { id: 'billing', label: 'license.key', icon: CreditCard },
    { id: 'settings', label: 'config.json', icon: Settings },
    { id: 'design-system', label: 'tokens.css', icon: Palette },
  ];

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#090b0e] text-[#c9d1d9] font-mono antialiased text-xs select-none">
      <WindowsTitleBar />

      {/* IDE Top Breadcrumb & Quick Action Bar */}
      <div className="h-8 bg-[#0d1117] border-b border-[#21262d] flex items-center justify-between px-3 text-[11px] text-[#8b949e]">
        <div className="flex items-center gap-2">
          <span className="text-blue-400 font-bold tracking-tight">SAARTHI_FORGE</span>
          <span>/</span>
          <span className="text-[#c9d1d9]">{activeSection}</span>
          <span>/</span>
          <span className="text-emerald-400 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            main*
          </span>
        </div>

        <div className="flex items-center gap-4 text-[10px]">
          <span className="text-[#8b949e]">HOTKEYS: <kbd className="px-1 py-0.5 rounded bg-[#161b22] border border-[#30363d] text-white">Ctrl+K</kbd> palette &bull; <kbd className="px-1 py-0.5 rounded bg-[#161b22] border border-[#30363d] text-white">Ctrl+J</kbd> copilot</span>
          <span className="text-blue-400 font-bold">{hardware.activeModel.split('/')[1] || 'nemotron-mini-4b'}</span>
        </div>
      </div>

      {/* Main Split: Tree Explorer + Editor View */}
      <div className="flex flex-1 overflow-hidden">
        {/* Compact IDE Tree Sidebar */}
        <aside className="w-56 bg-[#0d1117] border-r border-[#21262d] flex flex-col justify-between p-2 select-none shrink-0">
          <div className="space-y-4">
            {/* Tree Header */}
            <div className="px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-[#6e7681] flex items-center justify-between">
              <span>EXPLORER: CAREER_SYS</span>
              <FolderTree className="w-3 h-3 text-[#6e7681]" />
            </div>

            {/* Workspace Files */}
            <div className="space-y-0.5">
              <div className="px-2 text-[10px] text-[#8b949e] font-bold">src/career/</div>
              {workspaceTree.map((item) => {
                const Icon = item.icon;
                const isActive = activeSection === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveSection(item.id)}
                    className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-left transition-colors cursor-pointer ${
                      isActive
                        ? 'bg-[#1f242c] text-white font-bold border-l-2 border-blue-500 pl-1.5'
                        : 'text-[#8b949e] hover:text-[#c9d1d9] hover:bg-[#161b22]'
                    }`}
                  >
                    <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-blue-400' : 'text-[#6e7681]'}`} />
                    <span className="truncate">{item.label}</span>
                  </button>
                );
              })}
            </div>

            {/* System Config Files */}
            <div className="space-y-0.5 pt-2 border-t border-[#21262d]">
              <div className="px-2 text-[10px] text-[#8b949e] font-bold">config/sys/</div>
              {systemTree.map((item) => {
                const Icon = item.icon;
                const isActive = activeSection === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveSection(item.id)}
                    className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-left transition-colors cursor-pointer ${
                      isActive
                        ? 'bg-[#1f242c] text-white font-bold'
                        : 'text-[#8b949e] hover:text-[#c9d1d9] hover:bg-[#161b22]'
                    }`}
                  >
                    <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-blue-400' : 'text-[#6e7681]'}`} />
                    <span className="truncate">{item.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Local Host Diagnostics Box */}
          <div className="p-2 rounded bg-[#161b22] border border-[#21262d] space-y-1 text-[10px]">
            <div className="flex justify-between text-[#8b949e]">
              <span>OLLAMA DAEMON</span>
              <span className="text-emerald-400 font-bold">127.0.0.1:11434</span>
            </div>
            <div className="flex justify-between text-[#8b949e]">
              <span>VRAM USAGE</span>
              <span className="text-blue-400">{hardware.vramUsage}% (GDDR6)</span>
            </div>
            <div className="flex justify-between text-[#8b949e]">
              <span>SPEED</span>
              <span className="text-emerald-400">{hardware.isBenchmarked && hardware.inferenceSpeed !== null ? `${hardware.inferenceSpeed} tok/s` : 'Not benchmarked'}</span>
            </div>
          </div>
        </aside>

        {/* Technical Editor Main Panel */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-6 bg-[#090b0e]">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>

      {/* Bottom Technical Status Bar */}
      <footer className="h-6 bg-[#0d1117] border-t border-[#21262d] flex items-center justify-between px-3 text-[10px] text-[#6e7681] shrink-0">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1 text-emerald-400">
            <CheckCircle2 className="w-3 h-3" />
            0 SYNTAX ERRORS
          </span>
          <span>UTF-8</span>
          <span>LF</span>
          <span>SPACES: 2</span>
        </div>

        <div className="flex items-center gap-4 font-mono">
          <span className="text-[#8b949e]">CPU: 12 cores @ 4.2GHz</span>
          <span className="text-[#8b949e]">GPU: RTX 4070 (8GB)</span>
          <span className="text-emerald-400 font-bold">ZERO-CLOUD ENCLAVE: OK</span>
        </div>
      </footer>
    </div>
  );
};
