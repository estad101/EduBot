'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '../components/Layout';
import { apiClient } from '../lib/api-client';

interface Lead {
  id: number;
  phone_number: string;
  sender_name: string;
  first_message: string;
  last_message: string;
  message_count: number;
  converted_to_student: boolean;
  student_id: number | null;
  created_at: string;
  updated_at: string;
  last_message_time: string;
}

interface LeadsStats {
  total_leads: number;
  active_leads: number;
  converted_leads: number;
  unconverted_leads: number;
  conversion_rate: string;
}

export default function LeadsPage() {
  const router = useRouter();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [stats, setStats] = useState<LeadsStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'unconverted' | 'converted'>('unconverted');
  const [page, setPage] = useState(0);

  useEffect(() => {
    const fetchLeads = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('admin_token');
        if (!token) {
          router.push('/login');
          return;
        }

        // Fetch stats
        const statsResponse = await apiClient.get('/api/admin/leads/stats');
        if (statsResponse.status === 'success') {
          setStats(statsResponse.data);
        }

        // Fetch leads based on filter
        let url = '/api/admin/leads?skip=' + (page * 50) + '&limit=50';
        if (filter === 'converted') {
          url += '&converted=true';
        } else if (filter === 'unconverted') {
          url += '&converted=false';
        }

        const response = await apiClient.get(url);
        if (response.status === 'success') {
          setLeads(response.data);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load leads');
      } finally {
        setLoading(false);
      }
    };

    fetchLeads();
  }, [page, filter, router]);

  const handleDelete = async (leadId: number, phoneNumber: string) => {
    if (!confirm(`Are you sure you want to permanently delete this lead (${phoneNumber})? This cannot be undone.`)) {
      return;
    }

    try {
      const response = await apiClient.delete(`/api/admin/leads/${leadId}`);
      if (response.status === 'success') {
        setLeads(leads.filter(l => l.id !== leadId));
        alert('Lead permanently deleted');
      }
    } catch (err: any) {
      alert(`Failed to delete lead: ${err.message || 'Unknown error'}`);
    }
  };

  return (
    <Layout>
      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Leads */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Total Leads</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{stats?.total_leads || 0}</p>
            </div>
            <div className="text-4xl text-purple-600 opacity-20">
              <i className="fas fa-users"></i>
            </div>
          </div>
        </div>

        {/* Active Leads */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Active Leads</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{stats?.active_leads || 0}</p>
            </div>
            <div className="text-4xl text-blue-600 opacity-20">
              <i className="fas fa-phone"></i>
            </div>
          </div>
        </div>

        {/* Unconverted Leads */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Unconverted</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{stats?.unconverted_leads || 0}</p>
            </div>
            <div className="text-4xl text-yellow-600 opacity-20">
              <i className="fas fa-hourglass"></i>
            </div>
          </div>
        </div>

        {/* Conversion Rate */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Conversion Rate</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{stats?.conversion_rate || '0%'}</p>
            </div>
            <div className="text-4xl text-green-600 opacity-20">
              <i className="fas fa-check-circle"></i>
            </div>
          </div>
        </div>
      </div>

      {/* Leads Table */}
      <div className="bg-white rounded-lg shadow">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-800">
              <i className="fas fa-list mr-2 text-purple-600"></i>Leads List
            </h2>
          </div>

          {/* Filter Tabs */}
          <div className="flex gap-4 mb-4">
            <button
              onClick={() => { setFilter('unconverted'); setPage(0); }}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                filter === 'unconverted'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <i className="fas fa-phone mr-2"></i>Unconverted ({stats?.unconverted_leads || 0})
            </button>
            <button
              onClick={() => { setFilter('converted'); setPage(0); }}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                filter === 'converted'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <i className="fas fa-check mr-2"></i>Converted ({stats?.converted_leads || 0})
            </button>
            <button
              onClick={() => { setFilter('all'); setPage(0); }}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                filter === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <i className="fas fa-list mr-2"></i>All ({stats?.total_leads || 0})
            </button>
          </div>
        </div>

        {/* Table */}
        {loading ? (
          <div className="p-6 text-center">
            <i className="fas fa-spinner fa-spin text-2xl text-purple-600 mb-2"></i>
            <p className="text-gray-600">Loading leads...</p>
          </div>
        ) : error ? (
          <div className="p-6 bg-red-50 border border-red-200 rounded text-red-700">
            {error}
          </div>
        ) : leads.length === 0 ? (
          <div className="p-8 text-center">
            <i className="fas fa-inbox text-5xl text-gray-200 mb-3"></i>
            <p className="text-gray-500">No leads found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Phone</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Messages</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Last Message</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody>
                {leads.map((lead) => (
                  <tr key={lead.id} className="border-b hover:bg-gray-50 transition">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{lead.phone_number}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{lead.sender_name || '-'}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold">
                        {lead.message_count}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600 truncate max-w-xs">{lead.last_message}</td>
                    <td className="px-6 py-4 text-sm">
                      <span
                        className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                          lead.converted_to_student
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {lead.converted_to_student ? 'Converted' : 'Pending'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {new Date(lead.last_message_time).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-sm space-x-2">
                      <button
                        onClick={() => router.push(`/leads/${lead.id}`)}
                        className="text-blue-600 hover:text-blue-800 font-medium"
                      >
                        <i className="fas fa-eye mr-1"></i>View
                      </button>
                      <button
                        onClick={() => handleDelete(lead.id, lead.phone_number)}
                        className="text-red-600 hover:text-red-800 font-medium"
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
        {!loading && leads.length > 0 && (
          <div className="p-6 border-t border-gray-200 flex justify-between items-center">
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50"
            >
              Previous
            </button>
            <span className="text-sm text-gray-600">Page {page + 1}</span>
            <button
              onClick={() => setPage(page + 1)}
              disabled={leads.length < 50}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </Layout>
  );
}
