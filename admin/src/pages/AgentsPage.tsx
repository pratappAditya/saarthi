import React, { useState, useEffect, useMemo } from 'react';
import { agentsApi } from '../api/adminApi';
import type { AgentTaskRecord } from '../types/admin';
import { useAuth } from '../auth/AuthContext';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { SearchInput } from '../components/common/SearchInput';
import { Drawer } from '../components/common/Drawer';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Bot, RefreshCw, StopCircle, RotateCcw, ShieldAlert, Activity } from 'lucide-react';

export const AgentsPage: React.FC = () => {
  const { hasRole } = useAuth();
  const [activeTab, setActiveTab] = useState<'tasks' | 'permissions'>('tasks');
  const [tasks, setTasks] = useState<AgentTaskRecord[]>([]);
  const [pendingPermissions, setPendingPermissions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Diagnostics Drawer
  const [selectedTask, setSelectedTask] = useState<AgentTaskRecord | null>(null);
  const [diagnostics, setDiagnostics] = useState<any | null>(null);
  const [loadingDiag, setLoadingDiag] = useState(false);

  const fetchAgentData = async () => {
    setLoading(true);
    setError(null);
    try {
      if (activeTab === 'tasks') {
        const res = await agentsApi.listTasks();
        setTasks(res.tasks || []);
      } else {
        const res = await agentsApi.listPendingPermissions();
        setPendingPermissions(res.pending || []);
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch agent operations data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgentData();
  }, [activeTab]);

  const openDiagnostics = async (task: AgentTaskRecord) => {
    setSelectedTask(task);
    setLoadingDiag(true);
    try {
      const res = await agentsApi.getDiagnostics(task.task_id);
      setDiagnostics(res);
    } catch (err: any) {
      console.error('Error fetching diagnostics:', err);
    } finally {
      setLoadingDiag(false);
    }
  };

  const handleCancelTask = async (taskId: string) => {
    if (!confirm(`Are you sure you want to cancel agent task ${taskId}?`)) return;
    try {
      await agentsApi.cancelTask(taskId, 'Administrative task cancellation from control plane');
      alert(`Task ${taskId} cancelled.`);
      fetchAgentData();
      if (selectedTask?.task_id === taskId) {
        openDiagnostics(selectedTask);
      }
    } catch (err: any) {
      alert(`Failed to cancel task: ${err?.message || 'Unknown error'}`);
    }
  };

  const handleRecoverTask = async (taskId: string) => {
    try {
      await agentsApi.recoverTask(taskId, 'Administrative recovery triggered');
      alert(`Task ${taskId} recovery triggered.`);
      fetchAgentData();
      if (selectedTask?.task_id === taskId) {
        openDiagnostics(selectedTask);
      }
    } catch (err: any) {
      alert(`Failed to recover task: ${err?.message || 'Unknown error'}`);
    }
  };

  const handlePermissionAction = async (reqId: string, action: 'approve' | 'reject') => {
    try {
      await agentsApi.actionPermission(reqId, action, `Admin ${action} from control plane`);
      alert(`Permission request ${reqId} has been ${action}d.`);
      fetchAgentData();
    } catch (err: any) {
      alert(`Permission action failed: ${err?.message || 'Unknown error'}`);
    }
  };

  const filteredTasks = useMemo(() => {
    return tasks.filter((t) => {
      const matchesSearch =
        t.task_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (t.description && t.description.toLowerCase().includes(searchQuery.toLowerCase()));

      const matchesStatus = statusFilter === 'ALL' || t.status === statusFilter;

      return matchesSearch && matchesStatus;
    });
  }, [tasks, searchQuery, statusFilter]);

  const canManage = hasRole(['SUPER_ADMIN', 'ADMIN']);

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <Bot className="w-6 h-6 text-indigo-400" />
            Agent Operations & Step Diagnostics
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time tracking of agent task graphs, computer control step executions, failures, and security approvals.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={fetchAgentData} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-800">
        <nav className="flex space-x-6">
          <button
            onClick={() => setActiveTab('tasks')}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
              activeTab === 'tasks'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Activity className="w-4 h-4" />
            Agent Tasks ({tasks.length})
          </button>
          <button
            onClick={() => setActiveTab('permissions')}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
              activeTab === 'permissions'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <ShieldAlert className="w-4 h-4" />
            Pending Permissions ({pendingPermissions.length})
          </button>
        </nav>
      </div>

      {/* Tasks Tab Filter */}
      {activeTab === 'tasks' && (
        <Card orientation="none" className="p-4 bg-slate-900/60 border border-slate-800">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
            <div className="md:col-span-2">
              <SearchInput
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search agent tasks by ID or description..."
                onClear={() => setSearchQuery('')}
              />
            </div>
            <div>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="ALL">All Task Statuses</option>
                <option value="running">Running</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
          </div>
        </Card>
      )}

      {/* Main Tab Views */}
      {loading ? (
        <Card className="p-12 flex justify-center items-center">
          <LoadingSpinner size="lg" />
        </Card>
      ) : error ? (
        <Card className="p-8 text-center border-rose-900/40 bg-rose-950/20 text-rose-300">
          <p className="font-semibold">{error}</p>
          <Button variant="outline" size="sm" onClick={fetchAgentData} className="mt-4">
            Retry
          </Button>
        </Card>
      ) : activeTab === 'tasks' ? (
        filteredTasks.length === 0 ? (
          <Card className="p-12">
            <EmptyState
              icon={Bot}
              title="No agent tasks found"
              description={
                searchQuery || statusFilter !== 'ALL'
                  ? 'No agent tasks match the selected criteria.'
                  : 'No agent executions recorded yet.'
              }
            />
          </Card>
        ) : (
          <Card orientation="none" className="overflow-hidden border border-slate-800">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-950/80 text-xs uppercase text-slate-400 font-semibold border-b border-slate-800">
                  <tr>
                    <th className="px-6 py-4">Task ID</th>
                    <th className="px-6 py-4">Task Goal / Description</th>
                    <th className="px-6 py-4">Status</th>
                    <th className="px-6 py-4">Created</th>
                    <th className="px-6 py-4">Last Updated</th>
                    <th className="px-6 py-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {filteredTasks.map((t) => (
                    <tr key={t.task_id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-6 py-4 font-mono text-xs text-indigo-300">{t.task_id}</td>
                      <td className="px-6 py-4 font-medium text-slate-200 max-w-sm truncate">
                        {t.description || 'Autonomous Agent Execution'}
                      </td>
                      <td className="px-6 py-4">
                        <Badge
                          variant={
                            t.status === 'completed'
                              ? 'success'
                              : t.status === 'running'
                              ? 'indigo'
                              : t.status === 'failed'
                              ? 'danger'
                              : 'neutral'
                          }
                        >
                          {t.status}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 text-xs text-slate-400">
                        {t.created_at ? new Date(t.created_at).toLocaleTimeString() : '—'}
                      </td>
                      <td className="px-6 py-4 text-xs text-slate-400">
                        {t.updated_at ? new Date(t.updated_at).toLocaleTimeString() : '—'}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button variant="ghost" size="sm" onClick={() => openDiagnostics(t)}>
                            Diagnostics
                          </Button>
                          {canManage && t.status === 'running' && (
                            <Button
                              variant="danger"
                              size="sm"
                              onClick={() => handleCancelTask(t.task_id)}
                            >
                              <StopCircle className="w-3.5 h-3.5 mr-1" />
                              Cancel
                            </Button>
                          )}
                          {canManage && t.status === 'failed' && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleRecoverTask(t.task_id)}
                            >
                              <RotateCcw className="w-3.5 h-3.5 mr-1" />
                              Recover
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
        )
      ) : pendingPermissions.length === 0 ? (
        <Card className="p-12">
          <EmptyState
            icon={ShieldAlert}
            title="No pending security approvals"
            description="All sensitive actions and high-risk tool permissions have been reviewed or resolved."
          />
        </Card>
      ) : (
        <div className="space-y-4">
          {pendingPermissions.map((req) => (
            <Card key={req.request_id} className="p-5 border-amber-900/40 bg-amber-950/10">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <Badge variant="warning">Awaiting Approval</Badge>
                    <span className="font-mono text-xs text-slate-400">{req.request_id}</span>
                  </div>
                  <h3 className="text-base font-semibold text-slate-100 mt-2">
                    Tool Execution Request: {req.tool_name || req.action}
                  </h3>
                  <p className="text-xs text-slate-300 mt-1">
                    Requested by User: <span className="font-mono text-indigo-300">{req.user_id}</span> | Task:{' '}
                    <span className="font-mono text-slate-400">{req.task_id}</span>
                  </p>
                </div>
                {canManage && (
                  <div className="flex items-center gap-2">
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handlePermissionAction(req.request_id, 'reject')}
                    >
                      Reject
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => handlePermissionAction(req.request_id, 'approve')}
                    >
                      Approve Execution
                    </Button>
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Task Diagnostics Drawer */}
      <Drawer
        isOpen={Boolean(selectedTask)}
        onClose={() => {
          setSelectedTask(null);
          setDiagnostics(null);
        }}
        title="Agent Task Diagnostics"
        subtitle={selectedTask?.task_id || ''}
      >
        {loadingDiag ? (
          <div className="flex justify-center p-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : diagnostics ? (
          <div className="space-y-6">
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">Execution Status</span>
                <Badge
                  variant={
                    diagnostics.status === 'completed'
                      ? 'success'
                      : diagnostics.status === 'running'
                      ? 'indigo'
                      : 'danger'
                  }
                >
                  {diagnostics.status}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">Total Steps Recorded</span>
                <span className="text-sm font-semibold text-slate-200">{diagnostics.steps_count}</span>
              </div>
              {diagnostics.error_detail && (
                <div className="p-3 bg-rose-950/30 border border-rose-900/50 rounded-lg text-xs text-rose-300">
                  <div className="font-semibold mb-1">Execution Failure:</div>
                  {diagnostics.error_detail}
                </div>
              )}
            </div>

            {/* Execution Steps */}
            <div>
              <h3 className="text-xs font-semibold uppercase text-slate-400 tracking-wider mb-3">
                Execution Steps Timeline
              </h3>
              {!diagnostics.steps || diagnostics.steps.length === 0 ? (
                <div className="p-4 bg-slate-950 rounded-lg border border-slate-800 text-xs text-slate-400">
                  No individual step breakdown available.
                </div>
              ) : (
                <div className="space-y-2">
                  {diagnostics.steps.map((st: any, idx: number) => (
                    <div
                      key={idx}
                      className="p-3 bg-slate-950 rounded-lg border border-slate-800 flex items-center justify-between text-xs"
                    >
                      <div>
                        <span className="font-semibold text-slate-200">
                          Step {idx + 1}: {st.tool || st.action || 'Thinking'}
                        </span>
                        {st.timestamp && (
                          <span className="text-[11px] text-slate-500 block">
                            {new Date(st.timestamp).toLocaleTimeString()}
                          </span>
                        )}
                      </div>
                      <Badge variant={st.status === 'success' ? 'success' : 'neutral'}>
                        {st.status || 'ok'}
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ) : null}
      </Drawer>
    </div>
  );
};
