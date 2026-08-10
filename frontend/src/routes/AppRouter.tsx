import React, { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import type { UserRole } from '../types';
import AppShell from '../components/layout/AppShell';
import LoadingState from '../components/common/LoadingState';

// Lazy-load pages
const LoginPage = lazy(() => import('../pages/LoginPage'));
const DashboardPage = lazy(() => import('../pages/employee/DashboardPage'));
const MySkillsPage = lazy(() => import('../pages/employee/MySkillsPage'));
const SkillGapPage = lazy(() => import('../pages/employee/SkillGapPage'));
const LearningPage = lazy(() => import('../pages/employee/LearningPage'));
const CareerPage = lazy(() => import('../pages/employee/CareerPage'));
const AssistantPage = lazy(() => import('../pages/assistant/AssistantPage'));
const ManagerDashboard = lazy(() => import('../pages/manager/ManagerDashboard'));
const TeamAnalyticsPage = lazy(() => import('../pages/manager/TeamAnalyticsPage'));
const SkillRisksPage = lazy(() => import('../pages/manager/SkillRisksPage'));
const WorkforceForecastPage = lazy(() => import('../pages/manager/WorkforceForecastPage'));
const HRDashboardPage = lazy(() => import('../pages/hr/HRDashboardPage'));
const FutureSkillsPage = lazy(() => import('../pages/hr/FutureSkillsPage'));
const SettingsPage = lazy(() => import('../pages/SettingsPage'));

// ─── Route guard ─────────────────────────────────────────────────────────────
interface ProtectedProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

const Protected: React.FC<ProtectedProps> = ({ children, allowedRoles }) => {
  const { isAuthenticated, user } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return <Navigate to="/employee" replace />;
  }
  return <>{children}</>;
};

// ─── Shell-wrapped route ──────────────────────────────────────────────────────
const Shell: React.FC<{ children: React.ReactNode; roles?: UserRole[] }> = ({ children, roles }) => (
  <Protected allowedRoles={roles}>
    <AppShell>
      <Suspense fallback={<LoadingState />}>{children}</Suspense>
    </AppShell>
  </Protected>
);

// ─── Router ───────────────────────────────────────────────────────────────────
const AppRouter: React.FC = () => {
  const { isAuthenticated, user } = useAuth();

  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route
          path="/login"
          element={
            isAuthenticated
              ? <Navigate to={user?.role === 'hr' ? '/hr' : user?.role === 'manager' ? '/manager' : '/employee'} replace />
              : <Suspense fallback={<LoadingState />}><LoginPage /></Suspense>
          }
        />

        {/* Employee routes */}
        <Route path="/employee" element={<Shell roles={['employee', 'manager', 'hr']}><DashboardPage /></Shell>} />
        <Route path="/employee/skills" element={<Shell roles={['employee']}><MySkillsPage /></Shell>} />
        <Route path="/employee/skill-gaps" element={<Shell roles={['employee', 'manager', 'hr']}><SkillGapPage /></Shell>} />
        <Route path="/employee/learning" element={<Shell roles={['employee', 'manager', 'hr']}><LearningPage /></Shell>} />
        <Route path="/employee/career" element={<Shell roles={['employee', 'manager', 'hr']}><CareerPage /></Shell>} />

        {/* Assistant */}
        <Route path="/assistant" element={<Shell><AssistantPage /></Shell>} />

        {/* Manager routes */}
        <Route path="/manager" element={<Shell roles={['manager', 'hr']}><ManagerDashboard /></Shell>} />
        <Route path="/manager/team" element={<Shell roles={['manager', 'hr']}><TeamAnalyticsPage /></Shell>} />
        <Route path="/manager/risks" element={<Shell roles={['manager', 'hr']}><SkillRisksPage /></Shell>} />
        <Route path="/manager/forecast" element={<Shell roles={['manager', 'hr']}><WorkforceForecastPage /></Shell>} />

        {/* HR routes */}
        <Route path="/hr" element={<Shell roles={['hr']}><HRDashboardPage /></Shell>} />
        <Route path="/hr/future-skills" element={<Shell roles={['hr']}><FutureSkillsPage /></Shell>} />

        {/* Settings */}
        <Route path="/settings" element={<Shell><SettingsPage /></Shell>} />

        {/* Default redirect */}
        <Route
          path="*"
          element={
            isAuthenticated
              ? <Navigate to={user?.role === 'hr' ? '/hr' : user?.role === 'manager' ? '/manager' : '/employee'} replace />
              : <Navigate to="/login" replace />
          }
        />
      </Routes>
    </BrowserRouter>
  );
};

export default AppRouter;
