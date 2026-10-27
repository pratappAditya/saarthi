import React, { useRef, useState } from 'react';
import {
  Paperclip,
  FileText,
  Image as ImageIcon,
  Trash2,
  CheckCircle2,
  AlertCircle,
  ScanText,
  Layers,
  Sparkles,
  X
} from 'lucide-react';
import { Badge } from '../common/Badge';

export interface AttachmentItem {
  id: string;
  filename: string;
  mime_type: string;
  size_bytes: number;
  content_type: string;
  extraction_status: string;
  page_count?: number;
  ocr_text?: string;
}

interface MultimodalBarProps {
  attachments: AttachmentItem[];
  onUpload: (file: File) => void;
  onRemove: (id: string) => void;
  loading?: boolean;
}

export const MultimodalAttachmentBar: React.FC<MultimodalBarProps> = ({
  attachments,
  onUpload,
  onRemove,
  loading = false
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      // Client-side quick check: 25 MB limit
      if (file.size > 25 * 1024 * 1024) {
        setErrorMessage(`"${file.name}" exceeds 25 MB limit (${(file.size / (1024 * 1024)).toFixed(1)} MB).`);
        return;
      }
      setErrorMessage(null);
      onUpload(file);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="space-y-2 font-mono text-xs">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept=".pdf,.docx,.doc,.txt,.md,image/png,image/jpeg,image/webp,image/*"
      />

      {/* Error notice banner */}
      {errorMessage && (
        <div className="flex items-center justify-between p-2 rounded-lg bg-rose-950/60 border border-rose-800 text-rose-300 text-[11px]">
          <span className="flex items-center gap-1.5">
            <AlertCircle className="w-3.5 h-3.5 shrink-0" />
            {errorMessage}
          </span>
          <button onClick={() => setErrorMessage(null)} className="text-rose-400 hover:text-white">
            <X className="w-3 h-3" />
          </button>
        </div>
      )}

      {/* Attachment Cards Grid */}
      {attachments.length > 0 && (
        <div className="flex flex-wrap gap-2 py-1">
          {attachments.map((att) => {
            const isDoc = att.content_type === 'document';
            const isImg = att.content_type === 'image';
            const hasOcr = Boolean(att.ocr_text && att.ocr_text.length > 0);
            const Icon = isImg ? ImageIcon : FileText;

            return (
              <div
                key={att.id}
                className="px-2.5 py-1.5 rounded-xl bg-slate-900/90 border border-slate-700/80 flex items-center gap-2 text-slate-200 shadow-sm"
              >
                <Icon className="w-3.5 h-3.5 text-cyan-400" />
                <span className="max-w-[140px] truncate font-bold text-[11px] text-white">
                  {att.filename}
                </span>
                <span className="text-[9px] text-slate-400">
                  ({(att.size_bytes / 1024).toFixed(0)}KB)
                </span>

                {att.page_count && att.page_count > 1 && (
                  <span className="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-cyan-300 flex items-center gap-0.5">
                    <Layers className="w-2.5 h-2.5" />
                    {att.page_count}p
                  </span>
                )}

                {hasOcr && (
                  <span className="text-[9px] px-1 py-0.2 rounded bg-indigo-950 border border-indigo-700 text-indigo-300 flex items-center gap-0.5">
                    <ScanText className="w-2.5 h-2.5" />
                    OCR
                  </span>
                )}

                <Badge variant={att.extraction_status === 'completed' ? 'success' : 'accent'} size="xs">
                  {att.extraction_status}
                </Badge>

                <button
                  onClick={() => onRemove(att.id)}
                  className="text-slate-400 hover:text-rose-400 transition-all cursor-pointer ml-1"
                  title="Remove attachment"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* Upload Action Button */}
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={loading}
          className="px-3 py-1.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white flex items-center gap-1.5 transition-all cursor-pointer text-xs"
        >
          <Paperclip className="w-3.5 h-3.5 text-cyan-400" />
          <span>{loading ? 'Processing Multimodal File...' : '+ Attach PDF / DOCX / Image / Scan'}</span>
          <span className="text-[10px] text-slate-500 font-sans">(Max 25 MB)</span>
        </button>
      </div>
    </div>
  );
};
