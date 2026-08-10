import React from 'react';
import { AlertCircle } from 'lucide-react';

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

const ErrorState: React.FC<ErrorStateProps> = ({
  message = 'Unable to connect to the workforce service. Please try again.',
  onRetry,
}) => (
  <div className="flex flex-col items-center justify-center py-16 gap-4">
    <div className="flex items-center gap-2 text-red-600">
      <AlertCircle size={20} />
      <span className="text-sm font-medium">Something went wrong</span>
    </div>
    <p className="text-sm text-slate-500 max-w-sm text-center">{message}</p>
    {onRetry && (
      <button
        onClick={onRetry}
        className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus-visible:ring-2"
      >
        Try again
      </button>
    )}
  </div>
);

export default ErrorState;
