import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { getSkillGap, getReadiness, getTrainingRecommendations } from '../../api/mlApi';
import type { SkillGapResult, ReadinessResult, TrainingRecommendation } from '../../types';
import MetricCard from '../../components/common/MetricCard';
import ReadinessBar from '../../components/charts/ReadinessBar';
import LoadingState from '../../components/common/LoadingState';
import ErrorState from '../../components/common/ErrorState';
import PageHeader from '../../components/common/PageHeader';
import { pct, readinessColour } from '../../utils/formatters';
import { Zap, BookOpen, TrendingUp, AlertTriangle } from 'lucide-react';

// Demo constants — employee 1 targeting role 5 (EAF Mechanical Specialist)
const EMPLOYEE_ID = 1;
const TARGET_ROLE_ID = 5;

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [gap, setGap] = useState<SkillGapResult | null>(null);
  const [readiness, setReadiness] = useState<ReadinessResult | null>(null);
  const [recs, setRecs] = useState<TrainingRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [gapData, readinessData, recsData] = await Promise.all([
        getSkillGap(EMPLOYEE_ID, TARGET_ROLE_ID),
        getReadiness(EMPLOYEE_ID, TARGET_ROLE_ID),
        getTrainingRecommendations(EMPLOYEE_ID, TARGET_ROLE_ID),
      ]);
      setGap(gapData);
      setReadiness(readinessData);
      setRecs(recsData);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  if (loading) return <LoadingState message="Loading your dashboard…" />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;

  return (
    <div>
      <PageHeader
        title={`Welcome back, ${user?.name?.split(' ')[0]}`}
        subtitle={`${user?.jobTitle} · ${user?.department}`}
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <MetricCard
          label="Role Readiness"
          value={readiness ? pct(readiness.readiness_score) : '—'}
          sub={readiness?.classification}
          icon={<TrendingUp size={16} />}
          accent={readiness ? readinessColour(readiness.classification) : 'text-slate-900'}
        />
        <MetricCard
          label="Skill Coverage"
          value={gap ? pct(gap.coverage_percentage) : '—'}
          sub={`${gap?.met_requirements ?? 0} / ${gap?.total_requirements ?? 0} skills met`}
          icon={<Zap size={16} />}
        />
        <MetricCard
          label="Skill Gaps"
          value={gap ? (gap.missing_skills.length + gap.upgrade_needed.length) : '—'}
          sub="Skills requiring attention"
          icon={<AlertTriangle size={16} />}
          accent={gap && (gap.missing_skills.length + gap.upgrade_needed.length) > 0 ? 'text-amber-700' : 'text-green-700'}
        />
        <MetricCard
          label="Recommendations"
          value={recs.length}
          sub="Courses suggested"
          icon={<BookOpen size={16} />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Readiness breakdown */}
        {readiness && (
          <div className="bg-white border border-slate-200 rounded-lg p-5">
            <h2 className="text-sm font-semibold text-slate-800 mb-4">
              Role Readiness — EAF Mechanical Specialist
            </h2>
            <ReadinessBar score={readiness.readiness_score} classification={readiness.classification} />
            <p className={`text-sm font-medium mt-2 ${readinessColour(readiness.classification)}`}>
              {readiness.classification}
            </p>
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
              {Object.entries(readiness.breakdown).map(([key, val]) => (
                <div key={key} className="flex justify-between border-b border-slate-100 pb-1">
                  <span className="text-slate-500 capitalize">{key.replace('_points', '')}</span>
                  <span className="font-medium text-slate-800">{val} pts</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Top skill gaps */}
        {gap && (
          <div className="bg-white border border-slate-200 rounded-lg p-5">
            <h2 className="text-sm font-semibold text-slate-800 mb-4">
              Priority Skill Gaps
            </h2>
            {gap.missing_skills.length + gap.upgrade_needed.length === 0 ? (
              <p className="text-sm text-green-700">All skill requirements met for this role.</p>
            ) : (
              <ul className="space-y-2">
                {[...gap.missing_skills.slice(0, 3), ...gap.upgrade_needed.slice(0, 3)].map((s, i) => (
                  <li key={i} className="flex items-center justify-between text-sm">
                    <span className="text-slate-700">{s.skill}</span>
                    <span className="px-2 py-0.5 text-xs rounded bg-amber-50 text-amber-700 border border-amber-200">
                      Gap: {s.gap}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {/* Top recommendations */}
        {recs.length > 0 && (
          <div className="bg-white border border-slate-200 rounded-lg p-5 lg:col-span-2">
            <h2 className="text-sm font-semibold text-slate-800 mb-4">Recommended Courses</h2>
            <ul className="space-y-3">
              {recs.slice(0, 3).map((r) => (
                <li key={r.course_id} className="flex items-start justify-between gap-4 border-b border-slate-100 pb-3">
                  <div>
                    <p className="text-sm font-medium text-slate-800">{r.title}</p>
                    <p className="text-xs text-slate-500 mt-0.5">{r.explanation}</p>
                  </div>
                  <span className="text-xs font-medium text-blue-700 shrink-0">{r.overall_score}%</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
