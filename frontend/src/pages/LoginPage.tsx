import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import type { UserRole } from '../types';
import { BarChart2, AlertCircle } from 'lucide-react';

const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('gareth.williams@steelcore.com');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<UserRole>('employee');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please enter your email and password.');
      return;
    }
    setIsLoading(true);
    setError('');
    try {
      await login(email, password, role);
      navigate(role === 'employee' ? '/employee' : role === 'manager' ? '/manager' : '/hr');
    } catch {
      setError('Sign in failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center mb-3">
            <BarChart2 size={22} className="text-white" />
          </div>
          <h1 className="text-xl font-semibold text-slate-900">AI Workforce Intelligence</h1>
          <p className="text-sm text-slate-500 mt-1">SteelCore Industries Ltd</p>
        </div>

        {/* Card */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
          <h2 className="text-base font-medium text-slate-800 mb-5">Sign in to your account</h2>

          {/* DEV notice */}
          <div className="mb-4 px-3 py-2 bg-amber-50 border border-amber-200 rounded text-xs text-amber-700">
            <strong>Development Mode:</strong> Select a role below — authentication is mocked.
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-xs font-medium text-slate-700 mb-1">
                Email address
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-md focus-visible:ring-2 focus-visible:ring-blue-500 outline-none"
                placeholder="you@steelcore.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-xs font-medium text-slate-700 mb-1">
                Password
              </label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-md focus-visible:ring-2 focus-visible:ring-blue-500 outline-none"
                placeholder="••••••••"
              />
            </div>

            <div>
              <label htmlFor="role" className="block text-xs font-medium text-slate-700 mb-1">
                Demo Role
              </label>
              <select
                id="role"
                value={role}
                onChange={(e) => setRole(e.target.value as UserRole)}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-md focus-visible:ring-2 focus-visible:ring-blue-500 outline-none bg-white"
              >
                <option value="employee">Employee — Gareth Williams</option>
                <option value="manager">Manager — Priya Sharma</option>
                <option value="hr">HR — James Okonkwo</option>
              </select>
            </div>

            {error && (
              <div className="flex items-center gap-1.5 text-sm text-red-600">
                <AlertCircle size={14} />
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>
        </div>

        <p className="text-center text-xs text-slate-400 mt-6">
          AI Workforce Intelligence Platform v1.0 · SteelCore Industries
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
