'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '../components/Layout';
import { apiClient } from '../lib/api-client';

interface Student {
  id: number;
  full_name: string;
  phone_number: string;
  email: string;
  class_grade: string;
  status: string;
  created_at: string;
}

export default function StudentsPage() {
  const router = useRouter();
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(0);
  const [totalCount, setTotalCount] = useState(0);

  useEffect(() => {
    const fetchStudents = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('admin_token');
        if (!token) {
          router.push('/login');
          return;
        }

        const response = await apiClient.getStudents(page * 50, 50);
        if (response.status === 'success') {
          setStudents(response.data);
          setTotalCount(response.total || response.data.length);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load students');
      } finally {
        setLoading(false);
      }
    };

    fetchStudents();
  }, [page, router]);

  const handleDelete = async (studentId: number, studentName: string) => {
    if (!confirm(`Are you sure you want to permanently delete ${studentName}? This cannot be undone.`)) {
      return;
    }

    try {
      const response = await apiClient.delete(`/api/admin/students/${studentId}`);
      if (response.status === 'success' || response.status === 200) {
        // Remove student from list
        setStudents(students.filter(s => s.id !== studentId));
        setTotalCount(totalCount - 1);
        alert('Student deleted successfully');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to delete student');
    }
  };

  return (
    <Layout>
      <div className="bg-white rounded-lg shadow">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-800">
              <i className="fas fa-users mr-2 text-blue-600"></i>All Students
            </h2>
            <div className="text-sm text-gray-600">
              Total: <span className="font-bold text-gray-900">{totalCount}</span>
            </div>
          </div>

          {/* Search and Filters */}
          <form onSubmit={handleSearch} className="flex gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search by name, phone, or email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            >
              <option value="">All Statuses</option>
              <option value="NEW_USER">New User</option>
              <option value="REGISTERED_FREE">Free</option>
              <option value="ACTIVE_SUBSCRIBER">Subscriber</option>
            </select>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              <i className="fas fa-search mr-2"></i>Search
            </button>
          </form>
        </div>

        {/* Table */}
        {loading ? (
          <div className="p-6 text-center">
            <i className="fas fa-spinner fa-spin text-2xl text-blue-600 mb-2"></i>
            <p className="text-gray-600">Loading students...</p>
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
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Phone</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Email</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Grade</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Joined</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody>
                {students.map((student) => (
                  <tr key={student.id} className="border-b hover:bg-gray-50 transition">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{student.full_name}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{student.phone_number}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{student.email}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{student.class_grade}</td>
                    <td className="px-6 py-4 text-sm">
                      <span
                        className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                          student.status === 'ACTIVE_SUBSCRIBER'
                            ? 'bg-green-100 text-green-800'
                            : student.status === 'REGISTERED_FREE'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {student.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {new Date(student.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-sm space-x-2">
                      <button
                        onClick={() => router.push(`/students/${student.id}`)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        <i className="fas fa-eye mr-1"></i>View
                      </button>
                      <button
                        onClick={() => handleDelete(student.id, student.full_name)}
                        className="text-red-600 hover:text-red-800"
                        title="Delete this student permanently"
                      >
                        <i className="fas fa-trash mr-1"></i>Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalCount > 50 && (
          <div className="p-6 border-t flex justify-center gap-2">
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span className="px-4 py-2">Page {page + 1}</span>
            <button
              onClick={() => setPage(page + 1)}
              disabled={page * 50 + 50 >= totalCount}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </Layout>
  );
}
