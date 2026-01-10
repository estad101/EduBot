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

interface HomeworkResponse {
  status: string;
  total: number;
  skip: number;
  limit: number;
  count: number;
  data: Homework[];
}

export default function HomeworkPage() {
  const router = useRouter();
  const [homeworks, setHomeworks] = useState<Homework[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedHomework, setSelectedHomework] = useState<Homework | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [imageError, setImageError] = useState(false);
  const [solutionText, setSolutionText] = useState('');
  const [deliveryMessage, setDeliveryMessage] = useState('Homework solution delivered successfully!');
  const [submittingAction, setSubmittingAction] = useState<string | null>(null);

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalCount, setTotalCount] = useState(0);

  // Filter state
  const [submissionTypeFilter, setSubmissionTypeFilter] = useState('');
  const [subjectFilter, setSubjectFilter] = useState('');

  // Get API URL for image serving
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://edubot-production-cf26.up.railway.app';

  const totalPages = Math.ceil(totalCount / pageSize);

  const fetchHomework = async (page: number = 1) => {
    try {
      setLoading(true);
      const token = localStorage.getItem('admin_token');
      if (!token) {
        router.push('/login');
        return;
      }

      const skip = (page - 1) * pageSize;
      const filters: any = {};

      if (submissionTypeFilter) {
        filters.submission_type = submissionTypeFilter;
      }
      if (subjectFilter) {
        filters.subject = subjectFilter;
      }

      const response: HomeworkResponse = await apiClient.getHomework(skip, pageSize, filters);
      if (response.status === 'success') {
        setHomeworks(response.data);
        setTotalCount(response.total);
        setCurrentPage(page);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load homework');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHomework(1);
  }, [submissionTypeFilter, subjectFilter, pageSize]);

  // Handle solution submission when text is set via prompt
  useEffect(() => {
    if (submittingAction === 'solution_prompt' && solutionText.trim()) {
      handleProvideSolution();
    }
  }, [solutionText, submittingAction]);

  const openModal = (homework: Homework) => {
    setSelectedHomework(homework);
    setShowModal(true);
    setSolutionText('');
    setDeliveryMessage('Homework solution delivered successfully!');
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedHomework(null);
    setImageError(false);
    setSolutionText('');
    setSubmittingAction(null);
  };

  const handleProvideSolution = async () => {
    if (!selectedHomework || !solutionText.trim()) {
      alert('Please enter a solution');
      return;
    }

    setSubmittingAction('solution');
    try {
      const response = await apiClient.post(
        `/api/admin/homework/${selectedHomework.id}/provide-solution`,
        { solution_text: solutionText }
      );

      if (response.status === 'success') {
        alert('✅ Solution sent to student successfully!');
        closeModal();
        fetchHomework(currentPage); // Refresh the list
      } else {
        alert(`Error: ${response.message}`);
      }
    } catch (err: any) {
      alert(`Failed to send solution: ${err.message}`);
    } finally {
      setSubmittingAction(null);
    }
  };

  const handleMarkSolved = async () => {
    if (!selectedHomework) {
      alert('No homework selected');
      return;
    }

    setSubmittingAction('solved');
    try {
      const response = await apiClient.post(
        `/api/admin/homework/${selectedHomework.id}/mark-solved`,
        { delivery_message: deliveryMessage }
      );

      if (response.status === 'success') {
        alert('✅ Homework marked as solved and student notified!');
        closeModal();
        fetchHomework(currentPage); // Refresh the list
      } else {
        alert(`Error: ${response.message}`);
      }
    } catch (err: any) {
      alert(`Failed to mark homework as solved: ${err.message}`);
    } finally {
      setSubmittingAction(null);
    }
  };

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      fetchHomework(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      fetchHomework(currentPage + 1);
    }
  };

  return (
    <Layout>
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            <i className="fas fa-book mr-2 text-blue-600"></i>All Submissions
          </h2>

          {/* Filters Section */}
          <div className="bg-gray-50 rounded-lg p-4 -mx-6 -mb-4 px-6 py-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Submission Type Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Submission Type
                </label>
                <select
                  value={submissionTypeFilter}
                  onChange={(e) => {
                    setSubmissionTypeFilter(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Types</option>
                  <option value="IMAGE">Image Only</option>
                  <option value="TEXT">Text Only</option>
                </select>
              </div>

              {/* Subject Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Subject
                </label>
                <input
                  type="text"
                  placeholder="Search subject..."
                  value={subjectFilter}
                  onChange={(e) => {
                    setSubjectFilter(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Page Size */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Items Per Page
                </label>
                <select
                  value={pageSize}
                  onChange={(e) => {
                    setPageSize(Number(e.target.value));
                    setCurrentPage(1);
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value={10}>10 per page</option>
                  <option value={25}>25 per page</option>
                  <option value={50}>50 per page</option>
                  <option value={100}>100 per page</option>
                </select>
              </div>
            </div>

            {/* Active Filters Display */}
            {(submissionTypeFilter || subjectFilter) && (
              <div className="mt-4 flex flex-wrap gap-2">
                {submissionTypeFilter && (
                  <span className="inline-block bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                    Type: {submissionTypeFilter}
                    <button
                      onClick={() => setSubmissionTypeFilter('')}
                      className="ml-2 font-bold"
                    >
                      ✕
                    </button>
                  </span>
                )}
                {subjectFilter && (
                  <span className="inline-block bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                    Subject: {subjectFilter}
                    <button
                      onClick={() => setSubjectFilter('')}
                      className="ml-2 font-bold"
                    >
                      ✕
                    </button>
                  </span>
                )}
              </div>
            )}
          </div>
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
        ) : homeworks.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            <i className="fas fa-inbox text-3xl mb-2"></i>
            <p>No homework submissions found</p>
          </div>
        ) : (
          <>
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

            {/* Pagination Controls */}
            <div className="bg-gray-50 border-t border-gray-200 px-6 py-4 flex items-center justify-between">
              <div className="text-sm text-gray-600">
                Showing <span className="font-semibold">{(currentPage - 1) * pageSize + 1}</span> to{' '}
                <span className="font-semibold">{Math.min(currentPage * pageSize, totalCount)}</span> of{' '}
                <span className="font-semibold">{totalCount}</span> submissions
              </div>

              <div className="flex gap-2">
                <button
                  onClick={handlePreviousPage}
                  disabled={currentPage === 1}
                  className={`px-4 py-2 rounded font-medium text-sm transition ${
                    currentPage === 1
                      ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                      : 'bg-blue-600 hover:bg-blue-700 text-white'
                  }`}
                >
                  <i className="fas fa-chevron-left mr-2"></i>Previous
                </button>

                <div className="flex items-center gap-2 px-4 py-2">
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    const pageNum = i + 1;
                    return (
                      <button
                        key={pageNum}
                        onClick={() => fetchHomework(pageNum)}
                        className={`w-8 h-8 rounded text-sm font-medium transition ${
                          currentPage === pageNum
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                </div>

                <button
                  onClick={handleNextPage}
                  disabled={currentPage >= totalPages}
                  className={`px-4 py-2 rounded font-medium text-sm transition ${
                    currentPage >= totalPages
                      ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                      : 'bg-blue-600 hover:bg-blue-700 text-white'
                  }`}
                >
                  Next<i className="fas fa-chevron-right ml-2"></i>
                </button>
              </div>
            </div>
          </>
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
                      // Show solution input modal
                      const solution = prompt('Enter the homework solution to send to the student:');
                      if (solution && solution.trim()) {
                        setSolutionText(solution);
                        setSubmittingAction('solution_prompt');
                      }
                    }}
                    disabled={submittingAction === 'solution'}
                    className="px-3 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded font-medium text-sm transition whitespace-nowrap"
                    title="Provide Solution"
                  >
                    {submittingAction === 'solution' ? (
                      <><i className="fas fa-spinner fa-spin mr-1"></i>Sending...</>
                    ) : (
                      <><i className="fas fa-check-circle mr-1"></i>Solution</>
                    )}
                  </button>
                  <button
                    onClick={handleMarkSolved}
                    disabled={submittingAction === 'solved'}
                    className="px-3 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white rounded font-medium text-sm transition whitespace-nowrap"
                    title="Mark Solved"
                  >
                    {submittingAction === 'solved' ? (
                      <><i className="fas fa-spinner fa-spin mr-1"></i>Marking...</>
                    ) : (
                      <><i className="fas fa-checkmark mr-1"></i>Solved</>
                    )}
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
                      {/* Extract filename from path like "6/homework_1767...png" */}
                      {(() => {
                        const filename = selectedHomework.file_path.includes('/') 
                          ? selectedHomework.file_path.split('/').pop() 
                          : selectedHomework.file_path;
                        const imageUrl = `${apiUrl}/api/homework/${selectedHomework.student_id}/image/${filename}`;
                        
                        return (
                          <>
                            <div className="flex items-center justify-center min-h-[300px] mb-4">
                              {imageError ? (
                                <div className="text-center">
                                  <div className="w-20 h-20 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <i className="fas fa-image text-4xl text-gray-400"></i>
                                  </div>
                                  <p className="text-gray-600 font-medium">Unable to load image</p>
                                  <p className="text-sm text-gray-500 mt-2">The image file may have been deleted or moved.</p>
                                </div>
                              ) : (
                                <img
                                  src={imageUrl}
                                  alt="Homework submission"
                                  className="max-w-full max-h-[500px] rounded"
                                  onError={() => {
                                    console.error('Failed to load image from:', imageUrl);
                                    setImageError(true);
                                  }}
                                />
                              )}
                            </div>
                            <div className="mt-4 p-4 bg-white rounded border border-gray-300">
                              <p className="text-sm text-gray-600 mb-2">📁 File Details:</p>
                              <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                                <div>
                                  <p className="text-gray-500 text-xs uppercase tracking-wide">Filename</p>
                                  <p className="text-gray-900 font-mono mt-1 break-all">{filename}</p>
                                </div>
                                <div>
                                  <p className="text-gray-500 text-xs uppercase tracking-wide">Student ID</p>
                                  <p className="text-gray-900 font-mono mt-1">{selectedHomework.student_id}</p>
                                </div>
                              </div>
                              <a
                                href={imageUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-block px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm font-medium transition"
                              >
                                <i className="fas fa-external-link-alt mr-1"></i>Open Image in New Tab
                              </a>
                            </div>
                          </>
                        );
                      })()}
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
