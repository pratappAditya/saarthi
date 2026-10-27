import React, { useEffect, useState } from 'react';
import { usersApi } from '../api/adminApi';
import type { UserRecord, UserDetails } from '../types/admin';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { SearchInput } from '../components/common/SearchInput';
import { Pagination } from '../components/common/Pagination';
import { Drawer } from '../components/common/Drawer';
import { Modal } from '../components/common/Modal';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { LoadingSpinner, TableSkeleton } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import {
  Users,
  Shield,
  Layers,
  UserCheck,
  UserX,
  Trash2,
  Eye,
  RefreshCw,
  Clock,
  HardDrive
} from 'lucide-react';
import { useAdminAuth } from '../auth/AuthContext';

export const UsersPage: React.FC = () => {
  const { role: adminRole } = useAdminAuth();
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters & Search
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [planFilter, setPlanFilter] = useState('');

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  // Selected User Detail Drawer
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const [userDetails, setUserDetails] = useState<UserDetails | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // Action Dialogs State
  const [roleModalUser, setRoleModalUser] = useState<UserRecord | null>(null);
  const [newRole, setNewRole] = useState('USER');
  const [roleReason, setRoleReason] = useState('');

  const [planModalUser, setPlanModalUser] = useState<UserRecord | null>(null);
  const [newPlan, setNewPlan] = useState('FREE');
  const [planReason, setPlanReason] = useState('');

  const [confirmSuspendUser, setConfirmSuspendUser] = useState<UserRecord | null>(null);
  const [confirmRestoreUser, setConfirmRestoreUser] = useState<UserRecord | null>(null);
  const [confirmDeleteUser, setConfirmDeleteUser] = useState<UserRecord | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await usersApi.list({
        query: searchQuery || undefined,
        role: roleFilter || undefined,
        plan: planFilter || undefined
      });
      setUsers(res.users || []);
      setCurrentPage(1);
    } catch (err: any) {
      setError(err.message || 'Failed to load users.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [roleFilter, planFilter]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchUsers();
  };

  const handleViewDetails = async (userId: string) => {
    setSelectedUserId(userId);
    setDetailLoading(true);
    try {
      const data = await usersApi.getDetails(userId);
      setUserDetails(data);
    } catch (err: any) {
      alert(`Failed to load user details: ${err.message}`);
      setSelectedUserId(null);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleUpdateRole = async () => {
    if (!roleModalUser) return;
    setActionLoading(true);
    try {
      await usersApi.updateRole(roleModalUser.user_id, newRole, roleReason);
      setRoleModalUser(null);
      fetchUsers();
    } catch (err: any) {
      alert(err.message || 'Failed to update user role.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleUpdatePlan = async () => {
    if (!planModalUser) return;
    setActionLoading(true);
    try {
      await usersApi.updatePlan(planModalUser.user_id, newPlan, planReason);
      setPlanModalUser(null);
      fetchUsers();
    } catch (err: any) {
      alert(err.message || 'Failed to update user plan.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleSuspend = async () => {
    if (!confirmSuspendUser) return;
    setActionLoading(true);
    try {
      await usersApi.suspend(confirmSuspendUser.user_id, 'Administrative suspension');
      setConfirmSuspendUser(null);
      fetchUsers();
    } catch (err: any) {
      alert(err.message || 'Failed to suspend user.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleRestore = async () => {
    if (!confirmRestoreUser) return;
    setActionLoading(true);
    try {
      await usersApi.restore(confirmRestoreUser.user_id, 'Administrative restoration');
      setConfirmRestoreUser(null);
      fetchUsers();
    } catch (err: any) {
      alert(err.message || 'Failed to restore user.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirmDeleteUser) return;
    setActionLoading(true);
    try {
      await usersApi.delete(confirmDeleteUser.user_id, 'Administrative deletion');
      setConfirmDeleteUser(null);
      fetchUsers();
    } catch (err: any) {
      alert(err.message || 'Failed to delete user.');
    } finally {
      setActionLoading(false);
    }
  };

  // Pagination calculation
  const totalPages = Math.ceil(users.length / pageSize);
  const paginatedUsers = users.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const getRoleBadgeVariant = (role: string): 'rose' | 'amber' | 'blue' | 'purple' | 'slate' => {
    switch (role.toUpperCase()) {
      case 'SUPER_ADMIN': return 'rose';
      case 'ADMIN': return 'amber';
      case 'ANALYST': return 'purple';
      case 'SUSPENDED': return 'rose';
      default: return 'slate';
    }
  };

  return (
    <div className="space-y-6">
      {/* Title & Filter Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight">Users Management</h1>
          <p className="text-xs text-slate-400 mt-0.5">Manage accounts, inspect quotas, assign administrative roles, and enforce policies</p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchUsers} leftIcon={<RefreshCw className="w-3 h-3" />}>
          Refresh
        </Button>
      </div>

      {/* Filters Card */}
      <Card bodyClassName="p-4">
        <form onSubmit={handleSearch} className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <div className="flex-1">
            <SearchInput
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by email, name, or user ID..."
            />
          </div>
          <div className="flex items-center gap-2">
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="text-xs bg-[#0d1118] border border-white/10 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500"
            >
              <option value="">All Roles</option>
              <option value="USER">USER</option>
              <option value="ADMIN">ADMIN</option>
              <option value="SUPER_ADMIN">SUPER_ADMIN</option>
              <option value="ANALYST">ANALYST</option>
              <option value="SUSPENDED">SUSPENDED</option>
            </select>

            <select
              value={planFilter}
              onChange={(e) => setPlanFilter(e.target.value)}
              className="text-xs bg-[#0d1118] border border-white/10 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500"
            >
              <option value="">All Plans</option>
              <option value="FREE">FREE</option>
              <option value="STUDENT">STUDENT</option>
              <option value="PERSONAL">PERSONAL</option>
              <option value="POWER">POWER</option>
              <option value="TEAMS">TEAMS</option>
              <option value="ENTERPRISE">ENTERPRISE</option>
            </select>

            <Button type="submit" variant="secondary" size="sm">
              Filter
            </Button>
          </div>
        </form>
      </Card>

      {/* Table Card */}
      <Card bodyClassName="p-0 overflow-hidden">
        {loading ? (
          <TableSkeleton rows={8} cols={6} />
        ) : error ? (
          <div className="p-8 text-center text-xs text-rose-400">{error}</div>
        ) : users.length === 0 ? (
          <EmptyState
            icon={<Users className="w-6 h-6" />}
            title="No Users Found"
            description="No user accounts match your search query or filter criteria."
            actionText="Clear Filters"
            onAction={() => { setSearchQuery(''); setRoleFilter(''); setPlanFilter(''); }}
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/60 border-b border-white/8 text-[11px] font-mono uppercase text-slate-400">
                <tr>
                  <th className="py-3 px-4">User</th>
                  <th className="py-3 px-4">Role</th>
                  <th className="py-3 px-4">Plan</th>
                  <th className="py-3 px-4">Verified</th>
                  <th className="py-3 px-4">Created Date</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/6">
                {paginatedUsers.map((u) => {
                  const isSuspended = u.role === 'SUSPENDED';
                  return (
                    <tr key={u.user_id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-3 px-4">
                        <div className="font-medium text-slate-200">{u.full_name || 'Anonymous User'}</div>
                        <div className="text-[11px] text-slate-400 font-mono">{u.email}</div>
                        <div className="text-[10px] text-slate-400 font-mono">{u.user_id}</div>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant={getRoleBadgeVariant(u.role)}>{u.role}</Badge>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant={u.subscription_plan === 'FREE' ? 'slate' : 'emerald'}>
                          {u.subscription_plan}
                        </Badge>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center gap-1 text-[11px] font-mono ${u.is_verified ? 'text-emerald-400' : 'text-slate-400'}`}>
                          {u.is_verified ? 'VERIFIED' : 'PENDING'}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono text-[11px] text-slate-400">
                        {u.created_at ? new Date(u.created_at).toLocaleDateString() : 'N/A'}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleViewDetails(u.user_id)}
                            title="Inspect User Details"
                          >
                            <Eye className="w-3.5 h-3.5 text-blue-400" />
                          </Button>

                          {adminRole !== 'ANALYST' && (
                            <>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                  setRoleModalUser(u);
                                  setNewRole(u.role);
                                  setRoleReason('');
                                }}
                                title="Change Role"
                              >
                                <Shield className="w-3.5 h-3.5 text-amber-400" />
                              </Button>

                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                  setPlanModalUser(u);
                                  setNewPlan(u.subscription_plan);
                                  setPlanReason('');
                                }}
                                title="Update Plan"
                              >
                                <Layers className="w-3.5 h-3.5 text-emerald-400" />
                              </Button>

                              {isSuspended ? (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => setConfirmRestoreUser(u)}
                                  title="Restore Account"
                                >
                                  <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
                                </Button>
                              ) : (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => setConfirmSuspendUser(u)}
                                  title="Suspend Account"
                                >
                                  <UserX className="w-3.5 h-3.5 text-rose-400" />
                                </Button>
                              )}

                              {adminRole === 'SUPER_ADMIN' && (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => setConfirmDeleteUser(u)}
                                  title="Delete User"
                                >
                                  <Trash2 className="w-3.5 h-3.5 text-rose-500" />
                                </Button>
                              )}
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        <div className="p-4 border-t border-white/6">
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            totalItems={users.length}
            pageSize={pageSize}
            onPageChange={setCurrentPage}
          />
        </div>
      </Card>

      {/* User Details Drawer */}
      <Drawer
        isOpen={!!selectedUserId}
        onClose={() => { setSelectedUserId(null); setUserDetails(null); }}
        title="User Account Details"
        width="lg"
      >
        {detailLoading ? (
          <LoadingSpinner message="Fetching user details & telemetry..." />
        ) : userDetails ? (
          <div className="space-y-6 text-xs">
            {/* User Meta */}
            <div className="p-4 rounded-xl bg-slate-900 border border-white/6 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-100 text-sm">{userDetails.user.full_name || 'Anonymous User'}</span>
                <Badge variant={getRoleBadgeVariant(userDetails.user.role)}>{userDetails.user.role}</Badge>
              </div>
              <div className="font-mono text-slate-300">{userDetails.user.email}</div>
              <div className="font-mono text-[11px] text-slate-400">ID: {userDetails.user.user_id}</div>
              <div className="flex gap-4 pt-2 text-[11px] text-slate-400 border-t border-white/6">
                <span>Plan: <strong className="text-slate-200">{userDetails.user.subscription_plan}</strong></span>
                <span>Verified: <strong className="text-slate-200">{userDetails.user.is_verified ? 'Yes' : 'No'}</strong></span>
              </div>
            </div>

            {/* Quota Details */}
            <div className="space-y-2">
              <h4 className="font-semibold text-slate-200 flex items-center gap-1.5">
                <Clock className="w-4 h-4 text-blue-400" />
                <span>Usage & Free Quota Telemetry</span>
              </h4>
              <div className="p-3 bg-slate-900/60 border border-white/6 rounded-lg space-y-1.5 font-mono text-[11px]">
                <div className="flex justify-between">
                  <span className="text-slate-400">Daily Requests Count:</span>
                  <span className="text-slate-200">{userDetails.quota?.request_count || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Tokens Consumed:</span>
                  <span className="text-slate-200">{userDetails.quota?.token_count || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Cooldown Active:</span>
                  <span className="text-slate-200">{userDetails.quota?.cooldown_until || 'None'}</span>
                </div>
              </div>
            </div>

            {/* Registered Devices */}
            <div className="space-y-2">
              <h4 className="font-semibold text-slate-200 flex items-center gap-1.5">
                <HardDrive className="w-4 h-4 text-emerald-400" />
                <span>Registered Devices ({userDetails.devices?.length || 0})</span>
              </h4>
              <div className="space-y-1.5">
                {userDetails.devices?.length === 0 ? (
                  <p className="text-slate-400 italic">No devices registered.</p>
                ) : (
                  userDetails.devices?.map((d, i) => (
                    <div key={i} className="p-2.5 bg-slate-900/40 border border-white/6 rounded-lg flex items-center justify-between font-mono text-[11px]">
                      <span className="text-slate-300 truncate max-w-xs">{d.device_id}</span>
                      <span className="text-slate-400 text-[10px]">{d.created_at ? new Date(d.created_at).toLocaleDateString() : ''}</span>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Payment Orders */}
            <div className="space-y-2">
              <h4 className="font-semibold text-slate-200">Payment Orders History</h4>
              <div className="space-y-1.5">
                {userDetails.payment_orders?.length === 0 ? (
                  <p className="text-slate-400 italic">No payment history found.</p>
                ) : (
                  userDetails.payment_orders?.map((po, i) => (
                    <div key={i} className="p-2.5 bg-slate-900/40 border border-white/6 rounded-lg flex items-center justify-between text-xs">
                      <div>
                        <div className="font-mono text-slate-200 font-semibold">₹{(po.amount / 100).toFixed(2)}</div>
                        <div className="text-[10px] text-slate-400 font-mono">{po.order_id}</div>
                      </div>
                      <Badge variant={po.status === 'PAID' ? 'emerald' : po.status === 'REFUNDED' ? 'amber' : 'rose'}>
                        {po.status}
                      </Badge>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        ) : null}
      </Drawer>

      {/* Role Change Modal */}
      <Modal
        isOpen={!!roleModalUser}
        onClose={() => setRoleModalUser(null)}
        title="Update User Role"
        maxWidth="sm"
        footer={
          <>
            <Button variant="ghost" size="sm" onClick={() => setRoleModalUser(null)}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" onClick={handleUpdateRole} isLoading={actionLoading}>
              Update Role
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-xs text-slate-300">
            Updating administrative role for <span className="font-mono text-blue-400">{roleModalUser?.email}</span>.
          </p>
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">New Role</label>
            <select
              value={newRole}
              onChange={(e) => setNewRole(e.target.value)}
              className="w-full text-xs bg-slate-900 border border-white/10 rounded-lg p-2 text-slate-100 focus:outline-none focus:border-blue-500"
            >
              <option value="USER">USER (Regular User)</option>
              <option value="ANALYST">ANALYST (Read-Only Control Plane)</option>
              <option value="SUPPORT">SUPPORT (Diagnostics & Support)</option>
              <option value="ADMIN">ADMIN (Full Operations)</option>
              <option value="SUPER_ADMIN">SUPER_ADMIN (Unrestricted Operations)</option>
              <option value="SUSPENDED">SUSPENDED (Access Blocked)</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Reason (Audit Requirement)</label>
            <input
              type="text"
              value={roleReason}
              onChange={(e) => setRoleReason(e.target.value)}
              placeholder="e.g. Authorized staff promotion"
              className="w-full text-xs bg-slate-900 border border-white/10 rounded-lg p-2 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>
      </Modal>

      {/* Plan Change Modal */}
      <Modal
        isOpen={!!planModalUser}
        onClose={() => setPlanModalUser(null)}
        title="Update Subscription Plan"
        maxWidth="sm"
        footer={
          <>
            <Button variant="ghost" size="sm" onClick={() => setPlanModalUser(null)}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" onClick={handleUpdatePlan} isLoading={actionLoading}>
              Update Plan
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-xs text-slate-300">
            Modifying plan entitlement for <span className="font-mono text-emerald-400">{planModalUser?.email}</span>.
          </p>
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Target Plan</label>
            <select
              value={newPlan}
              onChange={(e) => setNewPlan(e.target.value)}
              className="w-full text-xs bg-slate-900 border border-white/10 rounded-lg p-2 text-slate-100 focus:outline-none focus:border-blue-500"
            >
              <option value="FREE">FREE (₹0)</option>
              <option value="STUDENT">STUDENT (₹99/mo)</option>
              <option value="PERSONAL">PERSONAL (₹399/mo)</option>
              <option value="POWER">POWER (₹799/mo)</option>
              <option value="TEAMS">TEAMS (₹699/user/mo)</option>
              <option value="ENTERPRISE">ENTERPRISE (Custom)</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Reason (Audit Requirement)</label>
            <input
              type="text"
              value={planReason}
              onChange={(e) => setPlanReason(e.target.value)}
              placeholder="e.g. Special customer upgrade approval"
              className="w-full text-xs bg-slate-900 border border-white/10 rounded-lg p-2 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>
      </Modal>

      {/* Suspend Confirmation */}
      <ConfirmDialog
        isOpen={!!confirmSuspendUser}
        onClose={() => setConfirmSuspendUser(null)}
        onConfirm={handleSuspend}
        title="Suspend User Account"
        message={`Are you sure you want to suspend '${confirmSuspendUser?.email}'? The user will immediately be locked out of all Saarthi services.`}
        confirmText="Suspend User"
        isDestructive={true}
        isLoading={actionLoading}
      />

      {/* Restore Confirmation */}
      <ConfirmDialog
        isOpen={!!confirmRestoreUser}
        onClose={() => setConfirmRestoreUser(null)}
        onConfirm={handleRestore}
        title="Restore User Account"
        message={`Restore active status for '${confirmRestoreUser?.email}'?`}
        confirmText="Restore Account"
        isDestructive={false}
        isLoading={actionLoading}
      />

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={!!confirmDeleteUser}
        onClose={() => setConfirmDeleteUser(null)}
        onConfirm={handleDelete}
        title="Permanently Delete User"
        message={`This action cannot be undone. User '${confirmDeleteUser?.email}' and all associated sessions will be permanently purged.`}
        confirmText="Delete Account"
        isDestructive={true}
        isLoading={actionLoading}
      />
    </div>
  );
};
