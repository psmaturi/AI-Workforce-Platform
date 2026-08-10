import React, { useEffect, useState } from 'react';
import { getWorkforceRisks } from '../../api/mlApi';
import type { SkillRisk } from '../../types';
import PageHeader from '../../components/common/PageHeader';
import LoadingState from '../../components/common/LoadingState';
import ErrorState from '../../components/common/ErrorState';
import EmptyState from '../../components/common/EmptyState';
import StatusBadge from '../../components/common/StatusBadge';
import { riskColour } from '../../utils/formatters';
import { ShieldAlert } from 'lucide-react';

const DEPARTMENT_ID = 1;

const SkillRisksPage: React.FC = () => {
  const [risks, setRisks] = useState<SkillRisk[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState('All');

  const fetch = async () => {
    setLoading(true); setError(null);
    try { setRisks(await getWorkforceRisks(DEPARTMENT_ID)); }
    catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetch(); }, []);

  if (loading) return <LoadingState message="Identifying skill risks…" />;
  if (error) return <ErrorState message={error} onRetry={fetch} />;

  const levels = ['All', 'Critical', 'High', 'Medium', 'Low'];
  const filtered = filter === 'All' ? risks : risks.filter(r => r.risk_level === filter);

  return (
    <div>
      <PageHeader
        title="Workforce Skill Risks"
        subtitle="Identified skill risks for the Mechanical Engineering department"
      />

      {/* Filter tabs */}
      <div className="flex gap-2 mb-5">
        {levels.map(l => (
          <button
            key={l}
            onClick={() => setFilter(l)}
            className={`px-3 py-1.5 text-xs font-medium rounded-md border transition-colors ${
              filter === l
                ? 'bg-slate-800 text-white border-slate-800'
                : 'bg-white text-slate-600 border-slate-200 hover:border-slate-400'
            }`}
          >
            {l}
            {l !== 'All' && (
              <span className="ml-1 text-xs opacity-70">({risks.filter(r => r.risk_level === l).length})</span>
            )}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <EmptyState message="No risks at this level." icon={<ShieldAlert size={28} className="text-slate-300" />} />
      ) : (
        <div className="space-y-3">
          {filtered.map((r, i) => (
            <div key={i} className="bg-white border border-slate-200 rounded-lg p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <StatusBadge label={r.risk_level} className={riskColour(r.risk_level)} />
                    <span className="text-sm font-medium text-slate-800">{r.risk_type}</span>
                  </div>
                  {r.skill && <p className="text-xs text-slate-500 mb-1">Skill: {r.skill}</p>}
                  {r.explanation && <p className="text-sm text-slate-600">{r.explanation}</p>}
                </div>
                <div className="text-xs text-slate-400 text-right shrink-0">
                  <p>{r.department}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SkillRisksPage;
