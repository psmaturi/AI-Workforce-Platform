import React from 'react';
import { Menu, Bell } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface TopbarProps {
  onMenuClick: () => void;
}

const Topbar: React.FC<TopbarProps> = ({ onMenuClick }) => {
  const { user } = useAuth();

  return (
    <header className="h-14 bg-white border-b border-slate-200 flex items-center justify-between px-4 shrink-0">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-1.5 rounded text-slate-500 hover:bg-slate-100"
          aria-label="Open navigation menu"
        >
          <Menu size={20} />
        </button>
        <span className="text-sm text-slate-500 hidden sm:block">
          AI Workforce Intelligence Platform
        </span>
      </div>
      <div className="flex items-center gap-2">
        <button className="p-1.5 rounded text-slate-400 hover:bg-slate-100" aria-label="Notifications">
          <Bell size={18} />
        </button>
        {user && (
          <div className="flex items-center gap-2 ml-1">
            <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-xs font-bold text-white">
              {user.name.charAt(0)}
            </div>
            <span className="text-sm text-slate-700 hidden sm:block">{user.name}</span>
          </div>
        )}
      </div>
    </header>
  );
};

export default Topbar;
