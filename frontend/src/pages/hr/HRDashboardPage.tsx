import React, { useEffect, useState } from 'react';
import { getHRDashboard } from '../../api/mlApi';
import PageHeader from '../../components/common/PageHeader';
import MetricCard from '../../components/common/MetricCard';
import LoadingState from '../../components/common/LoadingState';
import ErrorState from '../../components/common/ErrorState';
import StatusBadge from '../../components/common/StatusBadge';
import { riskColour, pct, readinessColour } from '../../utils/formatters';
import { Building2, Users, AlertTriangle, TrendingUp, Shield, GraduationCap, Briefcase } from 'lucide-react';

const HRDashboardPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getHRDashboard();
      setData(res);
    }
    catch (e: any) {
      setError(e.message || 'Failed to fetch HR organizational data.');
    }
    finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetch();
  }, []);

  if (loading) return <LoadingState message="Loading organisation overview…" />;
  if (error) return <ErrorState message={error} onRetry={fetch} />;

  const risks = data?.risks ?? [];
  const critRisks = risks.filter((r: any) => r.risk_level === 'Critical' || r.risk_level === 'High');

  return (
    <div>
      <PageHeader title="Organisation Overview" subtitle="HR Intelligence Dashboard · SteelCore Industries" />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <MetricCard label="Departments" value={data?.departments_count ?? 0} sub="Active departments" icon={<Building2 size={16} />} />
        <MetricCard label="Total Employees" value={data?.total_employees ?? 0} sub="Active workforce" icon={<Users size={16} />} />
        <MetricCard
          label="Avg Workforce Readiness"
          value={data ? pct(data.avg_readiness) : '—'}
          sub="Across organization"
          icon={<TrendingUp size={16} />}
        />
        <MetricCard
          label="High-Risk Skills"
          value={data?.high_risk_skills_count ?? 0}
          sub="Critical or high level"
          icon={<AlertTriangle size={16} />}
          accent={(data?.high_risk_skills_count ?? 0) > 0 ? 'text-red-700' : 'text-green-700'}
        />
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <MetricCard label="Roles" value={data?.roles_count ?? 0} sub="Active job roles" icon={<Briefcase size={16} />} />
        <MetricCard label="Training Completion" value={data ? pct(data.training_completion) : '—'} sub="Average completion" icon={<GraduationCap size={16} />} />
        <MetricCard label="Critical Skills" value={data?.critical_skills ?? 0} sub="Key competencies" icon={<Shield size={16} />} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Departments */}
        <div className="bg-white border border-slate-200 rounded-lg p-5">
          <h2 className="text-sm font-semibold text-slate-800 mb-4">Departments</h2>
          <div className="max-h-60 overflow-y-auto space-y-2 pr-2">
            {(data?.departments ?? []).map((d: any) => (
              <div key={d.code} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
                <div>
                  <p className="text-sm font-medium text-slate-800">{d.name}</p>
                  <p className="text-xs text-slate-400">{d.code}</p>
                </div>
                <span className="text-sm text-slate-600">{d.employees} employees</span>
              </div>
            ))}
          </div>
        </div>

        {/* Skill risks */}
        <div className="bg-white border border-slate-200 rounded-lg p-5">
          <h2 className="text-sm font-semibold text-slate-800 mb-4">
            Workforce Skill Risks <span className="text-slate-400 font-normal">({risks.length})</span>
          </h2>
          {risks.length === 0 ? (
            <div className="flex items-center gap-2 text-sm text-green-700">
              <Shield size={16} /> No significant risks detected.
            </div>
          ) : (
            <ul className="space-y-2 max-h-60 overflow-y-auto pr-2">
              {risks.map((r: any, i: number) => (
                <li key={i} className="flex items-center justify-between gap-3 text-sm py-1.5 border-b border-slate-100 last:border-0">
                  <div>
                    <p className="font-medium text-slate-800">{r.risk_type}</p>
                    {r.skill && <p className="text-xs text-slate-500">{r.skill} ({r.department})</p>}
                  </div>
                  <StatusBadge label={r.risk_level} className={riskColour(r.risk_level)} />
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default HRDashboardPage;
