import React, { useState, useEffect, useMemo } from 'react';
import { auditApi } from '../api/adminApi';
import type { AuditLogEvent } from '../types/admin';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { SearchInput } from '../components/common/SearchInput';
import { Drawer } from '../components/common/Drawer';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Shield, RefreshCw, Eye } from 'lucide-react';

export const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [actionFilter, setActionFilter] = useState('ALL');
  const [limit, setLimit] = useState(100);

  const [inspectedLog, setInspectedLog] = useState<AuditLogEvent | null>(null);

  const fetchLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await auditApi.listLogs(limit);
      setLogs(res.audit_logs || []);
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch audit logs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [limit]);

  const uniqueActions = useMemo(() => {
    const set = new Set<string>();
    logs.forEach((l) => {
      if (l.action) set.add(l.action);
    });
    return Array.from(set);
  }, [logs]);

  const filteredLogs = useMemo(() => {
    return logs.filter((l) => {
      const matchesSearch =
        (l.action && l.action.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (l.admin_id && l.admin_id.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (l.target && l.target.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (l.reason && l.reason.toLowerCase().includes(searchQuery.toLowerCase()));

      const matchesAction = actionFilter === 'ALL' || l.action === actionFilter;

      return matchesSearch && matchesAction;
    });
  }, [logs, searchQuery, actionFilter]);

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <Shield className="w-6 h-6 text-indigo-400" />
            Security & Operational Audit Trail
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Immutable log of all administrative interventions, entitlement overrides, plan updates, and security events.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={fetchLogs} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <select
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value={50}>Last 50</option>
            <option value={100}>Last 100</option>
            <option value={250}>Last 250</option>
          </select>
        </div>
      </div>

      {/* Filter / Search Bar */}
      <Card orientation="none" className="p-4 bg-slate-900/60 border border-slate-800">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
          <div className="md:col-span-2">
            <SearchInput
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by action, administrator, target ID, or audit reason..."
              onClear={() => setSearchQuery('')}
            />
          </div>
          <div>
            <select
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="ALL">All Recorded Actions</option>
              {uniqueActions.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
          </div>
        </div>
      </Card>

      {/* Audit Log Table */}
      {loading ? (
        <Card className="p-12 flex justify-center items-center">
          <LoadingSpinner size="lg" />
        </Card>
      ) : error ? (
        <Card className="p-8 text-center border-rose-900/40 bg-rose-950/20 text-rose-300">
          <p className="font-semibold">{error}</p>
          <Button variant="outline" size="sm" onClick={fetchLogs} className="mt-4">
            Retry
          </Button>
        </Card>
      ) : filteredLogs.length === 0 ? (
        <Card className="p-12">
          <EmptyState
            icon={Shield}
            title="No audit events found"
            description={
              searchQuery || actionFilter !== 'ALL'
                ? 'No audit records match the current filter criteria.'
                : 'No administrative actions have been logged yet.'
            }
          />
        </Card>
      ) : (
        <Card orientation="none" className="overflow-hidden border border-slate-800">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950/80 text-xs uppercase text-slate-400 font-semibold border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4">Timestamp</th>
                  <th className="px-6 py-4">Administrator</th>
                  <th className="px-6 py-4">Action</th>
                  <th className="px-6 py-4">Target / Entity</th>
                  <th className="px-6 py-4">Reason / Notes</th>
                  <th className="px-6 py-4 text-right">Inspection</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredLogs.map((log, idx) => (
                  <tr key={log.id || log.audit_id || idx} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4 text-xs font-mono text-slate-400 whitespace-nowrap">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-indigo-300">
                      {log.admin_id}
                    </td>
                    <td className="px-6 py-4">
                      <Badge
                        variant={
                          log.action?.includes('suspend') || log.action?.includes('delete') || log.action?.includes('ban')
                            ? 'danger'
                            : log.action?.includes('override') || log.action?.includes('update')
                            ? 'warning'
                            : 'indigo'
                        }
                      >
                        {log.action}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-slate-200">
                      {log.target || '—'}
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-300 max-w-xs truncate">
                      {log.reason || '—'}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setInspectedLog(log)}
                      >
                        <Eye className="w-3.5 h-3.5 mr-1" />
                        Inspect
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Audit Event Drawer */}
      <Drawer
        isOpen={Boolean(inspectedLog)}
        onClose={() => setInspectedLog(null)}
        title="Audit Event Details"
        subtitle={inspectedLog?.action || ''}
      >
        {inspectedLog && (
          <div className="space-y-6">
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">Timestamp</span>
                <span className="text-xs font-mono text-slate-200">
                  {new Date(inspectedLog.timestamp).toISOString()}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">Administrator Actor</span>
                <span className="text-xs font-mono text-indigo-300">{inspectedLog.admin_id}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">Action</span>
                <Badge variant="indigo">{inspectedLog.action}</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">Target</span>
                <span className="text-xs font-mono text-slate-200">{inspectedLog.target || 'N/A'}</span>
              </div>
              {inspectedLog.reason && (
                <div>
                  <span className="text-xs text-slate-400 block mb-1">Audit Reason</span>
                  <div className="p-2.5 bg-slate-900 rounded border border-slate-800 text-xs text-slate-200">
                    {inspectedLog.reason}
                  </div>
                </div>
              )}
            </div>

            {inspectedLog.previous_state_json && (
              <div>
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                  Previous State
                </span>
                <pre className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs font-mono text-slate-300 overflow-x-auto whitespace-pre-wrap">
                  {inspectedLog.previous_state_json}
                </pre>
              </div>
            )}

            {inspectedLog.resulting_state_json && (
              <div>
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                  Resulting State
                </span>
                <pre className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs font-mono text-slate-300 overflow-x-auto whitespace-pre-wrap">
                  {inspectedLog.resulting_state_json}
                </pre>
              </div>
            )}

            {inspectedLog.request_metadata_json && (
              <div>
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                  Request Metadata
                </span>
                <pre className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs font-mono text-slate-400 overflow-x-auto whitespace-pre-wrap">
                  {inspectedLog.request_metadata_json}
                </pre>
              </div>
            )}
          </div>
        )}
      </Drawer>
    </div>
  );
};
