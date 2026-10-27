import React, { useState } from 'react';
import {
  Search, BookOpen, ShieldCheck, HelpCircle, AlertTriangle,
  ExternalLink, Calendar, Layers, CheckCircle2, Split
} from 'lucide-react';
import { Badge } from '../common/Badge';

export interface EvidenceItemData {
  statement: string;
  classification: 'FACT' | 'SOURCE-DERIVED' | 'INFERENCE' | 'UNCERTAIN' | 'UNKNOWN';
  source_title: string;
  confidence: number;
  citation_url?: string;
  limitations?: string;
  domain_confidence_tier?: string;
}

export interface CitationData {
  citation_id: string;
  title: string;
  url?: string;
  publisher?: string;
  author?: string;
  publication_date?: string;
  supporting_passage?: string;
}

export interface ConflictData {
  conflict_id: string;
  topic: string;
  source_a_claim: string;
  source_b_claim: string;
  explanation: string;
  resolution_caveats: string;
}

interface ResearchPanelProps {
  question: string;
  subqueries?: string[];
  evidence?: EvidenceItemData[];
  citations?: CitationData[];
  conflicts?: ConflictData[];
  summary?: string;
  outputMode?: string;
  verificationStatus?: 'VERIFIED' | 'PARTIAL' | 'UNVERIFIED';
}

