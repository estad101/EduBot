'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '../components/Layout';
import { apiClient } from '../lib/api-client';

export default function ReportsPage() {
  const router = useRouter();
  const [reports, setReports] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('admin_token');
        if (!token) {
          router.push('/login');
          return;
        }

        const response = await apiClient.getReports();
        if (response.status === 'success') {
          setReports(response.data);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load reports');
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, [router]);

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <i className="fas fa-spinner fa-spin text-4xl text-blue-600 mb-4"></i>
            <p className="text-gray-600">Loading reports...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Student Analytics */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-6">
            <i className="fas fa-users mr-2 text-blue-600"></i>Student Distribution
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2">
              <span className="text-gray-600">New Users</span>
              <span className="font-semibold text-gray-800">{reports?.new_users || 0}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-t">
              <span className="text-gray-600">Free Users</span>
              <span className="font-semibold text-gray-800">{reports?.free_users || 0}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-t">
              <span className="text-gray-600">Active Subscribers</span>
              <span className="font-semibold text-gray-800">{reports?.active_subscribers || 0}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-t">
              <span className="text-gray-600 font-semibold">Total Students</span>
              <span className="font-bold text-gray-900">{reports?.total_students || 0}</span>
            </div>
          </div>
        </div>

        {/* Payment Analytics */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-6">
            <i className="fas fa-credit-card mr-2 text-blue-600"></i>Payment Status
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2">
              <span className="text-gray-600">Successful</span>
              <span className="font-semibold text-green-600">{reports?.successful_payments || 0}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-t">
              <span className="text-gray-600">Pending</span>
              <span className="font-semibold text-yellow-600">{reports?.pending_payments || 0}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-t">
              <span className="text-gray-600">Failed</span>
              <span className="font-semibold text-red-600">{reports?.failed_payments || 0}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-t">
              <span className="text-gray-600 font-semibold">Total Payments</span>
              <span className="font-bold text-gray-900">{reports?.total_payments || 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm">Conversion Rate</p>
          <p className="text-3xl font-bold text-blue-600 mt-2">
            {reports && reports.total_students > 0
              ? ((reports.active_subscribers / reports.total_students) * 100).toFixed(0)
              : 0}
            %
          </p>
          <p className="text-xs text-gray-600 mt-2">
            {reports?.active_subscribers || 0} of {reports?.total_students || 0} students
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm">Avg Revenue per Payment</p>
          <p className="text-3xl font-bold text-green-600 mt-2">
            ₦{reports?.total_payments > 0 ? (reports.total_revenue / reports.total_payments).toFixed(0) : 0}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm">Total Revenue</p>
          <p className="text-3xl font-bold text-yellow-600 mt-2">₦{reports?.total_revenue || 0}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm">Success Rate</p>
          <p className="text-3xl font-bold text-purple-600 mt-2">
            {reports && reports.total_payments > 0
              ? ((reports.successful_payments / reports.total_payments) * 100).toFixed(0)
              : 0}
            %
          </p>
        </div>
      </div>
    </Layout>
  );
}
