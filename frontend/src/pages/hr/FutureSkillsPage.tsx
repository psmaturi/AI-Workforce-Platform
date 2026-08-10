import React, { useState } from 'react';
import { getFutureDemand } from '../../api/mlApi';
import type { FutureDemandResult } from '../../types';
import PageHeader from '../../components/common/PageHeader';
import DemoDataLabel from '../../components/common/DemoDataLabel';
import LoadingState from '../../components/common/LoadingState';
import ErrorState from '../../components/common/ErrorState';
import StatusBadge from '../../components/common/StatusBadge';
import { demandColour } from '../../utils/formatters';

// Pre-defined skills to evaluate — realistic for a steel plant
const SKILL_SCENARIOS = [
  { name: 'Predictive Maintenance', currentDemand: 70, hiringDemand: 80, trend: 0.9 },
  { name: 'EAF Operations', currentDemand: 85, hiringDemand: 90, trend: 0.7 },
  { name: 'Digital Twin Modelling', currentDemand: 40, hiringDemand: 75, trend: 1.2 },
  { name: 'AI/ML for Metallurgy', currentDemand: 30, hiringDemand: 60, trend: 1.5 },
  { name: 'Safety Management', currentDemand: 80, hiringDemand: 85, trend: 0.5 },
  { name: 'Hydraulic Systems', currentDemand: 65, hiringDemand: 65, trend: 0.3 },
];

const DEPARTMENT_ID = 1;

interface SkillDemandRow {
  name: string;
  currentDemand: number;
  hiringDemand: number;
  trend: number;
  prediction: FutureDemandResult | null;
  error: boolean;
}

const FutureSkillsPage: React.FC = () => {
  const [rows, setRows] = useState<SkillDemandRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ran, setRan] = useState(false);

  const runPredictions = async () => {
    setLoading(true); setError(null); setRan(true);
    try {
      const results = await Promise.all(
        SKILL_SCENARIOS.map(async (s) => {
          try {
            const pred = await getFutureDemand({
              department_id: DEPARTMENT_ID,
              current_demand: s.currentDemand,
              hiring_demand: s.hiringDemand,
              industry_trend: s.trend,
            });
            return { ...s, prediction: pred, error: false };
          } catch {
            return { ...s, prediction: null, error: true };
          }
        })
      );
      setRows(results);
    }
    catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  return (
    <div>
      <PageHeader
        title="Future Skills"
        subtitle="Predicted skill demand for strategic workforce planning"
        actions={<DemoDataLabel />}
      />

      <div className="mb-5">
        <button
          onClick={runPredictions}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {loading ? 'Running predictions…' : 'Predict Skill Demand'}
        </button>
        <p className="text-xs text-slate-400 mt-1.5">
          Uses ML classification model trained on industry demand data.
        </p>
      </div>

      {loading && <LoadingState message="Running ML demand model…" />}
      {error && <ErrorState message={error} onRetry={runPredictions} />}

      {rows.length > 0 && !loading && (
        <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50">
                <tr>
                  {['Skill', 'Current Demand', 'Hiring Demand', 'Industry Trend', 'Predicted Category'].map(h => (
                    <th key={h} className="px-5 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {rows.map((r, i) => (
                  <tr key={i} className="hover:bg-slate-50">
                    <td className="px-5 py-3 font-medium text-slate-800">{r.name}</td>
                    <td className="px-5 py-3 text-slate-600">{r.currentDemand}</td>
                    <td className="px-5 py-3 text-slate-600">{r.hiringDemand}</td>
                    <td className="px-5 py-3 text-slate-600">{r.trend}</td>
                    <td className="px-5 py-3">
                      {r.error ? (
                        <span className="text-xs text-red-400">Error</span>
                      ) : r.prediction ? (
                        <StatusBadge
                          label={r.prediction.demand_category}
                          className={demandColour(r.prediction.demand_category)}
                        />
                      ) : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {!ran && !loading && (
        <div className="bg-white border border-slate-200 rounded-lg p-8 text-center">
          <p className="text-sm text-slate-500">Click <strong>Predict Skill Demand</strong> to run the ML model.</p>
          <p className="text-xs text-amber-600 mt-2">Results are ML-generated predictions for strategic planning only.</p>
        </div>
      )}
    </div>
  );
};

export default FutureSkillsPage;
