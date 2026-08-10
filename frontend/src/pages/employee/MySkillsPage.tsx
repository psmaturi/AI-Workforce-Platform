import React from 'react';
import PageHeader from '../../components/common/PageHeader';
import { Zap } from 'lucide-react';

// My Skills page: shows employee's current skills from profile context
// Data comes from AuthContext which contains the authenticated user's profile
const SKILL_LEVELS = ['Beginner', 'Intermediate', 'Advanced', 'Expert'];

// Demo skill data aligned with the EMP1000 / Gareth Williams database entry
const DEMO_SKILLS = [
  { name: 'Electric Arc Furnace Operations', category: 'Technical', level: 'Beginner', years: 1.5, certified: false },
  { name: 'Mechanical Maintenance', category: 'Technical', level: 'Advanced', years: 6.0, certified: true },
  { name: 'Hydraulic Systems', category: 'Technical', level: 'Intermediate', years: 3.0, certified: false },
  { name: 'Predictive Maintenance', category: 'Technical', level: 'Beginner', years: 0.5, certified: false },
  { name: 'Safety Management', category: 'Safety', level: 'Intermediate', years: 4.0, certified: true },
  { name: 'Team Leadership', category: 'Behavioral', level: 'Intermediate', years: 2.0, certified: false },
  { name: 'Root Cause Analysis', category: 'Technical', level: 'Intermediate', years: 2.5, certified: false },
  { name: 'Data Analysis', category: 'Digital', level: 'Beginner', years: 0.5, certified: false },
];

const levelColour = (l: string) => {
  if (l === 'Expert') return 'bg-blue-100 text-blue-800 border-blue-200';
  if (l === 'Advanced') return 'bg-green-100 text-green-800 border-green-200';
  if (l === 'Intermediate') return 'bg-amber-100 text-amber-800 border-amber-200';
  return 'bg-slate-100 text-slate-700 border-slate-200';
};

const MySkillsPage: React.FC = () => {
  const [search, setSearch] = React.useState('');
  const [filterCat, setFilterCat] = React.useState('All');
  const [filterLevel, setFilterLevel] = React.useState('All');

  const categories = ['All', ...Array.from(new Set(DEMO_SKILLS.map(s => s.category)))];

  const filtered = DEMO_SKILLS.filter(s => {
    const matchSearch = s.name.toLowerCase().includes(search.toLowerCase());
    const matchCat = filterCat === 'All' || s.category === filterCat;
    const matchLv = filterLevel === 'All' || s.level === filterLevel;
    return matchSearch && matchCat && matchLv;
  });

  return (
    <div>
      <PageHeader title="My Skills" subtitle="Your current verified skill portfolio" />

      {/* Filters */}
      <div className="flex flex-wrap gap-2 mb-5">
        <input
          type="search"
          placeholder="Search skills…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="px-3 py-1.5 text-sm border border-slate-300 rounded-md outline-none focus-visible:ring-2 focus-visible:ring-blue-500 w-48"
          aria-label="Search skills"
        />
        <select
          value={filterCat}
          onChange={e => setFilterCat(e.target.value)}
          className="px-3 py-1.5 text-sm border border-slate-300 rounded-md outline-none focus-visible:ring-2 focus-visible:ring-blue-500 bg-white"
          aria-label="Filter by category"
        >
          {categories.map(c => <option key={c}>{c}</option>)}
        </select>
        <select
          value={filterLevel}
          onChange={e => setFilterLevel(e.target.value)}
          className="px-3 py-1.5 text-sm border border-slate-300 rounded-md outline-none focus-visible:ring-2 focus-visible:ring-blue-500 bg-white"
          aria-label="Filter by level"
        >
          {['All', ...SKILL_LEVELS].map(l => <option key={l}>{l}</option>)}
        </select>
      </div>

      {/* Skills Table */}
      <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                {['Skill', 'Category', 'Proficiency', 'Experience', 'Certified'].map(h => (
                  <th key={h} className="px-5 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.length === 0 ? (
                <tr><td colSpan={5} className="px-5 py-8 text-center text-sm text-slate-400">No skills match your filters.</td></tr>
              ) : filtered.map((s, i) => (
                <tr key={i} className="hover:bg-slate-50">
                  <td className="px-5 py-3 font-medium text-slate-800 flex items-center gap-2">
                    <Zap size={14} className="text-slate-400 shrink-0" />{s.name}
                  </td>
                  <td className="px-5 py-3 text-slate-600">{s.category}</td>
                  <td className="px-5 py-3">
                    <span className={`inline-flex px-2 py-0.5 rounded text-xs font-medium border ${levelColour(s.level)}`}>
                      {s.level}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-slate-600">{s.years} yrs</td>
                  <td className="px-5 py-3">
                    {s.certified
                      ? <span className="text-xs text-green-700 font-medium">Yes</span>
                      : <span className="text-xs text-slate-400">No</span>}
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

export default MySkillsPage;
