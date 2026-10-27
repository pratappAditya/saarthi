import React, { useState } from 'react';
import { 
  Zap, 
  Sparkles, 
  Download, 
  Plus
} from 'lucide-react';
import { useApp } from '../../../context/AppContext';
import { Button } from '../../common/Button';
import { useDocumentImport } from '../../../hooks/useDocumentImport';
import { api } from '../../../api';

export const PulseResume: React.FC = () => {
  const { resumes, selectedResume, setSelectedResume, addToast, setActiveSection, activeResume } = useApp();
  const { fileInputRef, openFilePicker, handleFileUpload } = useDocumentImport();
  const currentResume = activeResume || selectedResume || resumes[0];

  if (resumes.length === 0 && (!currentResume || !currentResume.id)) {
    return (
      <div className="flex flex-col items-center justify-center p-12 bg-[#12141a] border border-[#2b303c] rounded-2xl text-center space-y-4 my-6">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileUpload}
          accept=".pdf,.docx,.doc,.txt,.md"
          className="hidden"
        />
        <Zap className="w-8 h-8 text-amber-400" />
        <div>
          <h2 className="text-lg font-bold text-white">No resume uploaded yet.</h2>
          <p className="text-xs text-[#94a3b8] mt-1 max-w-sm">
            Import your document (.pdf, .docx, .txt) to launch high-momentum tailoring.
          </p>
        </div>
        <Button variant="primary" size="sm" icon={Plus} onClick={openFilePicker}>
          + Import Resume (.pdf, .docx, .txt)
        </Button>
      </div>
    );
  }

  const handleExportPDF = async () => {
    try {
      const content = `# ${currentResume.title}\n\n**Target Role**: ${currentResume.targetRole}\n\n${currentResume.summary}\n\n**Skills**: ${currentResume.skills.join(', ')}`;
      const filename = `${currentResume.title.replace(/\s+/g, '_')}_Pulse.pdf`;
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
    <div className="space-y-6 animate-in fade-in duration-200">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        accept=".pdf,.docx,.doc,.txt,.md"
        className="hidden"
      />

      {/* Header with Quick Action Bar */}
      <div className="p-6 rounded-2xl bg-[#101524] border border-[#1c2438] flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-md">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-indigo-400 uppercase">
            <Zap className="w-4 h-4" />
            <span>Resume Studio &bull; Bullet Booster</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            {currentResume.title}
          </h1>
          <p className="text-xs text-[#94a3b8] mt-0.5">
            Optimize bullet impact scores and inject high-yield ATS keywords in seconds.
          </p>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <Button
            variant="primary"
            size="sm"
            icon={Plus}
            onClick={openFilePicker}
          >
            + Import Resume
          </Button>
          <Button 
            variant="ai" 
            size="sm" 
            icon={Sparkles}
            onClick={() => setActiveSection('tailor')}
          >
            Boost Bullet Points
          </Button>
          <Button
            variant="outline"
            size="sm"
            icon={Download}
            onClick={handleExportPDF}
          >
            Export PDF
          </Button>
        </div>
      </div>

      <div className="p-6 bg-[#101524] border border-[#1c2438] rounded-2xl space-y-4">
        <h3 className="text-lg font-bold text-white">Extracted Summary</h3>
        <p className="text-xs text-[#94a3b8] leading-relaxed">{currentResume.summary}</p>
        <div className="flex flex-wrap gap-2 pt-2">
          {currentResume.skills.map(skill => (
            <span key={skill} className="px-3 py-1 bg-[#1a233a] text-indigo-300 rounded-full text-xs font-semibold border border-indigo-500/20">
              {skill}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};
