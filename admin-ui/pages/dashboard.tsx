'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '../components/Layout';
import { apiClient } from '../lib/api-client';
import { useDashboardStore } from '../store/dashboard';

interface DashboardStats {
  total_students: number;
  active_subscribers: number;
  total_revenue: number;
  system_status: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { setStats: setDashboardStats } = useDashboardStore();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('admin_token');
        if (!token) {
          router.push('/login');
          return;
        }

        const response = await apiClient.getDashboardStats();
        if (response.status === 'success') {
          setStats(response.data);
          setDashboardStats({
            totalStudents: response.data.total_students,
            activeSubscribers: response.data.active_subscribers,
            totalRevenue: response.data.total_revenue,
          });
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [router]);

  if (loading && !stats) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <i className="fas fa-spinner fa-spin text-4xl text-blue-600 mb-4"></i>
            <p className="text-gray-600">Loading dashboard...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Students Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Total Students</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{stats?.total_students || 0}</p>
            </div>
            <div className="text-4xl text-blue-600 opacity-20">
              <i className="fas fa-users"></i>
            </div>
          </div>
          <p className="text-green-600 text-sm mt-4">
            <i className="fas fa-arrow-up mr-1"></i>Up from last month
          </p>
        </div>

        {/* Active Subscribers Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Active Subscribers</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{stats?.active_subscribers || 0}</p>
            </div>
            <div className="text-4xl text-green-600 opacity-20">
              <i className="fas fa-check-circle"></i>
            </div>
          </div>
          <p className="text-sm text-gray-600 mt-4">
            {stats?.total_students ? ((stats.active_subscribers / stats.total_students) * 100).toFixed(0) : 0}% of total
          </p>
        </div>

        {/* Payments Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Total Payments</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">₦{stats?.total_revenue || 0}</p>
            </div>
            <div className="text-4xl text-yellow-600 opacity-20">
              <i className="fas fa-credit-card"></i>
            </div>
          </div>
          <p className="text-sm text-gray-600 mt-4">Successful transactions</p>
        </div>

        {/* System Health Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">System Status</p>
              <p className="text-3xl font-bold text-green-600 mt-2">
                <i className="fas fa-check-circle"></i>
              </p>
            </div>
            <div className="text-4xl text-green-600 opacity-20">
              <i className="fas fa-heartbeat"></i>
            </div>
          </div>
          <p className="text-green-600 text-sm mt-4">All systems operational</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-4 mb-6">
          <p className="text-red-700">{error}</p>
        </div>
      )}
    </Layout>
  );
}
