import React from 'react';
import { FlaskConical } from 'lucide-react';

/** Shown on pages that display ML-generated synthetic/demo data */
const DemoDataLabel: React.FC = () => (
  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
    <FlaskConical size={11} />
    Synthetic Demo Data
  </span>
);

export default DemoDataLabel;
