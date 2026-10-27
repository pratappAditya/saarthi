import React, { useState, useEffect } from 'react';
import { billingApi } from '../api/adminApi';
import type {
  SubscriptionRecord,
  PaymentRecord,
  InvoiceRecord,
  RefundRecord,
  WebhookEventRecord
} from '../types/admin';
import { useAuth } from '../auth/AuthContext';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { SearchInput } from '../components/common/SearchInput';
import { Modal } from '../components/common/Modal';
import { Drawer } from '../components/common/Drawer';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import {
  CreditCard,
  Receipt,
  RotateCcw,
  Webhook,
  DollarSign,
  AlertCircle,
  RefreshCw
} from 'lucide-react';

type BillingTab = 'subscriptions' | 'payments' | 'invoices' | 'refunds' | 'webhooks';

export const BillingPage: React.FC = () => {
  const { hasRole } = useAuth();
  const [activeTab, setActiveTab] = useState<BillingTab>('subscriptions');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Data states
  const [overview, setOverview] = useState<any | null>(null);
  const [subscriptions, setSubscriptions] = useState<SubscriptionRecord[]>([]);
  const [payments, setPayments] = useState<PaymentRecord[]>([]);
  const [invoices, setInvoices] = useState<InvoiceRecord[]>([]);
  const [refunds, setRefunds] = useState<RefundRecord[]>([]);
  const [webhooks, setWebhooks] = useState<WebhookEventRecord[]>([]);

  // Search & Filter
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Inspection Drawer
  const [inspectedItem, setInspectedItem] = useState<{ title: string; data: any } | null>(null);

  // Refund Modal State
  const [refundModalOpen, setRefundModalOpen] = useState(false);
  const [refundPaymentId, setRefundPaymentId] = useState('');
  const [refundReason, setRefundReason] = useState('');
  const [processingRefund, setProcessingRefund] = useState(false);

  const fetchTabContent = async () => {
    setLoading(true);
    setError(null);
    try {
      if (activeTab === 'subscriptions') {
        const [subRes, ovRes] = await Promise.all([
          billingApi.listSubscriptions(),
          billingApi.getOverview().catch(() => null)
        ]);
        setSubscriptions(subRes.subscriptions || []);
        if (ovRes?.overview) setOverview(ovRes.overview);
      } else if (activeTab === 'payments') {
        const res = await billingApi.listPayments();
        setPayments(res.payments || []);
      } else if (activeTab === 'invoices') {
        const res = await billingApi.listInvoices();
        setInvoices(res.invoices || []);
      } else if (activeTab === 'refunds') {
        const res = await billingApi.listRefunds();
        setRefunds(res.refunds || []);
      } else if (activeTab === 'webhooks') {
        const res = await billingApi.listWebhooks();
        setWebhooks(res.webhooks || []);
      }
    } catch (err: any) {
      setError(err?.message || `Failed to fetch ${activeTab} data.`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTabContent();
    setSearchQuery('');
    setStatusFilter('ALL');
  }, [activeTab]);

  const handleProcessRefund = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!refundPaymentId.trim() || !refundReason.trim()) return;
    setProcessingRefund(true);
    try {
      await billingApi.processRefund(refundPaymentId.trim(), refundReason.trim());
      alert('Refund processed successfully.');
      setRefundModalOpen(false);
      setRefundPaymentId('');
      setRefundReason('');
      fetchTabContent();
    } catch (err: any) {
      alert(`Refund failed: ${err?.message || 'Unknown error'}`);
    } finally {
      setProcessingRefund(false);
    }
  };

  const canManage = hasRole(['SUPER_ADMIN', 'ADMIN']);

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <DollarSign className="w-6 h-6 text-emerald-400" />
            Billing & Revenue Center
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Subscription lifecycles, payments audit, invoice tracking, refund operations, and webhook verification.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={fetchTabContent} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          {activeTab === 'refunds' && canManage && (
            <Button size="sm" variant="danger" onClick={() => setRefundModalOpen(true)}>
              <RotateCcw className="w-4 h-4 mr-2" />
              Process Refund
            </Button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-800">
        <nav className="flex space-x-6">
          <button
            onClick={() => setActiveTab('subscriptions')}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
              activeTab === 'subscriptions'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <CreditCard className="w-4 h-4" />
            Subscriptions
          </button>
          <button
            onClick={() => setActiveTab('payments')}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
              activeTab === 'payments'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <DollarSign className="w-4 h-4" />
            Payments
          </button>
          <button
            onClick={() => setActiveTab('invoices')}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
              activeTab === 'invoices'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Receipt className="w-4 h-4" />
            Invoices
          </button>
          <button
            onClick={() => setActiveTab('refunds')}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
              activeTab === 'refunds'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <RotateCcw className="w-4 h-4" />
            Refunds
          </button>
          <button
            onClick={() => setActiveTab('webhooks')}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
              activeTab === 'webhooks'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Webhook className="w-4 h-4" />
            Webhook Monitor
          </button>
        </nav>
      </div>

      {/* Tab Filter / Search Bar */}
      <Card orientation="none" className="p-4 bg-slate-900/60 border border-slate-800">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
          <div className="md:col-span-2">
            <SearchInput
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={`Search ${activeTab} by ID, user, or status...`}
              onClear={() => setSearchQuery('')}
            />
          </div>
          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="ALL">All Statuses</option>
              <option value="active">Active</option>
              <option value="paid">Paid</option>
              <option value="created">Created</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
              <option value="refunded">Refunded</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Tab Content Loading / Error / Table */}
      {loading ? (
        <Card className="p-12 flex justify-center items-center">
          <LoadingSpinner size="lg" />
        </Card>
      ) : error ? (
        <Card className="p-8 text-center border-rose-900/40 bg-rose-950/20 text-rose-300">
          <p className="font-semibold">{error}</p>
          <Button variant="outline" size="sm" onClick={fetchTabContent} className="mt-4">
            Retry
          </Button>
        </Card>
      ) : (
        <>
          {/* Subscriptions Tab */}
          {activeTab === 'subscriptions' && (
            <div className="space-y-4">
              {overview && (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl">
                    <span className="text-xs text-slate-400">Total Monthly Recurring Revenue (MRR)</span>
                    <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
                      ₹{overview.mrr_inr?.toLocaleString() || 0}
                    </div>
                  </div>
                  <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl">
                    <span className="text-xs text-slate-400">Annual Run Rate (ARR)</span>
                    <div className="text-xl font-bold font-mono text-slate-100 mt-1">
                      ₹{overview.arr_inr?.toLocaleString() || 0}
                    </div>
                  </div>
                  <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl">
                    <span className="text-xs text-slate-400">Active Subscriptions</span>
                    <div className="text-xl font-bold font-mono text-indigo-400 mt-1">
                      {overview.active_subscriptions || subscriptions.length}
                    </div>
                  </div>
                </div>
              )}
              <Card orientation="none" className="overflow-hidden border border-slate-800">
              {subscriptions.length === 0 ? (
                <div className="p-8 text-center text-slate-400 text-sm">No active subscriptions found.</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm text-slate-300">
                    <thead className="bg-slate-950/80 text-xs uppercase text-slate-400 font-semibold border-b border-slate-800">
                      <tr>
                        <th className="px-6 py-4">Subscription ID</th>
                        <th className="px-6 py-4">User / Org</th>
                        <th className="px-6 py-4">Plan & Version</th>
                        <th className="px-6 py-4">Status</th>
                        <th className="px-6 py-4">Seats / Price</th>
                        <th className="px-6 py-4">Current Period</th>
                        <th className="px-6 py-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {subscriptions.map((sub) => (
                        <tr key={sub.subscription_id} className="hover:bg-slate-800/30 transition-colors">
                          <td className="px-6 py-4 font-mono text-xs text-indigo-300">
                            {sub.subscription_id}
                          </td>
                          <td className="px-6 py-4 text-xs font-mono text-slate-300">
                            {sub.user_email || sub.user_id}
                            {sub.org_id && (
                              <span className="block text-[11px] text-slate-500">Org: {sub.org_id}</span>
                            )}
                          </td>
                          <td className="px-6 py-4">
                            <span className="font-semibold text-slate-100">{sub.plan_name}</span>
                            <span className="text-xs text-slate-400 block">v{sub.plan_version || '2.0'}</span>
                          </td>
                          <td className="px-6 py-4">
                            <Badge variant={sub.status === 'active' ? 'success' : 'neutral'}>
                              {sub.status}
                            </Badge>
                          </td>
                          <td className="px-6 py-4 text-xs text-slate-300">
                            <div>{sub.seat_count} seats</div>
                            <div className="font-semibold text-slate-100">₹{sub.total_amount?.toLocaleString()}</div>
                          </td>
                          <td className="px-6 py-4 text-xs text-slate-400">
                            {sub.current_period_end
                              ? new Date(sub.current_period_end).toLocaleDateString()
                              : '—'}
                          </td>
                          <td className="px-6 py-4 text-right">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() =>
                                setInspectedItem({
                                  title: `Subscription: ${sub.subscription_id}`,
                                  data: sub
                                })
                              }
                            >
                              Inspect
                            </Button>
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

          {/* Payments Tab */}
          {activeTab === 'payments' && (
            <Card orientation="none" className="overflow-hidden border border-slate-800">
              {payments.length === 0 ? (
                <div className="p-8 text-center text-slate-400 text-sm">No payment records found.</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm text-slate-300">
                    <thead className="bg-slate-950/80 text-xs uppercase text-slate-400 font-semibold border-b border-slate-800">
                      <tr>
                        <th className="px-6 py-4">Payment ID</th>
                        <th className="px-6 py-4">Order ID</th>
                        <th className="px-6 py-4">User</th>
                        <th className="px-6 py-4">Provider</th>
                        <th className="px-6 py-4">Amount</th>
                        <th className="px-6 py-4">Status</th>
                        <th className="px-6 py-4">Timestamp</th>
                        <th className="px-6 py-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {payments.map((p) => (
                        <tr key={p.payment_id} className="hover:bg-slate-800/30 transition-colors">
                          <td className="px-6 py-4 font-mono text-xs text-indigo-300">{p.payment_id}</td>
                          <td className="px-6 py-4 font-mono text-xs text-slate-400">{p.order_id}</td>
                          <td className="px-6 py-4 font-mono text-xs text-slate-300">
                            {p.user_email || p.user_id}
                          </td>
                          <td className="px-6 py-4">
                            <Badge variant="neutral">{p.provider || 'local'}</Badge>
                          </td>
                          <td className="px-6 py-4 font-semibold text-slate-100">
                            ₹{p.amount?.toLocaleString()} {p.currency}
                          </td>
                          <td className="px-6 py-4">
                            <Badge
                              variant={
                                p.status === 'paid' || p.status === 'completed'
                                  ? 'success'
                                  : p.status === 'failed'
                                  ? 'danger'
                                  : 'warning'
                              }
                            >
                              {p.status}
                            </Badge>
                          </td>
                          <td className="px-6 py-4 text-xs text-slate-400">
                            {new Date(p.created_at).toLocaleString()}
                          </td>
                          <td className="px-6 py-4 text-right">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() =>
                                setInspectedItem({
                                  title: `Payment: ${p.payment_id}`,
                                  data: p
                                })
                              }
                            >
                              Inspect
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>
          )}

          {/* Invoices Tab */}
          {activeTab === 'invoices' && (
            <Card orientation="none" className="overflow-hidden border border-slate-800">
              {invoices.length === 0 ? (
                <div className="p-8 text-center text-slate-400 text-sm">No invoice records found.</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm text-slate-300">
                    <thead className="bg-slate-950/80 text-xs uppercase text-slate-400 font-semibold border-b border-slate-800">
                      <tr>
                        <th className="px-6 py-4">Invoice ID</th>
                        <th className="px-6 py-4">Subscription</th>
                        <th className="px-6 py-4">User</th>
                        <th className="px-6 py-4">Amount</th>
                        <th className="px-6 py-4">Status</th>
                        <th className="px-6 py-4">Reason</th>
                        <th className="px-6 py-4">Issued At</th>
                        <th className="px-6 py-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {invoices.map((inv) => (
                        <tr key={inv.invoice_id} className="hover:bg-slate-800/30 transition-colors">
                          <td className="px-6 py-4 font-mono text-xs text-indigo-300">{inv.invoice_id}</td>
                          <td className="px-6 py-4 font-mono text-xs text-slate-400">
                            {inv.subscription_id || '—'}
                          </td>
                          <td className="px-6 py-4 font-mono text-xs text-slate-300">
                            {inv.user_email || inv.user_id}
                          </td>
                          <td className="px-6 py-4 font-semibold text-slate-100">
                            ₹{inv.amount?.toLocaleString()} {inv.currency}
                          </td>
                          <td className="px-6 py-4">
                            <Badge variant={inv.status === 'paid' ? 'success' : 'warning'}>
                              {inv.status}
                            </Badge>
                          </td>
                          <td className="px-6 py-4 text-xs text-slate-400">
                            {inv.billing_reason || 'subscription_cycle'}
                          </td>
                          <td className="px-6 py-4 text-xs text-slate-400">
                            {new Date(inv.created_at).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-4 text-right">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() =>
                                setInspectedItem({
                                  title: `Invoice: ${inv.invoice_id}`,
                                  data: inv
                                })
                              }
                            >
                              Inspect
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>
          )}

          {/* Refunds Tab */}
          {activeTab === 'refunds' && (
            <Card orientation="none" className="overflow-hidden border border-slate-800">
              {refunds.length === 0 ? (
                <div className="p-8 text-center text-slate-400 text-sm">No refund records found.</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm text-slate-300">
                    <thead className="bg-slate-950/80 text-xs uppercase text-slate-400 font-semibold border-b border-slate-800">
                      <tr>
                        <th className="px-6 py-4">Refund ID</th>
                        <th className="px-6 py-4">Payment ID</th>
                        <th className="px-6 py-4">User</th>
                        <th className="px-6 py-4">Amount</th>
                        <th className="px-6 py-4">Status</th>
                        <th className="px-6 py-4">Reason</th>
                        <th className="px-6 py-4">Timestamp</th>
                        <th className="px-6 py-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {refunds.map((ref) => (
                        <tr key={ref.refund_id} className="hover:bg-slate-800/30 transition-colors">
                          <td className="px-6 py-4 font-mono text-xs text-rose-300">{ref.refund_id}</td>
                          <td className="px-6 py-4 font-mono text-xs text-slate-400">{ref.payment_id}</td>
                          <td className="px-6 py-4 font-mono text-xs text-slate-300">
                            {ref.user_email || ref.user_id}
                          </td>
                          <td className="px-6 py-4 font-semibold text-slate-100">
                            ₹{ref.amount?.toLocaleString()}
                          </td>
                          <td className="px-6 py-4">
                            <Badge variant={ref.status === 'completed' ? 'success' : 'warning'}>
                              {ref.status}
                            </Badge>
                          </td>
                          <td className="px-6 py-4 text-xs text-slate-300">{ref.reason}</td>
                          <td className="px-6 py-4 text-xs text-slate-400">
                            {new Date(ref.created_at).toLocaleString()}
                          </td>
                          <td className="px-6 py-4 text-right">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() =>
                                setInspectedItem({
                                  title: `Refund: ${ref.refund_id}`,
                                  data: ref
                                })
                              }
                            >
                              Inspect
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>
          )}

          {/* Webhook Monitor Tab */}
          {activeTab === 'webhooks' && (
            <Card orientation="none" className="overflow-hidden border border-slate-800">
              {webhooks.length === 0 ? (
                <div className="p-8 text-center text-slate-400 text-sm">No webhook events recorded yet.</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm text-slate-300">
                    <thead className="bg-slate-950/80 text-xs uppercase text-slate-400 font-semibold border-b border-slate-800">
                      <tr>
                        <th className="px-6 py-4">Event ID</th>
                        <th className="px-6 py-4">Provider</th>
                        <th className="px-6 py-4">Event Type</th>
                        <th className="px-6 py-4">Processed Timestamp</th>
                        <th className="px-6 py-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {webhooks.map((wh) => (
                        <tr key={wh.event_id} className="hover:bg-slate-800/30 transition-colors">
                          <td className="px-6 py-4 font-mono text-xs text-indigo-300">{wh.event_id}</td>
                          <td className="px-6 py-4">
                            <Badge variant="neutral">{wh.provider}</Badge>
                          </td>
                          <td className="px-6 py-4 font-mono text-xs text-slate-200">{wh.event_type}</td>
                          <td className="px-6 py-4 text-xs text-slate-400">
                            {new Date(wh.processed_at).toLocaleString()}
                          </td>
                          <td className="px-6 py-4 text-right">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() =>
                                setInspectedItem({
                                  title: `Webhook: ${wh.event_id} (${wh.event_type})`,
                                  data: wh
                                })
                              }
                            >
                              Inspect Payload
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>
          )}
        </>
      )}

      {/* Item Inspection Drawer */}
      <Drawer
        isOpen={Boolean(inspectedItem)}
        onClose={() => setInspectedItem(null)}
        title="Sanitized Record Inspection"
        subtitle={inspectedItem?.title || ''}
      >
        {inspectedItem && (
          <div className="space-y-4">
            <p className="text-xs text-slate-400">
              Displaying sanitized metadata from the backend registry. Secrets, private keys, and user message bodies
              are excluded by security policy.
            </p>
            <pre className="p-4 bg-slate-950 rounded-xl border border-slate-800 text-xs font-mono text-slate-300 overflow-x-auto whitespace-pre-wrap">
              {JSON.stringify(inspectedItem.data, null, 2)}
            </pre>
          </div>
        )}
      </Drawer>

      {/* Process Refund Modal */}
      <Modal
        isOpen={refundModalOpen}
        onClose={() => setRefundModalOpen(false)}
        title="Process Administrative Refund"
      >
        <form onSubmit={handleProcessRefund} className="space-y-4">
          <div className="p-3 bg-rose-950/20 border border-rose-900/40 rounded-lg text-xs text-rose-300 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>
              This operation executes a server-validated refund workflow. It marks the payment as refunded, revokes
              associated tier entitlements, and logs an immutable audit event.
            </span>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
              Payment ID
            </label>
            <input
              type="text"
              required
              value={refundPaymentId}
              onChange={(e) => setRefundPaymentId(e.target.value)}
              placeholder="e.g. pay_..."
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-rose-500 font-mono"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
              Refund Justification Reason
            </label>
            <textarea
              required
              rows={3}
              value={refundReason}
              onChange={(e) => setRefundReason(e.target.value)}
              placeholder="State the customer or operational reason for refund..."
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-rose-500"
            />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
            <Button variant="ghost" type="button" onClick={() => setRefundModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="danger" type="submit" disabled={processingRefund}>
              {processingRefund ? 'Processing...' : 'Authorize Refund'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