export const ResearchModePanel: React.FC<ResearchPanelProps> = ({
  question,
  subqueries = [],
  evidence = [],
  citations = [],
  conflicts = [],
  summary = '',
  outputMode = 'evidence_summary',
  verificationStatus = 'VERIFIED'
}) => {
  const [activeTab, setActiveTab] = useState<'evidence' | 'citations' | 'conflicts'>('evidence');

  return (
    <div className="bg-[#0b0f19] border border-blue-500/30 rounded-2xl p-4 space-y-4 font-mono text-xs shadow-2xl backdrop-blur-md">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-white/10 pb-3">
        <div className="flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-blue-400" />
          <span className="font-bold text-white text-sm tracking-wide">UNIVERSAL RESEARCH SYNTHESIS</span>
          <span className="px-2 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-300 text-[10px] uppercase">
            {outputMode.replace('_', ' ')}
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-[10px] text-emerald-400 font-semibold tracking-wider">
            {verificationStatus}
          </span>
        </div>
      </div>

      {/* Query Title */}
      <div className="bg-white/5 rounded-xl p-2.5 border border-white/10">
        <span className="text-[10px] text-gray-400 block mb-0.5">RESEARCH QUESTION:</span>
        <p className="text-white text-xs font-sans font-medium">{question}</p>
      </div>

      {/* Subqueries / Research Dimensions */}
      {subqueries.length > 0 && (
        <div className="space-y-1.5">
          <span className="text-[10px] text-gray-400 flex items-center gap-1">
            <Layers className="w-3 h-3 text-gray-400" />
            DECOMPOSED RESEARCH DIMENSIONS ({subqueries.length}):
          </span>
          <div className="flex flex-wrap gap-1.5">
            {subqueries.map((q, i) => (
              <span key={i} className="px-2.5 py-1 rounded-lg bg-blue-500/5 border border-blue-500/20 text-gray-300 text-[10px]">
                {q}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-white/10 pb-1">
        <button
          onClick={() => setActiveTab('evidence')}
          className={`px-3 py-1 rounded-lg transition-colors text-[11px] ${
            activeTab === 'evidence'
              ? 'bg-blue-600 text-white font-semibold'
              : 'text-gray-400 hover:text-white bg-white/5'
          }`}
        >
          Evidence ({evidence.length})
        </button>
        <button
          onClick={() => setActiveTab('citations')}
          className={`px-3 py-1 rounded-lg transition-colors text-[11px] ${
            activeTab === 'citations'
              ? 'bg-blue-600 text-white font-semibold'
              : 'text-gray-400 hover:text-white bg-white/5'
          }`}
        >
          Sources & Citations ({citations.length})
        </button>
        {conflicts.length > 0 && (
          <button
            onClick={() => setActiveTab('conflicts')}
            className={`px-3 py-1 rounded-lg transition-colors text-[11px] flex items-center gap-1 ${
              activeTab === 'conflicts'
                ? 'bg-amber-600 text-white font-semibold'
                : 'text-amber-400 hover:text-amber-300 bg-amber-500/10 border border-amber-500/20'
            }`}
          >
            <Split className="w-3 h-3" />
            Disagreements ({conflicts.length})
          </button>
        )}
      </div>

      {/* Tab 1: Evidence */}
      {activeTab === 'evidence' && (
        <div className="space-y-2">
          {evidence.map((item, idx) => {
            const badgeVariant =
              item.classification === 'FACT'
                ? 'success'
                : item.classification === 'INFERENCE'
                ? 'warning'
                : item.classification === 'UNCERTAIN'
                ? 'danger'
                : 'accent';

            return (
              <div key={idx} className="p-3 rounded-xl bg-white/5 border border-white/10 space-y-1.5 hover:border-blue-500/30 transition-all">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge variant={badgeVariant} size="xs">
                      {item.classification}
                    </Badge>
                    {item.domain_confidence_tier && (
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-white/10 text-gray-300 font-mono">
                        {item.domain_confidence_tier}
                      </span>
                    )}
                  </div>
                  <span className="text-[9px] text-gray-400">
                    Source: {item.source_title}
                  </span>
                </div>
                <p className="text-white text-xs leading-relaxed font-sans">{item.statement}</p>
                {item.limitations && (
                  <p className="text-[10px] text-amber-300/80 italic">
                    Caveat: {item.limitations}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Tab 2: Citations */}
      {activeTab === 'citations' && (
        <div className="space-y-2">
          {citations.length === 0 ? (
            <p className="text-gray-400 text-xs italic">No external citations available.</p>
          ) : (
            citations.map((c, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-white/5 border border-white/10 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold text-blue-400">[{c.citation_id}] {c.title}</span>
                  {c.publication_date && (
                    <span className="text-[9px] text-gray-400 flex items-center gap-1">
                      <Calendar className="w-2.5 h-2.5" />
                      {c.publication_date}
                    </span>
                  )}
                </div>
                {(c.author || c.publisher) && (
                  <div className="text-[10px] text-gray-400">
                    {c.author && <span>Author: {c.author} </span>}
                    {c.publisher && <span>| Publisher: {c.publisher}</span>}
                  </div>
                )}
                {c.url && (
                  <a
                    href={c.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[10px] text-blue-400 hover:text-blue-300 flex items-center gap-1 underline"
                  >
                    <ExternalLink className="w-2.5 h-2.5" />
                    {c.url}
                  </a>
                )}
                {c.supporting_passage && (
                  <p className="text-[10px] text-gray-300 bg-white/5 p-2 rounded-lg italic">
                    "{c.supporting_passage}"
                  </p>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Tab 3: Conflicts */}
      {activeTab === 'conflicts' && (
        <div className="space-y-2">
          {conflicts.map((conf, idx) => (
            <div key={idx} className="p-3 rounded-xl bg-amber-500/5 border border-amber-500/20 space-y-2">
              <div className="flex items-center gap-1.5 text-amber-300 font-semibold text-xs">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>{conf.topic}</span>
              </div>
              <div className="space-y-1 text-[11px]">
                <p className="text-gray-300"><span className="text-white font-medium">Claim A:</span> {conf.source_a_claim}</p>
                <p className="text-gray-300"><span className="text-white font-medium">Claim B:</span> {conf.source_b_claim}</p>
              </div>
              <p className="text-[10px] text-amber-200/90 bg-amber-500/10 p-2 rounded-lg">
                <span className="font-semibold">Context & Resolution:</span> {conf.explanation} — {conf.resolution_caveats}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Summary Box */}
      {summary && (
        <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-100 text-xs leading-relaxed font-sans whitespace-pre-line">
          {summary}
        </div>
      )}
    </div>
  );
};
