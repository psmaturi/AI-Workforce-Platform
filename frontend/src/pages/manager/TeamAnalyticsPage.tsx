import React, { useEffect, useState } from 'react';
import { getSkillGap, getReadiness } from '../../api/mlApi';
import type { SkillGapResult, ReadinessResult } from '../../types';
import PageHeader from '../../components/common/PageHeader';
import StatusBadge from '../../components/common/StatusBadge';
import ReadinessBar from '../../components/charts/ReadinessBar';
import LoadingState from '../../components/common/LoadingState';
import ErrorState from '../../components/common/ErrorState';
import { pct } from '../../utils/formatters';

const TARGET_ROLE_ID = 5;

const TEAM_MEMBERS = [
  { id: 1, name: 'Gareth Williams', role: 'Mechanical Engineer', grade: 5 },
  { id: 2, name: 'Ahmed Khalil', role: 'Sr. Mechanical Engineer', grade: 6 },
  { id: 3, name: 'Natasha Reeves', role: 'Jr. Mechanical Engineer', grade: 3 },
];

interface RowData {
  empId: number;
  name: string;
  role: string;
  grade: number;
  gap: SkillGapResult | null;
  readiness: ReadinessResult | null;
  error: boolean;
}

const TeamAnalyticsPage: React.FC = () => {
  const [rows, setRows] = useState<RowData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = async () => {
    setLoading(true); setError(null);
    try {
      const results = await Promise.all(
        TEAM_MEMBERS.map(async (m) => {
          try {
            const [gap, readiness] = await Promise.all([
              getSkillGap(m.id, TARGET_ROLE_ID),
              getReadiness(m.id, TARGET_ROLE_ID),
            ]);
            return { empId: m.id, name: m.name, role: m.role, grade: m.grade, gap, readiness, error: false };
          } catch {
            return { empId: m.id, name: m.name, role: m.role, grade: m.grade, gap: null, readiness: null, error: true };
          }
        })
      );
      setRows(results);
    }
    catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetch(); }, []);

  if (loading) return <LoadingState message="Loading team analytics…" />;
  if (error) return <ErrorState message={error} onRetry={fetch} />;

  return (
    <div>
      <PageHeader title="Team Analytics" subtitle="Mechanical Engineering — skill coverage and readiness overview" />
      <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                {['Employee', 'Role', 'Coverage', 'Readiness', 'Skill Gaps', 'Status'].map(h => (
                  <th key={h} className="px-5 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rows.map((row) => (
                <tr key={row.empId} className="hover:bg-slate-50">
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-full bg-slate-200 flex items-center justify-center text-xs font-semibold text-slate-600">
                        {row.name.charAt(0)}
                      </div>
                      <div>
                        <p className="font-medium text-slate-800">{row.name}</p>
                        <p className="text-xs text-slate-400">Grade {row.grade}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-4 text-slate-600">{row.role}</td>
                  <td className="px-5 py-4">
                    {row.gap ? (
                      <div className="flex items-center gap-2">
                        <div className="w-20 h-1.5 bg-slate-100 rounded-full">
                          <div className="h-full bg-blue-500 rounded-full" style={{ width: `${row.gap.coverage_percentage}%` }} />
                        </div>
                        <span className="text-xs text-slate-600">{pct(row.gap.coverage_percentage)}</span>
                      </div>
                    ) : <span className="text-xs text-slate-400">—</span>}
                  </td>
                  <td className="px-5 py-4">
                    {row.readiness ? (
                      <div className="w-32">
                        <ReadinessBar score={row.readiness.readiness_score} classification={row.readiness.classification} />
                      </div>
                    ) : <span className="text-xs text-slate-400">—</span>}
                  </td>
                  <td className="px-5 py-4 text-slate-600">
                    {row.gap ? `${row.gap.missing_skills.length + row.gap.upgrade_needed.length}` : '—'}
                  </td>
                  <td className="px-5 py-4">
                    {row.readiness ? (
                      <StatusBadge
                        label={row.readiness.classification}
                        className={`${
                          row.readiness.classification === 'Ready' ? 'bg-green-100 text-green-800 border border-green-200' :
                          row.readiness.classification === 'Nearly Ready' ? 'bg-amber-100 text-amber-800 border border-amber-200' :
                          'bg-orange-100 text-orange-800 border border-orange-200'
                        }`}
                      />
                    ) : <span className="text-xs text-red-400">Error</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default TeamAnalyticsPage;
