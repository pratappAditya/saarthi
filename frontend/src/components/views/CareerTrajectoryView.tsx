import React, { useState, useEffect } from 'react';
import { 
  GitCommit, GraduationCap, Briefcase, Code, Award, ShieldCheck, Sparkles 
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { api } from '../../api';

export const CareerTrajectoryView: React.FC = () => {
  const { activeResume } = useApp();
  const [trajectory, setTrajectory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTrajectory();
  }, [activeResume]);

  const loadTrajectory = async () => {
    try {
      setLoading(true);
      const res = await api.getCareerTrajectory();
      setTrajectory(res.trajectory || []);
    } catch (err) {
      console.error("Failed to load trajectory", err);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'education': return <GraduationCap className="w-4 h-4 text-blue-400" />;
      case 'experience': return <Briefcase className="w-4 h-4 text-emerald-400" />;
      case 'project': return <Code className="w-4 h-4 text-purple-400" />;
      default: return <Award className="w-4 h-4 text-amber-400" />;
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[var(--border-subtle)]">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)] mb-1">
            <GitCommit className="w-3.5 h-3.5 text-blue-400" />
            <span>VERIFIED CANDIDATE CAREER TRAJECTORY</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Visual Career Trajectory Timeline
          </h1>
          <p className="text-xs text-gray-400 mt-0.5">
            Strictly compiled from verified candidate facts stored in your Master Resume in SQLite. Zero hallucinated employment history.
          </p>
        </div>

        <Badge variant="ai" size="sm" dot>
          Derived from Master Resume
        </Badge>
      </div>

      {/* Trajectory Timeline List */}
      {loading ? (
        <div className="p-12 text-center text-xs text-gray-400">Loading Visual Trajectory...</div>
      ) : trajectory.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-[var(--border-subtle)] rounded-xl space-y-2 text-xs text-gray-400">
          <GitCommit className="w-8 h-8 mx-auto text-blue-400 opacity-60" />
          <p className="font-bold text-white">No Trajectory Events Derived</p>
          <p className="max-w-xs mx-auto">Upload or import your Master Resume to generate your verified visual career timeline.</p>
        </div>
      ) : (
        <div className="relative border-l-2 border-blue-500/30 ml-4 space-y-6 py-2">
          {trajectory.map((item, index) => (
            <div key={index} className="relative pl-6">
              {/* Dot Icon */}
              <div className="absolute -left-[17px] top-1 p-1.5 rounded-full bg-[#101524] border border-blue-500/40 text-blue-400">
                {getCategoryIcon(item.category)}
              </div>

              <Card variant="default" padding="md" className="space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-blue-400 font-mono font-bold text-[11px]">{item.period}</span>
                  <Badge variant="outline" size="xs">{item.category}</Badge>
                </div>
                <h3 className="font-bold text-white text-sm">{item.title}</h3>
                <p className="text-gray-400 font-mono text-[11px]">{item.organization}</p>

                {item.highlights && item.highlights.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-2 border-t border-white/10">
                    {item.highlights.map((h: string, hi: number) => (
                      <span key={hi} className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-gray-300 text-[10px] font-mono">
                        • {h}
                      </span>
                    ))}
                  </div>
                )}
              </Card>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
