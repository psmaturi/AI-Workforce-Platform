import React from 'react';
import { Inbox } from 'lucide-react';

interface EmptyStateProps {
  message?: string;
  icon?: React.ReactNode;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  message = 'No data available.',
  icon = <Inbox size={28} className="text-slate-300" />,
}) => (
  <div className="flex flex-col items-center justify-center py-14 gap-3">
    {icon}
    <p className="text-sm text-slate-500">{message}</p>
  </div>
);

export default EmptyState;
