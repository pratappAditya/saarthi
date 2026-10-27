import React, { useState, useEffect, useMemo } from 'react';
import { automationsApi } from '../api/adminApi';
import type { AutomationRecord, RoutineRecord } from '../types/admin';
import { useAuth } from '../auth/AuthContext';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { SearchInput } from '../components/common/SearchInput';
import { Drawer } from '../components/common/Drawer';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Cpu, Clock, Zap, RefreshCw, Power } from 'lucide-react';

export const AutomationsPage: React.FC = () => {
  const { hasRole } = useAuth();
  const [activeTab, setActiveTab] = useState<'automations' | 'routines'>('automations');
  const [automations, setAutomations] = useState<AutomationRecord[]>([]);
  const [routines, setRoutines] = useState<RoutineRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedItem, setSelectedItem] = useState<{ type: string; data: any } | null>(null);

  const fetchAutomations = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await automationsApi.list();
      setAutomations(res.automations || []);
      setRoutines(res.routines || []);
    } catch (err: any) {
      setError(err?.message || 'Failed to load automations and routines.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAutomations();
  }, []);

  const handleToggleRoutine = async (routine: RoutineRecord) => {
    try {
      await automationsApi.toggleRoutine(routine.id, 'Administrative routine status toggle');
      await fetchAutomations();
    } catch (err: any) {
      alert(`Failed to toggle routine: ${err?.message || 'Unknown error'}`);
    }
  };

  const filteredAutomations = useMemo(() => {
    return automations.filter((a) => {
      return (
        a.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        a.automation_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        a.domain?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        a.user_id.toLowerCase().includes(searchQuery.toLowerCase())
      );
    });
  }, [automations, searchQuery]);

  const filteredRoutines = useMemo(() => {
    return routines.filter((r) => {
      return (
        r.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.trigger_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.owner_user_id.toLowerCase().includes(searchQuery.toLowerCase())
      );
    });
  }, [routines, searchQuery]);

  const canManage = hasRole(['SUPER_ADMIN', 'ADMIN']);

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <Cpu className="w-6 h-6 text-indigo-400" />
            Automations & Scheduled Routines
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Operational visibility for Phase 9 unified automations, background triggers, schedules, and active execution loops.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={fetchAutomations} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-800">
        <nav className="flex space-x-6">
          <button
            onClick={() => setActiveTab('automations')}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
              activeTab === 'automations'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Zap className="w-4 h-4" />
            Unified Automations ({automations.length})
          </button>
          <button
            onClick={() => setActiveTab('routines')}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
              activeTab === 'routines'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Clock className="w-4 h-4" />
            Scheduled Routines ({routines.length})
          </button>
        </nav>
      </div>

      {/* Search Bar */}
      <Card orientation="none" className="p-4 bg-slate-900/60 border border-slate-800">
        <SearchInput
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder={`Search ${activeTab} by name, ID, user, or domain...`}
          onClear={() => setSearchQuery('')}
        />
      </Card>

      {/* List Content */}
      {loading ? (
        <Card className="p-12 flex justify-center items-center">
          <LoadingSpinner size="lg" />
        </Card>
      ) : error ? (
        <Card className="p-8 text-center border-rose-900/40 bg-rose-950/20 text-rose-300">
          <p className="font-semibold">{error}</p>
          <Button variant="outline" size="sm" onClick={fetchAutomations} className="mt-4">
            Retry
          </Button>
        </Card>
      ) : activeTab === 'automations' ? (
        filteredAutomations.length === 0 ? (
          <Card className="p-12">
            <EmptyState
              icon={Zap}
              title="No automations registered"
              description="No unified automations match your search filter or have been registered yet."
            />
          </Card>
        ) : (
          <Card orientation="none" className="overflow-hidden border border-slate-800">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-950/80 text-xs uppercase text-slate-400 font-semibold border-b border-slate-800">
                  <tr>
                    <th className="px-6 py-4">Automation</th>
                    <th className="px-6 py-4">Owner</th>
                    <th className="px-6 py-4">Domain</th>
                    <th className="px-6 py-4">Scope</th>
                    <th className="px-6 py-4">Status</th>
                    <th className="px-6 py-4">Next Run</th>
                    <th className="px-6 py-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {filteredAutomations.map((a) => (
                    <tr key={a.automation_id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-6 py-4">
                        <div className="font-medium text-slate-100">{a.name}</div>
                        <div className="text-xs font-mono text-slate-400 mt-0.5">{a.automation_id}</div>
                      </td>
                      <td className="px-6 py-4 font-mono text-xs text-slate-300">
                        {a.user_id}
                        {a.organization_id && (
                          <span className="block text-[11px] text-slate-500">Org: {a.organization_id}</span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <Badge variant="indigo">{a.domain || 'general'}</Badge>
                      </td>
                      <td className="px-6 py-4 text-xs text-slate-300 capitalize">
                        {a.scope || 'user'}
                      </td>
                      <td className="px-6 py-4">
                        <Badge variant={a.status === 'active' || a.enabled ? 'success' : 'neutral'}>
                          {a.status || (a.enabled ? 'active' : 'disabled')}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 text-xs text-slate-400">
                        {a.next_run_at ? new Date(a.next_run_at * 1000).toLocaleString() : 'Event-Driven'}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedItem({ type: 'Automation', data: a })}
                        >
                          Inspect
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )
      ) : filteredRoutines.length === 0 ? (
        <Card className="p-12">
          <EmptyState
            icon={Clock}
            title="No scheduled routines"
            description="No routines match your search filter or have been scheduled."
          />
        </Card>
      ) : (
        <Card orientation="none" className="overflow-hidden border border-slate-800">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950/80 text-xs uppercase text-slate-400 font-semibold border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4">Routine</th>
                  <th className="px-6 py-4">Owner</th>
                  <th className="px-6 py-4">Trigger Type</th>
                  <th className="px-6 py-4">Schedule</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredRoutines.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-medium text-slate-100">{r.name}</div>
                      <div className="text-xs font-mono text-slate-400 mt-0.5">{r.id}</div>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-slate-300">{r.owner_user_id}</td>
                    <td className="px-6 py-4">
                      <Badge variant="purple">{r.trigger_type}</Badge>
                    </td>
                    <td className="px-6 py-4 text-xs font-mono text-slate-300">
                      {r.schedule || 'N/A'} {r.timezone && `(${r.timezone})`}
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant={r.status === 'active' ? 'success' : 'neutral'}>
                        {r.status}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedItem({ type: 'Routine', data: r })}
                        >
                          Inspect
                        </Button>
                        {canManage && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleToggleRoutine(r)}
                          >
                            <Power className="w-3.5 h-3.5 mr-1" />
                            Toggle
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Drawer */}
      <Drawer
        isOpen={Boolean(selectedItem)}
        onClose={() => setSelectedItem(null)}
        title={`${selectedItem?.type} Inspection`}
        subtitle={selectedItem?.data?.name || selectedItem?.data?.id || ''}
      >
        {selectedItem && (
          <div className="space-y-4">
            <p className="text-xs text-slate-400">
              Sanitized configuration parameters for this execution node.
            </p>
            <pre className="p-4 bg-slate-950 rounded-xl border border-slate-800 text-xs font-mono text-slate-300 overflow-x-auto whitespace-pre-wrap">
              {JSON.stringify(selectedItem.data, null, 2)}
            </pre>
          </div>
        )}
      </Drawer>
    </div>
  );
};
