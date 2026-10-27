import React, { useState, useEffect } from 'react';
import { Sparkles, Calendar, Clock, Zap, ShieldCheck, Play, ArrowRight, RefreshCw, CheckCircle2, AlertCircle, Plus, Trash2 } from 'lucide-react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';
import { useApp } from '../../context/AppContext';
import { api } from '../../api';

interface RoutineBuilderProps {
  onSuccess?: () => void;
}

export const RoutineBuilderView: React.FC<RoutineBuilderProps> = ({ onSuccess }) => {
  const { addToast } = useApp();
  const [builderMode, setBuilderMode] = useState<'natural' | 'visual' | 'templates'>('natural');
  const [nlPrompt, setNlPrompt] = useState<string>('');
  const [parsing, setParsing] = useState<boolean>(false);
  const [parsedPreview, setParsedPreview] = useState<any | null>(null);
  const [templates, setTemplates] = useState<any[]>([]);

  // Visual Builder State
  const [name, setName] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [triggerType, setTriggerType] = useState<string>('TIME_TRIGGER');
  const [frequency, setFrequency] = useState<string>('daily');
  const [timeOfDay, setTimeOfDay] = useState<string>('09:00');
  const [dayOfWeek, setDayOfWeek] = useState<string>('monday');
  const [autonomyLevel, setAutonomyLevel] = useState<string>('ASK');
  const [approvalPolicy, setApprovalPolicy] = useState<string>('ASK_FOR_EACH_HIGH_RISK_ACTION');
  const [domain, setDomain] = useState<string>('general');
  const [actionDescription, setActionDescription] = useState<string>('');

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const res = await api.getRoutineTemplates();
      if (res && res.templates) {
        setTemplates(res.templates);
      }
    } catch (e: any) {
      console.error("Failed to load templates", e);
    }
  };

  const handleParseNL = async () => {
    if (!nlPrompt.trim()) return;
    try {
      setParsing(true);
      const res = await api.parseRoutinePrompt(nlPrompt, domain);
      if (res && res.parsed_definition) {
        setParsedPreview(res.parsed_definition);
        addToast({
          type: 'success',
          title: 'Routine Parsed',
          message: 'Review structured definition before activation.'
        });
      }
    } catch (e: any) {
      addToast({ type: 'error', title: 'Parsing Failed', message: e.message });
    } finally {
      setParsing(false);
    }
  };

  const handleActivateParsed = async () => {
    if (!parsedPreview) return;
    try {
      await api.createRoutine({
        name: parsedPreview.name,
        description: parsedPreview.description,
        natural_language_definition: parsedPreview.natural_language_prompt,
        domain: parsedPreview.domain,
        trigger_type: parsedPreview.trigger_type,
        schedule: parsedPreview.schedule,
        conditions: parsedPreview.conditions,
        actions: parsedPreview.actions,
        autonomy_level: parsedPreview.autonomy_level,
        approval_policy: parsedPreview.approval_policy
      });

      addToast({
        type: 'success',
        title: 'Routine Activated',
        message: `Activated routine '${parsedPreview.name}'.`
      });

      setNlPrompt('');
      setParsedPreview(null);
      if (onSuccess) onSuccess();
    } catch (e: any) {
      addToast({ type: 'error', title: 'Activation Failed', message: e.message });
    }
  };

  const handleCreateVisual = async () => {
    if (!name.trim()) {
      addToast({ type: 'error', title: 'Validation Error', message: 'Please provide a routine name.' });
      return;
    }

    try {
      const scheduleObj = {
        frequency,
        time_of_day: timeOfDay,
        day_of_week: frequency === 'weekly' ? dayOfWeek : undefined
      };

      const actionsArr = actionDescription.trim() ? [{
        action_type: "custom_action",
        description: actionDescription,
        risk_level: "low"
      }] : [{
        action_type: "general_workflow",
        description: name,
        risk_level: "low"
      }];

      await api.createRoutine({
        name,
        description,
        domain,
        trigger_type: triggerType,
        schedule: scheduleObj,
        actions: actionsArr,
        autonomy_level: autonomyLevel,
        approval_policy: approvalPolicy
      });

      addToast({
        type: 'success',
        title: 'Routine Created',
        message: `Created routine '${name}'.`
      });

      setName('');
      setDescription('');
      setActionDescription('');
      if (onSuccess) onSuccess();
    } catch (e: any) {
      addToast({ type: 'error', title: 'Creation Failed', message: e.message });
    }
  };

  const handleInstantiateTemplate = async (templateId: string, templateName: string) => {
    try {
      await api.createRoutine({ template_id: templateId });
      addToast({
        type: 'success',
        title: 'Template Activated',
        message: `Activated template '${templateName}'.`
      });
      if (onSuccess) onSuccess();
    } catch (e: any) {
      addToast({ type: 'error', title: 'Template Activation Failed', message: e.message });
    }
  };

  return (
    <div className="space-y-6 font-sans text-white">
      {/* Header & Mode Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-4">
        <div>
          <h2 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-400" />
            <span>ROUTINE & AUTOMATION BUILDER</span>
          </h2>
          <p className="text-xs text-gray-400 font-mono mt-0.5">
            Create recurring or condition-triggered workflows with explicit human approval & safety policies.
          </p>
        </div>

        <div className="flex bg-black/40 p-1 rounded-xl border border-white/10 font-mono text-xs">
          <button
            onClick={() => setBuilderMode('natural')}
            className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer ${
              builderMode === 'natural' ? 'bg-purple-600 font-bold text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            Natural Language
          </button>
          <button
            onClick={() => setBuilderMode('visual')}
            className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer ${
              builderMode === 'visual' ? 'bg-purple-600 font-bold text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            Visual WHEN/IF/THEN
          </button>
          <button
            onClick={() => setBuilderMode('templates')}
            className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer ${
              builderMode === 'templates' ? 'bg-purple-600 font-bold text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            Pre-built Templates
          </button>
        </div>
      </div>

      {/* MODE 1: NATURAL LANGUAGE BUILDER */}
      {builderMode === 'natural' && (
        <div className="space-y-6 font-mono text-xs">
          <Card variant="default" padding="lg" className="space-y-4">
            <label className="font-bold text-white text-sm block">Describe your automation routine in natural language:</label>
            <div className="flex gap-2">
              <input
                type="text"
                value={nlPrompt}
                onChange={(e) => setNlPrompt(e.target.value)}
                placeholder="e.g. Every Monday at 9 AM review my active projects and tell me what needs attention"
                className="flex-1 bg-[#070a12] border border-white/10 rounded-xl p-3 text-white focus:outline-none placeholder-gray-500"
              />
              <Button variant="primary" size="md" icon={Sparkles} onClick={handleParseNL} disabled={parsing || !nlPrompt.trim()}>
                {parsing ? 'Parsing...' : 'Parse Routine'}
              </Button>
            </div>

            <div className="flex flex-wrap gap-2 text-[11px] text-gray-400 pt-1">
              <span className="text-gray-500">Quick Examples:</span>
              <button onClick={() => setNlPrompt("Every morning at 8 AM give me a personalized briefing.")} className="hover:text-purple-300 underline cursor-pointer">
                Morning Briefing
              </button>
              <span>·</span>
              <button onClick={() => setNlPrompt("Every Friday summarize my progress toward my goals.")} className="hover:text-purple-300 underline cursor-pointer">
                Weekly Goal Summary
              </button>
              <span>·</span>
              <button onClick={() => setNlPrompt("When my application reaches interview stage, prepare interview questions.")} className="hover:text-purple-300 underline cursor-pointer">
                Interview Stage Trigger
              </button>
            </div>
          </Card>

          {/* PARSED PREVIEW CARD */}
          {parsedPreview && (
            <Card variant="ai" padding="lg" className="space-y-4 border-purple-500/40 animate-in fade-in duration-200">
              <div className="flex items-center justify-between border-b border-white/10 pb-3">
                <div className="flex items-center gap-2">
                  <Badge variant="success" size="sm">PARSED ROUTINE PREVIEW</Badge>
                  <span className="font-bold text-white text-sm">{parsedPreview.name}</span>
                </div>
                <Badge variant="outline" size="sm">{parsedPreview.trigger_type}</Badge>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-[11px]">
                <div className="p-3 rounded-xl bg-black/40 border border-white/10 space-y-1">
                  <span className="text-gray-400 block font-bold">WHEN (Trigger):</span>
                  <p className="text-purple-300">{parsedPreview.schedule?.frequency || parsedPreview.trigger_type} at {parsedPreview.schedule?.time_of_day || 'Scheduled Time'}</p>
                </div>

                <div className="p-3 rounded-xl bg-black/40 border border-white/10 space-y-1">
                  <span className="text-gray-400 block font-bold">WITH (Autonomy & Approval):</span>
                  <p className="text-emerald-300">Autonomy: {parsedPreview.autonomy_level} · Approval: {parsedPreview.approval_policy}</p>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-black/40 border border-white/10 space-y-2">
                <span className="text-gray-400 block font-bold">THEN (Actions):</span>
                {parsedPreview.actions?.map((act: any, idx: number) => (
                  <div key={idx} className="flex items-center gap-2 text-gray-200">
                    <span className="w-5 h-5 rounded-full bg-purple-900/60 text-purple-300 flex items-center justify-center font-bold text-[10px]">{idx + 1}</span>
                    <span>{act.description}</span>
                  </div>
                ))}
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <Button variant="outline" size="sm" onClick={() => setParsedPreview(null)}>
                  Discard
                </Button>
                <Button variant="primary" size="sm" icon={Play} onClick={handleActivateParsed}>
                  Activate Routine
                </Button>
              </div>
            </Card>
          )}
        </div>
      )}

      {/* MODE 2: VISUAL BUILDER */}
      {builderMode === 'visual' && (
        <Card variant="default" padding="lg" className="space-y-5 font-mono text-xs">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-gray-400 block mb-1">Routine Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Weekly Project Health Check"
                className="w-full bg-[#070a12] border border-white/10 rounded-xl p-2.5 text-white focus:outline-none"
              />
            </div>
            <div>
              <label className="text-gray-400 block mb-1">Domain Context</label>
              <select
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                className="w-full bg-[#070a12] border border-white/10 rounded-xl p-2.5 text-white focus:outline-none capitalize"
              >
                <option value="general">General AI Companion</option>
                <option value="career">Career Workspace</option>
                <option value="software">Software Engineering</option>
                <option value="cybersecurity">Cybersecurity</option>
                <option value="research">Academic Research</option>
              </select>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-3">
            <span className="font-bold text-purple-400 text-sm flex items-center gap-2">
              <Clock className="w-4 h-4" /> WHEN (Trigger Type & Schedule)
            </span>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <label className="text-gray-400 block mb-1">Trigger Type</label>
                <select
                  value={triggerType}
                  onChange={(e) => setTriggerType(e.target.value)}
                  className="w-full bg-[#070a12] border border-white/10 rounded-xl p-2 text-white focus:outline-none"
                >
                  <option value="TIME_TRIGGER">Time-Based Schedule</option>
                  <option value="CONDITION_TRIGGER">Condition Event Trigger</option>
                  <option value="MANUAL_TRIGGER">Manual Execution Only</option>
                </select>
              </div>

              <div>
                <label className="text-gray-400 block mb-1">Frequency</label>
                <select
                  value={frequency}
                  onChange={(e) => setFrequency(e.target.value)}
                  className="w-full bg-[#070a12] border border-white/10 rounded-xl p-2 text-white focus:outline-none"
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                </select>
              </div>

              <div>
                <label className="text-gray-400 block mb-1">Time of Day</label>
                <input
                  type="time"
                  value={timeOfDay}
                  onChange={(e) => setTimeOfDay(e.target.value)}
                  className="w-full bg-[#070a12] border border-white/10 rounded-xl p-2 text-white focus:outline-none"
                />
              </div>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-3">
            <span className="font-bold text-blue-400 text-sm flex items-center gap-2">
              <Zap className="w-4 h-4" /> THEN (Action Workflow)
            </span>
            <div>
              <label className="text-gray-400 block mb-1">Action Description</label>
              <textarea
                value={actionDescription}
                onChange={(e) => setActionDescription(e.target.value)}
                placeholder="e.g. Inspect active projects for unassigned issues and approaching deadlines."
                rows={2}
                className="w-full bg-[#070a12] border border-white/10 rounded-xl p-2.5 text-white focus:outline-none"
              />
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-3">
            <span className="font-bold text-emerald-400 text-sm flex items-center gap-2">
              <ShieldCheck className="w-4 h-4" /> WITH (Autonomy & Approval Policy)
            </span>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label className="text-gray-400 block mb-1">Autonomy Level</label>
                <select
                  value={autonomyLevel}
                  onChange={(e) => setAutonomyLevel(e.target.value)}
                  className="w-full bg-[#070a12] border border-white/10 rounded-xl p-2 text-white focus:outline-none"
                >
                  <option value="OBSERVE">OBSERVE (Notify only)</option>
                  <option value="SUGGEST">SUGGEST (Recommend actions)</option>
                  <option value="ASK">ASK (Confirm high-risk actions)</option>
                  <option value="ACT">ACT (Execute pre-authorized low-risk)</option>
                </select>
              </div>

              <div>
                <label className="text-gray-400 block mb-1">Approval Policy</label>
                <select
                  value={approvalPolicy}
                  onChange={(e) => setApprovalPolicy(e.target.value)}
                  className="w-full bg-[#070a12] border border-white/10 rounded-xl p-2 text-white focus:outline-none"
                >
                  <option value="ALWAYS_ASK">ALWAYS_ASK (Prompt every action)</option>
                  <option value="ASK_FOR_EACH_HIGH_RISK_ACTION">ASK_FOR_EACH_HIGH_RISK_ACTION</option>
                  <option value="PRE_APPROVED_LOW_RISK">PRE_APPROVED_LOW_RISK</option>
                </select>
              </div>
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <Button variant="primary" size="md" icon={Play} onClick={handleCreateVisual}>
              Create Routine
            </Button>
          </div>
        </Card>
      )}

      {/* MODE 3: PRE-BUILT TEMPLATES */}
      {builderMode === 'templates' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-xs">
          {templates.map((t) => (
            <div key={t.template_id} className="p-4 rounded-2xl bg-[#0e1426] border border-white/10 space-y-3 flex flex-col justify-between">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white text-sm">{t.name}</span>
                  <Badge variant="accent" size="xs">{t.domain.toUpperCase()}</Badge>
                </div>
                <p className="text-gray-300 text-xs">{t.description}</p>
                <p className="text-purple-300 text-[11px] italic bg-black/40 p-2 rounded-xl border border-white/5">
                  "{t.natural_language_definition}"
                </p>
              </div>

              <div className="pt-2 border-t border-white/10 flex items-center justify-between">
                <span className="text-emerald-400 text-[10px]">Autonomy: {t.autonomy_level}</span>
                <Button variant="primary" size="sm" icon={Play} onClick={() => handleInstantiateTemplate(t.template_id, t.name)}>
                  Activate Template
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
