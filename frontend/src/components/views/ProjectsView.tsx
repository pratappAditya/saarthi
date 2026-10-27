import React, { useState, useEffect } from 'react';
import { FolderKanban, Plus, Trash2, Tag, Layers, ArrowRight } from 'lucide-react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { Input } from '../common/Input';
import { useApp } from '../../context/AppContext';

export const ProjectsView: React.FC = () => {
  const { addToast } = useApp();
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [domain, setDomain] = useState('career');
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/projects');
      if (res.ok) {
        const data = await res.json();
        setProjects(data.projects || []);
      }
    } catch (err) {
      console.error("Failed to load projects", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description, domain })
      });
      if (res.ok) {
        const data = await res.json();
        setProjects([data.project, ...projects]);
        setName('');
        setDescription('');
        setIsOpen(false);
        addToast({ type: 'success', title: 'Project Created', message: `Created project '${name}'.` });
      }
    } catch (err) {
      addToast({ type: 'error', title: 'Creation Failed', message: 'Could not create project.' });
    }
  };

  const handleDeleteProject = async (id: string) => {
    try {
      const res = await fetch(`/api/projects/${id}`, { method: 'DELETE' });
      if (res.ok) {
        setProjects(projects.filter(p => p.project_id !== id));
        addToast({ type: 'info', title: 'Project Removed', message: 'Deleted project workspace.' });
      }
    } catch (err) {
      addToast({ type: 'error', title: 'Delete Failed', message: 'Could not delete project.' });
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-200 font-mono text-xs">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[var(--border-subtle)]">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)] mb-1">
            <FolderKanban className="w-3.5 h-3.5 text-blue-400" />
            <span>SAARTHI UNIVERSAL PROJECT WORKSPACE</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Multi-Domain Projects
          </h1>
          <p className="text-xs text-gray-400 mt-0.5">
            Organize career targets, software development, academic research papers, and study workspaces.
          </p>
        </div>

        <Button variant="primary" size="sm" icon={Plus} onClick={() => setIsOpen(!isOpen)}>
          + Create Project
        </Button>
      </div>

      {/* Form */}
      {isOpen && (
        <Card variant="default" padding="md" className="space-y-3">
          <h3 className="font-bold text-white text-sm">Create Multi-Domain Project</h3>
          <form onSubmit={handleCreateProject} className="space-y-3">
            <Input label="Project Name" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Stripe Security Architect Target / Biology Thesis" required />
            <Input label="Description" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="e.g. Target job applications and interview prep materials." />
            <div>
              <label className="block text-[11px] font-mono text-gray-400 mb-1">Domain Pack</label>
              <select value={domain} onChange={(e) => setDomain(e.target.value)} className="w-full p-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs">
                <option value="career">Career Workspace</option>
                <option value="software">Software Development</option>
                <option value="research">Academic Research</option>
                <option value="cybersecurity">Cybersecurity</option>
                <option value="education">Education & Study</option>
                <option value="business">Business & Finance</option>
                <option value="general">General</option>
              </select>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" size="sm" onClick={() => setIsOpen(false)}>Cancel</Button>
              <Button variant="primary" size="sm" type="submit">Save Project</Button>
            </div>
          </form>
        </Card>
      )}

      {/* Projects Grid */}
      {loading ? (
        <div className="p-12 text-center text-gray-400">Loading Projects...</div>
      ) : projects.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-white/10 rounded-xl space-y-2 text-gray-400">
          <FolderKanban className="w-8 h-8 mx-auto text-blue-400 opacity-60" />
          <p className="font-bold text-white">No Active Projects</p>
          <p className="max-w-xs mx-auto">Create a project workspace to organize conversations, tasks, and memories.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((p) => (
            <Card key={p.project_id} variant="default" padding="md" className="space-y-3 flex flex-col justify-between">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Badge variant="accent" size="xs">{p.domain.toUpperCase()}</Badge>
                  <button onClick={() => handleDeleteProject(p.project_id)} className="text-rose-400 hover:text-rose-300 transition-all cursor-pointer">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
                <h3 className="font-bold text-white text-sm">{p.name}</h3>
                <p className="text-gray-400 text-[11px] leading-relaxed">{p.description || 'No description provided.'}</p>
              </div>

              <div className="pt-2 border-t border-white/10 flex items-center justify-between text-[10px] text-gray-400">
                <span>Created {new Date(p.created_at).toLocaleDateString()}</span>
                <span className="text-blue-400 flex items-center gap-1 cursor-pointer">Open <ArrowRight className="w-3 h-3" /></span>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
