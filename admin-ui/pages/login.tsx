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
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      {/* Background Animation Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full mix-blend-screen filter blur-3xl opacity-20 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-purple-500 to-purple-600 rounded-full mix-blend-screen filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute top-1/2 left-1/2 w-80 h-80 bg-gradient-to-br from-pink-500 to-pink-600 rounded-full mix-blend-screen filter blur-3xl opacity-10 animate-blob animation-delay-4000"></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 w-full max-w-md">
        {/* Card Container */}
        <div className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl shadow-2xl overflow-hidden">
          {/* Card Content */}
          <div className="p-8 sm:p-10">
            {/* Header Section */}
            <div className="text-center mb-8">
              {/* Icon */}
              <div className="w-16 h-16 mx-auto mb-6 rounded-xl bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center shadow-lg">
                <i className="fas fa-shield-alt text-white text-3xl"></i>
              </div>

              {/* Title */}
              <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">
                {botName}
              </h1>
              <p className="text-sm text-gray-300">Admin Dashboard Login</p>
            </div>

            {/* Error Alert */}
            {error && (
              <div className="mb-6 p-4 bg-red-500/20 border border-red-500/50 rounded-lg backdrop-blur-sm">
                <div className="flex items-start gap-3">
                  <i className="fas fa-exclamation-circle text-red-400 text-lg mt-0.5 flex-shrink-0"></i>
                  <div>
                    <p className="text-red-200 text-sm font-semibold">Login Failed</p>
                    <p className="text-red-100/80 text-xs mt-1">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Username Field */}
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-200 mb-2">
                  Username
                </label>
                <input
                  type="text"
                  id="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter your username"
                  className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500/50 focus:bg-white/10 transition-all duration-200 backdrop-blur-sm"
                  required
                />
              </div>

              {/* Password Field */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-200 mb-2">
                  Password
                </label>
                <input
                  type="password"
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500/50 focus:bg-white/10 transition-all duration-200 backdrop-blur-sm"
                  required
                />
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full mt-6 px-4 py-2.5 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-blue-500/50 relative group overflow-hidden"
              >
                <div className="absolute inset-0 bg-white/20 transform -translate-x-full group-hover:translate-x-full transition-transform duration-500"></div>
                <div className="relative flex items-center justify-center gap-2">
                  {isLoading ? (
                    <>
                      <i className="fas fa-spinner fa-spin"></i>
                      <span>Signing in...</span>
                    </>
                  ) : (
                    <>
                      <span>Sign In</span>
                      <i className="fas fa-arrow-right"></i>
                    </>
                  )}
                </div>
              </button>
            </form>

            {/* Info Section */}
            <div className="mt-8 pt-6 border-t border-white/10 space-y-3">
              {/* Security Info */}
              <div className="flex items-center gap-3 text-xs text-gray-300">
                <i className="fas fa-lock text-green-400"></i>
                <span>Secure authentication • 60-minute session</span>
              </div>

              {/* Support Info */}
              <div className="flex items-center gap-3 text-xs text-gray-300">
                <i className="fas fa-headset text-blue-400"></i>
                <span>Need help? Contact support</span>
              </div>
            </div>
          </div>

          {/* Footer Bar */}
          <div className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border-t border-white/10 px-8 py-4 text-center text-xs text-gray-400">
            Protected Admin Portal
          </div>
        </div>

        {/* Demo Info Card */}
        <div className="mt-6 p-4 bg-amber-500/10 border border-amber-500/30 rounded-lg backdrop-blur-sm">
          <p className="text-xs font-semibold text-amber-200 mb-2 flex items-center gap-2">
            <i className="fas fa-info-circle"></i>
            Demo Credentials
          </p>
          <div className="space-y-1.5 text-xs text-amber-100/80">
            <p><span className="font-medium">Username:</span> <code className="bg-black/30 px-2 py-1 rounded text-amber-300 font-mono">admin</code></p>
            <p><span className="font-medium">Password:</span> <code className="bg-black/30 px-2 py-1 rounded text-amber-300 font-mono">marriage2020!</code></p>
          </div>
        </div>
      </div>

      {/* Animations */}
      <style jsx>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          25% { transform: translate(20px, -30px) scale(1.1); }
          50% { transform: translate(-20px, 20px) scale(0.9); }
          75% { transform: translate(30px, 10px) scale(1.05); }
        }

        .animate-blob {
          animation: blob 8s infinite;
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
