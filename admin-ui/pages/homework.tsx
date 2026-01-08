'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '../components/Layout';
import { apiClient } from '../lib/api-client';

interface Homework {
  id: number;
  student_id: number;
  subject: string;
  submission_type: string;
  content: string;
  created_at: string;
}

export default function HomeworkPage() {
  const router = useRouter();
  const [homeworks, setHomeworks] = useState<Homework[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHomework = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('admin_token');
        if (!token) {
          router.push('/login');
          return;
        }

        const response = await apiClient.getHomework(0, 50);
        if (response.status === 'success') {
          setHomeworks(response.data);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load homework');
      } finally {
        setLoading(false);
      }
    };

    fetchHomework();
  }, [router]);

  return (
    <Layout>
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-800">
            <i className="fas fa-book mr-2 text-blue-600"></i>All Submissions
          </h2>
        </div>

        {loading ? (
          <div className="p-6 text-center">
            <i className="fas fa-spinner fa-spin text-2xl text-blue-600 mb-2"></i>
            <p className="text-gray-600">Loading homework...</p>
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
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Subject</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Content</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Submitted</th>
                </tr>
              </thead>
              <tbody>
                {homeworks.map((hw) => (
                  <tr key={hw.id} className="border-b hover:bg-gray-50 transition">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{hw.student_id}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{hw.subject}</td>
                    <td className="px-6 py-4 text-sm">
                      <span
                        className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                          hw.submission_type === 'TEXT'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-green-100 text-green-800'
                        }`}
                      >
                        {hw.submission_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {hw.submission_type === 'TEXT' ? (hw.content ? hw.content.substring(0, 50) : '(No content)') : '📷 Image'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {new Date(hw.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  );
}
