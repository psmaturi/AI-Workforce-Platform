import React from 'react';
import { useAuth } from '../context/AuthContext';
import PageHeader from '../components/common/PageHeader';
import { User, Bell, Info } from 'lucide-react';

const SettingsPage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div>
      <PageHeader title="Settings" subtitle="Account and application preferences" />

      <div className="max-w-2xl space-y-4">
        {/* Profile */}
        <div className="bg-white border border-slate-200 rounded-lg p-5">
          <div className="flex items-center gap-2 mb-4">
            <User size={16} className="text-slate-500" />
            <h2 className="text-sm font-semibold text-slate-800">Profile</h2>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            {[
              { label: 'Full Name', value: user?.name },
              { label: 'Employee Number', value: user?.employeeNumber },
              { label: 'Email', value: user?.email },
              { label: 'Department', value: user?.department },
              { label: 'Role', value: user?.jobTitle },
              { label: 'Grade', value: user?.grade },
            ].map(f => (
              <div key={f.label}>
                <p className="text-xs text-slate-500 mb-0.5">{f.label}</p>
                <p className="font-medium text-slate-800">{f.value ?? '—'}</p>
              </div>
            ))}
          </div>
          <p className="text-xs text-slate-400 mt-4">
            To update your profile information, contact your HR Business Partner.
          </p>
        </div>

        {/* Notifications */}
        <div className="bg-white border border-slate-200 rounded-lg p-5">
          <div className="flex items-center gap-2 mb-4">
            <Bell size={16} className="text-slate-500" />
            <h2 className="text-sm font-semibold text-slate-800">Notifications</h2>
          </div>
          {[
            { label: 'Skill gap alerts', desc: 'Notify when new skill gaps are identified' },
            { label: 'Training reminders', desc: 'Reminders for upcoming training deadlines' },
            { label: 'Career milestone updates', desc: 'Notify when readiness improves' },
          ].map(n => (
            <div key={n.label} className="flex items-start justify-between py-3 border-b border-slate-100 last:border-0">
              <div>
                <p className="text-sm font-medium text-slate-800">{n.label}</p>
                <p className="text-xs text-slate-500">{n.desc}</p>
              </div>
              <input type="checkbox" defaultChecked className="mt-1 accent-blue-600" aria-label={n.label} />
            </div>
          ))}
        </div>

        {/* App info */}
        <div className="bg-white border border-slate-200 rounded-lg p-5">
          <div className="flex items-center gap-2 mb-3">
            <Info size={16} className="text-slate-500" />
            <h2 className="text-sm font-semibold text-slate-800">Application Information</h2>
          </div>
          <div className="text-sm space-y-1.5">
            {[
              { k: 'Platform', v: 'AI Workforce Intelligence Platform' },
              { k: 'Version', v: 'v1.0.0 (Phase 6)' },
              { k: 'Organisation', v: 'SteelCore Industries Ltd' },
              { k: 'AI Engine', v: 'Qwen2.5:7b via Ollama' },
              { k: 'Backend', v: 'FastAPI + LangGraph + PostgreSQL + ChromaDB' },
            ].map(i => (
              <div key={i.k} className="flex gap-4">
                <span className="text-slate-500 w-32 shrink-0">{i.k}</span>
                <span className="text-slate-800">{i.v}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
