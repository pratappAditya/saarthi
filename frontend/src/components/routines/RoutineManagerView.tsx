import React, { useState, useEffect } from 'react';
import { 
  Sparkles, Calendar, Clock, Play, Pause, RefreshCw, Trash2, Plus, AlertCircle, CheckCircle2, ShieldCheck, History, Eye, Copy, Zap
} from 'lucide-react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';
import { useApp } from '../../context/AppContext';
import { api } from '../../api';
import { RoutineBuilderView } from './RoutineBuilderView';

export const RoutineManagerView: React.FC = () => {
  const { addToast } = useApp();
  const [routines, setRoutines] = useState<any[]>([]);
  const [upcoming, setUpcoming] = useState<any[]>([]);
  const [executions, setExecutions] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<'routines' | 'upcoming' | 'history' | 'builder'>('routines');
  const [selectedRoutine, setSelectedRoutine] = useState<any | null>(null);

  useEffect(() => {
    loadRoutineData();
  }, []);

  const loadRoutineData = async () => {
    try {
      setLoading(true);
      const [rtnRes, upRes] = await Promise.all([
        api.getRoutines(),
        api.getUpcomingRoutines()
      ]);

      if (rtnRes && Array.isArray(rtnRes.routines)) {
        setRoutines(rtnRes.routines);
      }
      if (upRes && Array.isArray(upRes.upcoming)) {
        setUpcoming(upRes.upcoming);
      }
    } catch (e: any) {
      console.error("Failed to load routines:", e);
    } finally {
      setLoading(false);
    }
  };

  const handleRunNow = async (routineId: string, name: string) => {
    try {
      addToast({ type: 'info', title: 'Running Routine', message: `Executing routine '${name}'...` });
      const res = await api.runRoutine(routineId);
      if (res && res.execution) {
        addToast({
          type: res.execution.status === 'SUCCESS' ? 'success' : 'info',
          title: 'Execution Complete',
          message: `Routine '${name}' finished with status: ${res.execution.status}`
        });
        loadRoutineData();
      }
    } catch (e: any) {
      addToast({ type: 'error', title: 'Execution Failed', message: e.message });
    }
  };

  const handleTogglePause = async (routineId: string, currentStatus: string) => {
    try {
      if (currentStatus === 'ACTIVE') {
        await api.pauseRoutine(routineId);
        addToast({ type: 'info', title: 'Routine Paused', message: `Routine paused.` });
      } else {
        await api.resumeRoutine(routineId);
        addToast({ type: 'success', title: 'Routine Resumed', message: `Routine activated.` });
      }
      loadRoutineData();
    } catch (e: any) {
      addToast({ type: 'error', title: 'Action Failed', message: e.message });
    }
  };

  const handleDelete = async (routineId: string, name: string) => {
    if (!window.confirm(`Are you sure you want to delete routine '${name}'?`)) return;
    try {
      await api.deleteRoutine(routineId);
      addToast({ type: 'info', title: 'Routine Deleted', message: `Deleted '${name}'.` });
      loadRoutineData();
    } catch (e: any) {
      addToast({ type: 'error', title: 'Delete Failed', message: e.message });
    }
  };

  const handleInspectHistory = async (routine: any) => {
    setSelectedRoutine(routine);
    try {
      const res = await api.getRoutineExecutions(routine.id);
      if (res && Array.isArray(res.executions)) {
        setExecutions(res.executions);
        setActiveTab('history');
      }
    } catch (e: any) {
      addToast({ type: 'error', title: 'History Failed', message: e.message });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-xs font-mono text-gray-400">
        Loading Saarthi Routines & Automation Engine...
      </div>
    );
  }

  const activeRoutines = routines.filter(r => r.enabled && r.status === 'ACTIVE');
  const pausedRoutines = routines.filter(r => !r.enabled || r.status === 'PAUSED');
  const failedRoutines = routines.filter(r => r.status === 'FAILED' || (r.last_status === 'FAILED'));

  return (
    <div className="max-w-7xl mx-auto space-y-6 font-sans text-white p-2 animate-in fade-in duration-200">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-3 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-gradient-to-br from-purple-600/30 to-blue-600/30 border border-purple-500/40">
            <Zap className="w-6 h-6 text-purple-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-white">ROUTINES & AUTOMATION HUB</h1>
              <Badge variant="accent" size="sm">Phase 5J</Badge>
            </div>
            <p className="text-xs text-gray-400 mt-0.5 font-mono">
              Persistent scheduled & condition-triggered automation engine powered by AgentRuntime, Personalization, and Voice.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="primary" size="sm" icon={Plus} onClick={() => setActiveTab('builder')}>
            Create Routine
          </Button>
          <Button variant="outline" size="sm" icon={RefreshCw} onClick={loadRoutineData}>
            Refresh
          </Button>
        </div>
      </div>

      {/* Summary Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono text-xs">
        <Card variant="default" padding="md" className="space-y-2">
          <span className="text-gray-400 text-[10px]">ACTIVE ROUTINES</span>
          <p className="text-emerald-400 text-sm font-bold">{activeRoutines.length} Active</p>
          <span className="text-gray-500 text-[10px]">Persistent background schedules</span>
        </Card>

        <Card variant="default" padding="md" className="space-y-2">
          <span className="text-gray-400 text-[10px]">UPCOMING RUNS</span>
          <p className="text-purple-400 text-sm font-bold">{upcoming.length} Scheduled</p>
          <span className="text-gray-500 text-[10px]">Next: {upcoming[0] ? new Date(upcoming[0].next_run_at * 1000).toLocaleTimeString() : 'None'}</span>
        </Card>

        <Card variant="default" padding="md" className="space-y-2">
          <span className="text-gray-400 text-[10px]">PAUSED / STOPPED</span>
          <p className="text-amber-400 text-sm font-bold">{pausedRoutines.length} Paused</p>
          <span className="text-gray-500 text-[10px]">Manual or policy paused</span>
        </Card>

        <Card variant="default" padding="md" className="space-y-2">
          <span className="text-gray-400 text-[10px]">ATTENTION REQUIRED</span>
          <p className="text-rose-400 text-sm font-bold">{failedRoutines.length} Failed</p>
          <span className="text-gray-500 text-[10px]">Max retries exceeded</span>
        </Card>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-white/10 gap-4 font-mono text-xs">
        <button
          onClick={() => setActiveTab('routines')}
          className={`pb-2 border-b-2 transition-all cursor-pointer ${
            activeTab === 'routines' ? 'border-purple-500 text-white font-bold' : 'border-transparent text-gray-400 hover:text-white'
          }`}
        >
          All Routines ({routines.length})
        </button>
        <button
          onClick={() => setActiveTab('upcoming')}
          className={`pb-2 border-b-2 transition-all cursor-pointer ${
            activeTab === 'upcoming' ? 'border-purple-500 text-white font-bold' : 'border-transparent text-gray-400 hover:text-white'
          }`}
        >
          Upcoming Runs ({upcoming.length})
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={`pb-2 border-b-2 transition-all cursor-pointer ${
            activeTab === 'history' ? 'border-purple-500 text-white font-bold' : 'border-transparent text-gray-400 hover:text-white'
          }`}
        >
          Execution History
        </button>
        <button
          onClick={() => setActiveTab('builder')}
          className={`pb-2 border-b-2 transition-all cursor-pointer ${
            activeTab === 'builder' ? 'border-purple-500 text-white font-bold' : 'border-transparent text-gray-400 hover:text-white'
          }`}
        >
          + Create New Routine
        </button>
      </div>

      {/* TAB 1: ALL ROUTINES CARDS */}
      {activeTab === 'routines' && (
        <div className="space-y-4 font-mono">
          {routines.length === 0 ? (
            <div className="p-8 text-center border border-dashed border-white/10 rounded-2xl text-xs text-gray-400 space-y-3">
              <p>No routines created yet. Create a morning briefing, project review, or custom automation.</p>
              <Button variant="primary" size="sm" icon={Plus} onClick={() => setActiveTab('builder')}>
                Create First Routine
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              {routines.map((rtn) => (
                <div key={rtn.id} className="p-5 rounded-2xl bg-[#0e1426] border border-white/10 space-y-4 relative flex flex-col justify-between">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Badge variant={rtn.enabled && rtn.status === 'ACTIVE' ? 'success' : 'accent'} size="xs">
                          {rtn.status}
                        </Badge>
                        <span className="font-bold text-white text-sm">{rtn.name}</span>
                      </div>
                      <Badge variant="outline" size="xs">{rtn.trigger_type}</Badge>
                    </div>

                    <p className="text-gray-300 text-xs leading-relaxed">{rtn.description || rtn.natural_language_definition}</p>

                    <div className="grid grid-cols-2 gap-2 text-[10px] bg-black/40 p-2.5 rounded-xl border border-white/5">
                      <div>
                        <span className="text-gray-500 block">Next Run:</span>
                        <span className="text-purple-300 font-bold">
                          {rtn.next_run_at ? new Date(rtn.next_run_at * 1000).toLocaleString() : 'Manual / Event'}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500 block">Autonomy Level:</span>
                        <span className="text-emerald-300 font-bold">{rtn.autonomy_level}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-3 border-t border-white/10">
                    <button
                      onClick={() => handleInspectHistory(rtn)}
                      className="text-blue-400 hover:underline text-[10px] flex items-center gap-1 cursor-pointer"
                    >
                      <History className="w-3.5 h-3.5" /> History
                    </button>

                    <div className="flex items-center gap-2">
                      <Button variant="primary" size="sm" icon={Play} onClick={() => handleRunNow(rtn.id, rtn.name)}>
                        Run Now
                      </Button>
                      <button
                        onClick={() => handleTogglePause(rtn.id, rtn.status)}
                        className="p-1.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 hover:text-white cursor-pointer"
                        title={rtn.status === 'ACTIVE' ? 'Pause' : 'Resume'}
                      >
                        {rtn.status === 'ACTIVE' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 text-emerald-400" />}
                      </button>
                      <button
                        onClick={() => handleDelete(rtn.id, rtn.name)}
                        className="p-1.5 rounded-xl bg-white/5 border border-white/10 text-gray-400 hover:text-rose-400 cursor-pointer"
                        title="Delete routine"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: UPCOMING RUNS */}
      {activeTab === 'upcoming' && (
        <div className="space-y-4 font-mono text-xs">
          <span className="text-xs font-bold text-gray-300">UPCOMING SCHEDULED EXECUTION QUEUE</span>
          <div className="space-y-2">
            {upcoming.map((up, idx) => (
              <div key={idx} className="p-3.5 rounded-xl bg-[#0e1426] border border-white/10 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Clock className="w-4 h-4 text-purple-400" />
                  <div>
                    <span className="font-bold text-white">{up.name}</span>
                    <span className="text-gray-400 text-[10px] ml-2">Trigger: {up.trigger_type}</span>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-emerald-300 font-bold text-xs">{new Date(up.next_run_at * 1000).toLocaleString()}</span>
                  <Badge variant="outline" size="xs">{up.autonomy_level}</Badge>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 3: EXECUTION HISTORY */}
      {activeTab === 'history' && (
        <div className="space-y-4 font-mono text-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-300">
              EXECUTION TIMELINE {selectedRoutine ? `FOR '${selectedRoutine.name}'` : ''}
            </span>
            {selectedRoutine && (
              <button onClick={() => setSelectedRoutine(null)} className="text-blue-400 text-[10px] hover:underline cursor-pointer">
                Show All History
              </button>
            )}
          </div>

          {executions.length === 0 ? (
            <div className="p-6 text-center border border-dashed border-white/10 rounded-2xl text-gray-400">
              No executions recorded yet. Run a routine to inspect execution audit timeline.
            </div>
          ) : (
            <div className="space-y-3">
              {executions.map((ex) => (
                <div key={ex.execution_id} className="p-4 rounded-2xl bg-[#0e1426] border border-white/10 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge variant={ex.status === 'SUCCESS' ? 'success' : 'accent'} size="xs">
                        {ex.status}
                      </Badge>
                      <span className="font-bold text-white text-xs">{ex.execution_id}</span>
                    </div>
                    <span className="text-gray-400 text-[10px]">{new Date(ex.started_at * 1000).toLocaleString()}</span>
                  </div>

                  <p className="text-gray-300 text-xs">Trigger Source: <span className="text-purple-300 font-bold">{ex.trigger}</span></p>

                  {ex.actions_attempted && ex.actions_attempted.length > 0 && (
                    <div className="p-2.5 rounded-xl bg-black/40 border border-white/5 space-y-1">
                      <span className="text-gray-500 text-[10px] block font-bold">ACTIONS ATTEMPTED:</span>
                      {ex.actions_attempted.map((act: any, idx: number) => (
                        <div key={idx} className="text-emerald-300 text-[11px] flex items-center justify-between">
                          <span>- {act.description}</span>
                          <span className="text-gray-400 text-[10px]">[{act.status}]</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {ex.failure_reason && (
                    <div className="p-2 rounded-xl bg-rose-950/60 border border-rose-500/40 text-rose-300 text-[11px]">
                      Failure Reason: {ex.failure_reason}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 4: ROUTINE BUILDER */}
      {activeTab === 'builder' && (
        <RoutineBuilderView onSuccess={() => { loadRoutineData(); setActiveTab('routines'); }} />
      )}
    </div>
  );
};
