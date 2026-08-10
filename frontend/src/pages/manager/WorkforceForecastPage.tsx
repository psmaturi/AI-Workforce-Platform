import React, { useState } from 'react';
import { getWorkforceForecast } from '../../api/mlApi';
import PageHeader from '../../components/common/PageHeader';
import DemoDataLabel from '../../components/common/DemoDataLabel';
import LoadingState from '../../components/common/LoadingState';
import ErrorState from '../../components/common/ErrorState';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const WorkforceForecastPage: React.FC = () => {
  const [results, setResults] = useState<Array<{ year: number; required: number; current: number }>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ran, setRan] = useState(false);

  // Form state
  const [departmentId, setDepartmentId] = useState(1);
  const [roleId, setRoleId] = useState(5);
  const [currentHeadcount, setCurrentHeadcount] = useState(120);
  const [attritionRate, setAttritionRate] = useState(0.08);

  const runForecast = async () => {
    setLoading(true); setError(null); setRan(true);
    try {
      const years = [2025, 2026, 2027, 2028, 2029];
      const forecasts = await Promise.all(
        years.map(year => getWorkforceForecast({
          year,
          department_id: departmentId,
          role_id: roleId,
          current_headcount: currentHeadcount,
          attrition_rate: attritionRate,
        }))
      );
      setResults(years.map((y, i) => ({
        year: y,
        current: currentHeadcount,
        required: forecasts[i].required_headcount,
      })));
    }
    catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  return (
    <div>
      <PageHeader
        title="Workforce Forecast"
        subtitle="ML-based headcount projection"
        actions={<DemoDataLabel />}
      />

      {/* Parameters */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 mb-5">
        <h2 className="text-sm font-semibold text-slate-800 mb-4">Forecast Parameters</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Department ID</label>
            <input type="number" value={departmentId} onChange={e => setDepartmentId(+e.target.value)}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-md outline-none focus-visible:ring-2 focus-visible:ring-blue-500" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Role ID</label>
            <input type="number" value={roleId} onChange={e => setRoleId(+e.target.value)}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-md outline-none focus-visible:ring-2 focus-visible:ring-blue-500" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Current Headcount</label>
            <input type="number" value={currentHeadcount} onChange={e => setCurrentHeadcount(+e.target.value)}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-md outline-none focus-visible:ring-2 focus-visible:ring-blue-500" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Attrition Rate (0-1)</label>
            <input type="number" step="0.01" value={attritionRate} onChange={e => setAttritionRate(+e.target.value)}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-md outline-none focus-visible:ring-2 focus-visible:ring-blue-500" />
          </div>
        </div>
        <button
          onClick={runForecast}
          disabled={loading}
          className="mt-4 px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {loading ? 'Calculating…' : 'Run Forecast'}
        </button>
      </div>

      {loading && <LoadingState message="Running ML forecast model…" />}
      {error && <ErrorState message={error} onRetry={runForecast} />}

      {results.length > 0 && !loading && (
        <div className="space-y-4">
          {/* Chart */}
          <div className="bg-white border border-slate-200 rounded-lg p-5">
            <h2 className="text-sm font-semibold text-slate-800 mb-4">Headcount Forecast 2025–2029</h2>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={results}>
                <XAxis dataKey="year" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ fontSize: 12 }} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="current" name="Current" fill="#94a3b8" radius={[3, 3, 0, 0]} />
                <Bar dataKey="required" name="Required (Predicted)" fill="#3b82f6" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Table */}
          <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    {['Year', 'Current Headcount', 'Required (Predicted)', 'Gap'].map(h => (
                      <th key={h} className="px-5 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {results.map(r => (
                    <tr key={r.year} className="hover:bg-slate-50">
                      <td className="px-5 py-3 font-medium text-slate-800">{r.year}</td>
                      <td className="px-5 py-3 text-slate-600">{r.current}</td>
                      <td className="px-5 py-3 text-blue-700 font-medium">{r.required}</td>
                      <td className={`px-5 py-3 font-medium ${r.required - r.current > 0 ? 'text-amber-700' : 'text-green-700'}`}>
                        {r.required - r.current > 0 ? `+${r.required - r.current}` : r.required - r.current}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {!ran && !loading && (
        <div className="bg-white border border-slate-200 rounded-lg p-8 text-center">
          <p className="text-sm text-slate-500">Set your parameters and click <strong>Run Forecast</strong> to generate a prediction.</p>
          <p className="text-xs text-amber-600 mt-2">Results are ML-generated synthetic predictions for planning purposes only.</p>
        </div>
      )}
    </div>
  );
};

export default WorkforceForecastPage;
