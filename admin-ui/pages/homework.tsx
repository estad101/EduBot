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
                      {new Date(hw.created_at).toLocaleDateString()}
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
            <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 flex justify-between items-center">
              <div>
                <h3 className="text-xl font-bold">{selectedHomework.subject}</h3>
                <p className="text-blue-100 text-sm">
                  {selectedHomework.student_name} • {selectedHomework.student_class}
                </p>
              </div>
              <button
                onClick={closeModal}
                className="text-white hover:bg-blue-500 rounded-full p-2 transition"
              >
                <i className="fas fa-times text-xl"></i>
              </button>
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
                    <div className="bg-gray-50 rounded-lg p-4 flex items-center justify-center min-h-[300px]">
                      <img
                        src={`/uploads/${selectedHomework.file_path}`}
                        alt="Homework submission"
                        className="max-w-full max-h-[500px] rounded"
                        onError={(e) => {
                          console.error('Failed to load image:', selectedHomework.file_path);
                          e.currentTarget.src = '/placeholder-image.jpg';
                        }}
                      />
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
            <div className="bg-gray-50 border-t border-gray-200 p-6 flex justify-between gap-3">
              <div className="flex gap-3">
                <button
                  onClick={() => {
                    // TODO: Implement provide solution handler
                    alert('Provide Homework Solution feature coming soon');
                  }}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded font-medium transition"
                >
                  <i className="fas fa-check-circle mr-2"></i>Provide Solution
                </button>
                <button
                  onClick={() => {
                    // TODO: Implement mark solved handler
                    alert('Mark Homework Solved feature coming soon');
                  }}
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded font-medium transition"
                >
                  <i className="fas fa-checkmark mr-2"></i>Mark Solved
                </button>
              </div>
              <button
                onClick={closeModal}
                className="px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded font-medium transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}
