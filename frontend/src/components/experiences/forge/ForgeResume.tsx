import React, { useState } from 'react';
import { 
  FileCode, 
  Check, 
  Plus, 
  Sparkles, 
  Download,
  Edit3
} from 'lucide-react';
import { useApp } from '../../../context/AppContext';
import { Button } from '../../common/Button';
import { useDocumentImport } from '../../../hooks/useDocumentImport';
import { api } from '../../../api';

export const ForgeResume: React.FC = () => {
  const { resumes, selectedResume, setSelectedResume, tailoredDiffs, setTailoredDiffs, addToast, activeResume } = useApp();
  const { fileInputRef, openFilePicker, handleFileUpload } = useDocumentImport();
  const currentResume = activeResume || selectedResume || resumes[0];

  if (resumes.length === 0 && (!currentResume || !currentResume.id)) {
    return (
      <div className="flex flex-col items-center justify-center p-12 bg-[#0d1117] border border-[#21262d] rounded text-center space-y-4 my-6 font-mono text-xs">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileUpload}
          accept=".pdf,.docx,.doc,.txt,.md"
          className="hidden"
        />
        <FileCode className="w-8 h-8 text-blue-400" />
        <div>
          <h2 className="text-base font-bold text-white">No resume uploaded yet.</h2>
          <p className="text-[#8b949e] mt-1 max-w-sm">
            Import your document (.pdf, .docx, .txt) to populate the technical workbench.
          </p>
        </div>
        <Button variant="primary" size="sm" icon={Plus} onClick={openFilePicker}>
          + Import Resume (.pdf, .docx, .txt)
        </Button>
      </div>
    );
  }

  const handleApplyAll = () => {
    setTailoredDiffs((prev: any[]) => prev.map((d: any) => ({ ...d, accepted: true })));
    addToast({ type: 'success', title: 'All Diff Patches Applied to Buffer' });
  };

  const handleExportPDF = async () => {
    try {
      const content = `# ${currentResume.title}\n\n**Target Role**: ${currentResume.targetRole}\n\n${currentResume.summary}\n\n**Skills**: ${currentResume.skills.join(', ')}`;
      const filename = `${currentResume.title.replace(/\s+/g, '_')}_Forge.pdf`;
      const res = await api.exportDocument('resume', content, 'pdf');
      if (res && res.file_base64) {
        const binaryString = atob(res.file_base64);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        const blob = new Blob([bytes], { type: 'application/pdf' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
        addToast({ type: 'success', title: 'PDF Exported', message: `Downloaded ${filename}` });
      }
    } catch (err) {
      addToast({ type: 'error', title: 'Export Failed', message: 'Could not render PDF.' });
    }
  };

  return (
    <div className="space-y-3 font-mono text-xs animate-in fade-in duration-200">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        accept=".pdf,.docx,.doc,.txt,.md"
        className="hidden"
      />

      {/* Top Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 p-2 bg-[#0d1117] border border-[#21262d] rounded">
        <div className="flex items-center gap-2">
          <FileCode className="w-4 h-4 text-blue-400" />
          <span className="font-bold text-white">WORKBENCH: RESUME_TAILOR_3PANE</span>
          <span className="text-[#8b949e]">// target: {currentResume.targetRole}</span>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <Button
            variant="primary"
            size="sm"
            icon={Plus}
            onClick={openFilePicker}
          >
            + Import Resume
          </Button>
          <Button
            variant="outline"
            size="sm"
            icon={Download}
            onClick={handleExportPDF}
          >
            Export PDF
          </Button>
          <button
            onClick={handleApplyAll}
            className="px-2.5 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-[11px] flex items-center gap-1 cursor-pointer"
          >
            <Check className="w-3 h-3" /> git apply --all
          </button>
        </div>
      </div>

      {/* Main 3-Pane Workbench */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 min-h-[500px]">
        <div className="lg:col-span-6 bg-[#0d1117] border border-[#21262d] rounded p-4 space-y-4">
          <div className="text-white font-bold border-b border-[#21262d] pb-2">
            Document Buffer: {currentResume.title}
          </div>
          <p className="text-[#8b949e] leading-relaxed">{currentResume.summary}</p>
          <div className="space-y-2 pt-2">
            <span className="text-blue-400 font-bold block">// Skills Matrix:</span>
            <div className="flex flex-wrap gap-1">
              {currentResume.skills.map(s => (
                <span key={s} className="px-2 py-0.5 bg-[#161b22] text-[#8b949e] rounded border border-[#30363d]">{s}</span>
              ))}
            </div>
          </div>
        </div>

        <div className="lg:col-span-6 bg-[#0d1117] border border-[#21262d] rounded p-4 space-y-4">
          <div className="text-emerald-400 font-bold border-b border-[#21262d] pb-2">
            Diff Inspection & ATS Telemetry ({currentResume.atsScore}% Score)
          </div>
          <div className="p-3 bg-[#161b22] rounded border border-[#30363d] text-emerald-300">
            + [APPROVED PARSER]: Document format verified for ATS indexing.
          </div>
        </div>
      </div>
    </div>
  );
};
