// Utility formatters for display consistency across the app

/** Round to 1 decimal and append % */
export const pct = (value: number): string => `${Math.round(value)}%`;

/** Map readiness score to label */
export const readinessLabel = (score: number): string => {
  if (score >= 80) return 'Ready';
  if (score >= 60) return 'Nearly Ready';
  if (score >= 40) return 'Developing';
  return 'Not Ready';
};

/** Map proficiency integer (1-5) to label */
export const proficiencyLabel = (level: number): string => {
  const map: Record<number, string> = { 1: 'Beginner', 2: 'Intermediate', 3: 'Advanced', 4: 'Expert', 5: 'Master' };
  return map[level] ?? `Level ${level}`;
};

/** Map gap size to severity label */
export const gapSeverity = (gap: number): 'None' | 'Low' | 'Medium' | 'High' => {
  if (gap === 0) return 'None';
  if (gap === 1) return 'Low';
  if (gap === 2) return 'Medium';
  return 'High';
};

/** Map risk level to Tailwind colour classes */
export const riskColour = (level: string): string => {
  const map: Record<string, string> = {
    Critical: 'bg-red-100 text-red-800 border border-red-200',
    High: 'bg-orange-100 text-orange-800 border border-orange-200',
    Medium: 'bg-amber-100 text-amber-800 border border-amber-200',
    Low: 'bg-green-100 text-green-800 border border-green-200',
  };
  return map[level] ?? 'bg-slate-100 text-slate-700 border border-slate-200';
};

/** Map demand category to Tailwind colour classes */
export const demandColour = (cat: string): string => {
  const map: Record<string, string> = {
    Critical: 'bg-red-100 text-red-800 border border-red-200',
    High: 'bg-orange-100 text-orange-800 border border-orange-200',
    Medium: 'bg-amber-100 text-amber-800 border border-amber-200',
    Low: 'bg-slate-100 text-slate-600 border border-slate-200',
  };
  return map[cat] ?? 'bg-slate-100 text-slate-700 border border-slate-200';
};

/** Map readiness classification to colour */
export const readinessColour = (cls: string): string => {
  const map: Record<string, string> = {
    Ready: 'text-green-700',
    'Nearly Ready': 'text-amber-700',
    Developing: 'text-orange-700',
    'Not Ready': 'text-red-700',
  };
  return map[cls] ?? 'text-slate-700';
};

/** Map readiness classification to progress bar colour */
export const readinessBarColour = (cls: string): string => {
  const map: Record<string, string> = {
    Ready: 'bg-green-500',
    'Nearly Ready': 'bg-amber-500',
    Developing: 'bg-orange-500',
    'Not Ready': 'bg-red-500',
  };
  return map[cls] ?? 'bg-slate-400';
};
