import React, { useState, useEffect } from 'react';
import { settingsApi } from '../api/adminApi';
import type { FeatureFlagRecord, ToolPolicyRecord, MaintenanceModeRecord } from '../types/admin';
import { useAuth } from '../auth/AuthContext';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Modal } from '../components/common/Modal';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import {
  Settings,
  Flag,
  Shield,
  Sliders,
  Cpu,
  RefreshCw,
  Power,
  Plus,
  Trash2
} from 'lucide-react';

type SettingsTab = 'flags' | 'maintenance' | 'ai' | 'tools' | 'security';

export const SettingsPage: React.FC = () => {
  const { hasRole } = useAuth();
  const [activeTab, setActiveTab] = useState<SettingsTab>('flags');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Feature Flags State
  const [flags, setFlags] = useState<FeatureFlagRecord[]>([]);

  // Maintenance Mode State
  const [maintenance, setMaintenance] = useState<MaintenanceModeRecord | null>(null);
  const [maintMessage, setMaintMessage] = useState('');
  const [maintWhitelist, setMaintWhitelist] = useState('');
  const [updatingMaint, setUpdatingMaint] = useState(false);

  // AI Configuration State
  const [_aiConfig, setAiConfig] = useState<any | null>(null);
  const [aiProvider, setAiProvider] = useState('openai');
  const [aiModel, setAiModel] = useState('gpt-4o');
  const [aiTemp, setAiTemp] = useState(0.7);
  const [aiMaxTokens, setAiMaxTokens] = useState(4096);
  const [savingAi, setSavingAi] = useState(false);

  // Tool Policies State
  const [tools, setTools] = useState<ToolPolicyRecord[]>([]);

  // Security Bans State
  const [bans, setBans] = useState<any[]>([]);
  const [banModalOpen, setBanModalOpen] = useState(false);
  const [banIdentifier, setBanIdentifier] = useState('');
  const [banType, setBanType] = useState('ip');
  const [banReason, setBanReason] = useState('');
  const [submittingBan, setSubmittingBan] = useState(false);

  const fetchTabData = async () => {
    setLoading(true);
    setError(null);
    try {
      if (activeTab === 'flags') {
        const res = await settingsApi.listFeatureFlags();
        setFlags(res.flags || []);
      } else if (activeTab === 'maintenance') {
        const res = await settingsApi.getMaintenance();
        setMaintenance(res.maintenance);
        setMaintMessage(res.maintenance.message || '');
        setMaintWhitelist(res.maintenance.bypass_whitelist || '');
      } else if (activeTab === 'ai') {
        const res = await settingsApi.getAiConfig();
        setAiConfig(res.config);
        if (res.config) {
          setAiProvider(res.config.provider || 'openai');
          setAiModel(res.config.model_name || 'gpt-4o');
          setAiTemp(res.config.temperature ?? 0.7);
          setAiMaxTokens(res.config.max_tokens ?? 4096);
        }
      } else if (activeTab === 'tools') {
        const res = await settingsApi.listToolPolicies();
        setTools(res.tools || []);
      } else if (activeTab === 'security') {
        const res = await settingsApi.listBans();
        setBans(res.bans || []);
      }
    } catch (err: any) {
      setError(err?.message || `Failed to fetch ${activeTab} settings.`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTabData();
  }, [activeTab]);

  const handleToggleFlag = async (flag: FeatureFlagRecord) => {
    try {
      const isEnabled = typeof flag.enabled === 'boolean' ? flag.enabled : Boolean(flag.enabled);
      await settingsApi.updateFeatureFlag(flag.key, !isEnabled, flag.rollout_percentage);
      fetchTabData();
    } catch (err: any) {
      alert(`Failed to update feature flag: ${err?.message || 'Unknown error'}`);
    }
  };

  const handleToggleMaintenance = async () => {
    if (!maintenance) return;
    setUpdatingMaint(true);
    try {
      await settingsApi.toggleMaintenance(!maintenance.enabled, maintMessage, maintWhitelist);
      await fetchTabData();
      alert(`Maintenance mode ${!maintenance.enabled ? 'activated' : 'deactivated'}.`);
    } catch (err: any) {
      alert(`Failed to toggle maintenance mode: ${err?.message || 'Unknown error'}`);
    } finally {
      setUpdatingMaint(false);
    }
  };

  const handleSaveAiConfig = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingAi(true);
    try {
      await settingsApi.updateAiConfig({
        provider: aiProvider,
        model_name: aiModel,
        temperature: Number(aiTemp),
        max_tokens: Number(aiMaxTokens),
        reason: 'Administrative AI configuration update from Control Plane'
      });
      alert('AI Configuration updated successfully.');
      fetchTabData();
    } catch (err: any) {
      alert(`Failed to save AI configuration: ${err?.message || 'Unknown error'}`);
    } finally {
      setSavingAi(false);
    }
  };

  const handleToggleTool = async (tool: ToolPolicyRecord) => {
    try {
      await settingsApi.setToolPolicy({
        tool_id: tool.id,
        risk_classification: tool.risk_classification,
        permission_level: tool.permission_level,
        enabled: !tool.enabled
      });
      fetchTabData();
    } catch (err: any) {
      alert(`Failed to update tool policy: ${err?.message || 'Unknown error'}`);
    }
  };

  const handleAddBan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!banIdentifier.trim()) return;
    setSubmittingBan(true);
    try {
      await settingsApi.addBan({
        identifier: banIdentifier.trim(),
        ban_type: banType,
        reason: banReason.trim() || 'Administrative security ban'
      });
      setBanModalOpen(false);
      setBanIdentifier('');
      setBanReason('');
      fetchTabData();
    } catch (err: any) {
      alert(`Failed to add ban: ${err?.message || 'Unknown error'}`);
    } finally {
      setSubmittingBan(false);
    }
  };

  const handleRemoveBan = async (identifier: string) => {
    if (!confirm(`Are you sure you want to lift the ban on ${identifier}?`)) return;
    try {
      await settingsApi.removeBan(identifier);
      fetchTabData();
    } catch (err: any) {
      alert(`Failed to remove ban: ${err?.message || 'Unknown error'}`);
    }
  };

  const canManage = hasRole(['SUPER_ADMIN', 'ADMIN']);

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <Settings className="w-6 h-6 text-indigo-400" />
            System Control & Operations Settings
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Server-backed configuration for feature rollouts, maintenance windows, model parameters, and security bounds.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchTabData} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-800">
        <nav className="flex space-x-6">
          <button
            onClick={() => setActiveTab('flags')}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
              activeTab === 'flags'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Flag className="w-4 h-4" />
            Feature Flags
          </button>
          <button
            onClick={() => setActiveTab('maintenance')}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
              activeTab === 'maintenance'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Power className="w-4 h-4" />
            Maintenance Mode
          </button>
          <button
            onClick={() => setActiveTab('ai')}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
              activeTab === 'ai'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Cpu className="w-4 h-4" />
            AI & Models
          </button>
          <button
            onClick={() => setActiveTab('tools')}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
              activeTab === 'tools'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sliders className="w-4 h-4" />
            Tool Security Policies
          </button>
          <button
            onClick={() => setActiveTab('security')}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
              activeTab === 'security'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Shield className="w-4 h-4" />
            IP & User Bans
          </button>
        </nav>
      </div>

      {loading ? (
        <Card className="p-12 flex justify-center items-center">
          <LoadingSpinner size="lg" />
        </Card>
      ) : error ? (
        <Card className="p-8 text-center border-rose-900/40 bg-rose-950/20 text-rose-300">
          <p className="font-semibold">{error}</p>
          <Button variant="outline" size="sm" onClick={fetchTabData} className="mt-4">
            Retry
          </Button>
        </Card>
      ) : (
        <>
          {/* Feature Flags */}
          {activeTab === 'flags' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {flags.map((flag) => {
                  const isEnabled = typeof flag.enabled === 'boolean' ? flag.enabled : Boolean(flag.enabled);
                  return (
                    <Card
                      key={flag.key}
                      orientation="none"
                      className="p-5 border border-slate-800 bg-slate-900/60 flex items-center justify-between"
                    >
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-sm font-bold text-slate-100">{flag.key}</span>
                          <Badge variant={isEnabled ? 'success' : 'neutral'}>
                            {isEnabled ? 'Enabled' : 'Disabled'}
                          </Badge>
                        </div>
                        <p className="text-xs text-slate-400 mt-1">
                          {flag.description || 'Controls system functionality and feature rollout.'}
                        </p>
                        <span className="text-[11px] font-mono text-slate-500 mt-1 block">
                          Rollout: {flag.rollout_percentage}% of target population
                        </span>
                      </div>
                      {canManage && (
                        <Button
                          size="sm"
                          variant={isEnabled ? 'outline' : 'primary'}
                          onClick={() => handleToggleFlag(flag)}
                        >
                          {isEnabled ? 'Turn Off' : 'Turn On'}
                        </Button>
                      )}
                    </Card>
                  );
                })}
              </div>
            </div>
          )}

          {/* Maintenance Mode */}
          {activeTab === 'maintenance' && (
            <Card orientation="none" className="p-6 border border-slate-800 bg-slate-900/60 max-w-2xl">
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <div>
                  <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
                    <Power className="w-5 h-5 text-indigo-400" />
                    Global Maintenance Window
                  </h2>
                  <p className="text-xs text-slate-400 mt-1">
                    When active, incoming non-admin HTTP traffic receives a 503 Service Unavailable response.
                  </p>
                </div>
                <Badge variant={maintenance?.enabled ? 'danger' : 'success'}>
                  {maintenance?.enabled ? 'MAINTENANCE ACTIVE' : 'SYSTEM OPERATIONAL'}
                </Badge>
              </div>

              <div className="space-y-4 pt-4">
                <div>
                  <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
                    Maintenance Banner / Public Message
                  </label>
                  <input
                    type="text"
                    disabled={!canManage}
                    value={maintMessage}
                    onChange={(e) => setMaintMessage(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
                    IP & Email Whitelist (Comma-separated)
                  </label>
                  <input
                    type="text"
                    disabled={!canManage}
                    value={maintWhitelist}
                    onChange={(e) => setMaintWhitelist(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono"
                  />
                </div>

                {canManage && (
                  <div className="pt-2">
                    <Button
                      variant={maintenance?.enabled ? 'primary' : 'danger'}
                      onClick={handleToggleMaintenance}
                      disabled={updatingMaint}
                    >
                      {updatingMaint
                        ? 'Updating...'
                        : maintenance?.enabled
                        ? 'Deactivate Maintenance (Resume Operations)'
                        : 'Activate Maintenance Mode'}
                    </Button>
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* AI & Models Config */}
          {activeTab === 'ai' && (
            <Card orientation="none" className="p-6 border border-slate-800 bg-slate-900/60 max-w-2xl">
              <h2 className="text-base font-bold text-slate-100 flex items-center gap-2 mb-4">
                <Cpu className="w-5 h-5 text-indigo-400" />
                Default AI Model Configuration
              </h2>
              <form onSubmit={handleSaveAiConfig} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
                      Provider
                    </label>
                    <input
                      type="text"
                      disabled={!canManage}
                      value={aiProvider}
                      onChange={(e) => setAiProvider(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
                      Model Name
                    </label>
                    <input
                      type="text"
                      disabled={!canManage}
                      value={aiModel}
                      onChange={(e) => setAiModel(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
                      Temperature ({aiTemp})
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.05"
                      disabled={!canManage}
                      value={aiTemp}
                      onChange={(e) => setAiTemp(parseFloat(e.target.value))}
                      className="w-full accent-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
                      Max Output Tokens
                    </label>
                    <input
                      type="number"
                      min="256"
                      max="16384"
                      disabled={!canManage}
                      value={aiMaxTokens}
                      onChange={(e) => setAiMaxTokens(parseInt(e.target.value) || 4096)}
                      className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                </div>

                {canManage && (
                  <div className="pt-2">
                    <Button type="submit" disabled={savingAi}>
                      {savingAi ? 'Saving...' : 'Save AI Configuration'}
                    </Button>
                  </div>
                )}
              </form>
            </Card>
          )}

          {/* Tool Security Policies */}
          {activeTab === 'tools' && (
            <Card orientation="none" className="overflow-hidden border border-slate-800">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-300">
                  <thead className="bg-slate-950/80 text-xs uppercase text-slate-400 font-semibold border-b border-slate-800">
                    <tr>
                      <th className="px-6 py-4">Tool Identifier</th>
                      <th className="px-6 py-4">Description</th>
                      <th className="px-6 py-4">Risk Classification</th>
                      <th className="px-6 py-4">Permission Level</th>
                      <th className="px-6 py-4">Status</th>
                      <th className="px-6 py-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {tools.map((t) => (
                      <tr key={t.id} className="hover:bg-slate-800/30 transition-colors">
                        <td className="px-6 py-4 font-mono text-xs font-bold text-indigo-300">{t.name || t.id}</td>
                        <td className="px-6 py-4 text-xs text-slate-300 max-w-sm truncate">{t.description}</td>
                        <td className="px-6 py-4">
                          <Badge
                            variant={
                              t.risk_classification === 'CRITICAL'
                                ? 'danger'
                                : t.risk_classification === 'HIGH'
                                ? 'warning'
                                : 'neutral'
                            }
                          >
                            {t.risk_classification || 'LOW'}
                          </Badge>
                        </td>
                        <td className="px-6 py-4 text-xs font-mono text-slate-300">{t.permission_level}</td>
                        <td className="px-6 py-4">
                          <Badge variant={t.enabled ? 'success' : 'neutral'}>
                            {t.enabled ? 'Enabled' : 'Disabled'}
                          </Badge>
                        </td>
                        <td className="px-6 py-4 text-right">
                          {canManage && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleToggleTool(t)}
                            >
                              {t.enabled ? 'Disable' : 'Enable'}
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}

          {/* Security Bans */}
          {activeTab === 'security' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <p className="text-xs text-slate-400">
                  Manage blocked network IPs, suspicious user accounts, and brute-force mitigations.
                </p>
                {canManage && (
                  <Button size="sm" variant="danger" onClick={() => setBanModalOpen(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Security Ban
                  </Button>
                )}
              </div>

              <Card orientation="none" className="overflow-hidden border border-slate-800">
                {bans.length === 0 ? (
                  <div className="p-8 text-center text-xs text-slate-400">
                    No active security bans in effect.
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm text-slate-300">
                      <thead className="bg-slate-950/80 text-xs uppercase text-slate-400 font-semibold border-b border-slate-800">
                        <tr>
                          <th className="px-6 py-4">Banned Identifier</th>
                          <th className="px-6 py-4">Type</th>
                          <th className="px-6 py-4">Reason</th>
                          <th className="px-6 py-4 text-right">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {bans.map((b, idx) => (
                          <tr key={b.identifier || idx} className="hover:bg-slate-800/30 transition-colors">
                            <td className="px-6 py-4 font-mono text-xs text-rose-300">{b.identifier}</td>
                            <td className="px-6 py-4">
                              <Badge variant="purple">{b.ban_type || 'ip'}</Badge>
                            </td>
                            <td className="px-6 py-4 text-xs text-slate-300">{b.reason || 'Security ban'}</td>
                            <td className="px-6 py-4 text-right">
                              {canManage && (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleRemoveBan(b.identifier)}
                                >
                                  <Trash2 className="w-3.5 h-3.5 mr-1 text-rose-400" />
                                  Lift Ban
                                </Button>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </Card>
            </div>
          )}
        </>
      )}

      {/* Add Ban Modal */}
      <Modal
        isOpen={banModalOpen}
        onClose={() => setBanModalOpen(false)}
        title="Add Security Ban"
      >
        <form onSubmit={handleAddBan} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
              Ban Type
            </label>
            <select
              value={banType}
              onChange={(e) => setBanType(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-rose-500"
            >
              <option value="ip">IP Address</option>
              <option value="user_id">User ID</option>
              <option value="email">Email Domain</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
              Identifier (e.g. 192.168.1.50 or usr_123)
            </label>
            <input
              type="text"
              required
              value={banIdentifier}
              onChange={(e) => setBanIdentifier(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-rose-500 font-mono"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
              Audit Reason
            </label>
            <textarea
              required
              rows={2}
              value={banReason}
              onChange={(e) => setBanReason(e.target.value)}
              placeholder="State reason for security ban..."
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-rose-500"
            />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
            <Button variant="ghost" type="button" onClick={() => setBanModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="danger" type="submit" disabled={submittingBan}>
              {submittingBan ? 'Banning...' : 'Confirm Ban'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
