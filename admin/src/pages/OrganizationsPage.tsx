import React, { useState, useEffect, useMemo } from 'react';
import { orgsApi } from '../api/adminApi';
import type { OrganizationRecord } from '../types/admin';
import { useAuth } from '../auth/AuthContext';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { SearchInput } from '../components/common/SearchInput';
import { Drawer } from '../components/common/Drawer';
import { Modal } from '../components/common/Modal';
import { EmptyState } from '../components/common/EmptyState';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Building2, Users, Plus, RefreshCw, Layers } from 'lucide-react';

export const OrganizationsPage: React.FC = () => {
  const { hasRole } = useAuth();
  const [orgs, setOrgs] = useState<OrganizationRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPlan, setSelectedPlan] = useState('ALL');

  // Detail Drawer State
  const [selectedOrgId, setSelectedOrgId] = useState<string | null>(null);
  const [orgDetails, setOrgDetails] = useState<OrganizationRecord | null>(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  // Seat Update Modal
  const [seatModalOrg, setSeatModalOrg] = useState<OrganizationRecord | null>(null);
  const [newSeatLimit, setNewSeatLimit] = useState(10);
  const [updatingSeats, setUpdatingSeats] = useState(false);

  // Create Org Modal
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newOrgName, setNewOrgName] = useState('');
  const [newOrgPlan, setNewOrgPlan] = useState('TEAMS');
  const [newOrgSeats, setNewOrgSeats] = useState(10);
  const [creatingOrg, setCreatingOrg] = useState(false);

  const fetchOrgs = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await orgsApi.list();
      setOrgs(res.organizations || []);
    } catch (err: any) {
      setError(err?.message || 'Failed to load organizations.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrgs();
  }, []);

  const openDetails = async (orgId: string) => {
    setSelectedOrgId(orgId);
    setLoadingDetails(true);
    try {
      const res = await orgsApi.getDetails(orgId);
      setOrgDetails(res.organization);
    } catch (err: any) {
      console.error('Error fetching org details:', err);
    } finally {
      setLoadingDetails(false);
    }
  };

  const handleUpdateSeats = async () => {
    if (!seatModalOrg) return;
    setUpdatingSeats(true);
    try {
      await orgsApi.updateSeats(seatModalOrg.org_id, newSeatLimit);
      setSeatModalOrg(null);
      await fetchOrgs();
      if (selectedOrgId === seatModalOrg.org_id) {
        openDetails(seatModalOrg.org_id);
      }
    } catch (err: any) {
      alert(`Failed to update seats: ${err?.message || 'Unknown error'}`);
    } finally {
      setUpdatingSeats(false);
    }
  };

  const handleCreateOrg = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newOrgName.trim()) return;
    setCreatingOrg(true);
    try {
      await orgsApi.create({
        name: newOrgName.trim(),
        plan: newOrgPlan,
        max_seats: Number(newOrgSeats)
      });
      setCreateModalOpen(false);
      setNewOrgName('');
      setNewOrgPlan('TEAMS');
      setNewOrgSeats(10);
      await fetchOrgs();
    } catch (err: any) {
      alert(`Failed to create organization: ${err?.message || 'Unknown error'}`);
    } finally {
      setCreatingOrg(false);
    }
  };

  const filteredOrgs = useMemo(() => {
    return orgs.filter((org) => {
      const matchesSearch =
        org.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        org.org_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (org.owner_id && org.owner_id.toLowerCase().includes(searchQuery.toLowerCase()));

      const matchesPlan = selectedPlan === 'ALL' || org.subscription_plan === selectedPlan;

      return matchesSearch && matchesPlan;
    });
  }, [orgs, searchQuery, selectedPlan]);

  const canManage = hasRole(['SUPER_ADMIN', 'ADMIN']);

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <Building2 className="w-6 h-6 text-indigo-400" />
            Organizations & Teams
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Manage multi-seat organizations, member allocations, and seat quotas across tenants.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={fetchOrgs} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          {canManage && (
            <Button size="sm" onClick={() => setCreateModalOpen(true)}>
              <Plus className="w-4 h-4 mr-2" />
              New Organization
            </Button>
          )}
        </div>
      </div>

      {/* Filter / Search Bar */}
      <Card orientation="none" className="p-4 bg-slate-900/60 border border-slate-800">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
          <div className="md:col-span-2">
            <SearchInput
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by name, organization ID, or owner..."
              onClear={() => setSearchQuery('')}
            />
          </div>
          <div>
            <select
              value={selectedPlan}
              onChange={(e) => setSelectedPlan(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="ALL">All Subscription Plans</option>
              <option value="TEAMS">Teams</option>
              <option value="ENTERPRISE">Enterprise</option>
              <option value="FREE">Free</option>
              <option value="POWER">Power</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Orgs List */}
      {loading ? (
        <Card className="p-12 flex justify-center items-center">
          <LoadingSpinner size="lg" />
        </Card>
      ) : error ? (
        <Card className="p-8 text-center border-rose-900/40 bg-rose-950/20 text-rose-300">
          <p className="font-semibold">{error}</p>
          <Button variant="outline" size="sm" onClick={fetchOrgs} className="mt-4">
            Try Again
          </Button>
        </Card>
      ) : filteredOrgs.length === 0 ? (
        <Card className="p-12">
          <EmptyState
            icon={Building2}
            title="No organizations found"
            description={
              searchQuery || selectedPlan !== 'ALL'
                ? 'No organizations match your current search filters.'
                : 'No organizations have been created yet.'
            }
            action={
              canManage ? (
                <Button size="sm" onClick={() => setCreateModalOpen(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Create First Organization
                </Button>
              ) : undefined
            }
          />
        </Card>
      ) : (
        <Card orientation="none" className="overflow-hidden border border-slate-800">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950/80 text-xs uppercase text-slate-400 font-semibold border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4">Organization</th>
                  <th className="px-6 py-4">Plan</th>
                  <th className="px-6 py-4">Seat Limit</th>
                  <th className="px-6 py-4">Active Members</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Created Date</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredOrgs.map((org) => (
                  <tr key={org.org_id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-medium text-slate-100">{org.name}</div>
                      <div className="text-xs font-mono text-slate-400 mt-0.5">{org.org_id}</div>
                    </td>
                    <td className="px-6 py-4">
                      <Badge
                        variant={
                          org.subscription_plan === 'ENTERPRISE'
                            ? 'purple'
                            : org.subscription_plan === 'TEAMS'
                            ? 'indigo'
                            : 'neutral'
                        }
                      >
                        {org.subscription_plan}
                      </Badge>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-1.5 font-medium text-slate-200">
                        <Users className="w-4 h-4 text-slate-400" />
                        {org.seat_limit} seats
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-slate-300">
                        {org.member_count !== undefined ? org.member_count : '—'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant={org.status === 'active' || !org.status ? 'success' : 'danger'}>
                        {org.status || 'active'}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-400">
                      {new Date(org.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Button variant="ghost" size="sm" onClick={() => openDetails(org.org_id)}>
                          Inspect
                        </Button>
                        {canManage && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setSeatModalOrg(org);
                              setNewSeatLimit(org.seat_limit);
                            }}
                          >
                            Update Seats
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

      {/* Organization Details Drawer */}
      <Drawer
        isOpen={Boolean(selectedOrgId)}
        onClose={() => {
          setSelectedOrgId(null);
          setOrgDetails(null);
        }}
        title="Organization Details"
        subtitle={orgDetails?.name || selectedOrgId || ''}
      >
        {loadingDetails ? (
          <div className="flex justify-center p-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : orgDetails ? (
          <div className="space-y-6">
            {/* Meta Card */}
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">Organization Name</span>
                <span className="text-sm font-semibold text-slate-100">{orgDetails.name}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">Organization ID</span>
                <span className="text-xs font-mono text-slate-300">{orgDetails.org_id}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">Subscription Plan</span>
                <Badge variant="indigo">{orgDetails.subscription_plan}</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">Seat Allocation</span>
                <span className="text-sm font-medium text-slate-200">{orgDetails.seat_limit} Max Seats</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">Created At</span>
                <span className="text-xs text-slate-300">{new Date(orgDetails.created_at).toLocaleString()}</span>
              </div>
              {orgDetails.owner_id && (
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400">Owner User ID</span>
                  <span className="text-xs font-mono text-slate-300">{orgDetails.owner_id}</span>
                </div>
              )}
            </div>

            {/* Members Section */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-1.5">
                  <Users className="w-4 h-4 text-indigo-400" />
                  Organization Members ({orgDetails.members?.length || 0})
                </h3>
              </div>

              {!orgDetails.members || orgDetails.members.length === 0 ? (
                <div className="p-6 bg-slate-950/40 rounded-xl border border-slate-800/80 text-center text-xs text-slate-400">
                  No active members recorded in this organization.
                </div>
              ) : (
                <div className="space-y-2">
                  {orgDetails.members.map((m, idx) => (
                    <div
                      key={m.user_id || idx}
                      className="p-3 bg-slate-950 rounded-lg border border-slate-800 flex items-center justify-between"
                    >
                      <div>
                        <div className="text-sm font-medium text-slate-200">
                          {m.full_name || m.email || m.user_id}
                        </div>
                        <div className="text-xs text-slate-400 font-mono mt-0.5">{m.user_id}</div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={m.role === 'admin' || m.role === 'owner' ? 'purple' : 'neutral'}>
                          {m.role}
                        </Badge>
                        <Badge variant={m.status === 'active' ? 'success' : 'warning'}>
                          {m.status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Quick Actions */}
            {canManage && (
              <div className="pt-4 border-t border-slate-800">
                <Button
                  className="w-full"
                  variant="outline"
                  onClick={() => {
                    setSeatModalOrg(orgDetails);
                    setNewSeatLimit(orgDetails.seat_limit);
                  }}
                >
                  <Layers className="w-4 h-4 mr-2" />
                  Adjust Seat Limit
                </Button>
              </div>
            )}
          </div>
        ) : null}
      </Drawer>

      {/* Adjust Seats Modal */}
      <Modal
        isOpen={Boolean(seatModalOrg)}
        onClose={() => setSeatModalOrg(null)}
        title="Adjust Organization Seats"
      >
        <div className="space-y-4">
          <p className="text-sm text-slate-300">
            Update seat allocation for{' '}
            <span className="font-semibold text-indigo-300">{seatModalOrg?.name}</span>. This directly affects
            billing quotas and tenant member invitations.
          </p>
          <div>
            <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
              Maximum Allowed Seats
            </label>
            <input
              type="number"
              min="1"
              max="10000"
              value={newSeatLimit}
              onChange={(e) => setNewSeatLimit(parseInt(e.target.value) || 1)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
            <Button variant="ghost" onClick={() => setSeatModalOrg(null)}>
              Cancel
            </Button>
            <Button onClick={handleUpdateSeats} disabled={updatingSeats}>
              {updatingSeats ? 'Saving...' : 'Confirm Seat Limit'}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Create Organization Modal */}
      <Modal
        isOpen={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        title="Create Organization"
      >
        <form onSubmit={handleCreateOrg} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
              Organization Name
            </label>
            <input
              type="text"
              required
              value={newOrgName}
              onChange={(e) => setNewOrgName(e.target.value)}
              placeholder="e.g. Acme Corp Operations"
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
                Plan
              </label>
              <select
                value={newOrgPlan}
                onChange={(e) => setNewOrgPlan(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="TEAMS">Teams</option>
                <option value="ENTERPRISE">Enterprise</option>
                <option value="POWER">Power</option>
                <option value="FREE">Free</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
                Initial Seat Limit
              </label>
              <input
                type="number"
                min="1"
                max="5000"
                value={newOrgSeats}
                onChange={(e) => setNewOrgSeats(parseInt(e.target.value) || 1)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
            <Button variant="ghost" type="button" onClick={() => setCreateModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={creatingOrg}>
              {creatingOrg ? 'Creating...' : 'Create Organization'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
