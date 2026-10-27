import React, { useState, useEffect } from "react";
import { ShieldAlert, Users, Key, RefreshCw, Slash, CheckCircle, Lock, BarChart3, AlertCircle } from "lucide-react";
import { api } from "../../api";

interface VendorAdminModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function VendorAdminModal({ isOpen, onClose }: VendorAdminModalProps) {
  const [activeTab, setActiveTab] = useState<"customers" | "licenses" | "audit" | "analytics">("customers");
  
  const [customers, setCustomers] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [msg, setMsg] = useState<string | null>(null);

  // New Customer Form
  const [newCustName, setNewCustName] = useState<string>("");
  const [newCustEmail, setNewCustEmail] = useState<string>("");

  // New License Form
  const [selectedCustId, setSelectedCustId] = useState<string>("");
  const [selectedPlan, setSelectedPlan] = useState<string>("STUDENT");
  const [durationDays, setDurationDays] = useState<number>(30);

  const fetchVendorData = async () => {
    setLoading(true);
    try {
      const custRes = await api.listVendorCustomers();
      if (custRes.customers) setCustomers(custRes.customers);
      const logsRes = await api.getVendorAuditLogs();
      if (logsRes.audit_logs) setAuditLogs(logsRes.audit_logs);
      const anaRes = await api.getVendorAnalytics();
      if (anaRes) setAnalytics(anaRes);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) fetchVendorData();
  }, [isOpen]);

  if (!isOpen) return null;

  const handleCreateCustomer = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.createVendorCustomer(newCustName, newCustEmail);
      setMsg(`Customer created: ${res.customer.customer_id}`);
      setNewCustName("");
      setNewCustEmail("");
      fetchVendorData();
    } catch (err: any) {
      setMsg(`Error: ${err.message}`);
    }
  };

  const handleCreateLicense = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.createVendorLicense(selectedCustId, selectedPlan, durationDays);
      setMsg(`License issued: ${res.license.license_key}`);
      fetchVendorData();
    } catch (err: any) {
      setMsg(`Error: ${err.message}`);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden shadow-2xl">
        
        {/* MODAL HEADER */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950">
          <div className="flex items-center space-x-2">
            <ShieldAlert className="w-5 h-5 text-amber-400" />
            <div>
              <h2 className="text-sm font-bold text-slate-100">Vendor Control Center (Operator Admin)</h2>
              <p className="text-[11px] text-slate-400">Manage customers, Ed25519 signed licenses, entitlements, and CRL.</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200 text-xs px-2 py-1 rounded">
            ✕ Close
          </button>
        </div>

        {/* TABS */}
        <div className="flex items-center border-b border-slate-800 bg-slate-900/60 px-4 space-x-2 pt-2">
          <button
            onClick={() => setActiveTab("customers")}
            className={`px-3 py-2 text-xs font-medium border-b-2 transition-all flex items-center space-x-1.5 ${
              activeTab === "customers" ? "border-cyan-400 text-cyan-300" : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <Users className="w-3.5 h-3.5" />
            <span>Customers & Licensing</span>
          </button>

          <button
            onClick={() => setActiveTab("audit")}
            className={`px-3 py-2 text-xs font-medium border-b-2 transition-all flex items-center space-x-1.5 ${
              activeTab === "audit" ? "border-cyan-400 text-cyan-300" : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <Key className="w-3.5 h-3.5" />
            <span>Audit Logs</span>
          </button>

          <button
            onClick={() => setActiveTab("analytics")}
            className={`px-3 py-2 text-xs font-medium border-b-2 transition-all flex items-center space-x-1.5 ${
              activeTab === "analytics" ? "border-cyan-400 text-cyan-300" : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Operational Metrics</span>
          </button>
        </div>

        {/* CONTENT AREA */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-xs text-slate-300">
          
          {msg && (
            <div className="bg-cyan-950/60 border border-cyan-700/60 p-3 rounded-lg text-cyan-300 flex items-center justify-between">
              <span>{msg}</span>
              <button onClick={() => setMsg(null)} className="text-cyan-400 font-bold">✕</button>
            </div>
          )}

          {activeTab === "customers" && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* CREATE CUSTOMER & LICENSE */}
              <div className="space-y-4 bg-slate-950 p-4 rounded-xl border border-slate-800">
                <h3 className="font-bold text-slate-200">Issue Commercial License</h3>
                
                <form onSubmit={handleCreateCustomer} className="space-y-2 border-b border-slate-800 pb-4">
                  <div className="font-medium text-slate-400 text-[11px]">1. Add Customer</div>
                  <input
                    type="text"
                    required
                    placeholder="Customer Name"
                    value={newCustName}
                    onChange={(e) => setNewCustName(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-slate-200"
                  />
                  <input
                    type="email"
                    required
                    placeholder="customer@email.com"
                    value={newCustEmail}
                    onChange={(e) => setNewCustEmail(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-slate-200"
                  />
                  <button type="submit" className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium py-1.5 rounded">
                    Create Customer
                  </button>
                </form>

                <form onSubmit={handleCreateLicense} className="space-y-2">
                  <div className="font-medium text-slate-400 text-[11px]">2. Issue Signed License Key</div>
                  <select
                    required
                    value={selectedCustId}
                    onChange={(e) => setSelectedCustId(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-slate-200"
                  >
                    <option value="">Select Customer...</option>
                    {customers.map((c) => (
                      <option key={c.customer_id} value={c.customer_id}>
                        {c.name} ({c.email})
                      </option>
                    ))}
                  </select>

                  <select
                    value={selectedPlan}
                    onChange={(e) => setSelectedPlan(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-slate-200"
                  >
                    <option value="FREE">FREE</option>
                    <option value="STUDENT">STUDENT (₹149/mo)</option>
                    <option value="PERSONAL">PERSONAL (₹399/mo)</option>
                    <option value="POWER">POWER (₹999/mo)</option>
                    <option value="CUSTOM">CUSTOM</option>
                  </select>

                  <button type="submit" className="w-full bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-medium py-1.5 rounded">
                    Generate Signed License Key
                  </button>
                </form>
              </div>

              {/* CUSTOMER LIST */}
              <div className="space-y-3">
                <h3 className="font-bold text-slate-200">Registered Customers ({customers.length})</h3>
                <div className="space-y-2 max-h-80 overflow-y-auto">
                  {customers.map((c) => (
                    <div key={c.customer_id} className="bg-slate-950 p-3 rounded-lg border border-slate-800 space-y-1">
                      <div className="font-semibold text-slate-200">{c.name}</div>
                      <div className="text-[11px] text-slate-400">{c.email}</div>
                      <div className="text-[10px] text-cyan-400 font-mono">{c.customer_id}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === "audit" && (
            <div className="space-y-2">
              <h3 className="font-bold text-slate-200">Vendor Audit Events</h3>
              <div className="space-y-1.5 max-h-96 overflow-y-auto">
                {auditLogs.map((log) => (
                  <div key={log.log_id} className="bg-slate-950 p-2.5 rounded border border-slate-800 flex items-center justify-between text-[11px]">
                    <div>
                      <span className="font-bold text-cyan-400 mr-2">[{log.action}]</span>
                      <span className="text-slate-300">{log.details}</span>
                    </div>
                    <span className="text-slate-500 font-mono text-[10px]">{log.timestamp.slice(0, 19)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "analytics" && analytics && (
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                  <div className="text-slate-400 text-[11px]">Total Customers</div>
                  <div className="text-2xl font-bold text-slate-100">{analytics.total_customers}</div>
                </div>
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                  <div className="text-slate-400 text-[11px]">Active Licenses Issued</div>
                  <div className="text-2xl font-bold text-cyan-400">{analytics.active_licenses}</div>
                </div>
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                  <div className="text-slate-400 text-[11px]">Audit Events Logged</div>
                  <div className="text-2xl font-bold text-purple-400">{analytics.total_audit_events}</div>
                </div>
              </div>

              <div className="bg-slate-950 p-4 rounded-xl border border-emerald-500/30 text-xs text-slate-300">
                <div className="font-bold text-emerald-400 mb-1">Privacy Guarantee</div>
                <div>{analytics.privacy_guarantee}</div>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
