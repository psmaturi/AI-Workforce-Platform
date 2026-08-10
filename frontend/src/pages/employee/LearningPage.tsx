import React, { useEffect, useState } from 'react';
import { getTrainingRecommendations } from '../../api/mlApi';
import type { TrainingRecommendation } from '../../types';
import PageHeader from '../../components/common/PageHeader';
import LoadingState from '../../components/common/LoadingState';
import ErrorState from '../../components/common/ErrorState';
import EmptyState from '../../components/common/EmptyState';
import { BookOpen, Clock } from 'lucide-react';

const EMPLOYEE_ID = 1;
const TARGET_ROLE_ID = 5;

const LearningPage: React.FC = () => {
  const [recs, setRecs] = useState<TrainingRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = async () => {
    setLoading(true); setError(null);
    try { setRecs(await getTrainingRecommendations(EMPLOYEE_ID, TARGET_ROLE_ID)); }
    catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetch(); }, []);

  if (loading) return <LoadingState message="Loading course recommendations…" />;
  if (error) return <ErrorState message={error} onRetry={fetch} />;

  return (
    <div>
      <PageHeader
        title="Learning Recommendations"
        subtitle="Courses recommended based on your skill gaps for EAF Mechanical Specialist"
      />

      {recs.length === 0 ? (
        <EmptyState message="No course recommendations available. Ensure skill gap data is up to date." />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {recs.map((r) => (
            <div key={r.course_id} className="bg-white border border-slate-200 rounded-lg p-5 flex flex-col gap-3">
              <div className="flex items-start gap-2">
                <div className="p-2 bg-blue-50 rounded">
                  <BookOpen size={16} className="text-blue-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-900 leading-tight">{r.title}</p>
                  <p className="text-xs text-slate-500 mt-0.5">Skill: {r.target_skill}</p>
                </div>
              </div>

              <p className="text-xs text-slate-600 leading-relaxed">{r.explanation}</p>

              <div className="flex items-center justify-between mt-auto pt-2 border-t border-slate-100">
                <div className="flex items-center gap-1 text-xs text-slate-500">
                  <Clock size={11} />
                  <span>ML Score</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-1.5 w-24 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-500 rounded-full"
                      style={{ width: `${r.overall_score}%` }}
                    />
                  </div>
                  <span className="text-xs font-semibold text-blue-700">{r.overall_score}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default LearningPage;
