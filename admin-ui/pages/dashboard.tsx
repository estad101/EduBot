'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import Layout from '../components/Layout';
import { apiClient } from '../lib/api-client';
import { useDashboardStore } from '../store/dashboard';

interface DashboardStats {
  total_students: number;
  active_subscribers: number;
  total_revenue: number;
  system_status: string;
}

interface LeadsStats {
  total_leads: number;
  active_leads: number;
  converted_leads: number;
  unconverted_leads: number;
  conversion_rate: string;
}

interface RecentConversation {
  phone_number: string;
  student_name?: string;
  last_message: string;
  last_message_time: string;
  is_active: boolean;
}

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [leadsStats, setLeadsStats] = useState<LeadsStats | null>(null);
  const [conversations, setConversations] = useState<RecentConversation[]>([]);
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

        // Fetch leads stats
        const leadsResponse = await apiClient.get('/api/admin/leads/stats');
        if (leadsResponse.status === 'success') {
          setLeadsStats(leadsResponse.data);
        }

        // Fetch recent conversations
        const convResponse = await apiClient.get('/api/admin/conversations?limit=5');
        if (convResponse.status === 'success') {
          setConversations(convResponse.data);
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

      {/* Leads Statistics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Leads Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Total Leads</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{leadsStats?.total_leads || 0}</p>
            </div>
            <div className="text-4xl text-purple-600 opacity-20">
              <i className="fas fa-list"></i>
            </div>
          </div>
          <p className="text-sm text-gray-600 mt-4">
            <Link href="/leads">View all leads →</Link>
          </p>
        </div>

        {/* Active Leads Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Active Leads</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{leadsStats?.active_leads || 0}</p>
            </div>
            <div className="text-4xl text-blue-600 opacity-20">
              <i className="fas fa-phone"></i>
            </div>
          </div>
          <p className="text-sm text-gray-600 mt-4">Currently active</p>
        </div>

        {/* Unconverted Leads Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Pending Conversion</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{leadsStats?.unconverted_leads || 0}</p>
            </div>
            <div className="text-4xl text-yellow-600 opacity-20">
              <i className="fas fa-hourglass"></i>
            </div>
          </div>
          <p className="text-sm text-gray-600 mt-4">Awaiting registration</p>
        </div>

        {/* Conversion Rate Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Conversion Rate</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{leadsStats?.conversion_rate || '0%'}</p>
            </div>
            <div className="text-4xl text-green-600 opacity-20">
              <i className="fas fa-check-circle"></i>
            </div>
          </div>
          <p className="text-sm text-gray-600 mt-4">Lead to student ratio</p>
        </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-4 mb-6">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Recent Conversations */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200 flex justify-between items-center">
          <div>
            <h3 className="text-lg font-bold text-gray-800">
              <i className="fab fa-whatsapp text-green-600 mr-2"></i>Recent Messages
            </h3>
            <p className="text-sm text-gray-600 mt-1">Latest conversations from WhatsApp</p>
          </div>
          <Link href="/conversations">
            <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition">
              View All
            </button>
          </Link>
        </div>

        <div className="divide-y">
          {conversations.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <i className="fab fa-whatsapp text-5xl text-gray-200 mb-3"></i>
              <p>No messages yet</p>
            </div>
          ) : (
            conversations.map((conv) => (
              <Link key={conv.phone_number} href="/conversations">
                <div className="p-4 hover:bg-green-50 cursor-pointer transition">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <p className="font-bold text-gray-800">
                          {conv.student_name || conv.phone_number}
                        </p>
                        {conv.is_active && (
                          <span className="inline-block w-2 h-2 bg-green-500 rounded-full"></span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 truncate mt-1">{conv.last_message}</p>
                    </div>
                    <div className="text-right ml-4">
                      <p className="text-xs text-gray-400">
                        {new Date(conv.last_message_time).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                </div>
              </Link>
            ))
          )}
        </div>
      </div>
    </Layout>
  );
}
