'use client';

import { useState } from 'react';
import { useRouter } from 'next/router';
import { apiClient } from '../lib/api-client';
import { useAuthStore } from '../store/auth';

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { setAuthenticated, setError: setAuthError } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const response = await apiClient.login(username, password);
      if (response.status === 'success') {
        localStorage.setItem('admin_token', response.token || 'authenticated');
        setAuthenticated(true);
        // Small delay to ensure state is updated before navigation
        setTimeout(() => {
          router.push('/dashboard');
        }, 100);
      } else {
        setError(response.message || 'Login failed');
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || err.message || 'Login failed. Please try again.';
      setError(errorMsg);
      setAuthError(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gradient-to-br from-blue-900 to-blue-700 min-h-screen flex items-center justify-center">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-lg shadow-xl p-8">
          <div className="text-center mb-8">
            <i className="fas fa-robot text-4xl text-blue-600 mb-4"></i>
            <h1 className="text-3xl font-bold text-gray-800">WhatsApp Bot</h1>
            <p className="text-gray-600 mt-2">Admin Dashboard</p>
          </div>

          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-4 mb-6 flex items-start">
              <i className="fas fa-exclamation-circle text-red-600 text-lg mr-3 mt-0.5"></i>
              <div>
                <h3 className="font-semibold text-red-900">Login Failed</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          )}

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-6 text-center">
            <p className="text-xs text-blue-800">
              <i className="fas fa-lock mr-1"></i>
              Secure login required - Session expires after 1 hour
            </p>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <p className="text-xs text-yellow-800 font-semibold mb-2"><i className="fas fa-info-circle mr-1"></i>Demo Credentials:</p>
            <p className="text-xs text-yellow-700"><strong>Username:</strong> admin</p>
            <p className="text-xs text-yellow-700"><strong>Password:</strong> marriage2020!</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                <i className="fas fa-user mr-2"></i>Username
              </label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                placeholder="admin"
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                <i className="fas fa-lock mr-2"></i>Password
              </label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                placeholder="••••••••"
                required
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {isLoading ? (
                <span className="flex items-center justify-center">
                  <i className="fas fa-spinner fa-spin mr-2"></i>
                  Logging in...
                </span>
              ) : (
                'Login'
              )}
            </button>
          </form>

          <p className="text-center text-sm text-gray-600 mt-6">
            Default credentials are in .env file
          </p>
        </div>
      </div>
    </div>
  );
}
