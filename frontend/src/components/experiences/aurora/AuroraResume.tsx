import React from 'react';
import { 
  Sparkles, 
  Download, 
  Plus
} from 'lucide-react';
import { useApp } from '../../../context/AppContext';
import { Button } from '../../common/Button';
import { useDocumentImport } from '../../../hooks/useDocumentImport';
import { api } from '../../../api';

export const AuroraResume: React.FC = () => {
  const { resumes, activeResume, setActiveSection, addToast } = useApp();
  const { fileInputRef, openFilePicker, handleFileUpload } = useDocumentImport();
  const currentResume = activeResume || resumes[0];

  if (resumes.length === 0 && (!currentResume || !currentResume.id)) {
    return (
      <div className="flex flex-col items-center justify-center p-12 bg-white/5 backdrop-blur-xl border border-purple-500/20 rounded-3xl text-center space-y-4 my-6">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileUpload}
          accept=".pdf,.docx,.doc,.txt,.md"
          className="hidden"
        />
        <Sparkles className="w-8 h-8 text-purple-400" />
        <div>
          <h2 className="text-lg font-bold text-white">No resume uploaded yet.</h2>
          <p className="text-xs text-purple-200/70 mt-1 max-w-sm">
            Import your document (.pdf, .docx, .txt) to activate spatial AI resume workspace.
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
      const filename = `${currentResume.title.replace(/\s+/g, '_')}_Aurora.pdf`;
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
    <div className="space-y-6 animate-in fade-in duration-300">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        accept=".pdf,.docx,.doc,.txt,.md"
        className="hidden"
      />

      {/* Top Floating Glass Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 bg-[#0e1322]/80 backdrop-blur-xl border border-indigo-500/20 rounded-2xl">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 mb-1">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>AURORA SPATIAL RESUME CANVAS</span>
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight">
            {currentResume.title}
          </h1>
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
            variant="ai"
            size="sm"
            icon={Sparkles}
            onClick={() => setActiveSection('tailor')}
          >
            Tailor Spatial Resume
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

      <div className="p-6 bg-[#0e1322]/80 backdrop-blur-xl border border-indigo-500/20 rounded-2xl space-y-4">
        <h3 className="text-lg font-bold text-white">Spatial View: {currentResume.targetRole}</h3>
        <p className="text-xs text-slate-300 leading-relaxed">{currentResume.summary}</p>
        <div className="flex flex-wrap gap-2 pt-2">
          {currentResume.skills.map(skill => (
            <span key={skill} className="px-3 py-1 bg-indigo-950/60 text-cyan-300 rounded-lg text-xs font-mono border border-cyan-500/30">
              {skill}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};
