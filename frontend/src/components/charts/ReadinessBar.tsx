import React from 'react';
import { readinessBarColour } from '../../utils/formatters';

interface ReadinessBarProps {
  score: number;
  classification: string;
  showLabel?: boolean;
}

const ReadinessBar: React.FC<ReadinessBarProps> = ({ score, classification, showLabel = true }) => {
  const barColour = readinessBarColour(classification);
  const clampedScore = Math.min(Math.max(score, 0), 100);

  return (
    <div className="w-full">
      {showLabel && (
        <div className="flex justify-between items-baseline mb-1">
          <span className="text-xs text-slate-500">Readiness</span>
          <span className="text-sm font-semibold text-slate-800">{Math.round(clampedScore)}%</span>
        </div>
      )}
      <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${barColour}`}
          style={{ width: `${clampedScore}%` }}
          role="progressbar"
          aria-valuenow={clampedScore}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`Readiness: ${Math.round(clampedScore)}%`}
        />
      </div>
    </div>
  );
};

export default ReadinessBar;
