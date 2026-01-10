'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { apiClient } from '../lib/api-client';
import { useAuthStore } from '../store/auth';

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [botName, setBotName] = useState('EduBot');
  const { setAuthenticated, setError: setAuthError } = useAuthStore();

  // Fetch bot name from settings on component mount
  useEffect(() => {
    const fetchBotName = async () => {
      try {
        const response = await fetch('/api/admin/settings');
        if (response.ok) {
          const data = await response.json();
          if (data.data?.bot_name) {
            setBotName(data.data.bot_name);
          }
        }
      } catch (err) {
        // Silently fail - use default bot name
        console.warn('Could not fetch bot name:', err);
      }
    };
    fetchBotName();
  }, []);

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
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-900 to-slate-900 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
      <div className="absolute top-0 right-0 w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
      <div className="absolute -bottom-8 left-1/2 w-96 h-96 bg-pink-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>

      {/* Centered container */}
      <div className="w-full max-w-md mx-auto flex flex-col items-center justify-center relative z-10">
        {/* Main card */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl shadow-2xl p-8 border border-white/20 relative w-full">
          {/* Gradient border effect */}
          <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent rounded-2xl opacity-0 hover:opacity-100 transition-opacity duration-500"></div>

          <div className="relative z-10">
            {/* Header */}
            <div className="text-center mb-10">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-400 to-purple-500 rounded-2xl mb-4 shadow-lg">
                <i className="fas fa-robot text-3xl text-white"></i>
              </div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-200 via-purple-200 to-pink-200 bg-clip-text text-transparent mb-2">
                {botName} Admin
              </h1>
              <p className="text-blue-100/70 text-sm font-medium tracking-wide">
                Dashboard Login
              </p>
            </div>

            {/* Error message */}
            {error && (
              <div className="bg-red-500/20 border border-red-400/50 rounded-xl p-4 mb-6 flex items-start gap-3 backdrop-blur-sm">
                <i className="fas fa-circle-exclamation text-red-300 text-lg mt-1 flex-shrink-0"></i>
                <div>
                  <h3 className="font-semibold text-red-200 text-sm">Authentication Failed</h3>
                  <p className="text-red-100/80 text-xs mt-1">{error}</p>
                </div>
              </div>
            )}

            {/* Security info */}
            <div className="bg-blue-500/10 border border-blue-400/30 rounded-xl p-3 mb-6 backdrop-blur-sm">
              <p className="text-blue-100 text-xs font-medium flex items-center gap-2">
                <i className="fas fa-shield-halved"></i>
                Secure Session • Expires after 60 minutes
              </p>
            </div>

            {/* Demo credentials */}
            <div className="bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-400/30 rounded-xl p-4 mb-8 backdrop-blur-sm">
              <p className="text-amber-200 text-xs font-bold mb-3 flex items-center gap-2">
                <i className="fas fa-key"></i>
                Demo Credentials
              </p>
              <div className="space-y-2">
                <p className="text-amber-100/80 text-xs">
                  <span className="font-semibold">Username:</span> <code className="bg-black/20 px-2 py-1 rounded text-amber-300">admin</code>
                </p>
                <p className="text-amber-100/80 text-xs">
                  <span className="font-semibold">Password:</span> <code className="bg-black/20 px-2 py-1 rounded text-amber-300">marriage2020!</code>
                </p>
              </div>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Username field */}
              <div className="group">
                <label htmlFor="username" className="block text-sm font-semibold text-blue-100 mb-3 flex items-center gap-2">
                  <i className="fas fa-user text-blue-300"></i>
                  Username
                </label>
                <input
                  type="text"
                  id="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:outline-none focus:border-blue-400 focus:bg-white/15 transition-all duration-200 backdrop-blur-sm"
                  placeholder="Enter your username"
                  required
                />
              </div>

              {/* Password field */}
              <div className="group">
                <label htmlFor="password" className="block text-sm font-semibold text-blue-100 mb-3 flex items-center gap-2">
                  <i className="fas fa-lock text-blue-300"></i>
                  Password
                </label>
                <input
                  type="password"
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:outline-none focus:border-blue-400 focus:bg-white/15 transition-all duration-200 backdrop-blur-sm"
                  placeholder="Enter your password"
                  required
                />
              </div>

              {/* Submit button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full px-4 py-3 mt-8 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-bold rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-blue-500/50 hover:shadow-2xl relative group overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 group-hover:opacity-20 group-hover:translate-x-96 transition-all duration-500 -translate-x-96"></div>
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2 relative z-10">
                    <i className="fas fa-spinner fa-spin"></i>
                    Authenticating...
                  </span>
                ) : (
                  <span className="flex items-center justify-center gap-2 relative z-10">
                    <i className="fas fa-arrow-right"></i>
                    Sign In
                  </span>
                )}
              </button>
            </form>

            {/* Footer */}
            <p className="text-center text-white/40 text-xs mt-8 pt-6 border-t border-white/10">
              Protected Admin Portal • All access logged and monitored
            </p>
          </div>
        </div>

        {/* Decorative elements */}
        <div className="absolute -bottom-24 left-1/2 -translate-x-1/2 w-full h-32 bg-gradient-to-t from-blue-500/20 to-transparent rounded-full blur-3xl opacity-50"></div>
      </div>

      <style jsx>{`
        @keyframes blob {
          0%, 100% {
            transform: translate(0, 0) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
        }

        .animate-blob {
          animation: blob 7s infinite;
        }

        .animation-delay-2000 {
          animation-delay: 2s;
        }

        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  );
}
