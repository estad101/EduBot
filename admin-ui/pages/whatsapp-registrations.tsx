'use client';

import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import { apiClient } from '../lib/api-client';

interface Student {
  student_id: number;
  phone_number: string;
  full_name: string;
  email: string;
  class_grade: string;
  status: string;
  has_active_subscription: boolean;
  created_at?: string;
}

export default function WhatsAppRegistrations() {
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState({
    total_registered: 0,
    with_active_subscription: 0,
  });

  useEffect(() => {
    fetchStudents();
    fetchStats();
  }, []);

  const fetchStudents = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/students/list');
      if (response.data.status === 'success') {
        setStudents(response.data.data?.students || []);
      }
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch students');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await apiClient.get('/students/stats');
      if (response.data.status === 'success') {
        setStats(response.data.data);
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">WhatsApp Registrations</h1>
            <p className="text-gray-600 mt-1">
              Students who have registered via WhatsApp
            </p>
          </div>
          <button
            onClick={fetchStudents}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            🔄 Refresh
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 font-medium">Total Registered</p>
                <p className="text-3xl font-bold text-blue-900 mt-2">
                  {stats.total_registered}
                </p>
              </div>
              <div className="text-4xl">👥</div>
            </div>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 font-medium">Active Subscriptions</p>
                <p className="text-3xl font-bold text-green-900 mt-2">
                  {stats.with_active_subscription}
                </p>
              </div>
              <div className="text-4xl">✅</div>
            </div>
          </div>

          <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 font-medium">Conversion Rate</p>
                <p className="text-3xl font-bold text-purple-900 mt-2">
                  {stats.total_registered > 0
                    ? Math.round((stats.with_active_subscription / stats.total_registered) * 100)
                    : 0}
                  %
                </p>
              </div>
              <div className="text-4xl">📊</div>
            </div>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
            ❌ {error}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin">⏳</div>
            <p className="text-gray-600 mt-2">Loading students...</p>
          </div>
        )}

        {/* Students Table */}
        {!loading && students.length > 0 && (
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-gray-50">
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Phone Number
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Class
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Subscription
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Registered
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {students.map((student) => (
                    <tr
                      key={student.student_id}
                      className="border-b hover:bg-gray-50 transition"
                    >
                      <td className="px-6 py-4 text-sm text-gray-900 font-medium">
                        {student.phone_number}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-700">
                        {student.full_name}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-700">
                        {student.email}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-700">
                        {student.class_grade || 'N/A'}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        {student.has_active_subscription ? (
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                            ✅ Active
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                            ⭕ Free
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {formatDate(student.created_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && students.length === 0 && !error && (
          <div className="bg-gray-50 rounded-lg border border-gray-200 p-12 text-center">
            <div className="text-4xl mb-4">📭</div>
            <p className="text-gray-600 text-lg">
              No students registered yet. Students will appear here when they message the WhatsApp bot.
            </p>
          </div>
        )}

        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-3">🤖 How Auto-Registration Works</h3>
          <ul className="space-y-2 text-sm text-blue-800">
            <li>✅ When a user messages your WhatsApp bot, they are automatically registered</li>
            <li>✅ Their phone number becomes their unique identifier</li>
            <li>✅ They go through a conversation flow to complete registration (name, email, class)</li>
            <li>✅ Once registered, they can submit homework or buy subscriptions</li>
            <li>✅ This dashboard shows all auto-registered numbers</li>
          </ul>
        </div>
      </div>
    </Layout>
  );
}
