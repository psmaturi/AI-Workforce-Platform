import React from 'react';

interface StatusBadgeProps {
  label: string;
  className?: string;
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ label, className = '' }) => (
  <span className={`inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium ${className}`}>
    {label}
  </span>
);

export default StatusBadge;
