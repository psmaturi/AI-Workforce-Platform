interface MetricCardProps {
  label: string;
  value: string | number;
  sub?: string;
  icon?: React.ReactNode;
  accent?: string; // Tailwind text-colour class for value
}

const MetricCard: React.FC<MetricCardProps> = ({ label, value, sub, icon, accent = 'text-slate-900' }) => (
  <div className="bg-white border border-slate-200 rounded-lg p-5 flex flex-col gap-1">
    {icon && <div className="text-slate-400 mb-1">{icon}</div>}
    <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">{label}</span>
    <span className={`text-2xl font-semibold ${accent}`}>{value}</span>
    {sub && <span className="text-sm text-slate-500">{sub}</span>}
  </div>
);

export default MetricCard;
