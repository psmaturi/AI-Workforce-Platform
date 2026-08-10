import React, { createContext, useContext, useState, useCallback } from 'react';
import type { AuthUser, UserRole } from '../types';

// ─── Mock user presets for development demo ───────────────────────────────────
// Replace with real auth token handling when backend auth is implemented
const MOCK_USERS: Record<string, AuthUser> = {
  employee: {
    id: 1,
    name: 'Gareth Williams',
    email: 'gareth.williams@steelcore.com',
    employeeNumber: 'EMP1000',
    role: 'employee',
    department: 'Mechanical Engineering',
    jobTitle: 'Mechanical Engineer',
    grade: 5,
  },
  manager: {
    id: 2,
    name: 'Priya Sharma',
    email: 'priya.sharma@steelcore.com',
    employeeNumber: 'EMP1001',
    role: 'manager',
    department: 'Mechanical Engineering',
    jobTitle: 'Engineering Manager',
    grade: 8,
  },
  hr: {
    id: 3,
    name: 'James Okonkwo',
    email: 'james.okonkwo@steelcore.com',
    employeeNumber: 'EMP1002',
    role: 'hr',
    department: 'Human Resources',
    jobTitle: 'HR Business Partner',
    grade: 7,
  },
};

// ─── Context shape ────────────────────────────────────────────────────────────
interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  login: (email: string, password: string, role: UserRole) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

// ─── Provider ─────────────────────────────────────────────────────────────────
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(() => {
    // Restore from session storage on reload
    const stored = sessionStorage.getItem('wf_user');
    return stored ? JSON.parse(stored) : null;
  });

  const login = useCallback(async (_email: string, _password: string, role: UserRole) => {
    // [MOCK AUTH] — swaps in demo user based on role selection
    // Replace this block with a real POST /auth/token call when backend auth is ready
    const mockUser = MOCK_USERS[role];
    setUser(mockUser);
    sessionStorage.setItem('wf_user', JSON.stringify(mockUser));
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    sessionStorage.removeItem('wf_user');
  }, []);

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// ─── Hook ─────────────────────────────────────────────────────────────────────
export const useAuth = (): AuthContextValue => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
