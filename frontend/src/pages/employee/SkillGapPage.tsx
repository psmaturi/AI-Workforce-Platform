import React, { useEffect, useState } from 'react';
import { getSkillGap } from '../../api/mlApi';
import type { SkillGapResult } from '../../types';
import PageHeader from '../../components/common/PageHeader';
import LoadingState from '../../components/common/LoadingState';
import ErrorState from '../../components/common/ErrorState';
import EmptyState from '../../components/common/EmptyState';
import StatusBadge from '../../components/common/StatusBadge';
import { pct, gapSeverity, riskColour } from '../../utils/formatters';
import { CheckCircle2 } from 'lucide-react';

const EMPLOYEE_ID = 1;
const TARGET_ROLE_ID = 5;

const profLabel = (n: number) => ['', 'Beginner', 'Intermediate', 'Advanced', 'Expert', 'Master'][n] ?? `L${n}`;

const SkillGapPage: React.FC = () => {
  const [data, setData] = useState<SkillGapResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = async () => {
    setLoading(true); setError(null);
    try { setData(await getSkillGap(EMPLOYEE_ID, TARGET_ROLE_ID)); }
    catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetch(); }, []);

  if (loading) return <LoadingState message="Analysing skill gaps…" />;
  if (error) return <ErrorState message={error} onRetry={fetch} />;
  if (!data) return <EmptyState message="No skill gap data available." />;

  const allGaps = [
    ...data.missing_skills.map(s => ({ ...s, type: 'missing' as const })),
    ...data.upgrade_needed.map(s => ({ ...s, type: 'upgrade' as const })),
  ];

  return (
    <div>
      <PageHeader
        title="Skill Gap Analysis"
        subtitle="Target role: EAF Mechanical Specialist (Grade 7)"
      />

      {/* Summary */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Coverage', value: pct(data.coverage_percentage), accent: data.coverage_percentage >= 70 ? 'text-green-700' : 'text-amber-700' },
          { label: 'Gap', value: pct(data.gap_percentage), accent: data.gap_percentage > 0 ? 'text-red-700' : 'text-green-700' },
          { label: 'Skills Met', value: `${data.met_requirements} / ${data.total_requirements}`, accent: 'text-slate-900' },
          { label: 'Missing Skills', value: data.missing_skills.length, accent: data.missing_skills.length > 0 ? 'text-amber-700' : 'text-green-700' },
        ].map(c => (
          <div key={c.label} className="bg-white border border-slate-200 rounded-lg p-4">
            <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">{c.label}</p>
            <p className={`text-xl font-semibold ${c.accent}`}>{c.value}</p>
          </div>
        ))}
      </div>

      {/* Gap Table */}
      {allGaps.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-lg p-8 flex flex-col items-center gap-2">
          <CheckCircle2 size={28} className="text-green-500" />
          <p className="text-sm font-medium text-green-700">All skill requirements met for this role.</p>
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
          <div className="px-5 py-3 border-b border-slate-100">
            <h2 className="text-sm font-semibold text-slate-800">Skill Gaps ({allGaps.length})</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-5 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">Skill</th>
                  <th className="px-5 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">Current</th>
                  <th className="px-5 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">Required</th>
                  <th className="px-5 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">Gap</th>
                  <th className="px-5 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">Severity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {allGaps.map((s, i) => {
                  const severity = gapSeverity(s.gap);
                  return (
                    <tr key={i} className="hover:bg-slate-50">
                      <td className="px-5 py-3 font-medium text-slate-800">{s.skill}</td>
                      <td className="px-5 py-3 text-slate-600">{s.type === 'missing' ? '—' : profLabel(s.current)}</td>
                      <td className="px-5 py-3 text-slate-600">{profLabel(s.required)}</td>
                      <td className="px-5 py-3 text-slate-600">{s.gap}</td>
                      <td className="px-5 py-3">
                        <StatusBadge label={severity} className={riskColour(severity === 'None' ? 'Low' : severity)} />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default SkillGapPage;
