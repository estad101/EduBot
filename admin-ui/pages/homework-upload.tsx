'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

interface UploadState {
  loading: boolean;
  uploading: boolean;
  success: boolean;
  error: string | null;
  fileName: string | null;
  uploadProgress: number;
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
    uploadProgress: 0,
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
          {/* Animated Camera Icon */}
          <style>{`
            @keyframes bounce-camera {
              0%, 100% { transform: translateY(0); }
              50% { transform: translateY(-10px); }
            }
            @keyframes pulse-glow {
              0%, 100% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.5); }
              50% { box-shadow: 0 0 40px rgba(59, 130, 246, 0.8); }
            }
            .bounce-camera {
              animation: bounce-camera 0.6s ease-in-out infinite;
            }
            .pulse-glow {
              animation: pulse-glow 2s ease-in-out infinite;
            }
          `}</style>
          
          <div className="w-24 h-24 mx-auto mb-6 bg-white rounded-full flex items-center justify-center pulse-glow">
            <i className="fas fa-camera text-4xl text-blue-600 bounce-camera"></i>
          </div>
          
          <h2 className="text-2xl font-bold text-white mb-2">Preparing Upload</h2>
          <p className="text-blue-100 text-sm">Getting everything ready...</p>
          
          {/* Loading dots */}
          <div className="flex justify-center gap-1 mt-6">
            <style>{`
              @keyframes dot-bounce {
                0%, 80%, 100% { opacity: 0.5; }
                40% { opacity: 1; }
              }
              .dot-1 { animation: dot-bounce 1.4s ease-in-out infinite; }
              .dot-2 { animation: dot-bounce 1.4s ease-in-out 0.2s infinite; }
              .dot-3 { animation: dot-bounce 1.4s ease-in-out 0.4s infinite; }
            `}</style>
            <div className="w-3 h-3 bg-white rounded-full dot-1"></div>
            <div className="w-3 h-3 bg-white rounded-full dot-2"></div>
            <div className="w-3 h-3 bg-white rounded-full dot-3"></div>
          </div>
        </div>
      </div>
    );
  }

  if (state.error && !state.success) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-red-600 to-red-800 flex items-center justify-center p-4">
        <style>{`
          @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
          }
          .shake-animation {
            animation: shake 0.5s ease-in-out;
          }
        `}</style>
        
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center shake-animation">
          <div className="flex justify-center mb-4">
            <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center">
              <i className="fas fa-exclamation-circle text-4xl text-red-600"></i>
            </div>
          </div>
          <h1 className="text-2xl font-bold text-red-600 mb-2">Upload Error</h1>
          <p className="text-gray-700 mb-6">{state.error}</p>
          <button
            onClick={() => window.close()}
            className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition"
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
        <style>{`
          @keyframes scale-pop {
            0% { transform: scale(0.3); opacity: 0; }
            70% { transform: scale(1.1); }
            100% { transform: scale(1); opacity: 1; }
          }
          @keyframes checkmark-draw {
            0% { stroke-dashoffset: 100; }
            100% { stroke-dashoffset: 0; }
          }
          .scale-pop {
            animation: scale-pop 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
          }
          .checkmark-draw {
            stroke-dasharray: 100;
            animation: checkmark-draw 0.5s ease-out 0.2s forwards;
            stroke-dashoffset: 100;
          }
        `}</style>
        
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          {/* Animated success circle with checkmark */}
          <div className="flex justify-center mb-4">
            <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center scale-pop">
              <svg className="w-12 h-12" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="none" stroke="#16a34a" strokeWidth="2" />
                <polyline
                  points="30,50 45,65 70,40"
                  fill="none"
                  stroke="#16a34a"
                  strokeWidth="4"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="checkmark-draw"
                />
              </svg>
            </div>
          </div>
          
          <h1 className="text-2xl font-bold text-green-600 mb-2">Success!</h1>
          <p className="text-gray-700 mb-2">Your homework image has been uploaded successfully.</p>
          <p className="text-sm text-gray-500 mb-6">This page will close automatically in a few seconds.</p>
          
          {/* Auto-close countdown */}
          <style>{`
            @keyframes countdown-pulse {
              0%, 100% { opacity: 0.5; }
              50% { opacity: 1; }
            }
            .countdown-pulse {
              animation: countdown-pulse 1s ease-in-out;
            }
          `}</style>
          <p className="text-xs text-gray-400 mb-6 countdown-pulse">Closing in 3 seconds...</p>
          
          <button
            onClick={() => window.close()}
            className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition"
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
        <div className="bg-white rounded-t-lg shadow p-6 text-center border-b-4 border-blue-600">
          <style>{`
            @keyframes pulse-icon {
              0%, 100% { transform: scale(1); }
              50% { transform: scale(1.1); }
            }
            .pulse-icon {
              animation: pulse-icon 2s ease-in-out infinite;
            }
          `}</style>
          <i className="fas fa-camera text-4xl text-blue-600 mb-3 block pulse-icon"></i>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">📸 Upload Homework</h1>
          {subject && (
            <div className="flex items-center justify-center gap-2 text-gray-600">
              <i className="fas fa-book text-blue-600"></i>
              <span>Subject: <strong>{subject}</strong></span>
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="bg-white p-6 shadow">
          {/* File Input Area */}
          <label className="block">
            <div className="border-2 border-dashed border-blue-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition active:bg-blue-100">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                disabled={state.uploading}
                className="hidden"
              />
              <style>{`
                @keyframes float-up {
                  0%, 100% { transform: translateY(0); }
                  50% { transform: translateY(-8px); }
                }
                .float-up {
                  animation: float-up 2s ease-in-out infinite;
                }
              `}</style>
              <i className="fas fa-cloud-upload-alt text-4xl text-blue-400 mb-2 block float-up"></i>
              <p className="text-gray-700 font-medium mb-1">Tap to select an image</p>
              <p className="text-sm text-gray-500">or click to choose from gallery</p>
              <p className="text-xs text-gray-400 mt-3 flex items-center justify-center gap-1">
                <i className="fas fa-image"></i> JPG, PNG • Max 10MB
              </p>
            </div>
          </label>

          {/* Preview */}
          {preview && (
            <div className="mt-6">
              <p className="text-sm font-medium text-gray-700 mb-2">📸 Image Preview:</p>
              <div className="bg-gray-100 rounded-lg p-2 flex items-center justify-center border-2 border-green-300 shadow-sm">
                <img
                  src={preview}
                  alt="Preview"
                  className="max-w-full max-h-64 rounded"
                />
              </div>
              <p className="text-xs text-gray-500 mt-2 flex items-center justify-center">
                <i className="fas fa-check-circle text-green-600 mr-1"></i>
                {state.fileName}
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
            className={`w-full mt-6 py-3 rounded-lg font-medium text-white transition relative overflow-hidden ${
              !selectedFile || state.uploading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 active:bg-blue-800'
            }`}
          >
            {/* Progress bar background */}
            {state.uploading && (
              <div
                className="absolute inset-0 bg-blue-700 transition-all duration-300"
                style={{ width: `${state.uploadProgress}%` }}
              />
            )}
            
            {/* Button content */}
            <div className="relative flex items-center justify-center">
              {state.uploading ? (
                <>
                  <style>{`
                    @keyframes spin-smooth {
                      from { transform: rotate(0deg); }
                      to { transform: rotate(360deg); }
                    }
                    .spin-smooth {
                      animation: spin-smooth 1s linear infinite;
                    }
                  `}</style>
                  <i className="fas fa-spinner mr-2 spin-smooth"></i>
                  <span>Uploading {state.uploadProgress}%</span>
                </>
              ) : (
                <>
                  <i className="fas fa-upload mr-2"></i>
                  Upload Image
                </>
              )}
            </div>
          </button>
        </div>

        {/* Footer Info */}
        <div className="bg-white rounded-b-lg shadow p-4 text-center border-t border-gray-100">
          <p className="text-xs text-gray-500 flex items-center justify-center gap-2">
            <i className="fas fa-lightbulb text-yellow-500"></i>
            Make sure the image is clear, readable, and landscape oriented
          </p>
        </div>
      </div>
    </div>
  );
}
