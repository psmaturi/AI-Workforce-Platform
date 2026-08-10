import React, { useEffect, useState } from 'react';
import { getManagerDashboard } from '../../api/mlApi';
import { useAuth } from '../../context/AuthContext';
import PageHeader from '../../components/common/PageHeader';
import MetricCard from '../../components/common/MetricCard';
import LoadingState from '../../components/common/LoadingState';
import ErrorState from '../../components/common/ErrorState';
import StatusBadge from '../../components/common/StatusBadge';
import { pct, riskColour, readinessColour } from '../../utils/formatters';
import { Users, AlertTriangle, TrendingUp, CheckCircle2 } from 'lucide-react';

const ManagerDashboard: React.FC = () => {
  const { user } = useAuth();
  const managerId = user ? user.id : 2;
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getManagerDashboard(managerId);
      setData(res);
    }
    catch (e: any) {
      setError(e.message || 'Failed to fetch team analytics.');
    }
    finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetch();
  }, [managerId]);

  if (loading) return <LoadingState message="Loading manager dashboard…" />;
  if (error) return <ErrorState message={error} onRetry={fetch} />;

  const risks = data?.skill_risks ?? [];
  const criticalRisks = risks.filter((r: any) => r.risk_level === 'Critical' || r.risk_level === 'High');
  
  // Calculate average readiness status classification name
  let avgReadinessClass = 'Developing';
  if (data?.avg_readiness >= 80) avgReadinessClass = 'Ready';
  else if (data?.avg_readiness >= 60) avgReadinessClass = 'Developing';
  else avgReadinessClass = 'Needs Improvement';

  const reports = data?.reports ?? [];

  return (
    <div>
      <PageHeader title="Manager Dashboard" subtitle={`${user?.department || 'Mechanical Engineering'} Department`} />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <MetricCard label="Team Size" value={data?.team_size ?? 0} sub="Active employees" icon={<Users size={16} />} />
        <MetricCard
          label="Avg Readiness"
          value={data ? pct(data.avg_readiness) : '—'}
          sub={avgReadinessClass}
          icon={<TrendingUp size={16} />}
          accent={readinessColour(avgReadinessClass)}
        />
        <MetricCard
          label="Skill Coverage"
          value={data ? pct(data.avg_skill_coverage) : '—'}
          sub="Against target roles"
          icon={<CheckCircle2 size={16} />}
        />
        <MetricCard
          label="Critical Risks"
          value={criticalRisks.length}
          sub="High or critical level"
          icon={<AlertTriangle size={16} />}
          accent={criticalRisks.length > 0 ? 'text-red-700' : 'text-green-700'}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Team List */}
        <div className="bg-white border border-slate-200 rounded-lg p-5">
          <h2 className="text-sm font-semibold text-slate-800 mb-4">Direct Reports ({reports.length})</h2>
          {reports.length === 0 ? (
            <p className="text-sm text-slate-500">No direct reports found.</p>
          ) : (
            <div className="max-h-60 overflow-y-auto space-y-3 pr-2">
              {reports.map((r: any) => (
                <div key={r.id} className="flex items-center justify-between p-2 border border-slate-100 rounded-md hover:bg-slate-50">
                  <div>
                    <p className="text-sm font-medium text-slate-800">{r.name}</p>
                    <p className="text-xs text-slate-400">{r.role} • Target: {r.target_role}</p>
                  </div>
                  <div className="text-right">
                    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${readinessColour(r.classification)}`}>
                      {pct(r.readiness_score)} Readiness
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Skill risks */}
        <div className="bg-white border border-slate-200 rounded-lg p-5">
          <h2 className="text-sm font-semibold text-slate-800 mb-4">
            Skill Risks ({risks.length})
          </h2>
          {risks.length === 0 ? (
            <p className="text-sm text-green-700">No significant skill risks identified.</p>
          ) : (
            <ul className="space-y-2 max-h-60 overflow-y-auto pr-2">
              {risks.slice(0, 5).map((r: any, i: number) => (
                <li key={i} className="flex items-start justify-between gap-3 text-sm border-b border-slate-50 pb-2 last:border-0 last:pb-0">
                  <div>
                    <p className="font-medium text-slate-800">{r.risk_type}</p>
                    <p className="text-xs text-slate-500">{r.skill || 'Department-wide'}</p>
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

export default ManagerDashboard;
