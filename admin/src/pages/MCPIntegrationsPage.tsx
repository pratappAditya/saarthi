import React, { useState, useEffect } from 'react';
import { mcpApi } from '../api/adminApi';
import {
  Layers,
  Plus,
  Play,
  Trash2,
  CheckCircle,
  AlertTriangle,
  XCircle,
  RefreshCw,
  Cpu,
  Shield,
  Sliders,
  ExternalLink
} from 'lucide-react';

interface MCPServer {
  id: string;
  name: string;
  transport: 'stdio' | 'http' | 'sse';
  command?: string;
  url?: string;
  args?: string[];
  enabled: boolean;
  risk_tier: 'TIER_A' | 'TIER_B' | 'TIER_C';
  status: 'CONNECTED' | 'DISCONNECTED' | 'DEGRADED' | 'FAILED' | 'DISABLED';
  last_connected_at?: string;
  discovered_tools_count: number;
  error_message?: string;
}

interface MCPTool {
  id: string;
  name: string;
  description: string;
  risk_level: string;
  required_capability: string;
  requires_confirmation: boolean;
  operation_type: string;
}

export const MCPIntegrationsPage: React.FC = () => {
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [tools, setTools] = useState<MCPTool[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [testingId, setTestingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState<boolean>(false);

  // New Server Form State
  const [newId, setNewId] = useState('');
  const [newName, setNewName] = useState('');
  const [newTransport, setNewTransport] = useState<'stdio' | 'http'>('stdio');
  const [newCommand, setNewCommand] = useState('');
  const [newUrl, setNewUrl] = useState('');
  const [newRiskTier, setNewRiskTier] = useState<'TIER_A' | 'TIER_B' | 'TIER_C'>('TIER_A');

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [serversRes, toolsRes] = await Promise.all([
        mcpApi.listServers(),
        mcpApi.listTools()
      ]);
      setServers(serversRes.servers || []);
      setTools(toolsRes.mcp_tools || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load MCP server integrations.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleToggle = async (serverId: string, currentEnabled: boolean) => {
    try {
      await mcpApi.toggleServer(serverId, !currentEnabled);
      setServers(prev =>
        prev.map(s => (s.id === serverId ? { ...s, enabled: !currentEnabled } : s))
      );
    } catch (err: any) {
      alert(`Failed to toggle server: ${err.message}`);
    }
  };

  const handleTest = async (serverId: string) => {
    try {
      setTestingId(serverId);
      const res = await mcpApi.testServer(serverId);
      alert(`Handshake & Discovery Successful!\nDiscovered ${res.tools_discovered} tools from '${serverId}'.`);
      await fetchData();
    } catch (err: any) {
      alert(`Test Connection Failed: ${err.message}`);
    } finally {
      setTestingId(null);
    }
  };

  const handleDelete = async (serverId: string) => {
    if (!confirm(`Are you sure you want to unregister MCP server '${serverId}'?`)) return;
    try {
      await mcpApi.deleteServer(serverId);
      setServers(prev => prev.filter(s => s.id !== serverId));
      const toolsRes = await mcpApi.listTools();
      setTools(toolsRes.mcp_tools || []);
    } catch (err: any) {
      alert(`Failed to delete server: ${err.message}`);
    }
  };

  const handleAddServer = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await mcpApi.registerServer({
        id: newId.trim(),
        name: newName.trim(),
        transport: newTransport,
        command: newTransport === 'stdio' ? newCommand.trim() : undefined,
        url: newTransport === 'http' ? newUrl.trim() : undefined,
        risk_tier: newRiskTier,
        enabled: true
      });
      setShowAddModal(false);
      setNewId('');
      setNewName('');
      setNewCommand('');
      setNewUrl('');
      await fetchData();
    } catch (err: any) {
      alert(`Failed to register server: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Layers className="w-6 h-6 text-indigo-400" />
            Model Context Protocol (MCP) Manager
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Connect, discover, and govern external MCP servers under Saarthi's unified policy and execution boundary.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchData}
            className="flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-lg transition"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-lg shadow-sm transition"
          >
            <Plus className="w-4 h-4" />
            Register MCP Server
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-900/30 border border-red-500/50 rounded-lg flex items-center gap-3 text-red-200 text-sm">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Overview Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#0f141c] border border-slate-800 p-4 rounded-xl flex items-center justify-between">
          <div>
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Registered Servers</span>
            <div className="text-2xl font-bold text-white mt-1">{servers.length}</div>
          </div>
          <Cpu className="w-8 h-8 text-indigo-400/50" />
        </div>
        <div className="bg-[#0f141c] border border-slate-800 p-4 rounded-xl flex items-center justify-between">
          <div>
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Connected / Healthy</span>
            <div className="text-2xl font-bold text-emerald-400 mt-1">
              {servers.filter(s => s.status === 'CONNECTED').length}
            </div>
          </div>
          <CheckCircle className="w-8 h-8 text-emerald-400/50" />
        </div>
        <div className="bg-[#0f141c] border border-slate-800 p-4 rounded-xl flex items-center justify-between">
          <div>
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Discovered Tools</span>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{tools.length}</div>
          </div>
          <Sliders className="w-8 h-8 text-cyan-400/50" />
        </div>
        <div className="bg-[#0f141c] border border-slate-800 p-4 rounded-xl flex items-center justify-between">
          <div>
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Protocol Version</span>
            <div className="text-xl font-bold text-amber-400 mt-1">2024-11-05</div>
          </div>
          <Shield className="w-8 h-8 text-amber-400/50" />
        </div>
      </div>

      {/* Servers Table */}
      <div className="bg-[#0f141c] border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-base font-semibold text-white">Registered Integration Servers</h2>
          <span className="text-xs font-mono text-slate-400">Policy: Sandboxed & Audited</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-[#141a24] text-xs uppercase font-mono text-slate-400 border-b border-slate-800">
              <tr>
                <th className="px-6 py-3">Server / ID</th>
                <th className="px-6 py-3">Transport</th>
                <th className="px-6 py-3">Risk Tier</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Tools</th>
                <th className="px-6 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {servers.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-slate-500">
                    No MCP servers registered yet. Click "Register MCP Server" to add an integration.
                  </td>
                </tr>
              ) : (
                servers.map(server => (
                  <tr key={server.id} className="hover:bg-slate-800/30 transition">
                    <td className="px-6 py-4">
                      <div className="font-medium text-white">{server.name}</div>
                      <div className="text-xs font-mono text-slate-500">{server.id}</div>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                        {server.transport.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`text-xs px-2.5 py-0.5 rounded-full font-medium ${
                          server.risk_tier === 'TIER_A'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : server.risk_tier === 'TIER_B'
                            ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                            : 'bg-red-500/10 text-red-400 border border-red-500/20'
                        }`}
                      >
                        {server.risk_tier}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1.5 text-xs font-medium">
                        {server.status === 'CONNECTED' ? (
                          <span className="text-emerald-400 flex items-center gap-1">
                            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                            Connected
                          </span>
                        ) : server.status === 'DISABLED' ? (
                          <span className="text-slate-500">Disabled</span>
                        ) : (
                          <span className="text-amber-400">{server.status}</span>
                        )}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs font-mono text-indigo-400">
                      {server.discovered_tools_count} tools
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="inline-flex items-center gap-2">
                        <button
                          onClick={() => handleTest(server.id)}
                          disabled={testingId === server.id}
                          className="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs rounded transition flex items-center gap-1"
                          title="Run Handshake & Discover Tools"
                        >
                          <Play className="w-3 h-3 text-emerald-400" />
                          {testingId === server.id ? 'Testing...' : 'Discover'}
                        </button>
                        <button
                          onClick={() => handleToggle(server.id, server.enabled)}
                          className={`px-2.5 py-1.5 text-xs rounded transition ${
                            server.enabled
                              ? 'bg-amber-500/20 text-amber-300 hover:bg-amber-500/30'
                              : 'bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30'
                          }`}
                        >
                          {server.enabled ? 'Disable' : 'Enable'}
                        </button>
                        <button
                          onClick={() => handleDelete(server.id)}
                          className="p-1.5 hover:bg-red-900/30 text-slate-400 hover:text-red-400 rounded transition"
                          title="Delete Server"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Discovered Tools Catalog */}
      <div className="bg-[#0f141c] border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-base font-semibold text-white">Discovered MCP Tools (Synced into ToolRegistry)</h2>
          <span className="text-xs font-mono text-slate-400">{tools.length} active registered tools</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-[#141a24] text-xs uppercase font-mono text-slate-400 border-b border-slate-800">
              <tr>
                <th className="px-6 py-3">Tool ID</th>
                <th className="px-6 py-3">Description</th>
                <th className="px-6 py-3">Risk Level</th>
                <th className="px-6 py-3">Confirmation</th>
                <th className="px-6 py-3">Capability Scope</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {tools.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-6 text-center text-slate-500">
                    No MCP tools synchronized yet. Click "Discover" on any connected server above.
                  </td>
                </tr>
              ) : (
                tools.map(tool => (
                  <tr key={tool.id} className="hover:bg-slate-800/30 transition">
                    <td className="px-6 py-3 font-mono text-xs text-indigo-300 font-semibold">{tool.id}</td>
                    <td className="px-6 py-3 text-slate-400 text-xs max-w-md truncate">{tool.description}</td>
                    <td className="px-6 py-3">
                      <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                        {tool.risk_level}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-xs">
                      {tool.requires_confirmation ? (
                        <span className="text-amber-400 font-medium">Requires Approval</span>
                      ) : (
                        <span className="text-slate-400">Autonomous</span>
                      )}
                    </td>
                    <td className="px-6 py-3 font-mono text-xs text-slate-400">{tool.required_capability}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Registration Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#111622] border border-slate-800 rounded-xl max-w-md w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-2">Register New MCP Server</h3>
            <p className="text-xs text-slate-400 mb-4">
              Onboard an MCP-compatible service. All tools will pass through Saarthi's server-side authorization boundaries.
            </p>
            <form onSubmit={handleAddServer} className="space-y-4">
              <div>
                <label className="block text-xs font-mono text-slate-300 mb-1">Server ID (slug)</label>
                <input
                  type="text"
                  required
                  value={newId}
                  onChange={e => setNewId(e.target.value)}
                  placeholder="e.g. github-mcp"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-xs font-mono text-slate-300 mb-1">Display Name</label>
                <input
                  type="text"
                  required
                  value={newName}
                  onChange={e => setNewName(e.target.value)}
                  placeholder="e.g. GitHub Repository Integrations"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-mono text-slate-300 mb-1">Transport</label>
                  <select
                    value={newTransport}
                    onChange={e => setNewTransport(e.target.value as any)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="stdio">stdio (Subprocess)</option>
                    <option value="http">http (REST / SSE)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-mono text-slate-300 mb-1">Risk Classification</label>
                  <select
                    value={newRiskTier}
                    onChange={e => setNewRiskTier(e.target.value as any)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="TIER_A">Tier A (Read-Only)</option>
                    <option value="TIER_B">Tier B (User-Approved)</option>
                    <option value="TIER_C">Tier C (High-Risk)</option>
                  </select>
                </div>
              </div>
              {newTransport === 'stdio' ? (
                <div>
                  <label className="block text-xs font-mono text-slate-300 mb-1">Executable Command</label>
                  <input
                    type="text"
                    required
                    value={newCommand}
                    onChange={e => setNewCommand(e.target.value)}
                    placeholder="e.g. npx -y @modelcontextprotocol/server-github"
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
              ) : (
                <div>
                  <label className="block text-xs font-mono text-slate-300 mb-1">Endpoint URL (HTTPS)</label>
                  <input
                    type="url"
                    required
                    value={newUrl}
                    onChange={e => setNewUrl(e.target.value)}
                    placeholder="https://mcp.external-service.com/rpc"
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
              )}
              <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 text-sm text-slate-400 hover:text-white transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-lg shadow-sm transition"
                >
                  Register Server
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
