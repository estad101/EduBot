'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '../components/Layout';
import { apiClient } from '../lib/api-client';

interface Subscription {
  id: number;
  student_id: number;
  start_date: string;
  end_date: string;
  is_active: boolean;
}

export default function SubscriptionsPage() {
  const router = useRouter();
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState({ total: 0, active: 0, expiring_soon: 0 });

  useEffect(() => {
    const fetchSubscriptions = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('admin_token');
        if (!token) {
          router.push('/login');
          return;
        }

        const response = await apiClient.getSubscriptions(0, 50);
        if (response.status === 'success') {
          setSubscriptions(response.data);
          const now = new Date();
          const expiringSoon = response.data.filter((sub: Subscription) => {
            const endDate = new Date(sub.end_date);
            const daysUntilExpiry = (endDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24);
            return daysUntilExpiry < 7 && daysUntilExpiry > 0;
          }).length;

          setStats({
            total: response.data.length,
            active: response.data.filter((s: Subscription) => s.is_active).length,
            expiring_soon: expiringSoon,
          });
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load subscriptions');
      } finally {
        setLoading(false);
      }
    };

    fetchSubscriptions();
  }, [router]);

  const calculateDaysLeft = (endDate: string) => {
    const now = new Date();
    const end = new Date(endDate);
    const days = Math.ceil((end.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    return days;
  };

  return (
    <Layout>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm font-medium">Total Subscriptions</p>
          <p className="text-3xl font-bold text-gray-800 mt-2">{stats.total}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm font-medium">Active Now</p>
          <p className="text-3xl font-bold text-green-600 mt-2">{stats.active}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm font-medium">Expiring Soon</p>
          <p className="text-3xl font-bold text-orange-600 mt-2">{stats.expiring_soon}</p>
          <p className="text-xs text-gray-600 mt-2">Within 7 days</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-800">
            <i className="fas fa-calendar-alt mr-2 text-blue-600"></i>All Subscriptions
          </h2>
        </div>

        {loading ? (
          <div className="p-6 text-center">
            <i className="fas fa-spinner fa-spin text-2xl text-blue-600 mb-2"></i>
            <p className="text-gray-600">Loading subscriptions...</p>
          </div>
        ) : error ? (
          <div className="p-6 bg-red-50 border border-red-200 rounded text-red-700">
            {error}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Student ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Start Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">End Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Days Left</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Status</th>
                </tr>
              </thead>
              <tbody>
                {subscriptions.map((sub) => {
                  const daysLeft = calculateDaysLeft(sub.end_date);
                  return (
                    <tr key={sub.id} className="border-b hover:bg-gray-50 transition">
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">{sub.student_id}</td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {new Date(sub.start_date).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {new Date(sub.end_date).toLocaleDateString()}
                      </td>
                      <td
                        className={`px-6 py-4 text-sm font-semibold ${
                          daysLeft < 0
                            ? 'text-red-600'
                            : daysLeft < 7
                            ? 'text-orange-600'
                            : 'text-green-600'
                        }`}
                      >
                        {daysLeft > 0 ? `${daysLeft} days` : 'Expired'}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <span
                          className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                            sub.is_active
                              ? 'bg-green-100 text-green-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {sub.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  );
}
