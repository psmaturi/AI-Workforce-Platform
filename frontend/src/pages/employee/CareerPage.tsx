import React, { useEffect, useState } from 'react';
import { getReadiness, getSkillGap } from '../../api/mlApi';
import type { ReadinessResult, SkillGapResult } from '../../types';
import PageHeader from '../../components/common/PageHeader';
import ReadinessBar from '../../components/charts/ReadinessBar';
import LoadingState from '../../components/common/LoadingState';
import ErrorState from '../../components/common/ErrorState';
import { readinessColour } from '../../utils/formatters';
import { ArrowDown } from 'lucide-react';

const EMPLOYEE_ID = 1;
const TARGET_ROLE_ID = 5;

const CAREER_PATH = [
  { title: 'Mechanical Trainee', grade: 1, active: false },
  { title: 'Junior Mechanical Engineer', grade: 3, active: false },
  { title: 'Mechanical Engineer', grade: 5, active: true, current: true },
  { title: 'Senior Mechanical Engineer', grade: 6, active: false },
  { title: 'EAF Mechanical Specialist', grade: 7, active: false, target: true },
  { title: 'Maintenance Manager', grade: 9, active: false },
];

const CareerPage: React.FC = () => {
  const [readiness, setReadiness] = useState<ReadinessResult | null>(null);
  const [gap, setGap] = useState<SkillGapResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = async () => {
    setLoading(true); setError(null);
    try {
      const [r, g] = await Promise.all([
        getReadiness(EMPLOYEE_ID, TARGET_ROLE_ID),
        getSkillGap(EMPLOYEE_ID, TARGET_ROLE_ID),
      ]);
      setReadiness(r); setGap(g);
    }
    catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetch(); }, []);

  if (loading) return <LoadingState message="Loading career path…" />;
  if (error) return <ErrorState message={error} onRetry={fetch} />;

  return (
    <div>
      <PageHeader title="Career Path" subtitle="Your progression towards EAF Mechanical Specialist" />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Career ladder */}
        <div className="bg-white border border-slate-200 rounded-lg p-5">
          <h2 className="text-sm font-semibold text-slate-800 mb-4">Career Progression — Mechanical Track</h2>
          <ol className="space-y-1">
            {CAREER_PATH.map((step, i) => (
              <li key={i} className="flex flex-col">
                <div className={`flex items-center gap-3 px-3 py-2.5 rounded-md ${
                  step.current ? 'bg-blue-50 border border-blue-200' :
                  step.target ? 'bg-amber-50 border border-amber-200' :
                  'border border-transparent'
                }`}>
                  <div className={`w-2.5 h-2.5 rounded-full shrink-0 ${
                    step.current ? 'bg-blue-500' :
                    step.target ? 'bg-amber-500' :
                    'bg-slate-300'
                  }`} />
                  <div className="flex-1">
                    <p className={`text-sm font-medium ${step.current ? 'text-blue-800' : step.target ? 'text-amber-800' : 'text-slate-600'}`}>
                      {step.title}
                    </p>
                    <p className="text-xs text-slate-400">Grade {step.grade}</p>
                  </div>
                  {step.current && <span className="text-xs font-medium text-blue-600 bg-blue-100 px-2 py-0.5 rounded">Current</span>}
                  {step.target && <span className="text-xs font-medium text-amber-700 bg-amber-100 px-2 py-0.5 rounded">Target</span>}
                </div>
                {i < CAREER_PATH.length - 1 && (
                  <div className="flex justify-start ml-4 my-0.5">
                    <ArrowDown size={12} className="text-slate-300" />
                  </div>
                )}
              </li>
            ))}
          </ol>
        </div>

        {/* Readiness panel */}
        <div className="space-y-4">
          {readiness && (
            <div className="bg-white border border-slate-200 rounded-lg p-5">
              <h2 className="text-sm font-semibold text-slate-800 mb-3">Readiness for Target Role</h2>
              <ReadinessBar score={readiness.readiness_score} classification={readiness.classification} />
              <p className={`text-sm font-medium mt-2 ${readinessColour(readiness.classification)}`}>
                {readiness.classification}
              </p>
            </div>
          )}

          {gap && (
            <div className="bg-white border border-slate-200 rounded-lg p-5">
              <h2 className="text-sm font-semibold text-slate-800 mb-3">Skills to Develop</h2>
              {gap.missing_skills.length === 0 && gap.upgrade_needed.length === 0 ? (
                <p className="text-sm text-green-700">All skill requirements met.</p>
              ) : (
                <ul className="space-y-2">
                  {gap.missing_skills.map((s, i) => (
                    <li key={i} className="flex items-center justify-between text-sm">
                      <span className="text-slate-700">{s.skill}</span>
                      <span className="text-xs text-red-600 bg-red-50 border border-red-200 px-2 py-0.5 rounded">Missing</span>
                    </li>
                  ))}
                  {gap.upgrade_needed.map((s, i) => (
                    <li key={i} className="flex items-center justify-between text-sm">
                      <span className="text-slate-700">{s.skill}</span>
                      <span className="text-xs text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded">Upgrade needed</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CareerPage;
