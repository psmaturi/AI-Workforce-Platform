import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, MessageSquare, Zap, BookOpen, TrendingUp,
  Users, BarChart2, AlertTriangle, LineChart, Building2, Brain,
  Settings, X,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import type { UserRole } from '../../types';

interface NavItem {
  label: string;
  path: string;
  icon: React.ReactNode;
  roles?: UserRole[];
}

interface NavSection {
  heading?: string;
  items: NavItem[];
}

const NAV: NavSection[] = [
  {
    items: [
      { label: 'Dashboard', path: '/employee', icon: <LayoutDashboard size={16} />, roles: ['employee', 'manager', 'hr'] },
      { label: 'AI Assistant', path: '/assistant', icon: <MessageSquare size={16} />, roles: ['employee', 'manager', 'hr'] },
    ],
  },
  {
    heading: 'My Development',
    items: [
      { label: 'My Skills', path: '/employee/skills', icon: <Zap size={16} />, roles: ['employee'] },
      { label: 'Skill Gaps', path: '/employee/skill-gaps', icon: <AlertTriangle size={16} />, roles: ['employee'] },
      { label: 'Learning', path: '/employee/learning', icon: <BookOpen size={16} />, roles: ['employee'] },
      { label: 'Career Path', path: '/employee/career', icon: <TrendingUp size={16} />, roles: ['employee'] },
    ],
  },
  {
    heading: 'Management',
    items: [
      { label: 'Manager Dashboard', path: '/manager', icon: <LayoutDashboard size={16} />, roles: ['manager', 'hr'] },
      { label: 'Team Analytics', path: '/manager/team', icon: <Users size={16} />, roles: ['manager', 'hr'] },
      { label: 'Skill Risks', path: '/manager/risks', icon: <AlertTriangle size={16} />, roles: ['manager', 'hr'] },
      { label: 'Workforce Forecast', path: '/manager/forecast', icon: <LineChart size={16} />, roles: ['manager', 'hr'] },
    ],
  },
  {
    heading: 'HR & Organisation',
    items: [
      { label: 'Organisation', path: '/hr', icon: <Building2 size={16} />, roles: ['hr'] },
      { label: 'Future Skills', path: '/hr/future-skills', icon: <Brain size={16} />, roles: ['hr'] },
    ],
  },
  {
    items: [
      { label: 'Settings', path: '/settings', icon: <Settings size={16} />, roles: ['employee', 'manager', 'hr'] },
    ],
  },
];

interface SidebarProps {
  mobileOpen: boolean;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ mobileOpen, onClose }) => {
  const { user, logout } = useAuth();
  const { pathname } = useLocation();

  const isVisible = (roles?: UserRole[]) => {
    if (!roles || !user) return true;
    return roles.includes(user.role);
  };

  const isActive = (path: string) => pathname === path || (path !== '/employee' && pathname.startsWith(path));

  const sidebarContent = (
    <div className="flex flex-col h-full bg-slate-900 text-slate-100 w-60">
      {/* Logo */}
      <div className="flex items-center justify-between px-4 h-14 border-b border-slate-700 shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded bg-blue-600 flex items-center justify-center">
            <BarChart2 size={14} className="text-white" />
          </div>
          <span className="text-sm font-semibold tracking-tight">AI Workforce</span>
        </div>
        <button onClick={onClose} className="lg:hidden text-slate-400 hover:text-white" aria-label="Close menu">
          <X size={18} />
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-5" aria-label="Main navigation">
        {NAV.map((section, si) => (
          <div key={si}>
            {section.heading && (
              <p className="px-2 mb-1 text-xs font-medium text-slate-500 uppercase tracking-wider">
                {section.heading}
              </p>
            )}
            {section.items.filter(i => isVisible(i.roles)).map((item) => (
              <Link
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={`flex items-center gap-2.5 px-2 py-1.5 rounded-md text-sm mb-0.5 transition-colors ${
                  isActive(item.path)
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`}
              >
                {item.icon}
                {item.label}
              </Link>
            ))}
          </div>
        ))}
      </nav>

      {/* User */}
      {user && (
        <div className="px-3 py-3 border-t border-slate-700 shrink-0">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-xs font-bold text-white shrink-0">
              {user.name.charAt(0)}
            </div>
            <div className="min-w-0">
              <p className="text-xs font-medium text-slate-100 truncate">{user.name}</p>
              <p className="text-xs text-slate-400 truncate capitalize">{user.role}</p>
            </div>
          </div>
          <button
            onClick={logout}
            className="text-xs text-slate-400 hover:text-white transition-colors"
          >
            Sign out
          </button>
        </div>
      )}
    </div>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex shrink-0">{sidebarContent}</aside>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 flex lg:hidden">
          <div className="fixed inset-0 bg-black/50" onClick={onClose} aria-hidden="true" />
          <div className="relative flex">{sidebarContent}</div>
        </div>
      )}
    </>
  );
};

export default Sidebar;
