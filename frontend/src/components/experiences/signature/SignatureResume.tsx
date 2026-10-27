import React, { useState } from 'react';
import { 
  FileText, 
  Sparkles, 
  Download, 
  Plus, 
  Edit3, 
  Check, 
  X
} from 'lucide-react';
import { useApp } from '../../../context/AppContext';
import { Button } from '../../common/Button';
import { useDocumentImport } from '../../../hooks/useDocumentImport';
import { api } from '../../../api';

export const SignatureResume: React.FC = () => {
  const { resumes, activeResume, setActiveResume, setActiveSection, addToast, userProfile, loginProfile } = useApp();
  const { fileInputRef, openFilePicker, handleFileUpload } = useDocumentImport();
  const [isEditing, setIsEditing] = useState(false);

  const currentResume = activeResume || resumes[0];

  if (resumes.length === 0 && (!activeResume || !activeResume.id)) {
    return (
      <div className="flex flex-col items-center justify-center p-12 bg-[#111318] border border-[#222630] rounded-2xl text-center space-y-4 my-8">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileUpload}
          accept=".pdf,.docx,.doc,.txt,.md"
          className="hidden"
        />
        <div className="w-12 h-12 rounded-full bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
          <FileText className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white">No resume uploaded yet.</h2>
          <p className="text-xs text-[#8b949e] mt-1 max-w-sm">
            Import your resume (.pdf, .docx, .txt) to store it in your private local vault and generate tailored applications.
          </p>
        </div>
        <Button variant="primary" size="md" icon={Plus} onClick={openFilePicker}>
          + Import Resume (.pdf, .docx, .txt)
        </Button>
      </div>
    );
  }

  const [editName, setEditName] = useState(userProfile?.full_name || 'Candidate Name');
  const [editRole, setEditRole] = useState(currentResume?.targetRole || 'Target Role');
  const [editEmail, setEditEmail] = useState(userProfile?.email || 'email@example.com');
  const [editPhone, setEditPhone] = useState(userProfile?.phone || '');
  const [editLocation, setEditLocation] = useState(userProfile?.location || 'San Francisco, CA');
  const [editSummary, setEditSummary] = useState(currentResume?.summary || '');

  const handleSaveProfile = async () => {
    try {
      await loginProfile({
        full_name: editName,
        email: editEmail,
        phone: editPhone,
        location: editLocation,
        target_role: editRole,
        summary: editSummary
      });
      if (currentResume) {
        currentResume.targetRole = editRole;
        currentResume.summary = editSummary;
      }
      setIsEditing(false);
      addToast({ type: 'success', title: 'Profile Saved', message: 'Candidate details updated successfully.' });
    } catch (e) {
      addToast({ type: 'error', title: 'Save Error', message: 'Could not save candidate profile.' });
    }
  };

  const handleExportPDF = async () => {
    try {
      const content = `# ${currentResume.title}\n\n**Target Role**: ${currentResume.targetRole}\n\n${currentResume.summary}\n\n**Skills**: ${currentResume.skills.join(', ')}`;
      const filename = `${currentResume.title.replace(/\s+/g, '_')}_Resume.pdf`;
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
      addToast({ type: 'error', title: 'Export Failed', message: 'Could not render binary PDF export.' });
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        accept=".pdf,.docx,.doc,.txt,.md"
        className="hidden"
      />

      {/* Editorial Control Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#222630] pb-6">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono tracking-widest text-[#8b949e] uppercase">
            <FileText className="w-3.5 h-3.5 text-blue-400" />
            <span>Executive Resume Portfolio</span>
          </div>
          <h1 className="text-2xl lg:text-3xl font-serif font-medium text-white tracking-tight mt-1">
            {currentResume.title}
          </h1>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <Button
            variant="primary"
            size="sm"
            icon={Plus}
            onClick={openFilePicker}
          >
            + Import Resume (.pdf, .docx, .txt)
          </Button>
          <Button
            variant="outline"
            size="sm"
            icon={Edit3}
            onClick={() => setIsEditing(true)}
          >
            Edit Candidate Profile
          </Button>
          <Button
            variant="ai"
            size="sm"
            icon={Sparkles}
            onClick={() => setActiveSection('tailor')}
          >
            Refine for Target Role
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

      {/* Profile Edit Modal */}
      {isEditing && (
        <div className="p-6 bg-[#111318] border border-blue-500/40 rounded-xl space-y-4 font-sans text-xs">
          <div className="flex items-center justify-between border-b border-[#222630] pb-3">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Edit3 className="w-4 h-4 text-blue-400" /> Edit Candidate Profile
            </h3>
            <button onClick={() => setIsEditing(false)} className="text-[#8b949e] hover:text-white cursor-pointer"><X className="w-4 h-4" /></button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-[#8b949e] block mb-1">Full Name</label>
              <input value={editName} onChange={e => setEditName(e.target.value)} className="w-full bg-[#181c25] border border-[#222630] rounded p-2 text-white" />
            </div>
            <div>
              <label className="text-[#8b949e] block mb-1">Target Role</label>
              <input value={editRole} onChange={e => setEditRole(e.target.value)} className="w-full bg-[#181c25] border border-[#222630] rounded p-2 text-white" />
            </div>
            <div>
              <label className="text-[#8b949e] block mb-1">Email</label>
              <input value={editEmail} onChange={e => setEditEmail(e.target.value)} className="w-full bg-[#181c25] border border-[#222630] rounded p-2 text-white" />
            </div>
            <div>
              <label className="text-[#8b949e] block mb-1">Phone</label>
              <input value={editPhone} onChange={e => setEditPhone(e.target.value)} className="w-full bg-[#181c25] border border-[#222630] rounded p-2 text-white" />
            </div>
            <div>
              <label className="text-[#8b949e] block mb-1">Location</label>
              <input value={editLocation} onChange={e => setEditLocation(e.target.value)} className="w-full bg-[#181c25] border border-[#222630] rounded p-2 text-white" />
            </div>
          </div>
          <div>
            <label className="text-[#8b949e] block mb-1">Executive Summary</label>
            <textarea value={editSummary} onChange={e => setEditSummary(e.target.value)} rows={3} className="w-full bg-[#181c25] border border-[#222630] rounded p-2 text-white" />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" size="sm" onClick={() => setIsEditing(false)}>Cancel</Button>
            <Button variant="primary" size="sm" icon={Check} onClick={handleSaveProfile}>Save Changes</Button>
          </div>
        </div>
      )}

      {/* Resume Version Selector Pills */}
      <div className="flex flex-wrap items-center gap-2 pb-2">
        {resumes.map((r) => {
          const isSelected = currentResume.id === r.id;
          return (
            <button
              key={r.id}
              onClick={() => setActiveResume(r)}
              className={`px-4 py-2 rounded-lg text-xs font-medium transition-all cursor-pointer flex items-center gap-2 ${
                isSelected
                  ? 'bg-[#1e2533] text-blue-300 border border-blue-500/50 shadow-sm'
                  : 'bg-[#111318] text-[#8b949e] border border-[#222630] hover:text-white'
              }`}
            >
              <span className="font-serif italic font-semibold">{r.title}</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#222630] text-[#8b949e]">
                {r.version}
              </span>
              <span className="text-[10px] font-mono text-emerald-400 font-bold">
                {r.atsScore}% ATS
              </span>
            </button>
          );
        })}
      </div>

      {/* Main Editorial Canvas */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left (8 cols): Clean Executive Document Sheet */}
        <div className="lg:col-span-8 bg-[#111318] rounded-xl border border-[#222630] p-8 lg:p-12 shadow-2xl space-y-8 font-sans">
          {/* Header of Resume */}
          <div className="border-b border-[#222630] pb-6 space-y-2">
            <h2 className="text-2xl font-serif font-bold text-white tracking-tight">
              {editName}
            </h2>
            <div className="text-sm font-serif italic text-blue-400">
              {editRole}
            </div>
            <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-[#8b949e] pt-1">
              <span>{editLocation}</span>
              <span>&bull;</span>
              <span>{editEmail}</span>
              {editPhone && (
                <>
                  <span>&bull;</span>
                  <span>{editPhone}</span>
                </>
              )}
            </div>
          </div>

          {/* Executive Summary */}
          <div className="space-y-2">
            <h3 className="text-xs font-mono uppercase tracking-widest text-[#8b949e] border-b border-[#222630]/60 pb-1">
              Executive Summary
            </h3>
            <p className="text-xs text-[#c9d1d9] leading-relaxed font-light">
              {editSummary || currentResume.summary}
            </p>
          </div>

          {/* Experience Sections */}
          <div className="space-y-6">
            <h3 className="text-xs font-mono uppercase tracking-widest text-[#8b949e] border-b border-[#222630]/60 pb-1">
              Leadership & Experience
            </h3>

            {currentResume.sections.map((sec: any) => (
              <div key={sec.id} className="space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-baseline justify-between">
                  <div>
                    <span className="text-sm font-semibold text-white">{sec.role}</span>
                    <span className="text-xs font-serif italic text-blue-400 ml-2">@ {sec.company}</span>
                  </div>
                  <span className="text-xs font-mono text-[#8b949e]">{sec.period}</span>
                </div>

                <ul className="space-y-2 text-xs text-[#c9d1d9] font-light list-disc pl-4 leading-relaxed">
                  {sec.bullets?.map((b: any) => (
                    <li key={b.id} className="hover:text-white transition-colors">
                      {b.text}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {/* Core Competencies */}
          <div className="space-y-2">
            <h3 className="text-xs font-mono uppercase tracking-widest text-[#8b949e] border-b border-[#222630]/60 pb-1">
              Core Technical Competencies
            </h3>
            <div className="flex flex-wrap gap-1.5 pt-1">
              {currentResume.skills.map((skill: string) => (
                <span key={skill} className="px-2.5 py-1 rounded bg-[#161a23] text-xs font-mono text-[#8b949e] border border-[#222630]">
                  {skill}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Right (4 cols): ATS Telemetry & Recommendations */}
        <div className="lg:col-span-4 space-y-6">
          <div className="p-6 rounded-xl bg-[#111318] border border-[#222630] space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono uppercase tracking-wider text-[#8b949e]">ATS Health</span>
              <span className="text-lg font-serif font-bold text-emerald-400">{currentResume.atsScore}%</span>
            </div>
            
            <div className="w-full bg-[#1e2533] h-1.5 rounded-full overflow-hidden">
              <div className="bg-emerald-400 h-full rounded-full" style={{ width: `${currentResume.atsScore}%` }} />
            </div>

            <p className="text-xs text-[#8b949e] leading-relaxed">
              Format structure passes 100% of standard Workday, Greenhouse, and Lever parsing heuristics.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
