import React, { useState } from 'react';
import { 
  Kanban as KanbanIcon, 
  List, 
  Clock, 
  Plus, 
  Building2, 
  Calendar, 
  DollarSign, 
  MapPin, 
  FileText, 
  Send, 
  ChevronRight, 
  Trash2, 
  ExternalLink,
  Sparkles,
  Bot,
  Filter
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { Tabs } from '../common/Tabs';
import { Drawer } from '../common/Drawer';
import { Modal } from '../common/Modal';
import { Input, Textarea } from '../common/Input';
import type { ApplicationItem } from '../../types';

export const ApplicationsView: React.FC = () => {
  const { 
    applications, 
    activeApplication, 
    setActiveApplication, 
    updateApplicationStage, 
    addApplication, 
    deleteApplication,
    setIsAssistantOpen,
    setActiveSection,
    addToast
  } = useApp();

  const [viewMode, setViewMode] = useState<'kanban' | 'list' | 'timeline'>('kanban');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newCompany, setNewCompany] = useState('');
  const [newRole, setNewRole] = useState('');
  const [newSalary, setNewSalary] = useState('');
  const [newLocation, setNewLocation] = useState('Remote');

  const stages: { id: ApplicationItem['stage']; label: string; color: string }[] = [
    { id: 'saved', label: 'Saved', color: 'border-neutral-700' },
    { id: 'applied', label: 'Applied', color: 'border-blue-500/30' },
    { id: 'screening', label: 'Screening', color: 'border-indigo-500/30' },
    { id: 'interview', label: 'Interview', color: 'border-amber-500/30' },
    { id: 'offer', label: 'Offer', color: 'border-emerald-500/40' },
    { id: 'rejected', label: 'Archived', color: 'border-neutral-800' }
  ];

  const handleCreateApp = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCompany || !newRole) return;
    addApplication({
      company: newCompany,
      role: newRole,
      salaryRange: newSalary || '$180k – $220k',
      location: newLocation,
      stage: 'applied'
    });
    setIsAddModalOpen(false);
    setNewCompany('');
    setNewRole('');
    setNewSalary('');
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-200">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)] mb-1">
            <KanbanIcon className="w-3.5 h-3.5 text-blue-400" />
            <span>APPLICATION PIPELINE TRACKER</span>
          </div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)] tracking-tight font-display-title">
            Applications ({applications.length})
          </h1>
          <p className="text-xs text-[var(--text-secondary)] mt-0.5">
            Track interview rounds, follow-up deadlines, compensation offers, and tailored resume attachments.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Tabs
            tabs={[
              { id: 'kanban', label: 'Kanban', icon: KanbanIcon },
              { id: 'list', label: 'List View', icon: List },
              { id: 'timeline', label: 'Timeline', icon: Clock }
            ]}
            activeTab={viewMode}
            onChange={(t) => setViewMode(t as any)}
            variant="segmented"
          />

          <Button
            variant="primary"
            size="sm"
            icon={Plus}
            onClick={() => setIsAddModalOpen(true)}
          >
            New Application
          </Button>
        </div>
      </div>

      {/* KANBAN VIEW */}
      {viewMode === 'kanban' && (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-3 min-h-[520px] overflow-x-auto pb-4">
          {stages.map((stage) => {
            const stageApps = applications.filter(a => a.stage === stage.id);
            return (
              <div
                key={stage.id}
                className="flex flex-col rounded-[var(--radius-lg)] bg-[var(--bg-subtle)]/40 border border-[var(--border-subtle)] p-2.5 min-w-[200px]"
              >
                {/* Column Header */}
                <div className="flex items-center justify-between px-1 py-1.5 mb-2 border-b border-[var(--border-subtle)]">
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-bold text-[var(--text-primary)] font-display-title">
                      {stage.label}
                    </span>
                    <span className="text-[10px] font-mono px-1.5 rounded-full bg-[var(--bg-surface-elevated)] text-[var(--text-secondary)]">
                      {stageApps.length}
                    </span>
                  </div>
                </div>

                {/* Cards */}
                <div className="space-y-2 flex-1">
                  {stageApps.map((app) => (
                    <div
                      key={app.id}
                      onClick={() => setActiveApplication(app)}
                      className="p-3 rounded-[var(--radius-md)] bg-[var(--bg-surface)] hover:bg-[var(--bg-surface-elevated)] border border-[var(--border-subtle)] hover:border-[var(--border-strong)] transition-all cursor-pointer space-y-2 shadow-xs"
                    >
                      <div className="flex items-start justify-between gap-1">
                        <div>
                          <div className="text-xs font-bold text-[var(--text-primary)] font-display-title">
                            {app.company}
                          </div>
                          <div className="text-[11px] text-[var(--text-secondary)] line-clamp-1">
                            {app.role}
                          </div>
                        </div>
                        <span className="text-[10px] font-mono font-semibold text-emerald-400">
                          {app.matchScore}%
                        </span>
                      </div>

                      <div className="text-[10px] font-mono text-[var(--text-muted)] flex items-center justify-between pt-1 border-t border-[var(--border-subtle)]">
                        <span className="truncate">{app.salaryRange.split(' ')[0]}</span>
                        <span>{app.dateApplied.slice(5)}</span>
                      </div>
                    </div>
                  ))}

                  {stageApps.length === 0 && (
                    <div className="h-24 flex items-center justify-center text-[11px] text-[var(--text-muted)] border border-dashed border-[var(--border-subtle)] rounded-[var(--radius-md)]">
                      No applications
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* LIST VIEW */}
      {viewMode === 'list' && (
        <Card variant="default" padding="none" className="overflow-hidden">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-[var(--border-subtle)] bg-[var(--bg-surface-elevated)]/50 text-[var(--text-secondary)] font-mono text-[10px] uppercase">
                <th className="py-3 px-4">Company & Role</th>
                <th className="py-3 px-4">Stage</th>
                <th className="py-3 px-4">Match Score</th>
                <th className="py-3 px-4">Salary Range</th>
                <th className="py-3 px-4">Follow-Up Date</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border-subtle)]">
              {applications.map((app) => (
                <tr
                  key={app.id}
                  onClick={() => setActiveApplication(app)}
                  className="hover:bg-[var(--bg-surface-elevated)] cursor-pointer transition-colors"
                >
                  <td className="py-3 px-4">
                    <div className="font-bold text-[var(--text-primary)]">{app.company}</div>
                    <div className="text-[11px] text-[var(--text-muted)]">{app.role}</div>
                  </td>
                  <td className="py-3 px-4">
                    <Badge variant={app.stage === 'offer' ? 'success' : app.stage === 'interview' ? 'warning' : 'default'} size="xs">
                      {app.stage.toUpperCase()}
                    </Badge>
                  </td>
                  <td className="py-3 px-4 font-mono font-bold text-emerald-400">
                    {app.matchScore}%
                  </td>
                  <td className="py-3 px-4 font-mono text-[var(--text-secondary)]">
                    {app.salaryRange}
                  </td>
                  <td className="py-3 px-4 font-mono text-[var(--text-muted)]">
                    {app.nextFollowUpDate}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <Button variant="ghost" size="xs">
                      Details
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}

      {/* TIMELINE VIEW */}
      {viewMode === 'timeline' && (
        <Card variant="default" padding="lg" className="space-y-6">
          <h3 className="text-sm font-semibold text-[var(--text-primary)] font-display-title">
            Application Milestone Timeline
          </h3>

          <div className="space-y-6 pl-4 border-l-2 border-[var(--border-strong)]">
            {applications.flatMap(a => a.timeline.map(t => ({ ...t, company: a.company, role: a.role }))).slice(0, 8).map((event, idx) => (
              <div key={idx} className="relative pl-6 space-y-1">
                <div className="absolute -left-[31px] top-1 w-3 h-3 rounded-full bg-blue-500 border-2 border-[var(--bg-surface)]" />
                <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-muted)]">
                  <span>{event.date}</span>
                  <span>•</span>
                  <strong className="text-blue-400">{event.company}</strong>
                </div>
                <div className="text-xs font-bold text-[var(--text-primary)] font-display-title">
                  {event.event}
                </div>
                {event.details && (
                  <p className="text-[11px] text-[var(--text-secondary)] leading-relaxed">{event.details}</p>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* APPLICATION DETAILS DRAWER */}
      {activeApplication && (
        <Drawer
          isOpen={!!activeApplication}
          onClose={() => setActiveApplication(null)}
          title={
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded bg-[var(--bg-surface-elevated)] border border-[var(--border-strong)] flex items-center justify-center text-blue-400 font-bold text-xs">
                {activeApplication.companyLogoText}
              </div>
              <div>
                <h3 className="text-sm font-bold text-[var(--text-primary)] font-display-title">
                  {activeApplication.company}
                </h3>
                <p className="text-[11px] text-[var(--text-secondary)] truncate max-w-[260px]">
                  {activeApplication.role}
                </p>
              </div>
            </div>
          }
          width="lg"
        >
          {/* Stage Switcher */}
          <div className="p-3 rounded-[var(--radius-md)] bg-[var(--bg-subtle)] border border-[var(--border-subtle)] space-y-2">
            <span className="text-[10px] font-mono text-[var(--text-muted)] uppercase">Current Stage</span>
            <div className="flex flex-wrap gap-1.5">
              {stages.map((st) => (
                <button
                  key={st.id}
                  onClick={() => updateApplicationStage(activeApplication.id, st.id)}
                  className={`px-2.5 py-1 rounded text-xs font-medium transition-all cursor-pointer ${
                    activeApplication.stage === st.id
                      ? 'bg-[var(--accent-primary)] text-white font-bold'
                      : 'bg-[var(--bg-surface)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] border border-[var(--border-subtle)]'
                  }`}
                >
                  {st.label}
                </button>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-2 gap-2">
            <Button
              variant="primary"
              size="sm"
              icon={Send}
              onClick={() => setIsAssistantOpen(true)}
            >
              Draft Follow-up Note
            </Button>
            <Button
              variant="secondary"
              size="sm"
              icon={Sparkles}
              onClick={() => setActiveSection('interviews')}
            >
              Prep STAR Questions
            </Button>
          </div>

          {/* Key Details */}
          <div className="space-y-2 text-xs font-mono">
            <div className="flex justify-between p-2 rounded bg-[var(--bg-subtle)]">
              <span className="text-[var(--text-muted)]">Salary:</span>
              <span className="text-[var(--text-primary)]">{activeApplication.salaryRange}</span>
            </div>
            <div className="flex justify-between p-2 rounded bg-[var(--bg-subtle)]">
              <span className="text-[var(--text-muted)]">Location:</span>
              <span className="text-[var(--text-primary)]">{activeApplication.location}</span>
            </div>
            <div className="flex justify-between p-2 rounded bg-[var(--bg-subtle)]">
              <span className="text-[var(--text-muted)]">Attached Resume:</span>
              <span className="text-blue-400">{activeApplication.resumeUsedTitle.split(' ')[0]}</span>
            </div>
          </div>

          {/* Notes */}
          <div className="space-y-1">
            <span className="text-xs font-bold text-[var(--text-primary)] font-display-title">Interview & Recruiter Notes</span>
            <p className="text-xs text-[var(--text-secondary)] p-3 rounded-[var(--radius-md)] bg-[var(--bg-subtle)] border border-[var(--border-subtle)] leading-relaxed">
              {activeApplication.notes}
            </p>
          </div>

          {/* Timeline Events */}
          <div className="space-y-2 pt-2 border-t border-[var(--border-subtle)]">
            <span className="text-xs font-bold text-[var(--text-primary)] font-display-title">Timeline History</span>
            <div className="space-y-2">
              {activeApplication.timeline.map((ev, i) => (
                <div key={i} className="p-2 rounded bg-[var(--bg-subtle)] text-xs">
                  <div className="flex justify-between text-[10px] font-mono text-[var(--text-muted)]">
                    <span>{ev.date}</span>
                  </div>
                  <div className="font-semibold text-[var(--text-primary)] mt-0.5">{ev.event}</div>
                  {ev.details && <p className="text-[11px] text-[var(--text-secondary)] mt-0.5">{ev.details}</p>}
                </div>
              ))}
            </div>
          </div>

          {/* Delete Action */}
          <div className="pt-4 border-t border-[var(--border-subtle)] flex justify-end">
            <Button
              variant="danger"
              size="xs"
              icon={Trash2}
              onClick={() => deleteApplication(activeApplication.id)}
            >
              Remove Application
            </Button>
          </div>
        </Drawer>
      )}

      {/* CREATE APPLICATION MODAL */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Track New Application"
        subtitle="Add a target company and role to your career pipeline."
      >
        <form onSubmit={handleCreateApp} className="space-y-4">
          <Input
            label="Company Name"
            value={newCompany}
            onChange={(e) => setNewCompany(e.target.value)}
            placeholder="e.g. Stripe, Figma, Anthropic"
            required
          />

          <Input
            label="Role Title"
            value={newRole}
            onChange={(e) => setNewRole(e.target.value)}
            placeholder="e.g. Staff Frontend Architect"
            required
          />

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Salary Range"
              value={newSalary}
              onChange={(e) => setNewSalary(e.target.value)}
              placeholder="e.g. $220k – $280k"
            />
            <Input
              label="Location"
              value={newLocation}
              onChange={(e) => setNewLocation(e.target.value)}
              placeholder="e.g. Remote / San Francisco"
            />
          </div>

          <div className="flex justify-end gap-2 pt-4 border-t border-[var(--border-subtle)]">
            <Button variant="ghost" onClick={() => setIsAddModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              Track Application
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
