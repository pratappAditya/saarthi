import React, { useState, useEffect } from 'react';
import { researchApi } from '../api/adminApi';
import type { ResearchOverview, ResearchRunRecord } from '../types/admin';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { BookOpen, Database, Globe, RefreshCw, Layers, ShieldCheck } from 'lucide-react';

export const ResearchPage: React.FC = () => {
  const [overview, setOverview] = useState<ResearchOverview | null>(null);
  const [runs, setRuns] = useState<ResearchRunRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchResearchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [ovRes, runsRes] = await Promise.all([
        researchApi.getOverview(),
        researchApi.listRuns(50).catch(() => ({ status: 'ok', runs_count: 0, runs: [] }))
      ]);
      setOverview(ovRes);
      setRuns(runsRes.runs || []);
    } catch (err: any) {
      setError(err?.message || 'Failed to load research operations data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResearchData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-indigo-400" />
            Universal Research & Domain Intelligence
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Status of all 17 specialized research domain packs, cache utilization, external literature providers, and synthesis runs.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchResearchData} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {loading ? (
        <Card className="p-12 flex justify-center items-center">
          <LoadingSpinner size="lg" />
        </Card>
      ) : error ? (
        <Card className="p-8 text-center border-rose-900/40 bg-rose-950/20 text-rose-300">
          <p className="font-semibold">{error}</p>
          <Button variant="outline" size="sm" onClick={fetchResearchData} className="mt-4">
            Retry
          </Button>
        </Card>
      ) : (
        <>
          {/* Top Metrics Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card orientation="none" className="p-5 border border-slate-800 bg-slate-900/60">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400">Domain Packs Loaded</span>
                <Layers className="w-4 h-4 text-indigo-400" />
              </div>
              <div className="text-2xl font-bold text-slate-100 mt-2">
                {overview?.total_domains || 17} Domains
              </div>
              <span className="text-[11px] text-emerald-400 mt-1 block">Full Domain Intelligence Suite</span>
            </Card>

            <Card orientation="none" className="p-5 border border-slate-800 bg-slate-900/60">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400">Synthesis Cache Entries</span>
                <Database className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-bold text-slate-100 mt-2">
                {overview?.cache_entries_count || 0}
              </div>
              <span className="text-[11px] text-slate-400 mt-1 block">Cached verified queries</span>
            </Card>

            <Card orientation="none" className="p-5 border border-slate-800 bg-slate-900/60">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400">Connected Source Providers</span>
                <Globe className="w-4 h-4 text-purple-400" />
              </div>
              <div className="text-2xl font-bold text-slate-100 mt-2">
                {overview?.active_providers?.length || 5} Providers
              </div>
              <span className="text-[11px] text-slate-400 mt-1 block">ArXiv, PubMed, OpenAlex, Search</span>
            </Card>
          </div>

          {/* Domain Packs Grid */}
          <div>
            <h2 className="text-base font-bold text-slate-200 mb-3 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-indigo-400" />
              Domain Knowledge Packs (17)
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {overview?.domains?.map((d) => (
                <div
                  key={d.id}
                  className="p-3.5 bg-slate-900/70 border border-slate-800 rounded-xl hover:border-slate-700 transition-colors"
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-semibold text-xs text-slate-100">{d.name}</span>
                    <Badge variant={d.tier === 'core' ? 'indigo' : 'purple'}>{d.tier}</Badge>
                  </div>
                  <p className="text-[11px] text-slate-400 line-clamp-2">{d.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Anonymized Research Runs History */}
          <div>
            <h2 className="text-base font-bold text-slate-200 mb-3 flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-indigo-400" />
              Recent Research Telemetry (Privacy Redacted)
            </h2>
            <Card orientation="none" className="overflow-hidden border border-slate-800">
              {runs.length === 0 ? (
                <div className="p-8 text-center text-xs text-slate-400">
                  No research runs logged in this evaluation window.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm text-slate-300">
                    <thead className="bg-slate-950/80 text-xs uppercase text-slate-400 font-semibold border-b border-slate-800">
                      <tr>
                        <th className="px-6 py-4">Run ID</th>
                        <th className="px-6 py-4">Domain Pack</th>
                        <th className="px-6 py-4">Evaluated Sources</th>
                        <th className="px-6 py-4">Status</th>
                        <th className="px-6 py-4">Timestamp</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {runs.map((r, i) => (
                        <tr key={r.id || i} className="hover:bg-slate-800/30 transition-colors">
                          <td className="px-6 py-4 font-mono text-xs text-indigo-300">{r.id}</td>
                          <td className="px-6 py-4">
                            <Badge variant="indigo">{r.domain || 'general'}</Badge>
                          </td>
                          <td className="px-6 py-4 text-xs font-semibold text-slate-200">
                            {r.sources_count} sources
                          </td>
                          <td className="px-6 py-4">
                            <Badge variant={r.status === 'completed' ? 'success' : 'neutral'}>
                              {r.status}
                            </Badge>
                          </td>
                          <td className="px-6 py-4 text-xs text-slate-400">
                            {new Date(r.timestamp).toLocaleString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>
          </div>
        </>
      )}
    </div>
  );
};
