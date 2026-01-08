'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '../components/Layout';
import { apiClient } from '../lib/api-client';

interface Homework {
  id: number;
  student_id: number;
  student_name: string;
  student_class: string;
  subject: string;
  submission_type: string;
  content: string;
  file_path?: string;
  created_at: string;
}

export default function HomeworkPage() {
  const router = useRouter();
  const [homeworks, setHomeworks] = useState<Homework[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedHomework, setSelectedHomework] = useState<Homework | null>(null);
  const [showModal, setShowModal] = useState(false);

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
          // Sort by created_at in descending order (latest first)
          const sortedHomeworks = response.data.sort(
            (a: Homework, b: Homework) =>
              new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          );
          setHomeworks(sortedHomeworks);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load homework');
      } finally {
        setLoading(false);
      }
    };

    fetchHomework();
  }, [router]);

  const openModal = (homework: Homework) => {
    setSelectedHomework(homework);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedHomework(null);
  };

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
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Student Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Class</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Subject</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Action</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Submitted</th>
                </tr>
              </thead>
              <tbody>
                {homeworks.map((hw) => (
                  <tr key={hw.id} className="border-b hover:bg-gray-50 transition">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{hw.student_name}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{hw.student_class}</td>
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
                    <td className="px-6 py-4 text-sm">
                      <button
                        onClick={() => openModal(hw)}
                        className="inline-block px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded font-medium text-xs transition"
                      >
                        <i className="fas fa-eye mr-1"></i>View Homework
                      </button>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      <div>
                        <div className="font-medium">{new Date(hw.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}</div>
                        <div className="text-xs text-gray-500">{new Date(hw.created_at).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true })}</div>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && selectedHomework && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6">
              <div className="flex justify-between items-start gap-4 mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-bold">{selectedHomework.subject}</h3>
                  <p className="text-blue-100 text-sm">
                    {selectedHomework.student_name} • {selectedHomework.student_class}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      // TODO: Implement provide solution handler
                      alert('Provide Homework Solution feature coming soon');
                    }}
                    className="px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded font-medium text-sm transition whitespace-nowrap"
                    title="Provide Solution"
                  >
                    <i className="fas fa-check-circle mr-1"></i>Solution
                  </button>
                  <button
                    onClick={() => {
                      // TODO: Implement mark solved handler
                      alert('Mark Homework Solved feature coming soon');
                    }}
                    className="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded font-medium text-sm transition whitespace-nowrap"
                    title="Mark Solved"
                  >
                    <i className="fas fa-checkmark mr-1"></i>Solved
                  </button>
                  <button
                    onClick={closeModal}
                    className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded font-medium text-sm transition"
                    title="Close"
                  >
                    <i className="fas fa-times mr-1"></i>Close
                  </button>
                </div>
              </div>
            </div>

            {/* Modal Content */}
            <div className="p-8">
              {selectedHomework.submission_type === 'TEXT' ? (
                <div>
                  <h4 className="text-gray-700 font-semibold mb-4">📝 Text Submission</h4>
                  <div className="bg-gray-50 rounded-lg p-6 border border-gray-200 whitespace-pre-wrap text-gray-700">
                    {selectedHomework.content || '(No content provided)'}
                  </div>
                </div>
              ) : (
                <div>
                  <h4 className="text-gray-700 font-semibold mb-4">📷 Image Submission</h4>
                  {selectedHomework.file_path ? (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center justify-center min-h-[300px] mb-4">
                        <img
                          src={`/uploads/${selectedHomework.file_path}`}
                          alt="Homework submission"
                          className="max-w-full max-h-[500px] rounded"
                          onError={(e) => {
                            console.error('Failed to load image:', selectedHomework.file_path);
                            (e.currentTarget as HTMLImageElement).style.display = 'none';
                          }}
                        />
                      </div>
                      <div className="mt-4 p-4 bg-white rounded border border-gray-300">
                        <p className="text-sm text-gray-600 mb-2">📁 File Path:</p>
                        <p className="text-sm font-mono text-gray-900 mb-3 break-all">
                          {selectedHomework.file_path}
                        </p>
                        <a
                          href={`/uploads/${selectedHomework.file_path}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-block px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm font-medium transition"
                        >
                          <i className="fas fa-external-link-alt mr-1"></i>Open Image in New Tab
                        </a>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-gray-50 rounded-lg p-6 text-center text-gray-500">
                      (No image file available)
                    </div>
                  )}
                </div>
              )}

              {/* Metadata */}
              <div className="mt-8 pt-6 border-t border-gray-200">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">Student</p>
                    <p className="font-semibold text-gray-900">{selectedHomework.student_name}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Class</p>
                    <p className="font-semibold text-gray-900">{selectedHomework.student_class}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Subject</p>
                    <p className="font-semibold text-gray-900">{selectedHomework.subject}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Submitted On</p>
                    <p className="font-semibold text-gray-900">
                      {new Date(selectedHomework.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="bg-gray-50 border-t border-gray-200 p-6"></div>
          </div>
        </div>
      )}
    </Layout>
  );
}
