'use client';

import { useRouter } from 'next/router';
import { useEffect } from 'react';
import { apiClient } from '../lib/api-client';

export default function LogoutPage() {
  const router = useRouter();

  useEffect(() => {
    const logout = async () => {
      try {
        await apiClient.logout();
      } catch (err) {
        console.error('Logout error:', err);
      } finally {
        localStorage.removeItem('admin_token');
        router.push('/login');
      }
    };

    logout();
  }, [router]);

  return (
    <div className="flex items-center justify-center h-screen bg-gray-100">
      <div className="text-center">
        <i className="fas fa-spinner fa-spin text-4xl text-blue-600 mb-4"></i>
        <p className="text-gray-600">Logging out...</p>
      </div>
    </div>
  );
}
