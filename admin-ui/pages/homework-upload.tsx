'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

interface UploadState {
  loading: boolean;
  uploading: boolean;
  success: boolean;
  error: string | null;
  fileName: string | null;
}

export default function HomeworkUploadPage() {
  const router = useRouter();
  const { student_id, homework_id, subject, token } = router.query;
  const [state, setState] = useState<UploadState>({
    loading: true,
    uploading: false,
    success: false,
    error: null,
    fileName: null,
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  // Validate token on mount
  useEffect(() => {
    if (!router.isReady) return;

    if (!student_id || !homework_id || !token) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: 'Invalid upload link. Missing required parameters.'
      }));
      return;
    }

    setState(prev => ({ ...prev, loading: false }));
  }, [router.isReady, student_id, homework_id, token]);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setState(prev => ({
        ...prev,
        error: 'Please select an image file (JPG, PNG, etc.)'
      }));
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setState(prev => ({
        ...prev,
        error: 'Image size must be less than 10MB'
      }));
      return;
    }

    setSelectedFile(file);
    setState(prev => ({
      ...prev,
      error: null,
      fileName: file.name
    }));

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleUpload = async () => {
    if (!selectedFile || !student_id || !homework_id || !token) {
      setState(prev => ({
        ...prev,
        error: 'Missing file or upload parameters'
      }));
      return;
    }

    setState(prev => ({ ...prev, uploading: true, error: null }));

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('student_id', String(student_id));
      formData.append('homework_id', String(homework_id));
      formData.append('token', String(token));

      const response = await fetch('/api/homework/upload-image', {
        method: 'POST',
        body: formData,
        headers: {
          // Don't set Content-Type, let browser handle it for FormData
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.message || 'Upload failed');
      }

      setState(prev => ({
        ...prev,
        uploading: false,
        success: true,
        error: null
      }));

      // Auto-close after 3 seconds
      setTimeout(() => {
        window.close();
      }, 3000);
    } catch (error) {
      setState(prev => ({
        ...prev,
        uploading: false,
        error: error instanceof Error ? error.message : 'Upload failed'
      }));
    }
  };

  if (state.loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-blue-600 to-blue-800 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin mb-4">
            <i className="fas fa-spinner fa-2x text-white"></i>
          </div>
          <p className="text-white">Loading upload page...</p>
        </div>
      </div>
    );
  }

  if (state.error && !state.success) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-red-600 to-red-800 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <i className="fas fa-exclamation-circle text-5xl text-red-600 mb-4"></i>
          <h1 className="text-2xl font-bold text-red-600 mb-2">Upload Error</h1>
          <p className="text-gray-700 mb-6">{state.error}</p>
          <button
            onClick={() => window.close()}
            className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium"
          >
            Close
          </button>
        </div>
      </div>
    );
  }

  if (state.success) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-green-600 to-green-800 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <i className="fas fa-check-circle text-6xl text-green-600 mb-4"></i>
          <h1 className="text-2xl font-bold text-green-600 mb-2">Success!</h1>
          <p className="text-gray-700 mb-2">Your homework image has been uploaded successfully.</p>
          <p className="text-sm text-gray-500 mb-6">This page will close automatically in a few seconds.</p>
          <button
            onClick={() => window.close()}
            className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
          >
            Close Now
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-600 to-blue-800 py-8 px-4">
      <div className="max-w-md mx-auto">
        {/* Header */}
        <div className="bg-white rounded-t-lg shadow p-6 text-center">
          <i className="fas fa-camera text-4xl text-blue-600 mb-3"></i>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Upload Homework</h1>
          <p className="text-gray-600">
            {subject && <span>Subject: <strong>{subject}</strong></span>}
          </p>
        </div>

        {/* Main Content */}
        <div className="bg-white p-6 shadow">
          {/* File Input Area */}
          <label className="block">
            <div className="border-2 border-dashed border-blue-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                disabled={state.uploading}
                className="hidden"
              />
              <i className="fas fa-cloud-upload-alt text-4xl text-blue-400 mb-2"></i>
              <p className="text-gray-700 font-medium mb-1">Tap to select an image</p>
              <p className="text-sm text-gray-500">or click to choose from gallery</p>
              <p className="text-xs text-gray-400 mt-3">JPG, PNG • Max 10MB</p>
            </div>
          </label>

          {/* Preview */}
          {preview && (
            <div className="mt-6">
              <p className="text-sm font-medium text-gray-700 mb-2">Preview:</p>
              <div className="bg-gray-100 rounded-lg p-2 flex items-center justify-center">
                <img
                  src={preview}
                  alt="Preview"
                  className="max-w-full max-h-64 rounded"
                />
              </div>
              <p className="text-xs text-gray-500 mt-2">
                📄 {state.fileName}
              </p>
            </div>
          )}

          {/* Error Message */}
          {state.error && (
            <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-sm text-red-700">
                <i className="fas fa-exclamation-circle mr-2"></i>
                {state.error}
              </p>
            </div>
          )}

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={!selectedFile || state.uploading}
            className={`w-full mt-6 py-3 rounded-lg font-medium text-white transition ${
              !selectedFile || state.uploading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 active:bg-blue-800'
            }`}
          >
            {state.uploading ? (
              <>
                <i className="fas fa-spinner fa-spin mr-2"></i>
                Uploading...
              </>
            ) : (
              <>
                <i className="fas fa-upload mr-2"></i>
                Upload Image
              </>
            )}
          </button>
        </div>

        {/* Footer Info */}
        <div className="bg-white rounded-b-lg shadow p-4 text-center border-t border-gray-100">
          <p className="text-xs text-gray-500">
            <i className="fas fa-info-circle mr-1"></i>
            Make sure the image is clear and readable
          </p>
        </div>
      </div>
    </div>
  );
}
