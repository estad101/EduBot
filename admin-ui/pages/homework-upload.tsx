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
  fileSize: string | null;
}

interface FileValidation {
  valid: boolean;
  errors: string[];
  size: number;
  type: string;
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
    fileSize: null,
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [validation, setValidation] = useState<FileValidation>({ valid: true, errors: [], size: 0, type: '' });
  const [countdown, setCountdown] = useState(3);

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

  // Countdown timer for success page
  useEffect(() => {
    if (!state.success || countdown <= 0) return;
    
    const timer = setTimeout(() => {
      setCountdown(countdown - 1);
    }, 1000);
    
    return () => clearTimeout(timer);
  }, [state.success, countdown]);

  // Auto-close when countdown reaches 0
  useEffect(() => {
    if (countdown === 0 && state.success) {
      window.close();
    }
  }, [countdown, state.success]);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const validateFile = (file: File): FileValidation => {
    const errors: string[] = [];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!file.type.startsWith('image/')) {
      errors.push('File must be an image (JPG, PNG, etc.)');
    }

    if (file.size > maxSize) {
      errors.push(`File size is ${formatFileSize(file.size)}, but max is 10MB`);
    }

    return {
      valid: errors.length === 0,
      errors,
      size: file.size,
      type: file.type
    };
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const fileValidation = validateFile(file);

    if (!fileValidation.valid) {
      setState(prev => ({
        ...prev,
        error: fileValidation.errors.join(', ')
      }));
      setValidation(fileValidation);
      return;
    }

    setSelectedFile(file);
    setValidation(fileValidation);
    setState(prev => ({
      ...prev,
      error: null,
      fileName: file.name,
      fileSize: formatFileSize(file.size)
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

      // Use full API URL from environment
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://nurturing-exploration-production.up.railway.app';
      const uploadUrl = `${apiUrl}/api/homework/upload-image`;
      
      console.log('Uploading to:', uploadUrl);

      const response = await fetch(uploadUrl, {
        method: 'POST',
        body: formData,
        headers: {
          // Don't set Content-Type, let browser handle it for FormData
        }
      });

      // Try to parse as JSON
      let data: any;
      try {
        data = await response.json();
      } catch (parseError) {
        console.error('JSON parse error:', parseError);
        console.error('Response status:', response.status);
        console.error('Response text:', await response.text());
        throw new Error(`Server error: Invalid response from server (${response.status})`);
      }

      if (!response.ok) {
        throw new Error(data.error || data.message || `Upload failed (${response.status})`);
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
      console.error('Upload error:', error);
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
          @keyframes pulse-ring {
            0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
            70% { box-shadow: 0 0 0 20px rgba(34, 197, 94, 0); }
            100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
          }
          .scale-pop {
            animation: scale-pop 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
          }
          .checkmark-draw {
            stroke-dasharray: 100;
            animation: checkmark-draw 0.5s ease-out 0.2s forwards;
            stroke-dashoffset: 100;
          }
          .pulse-ring {
            animation: pulse-ring 2s ease-out infinite;
          }
        `}</style>
        
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          {/* Animated success circle with checkmark */}
          <div className="flex justify-center mb-6">
            <div className="relative w-28 h-28">
              <div className="absolute inset-0 bg-green-100 rounded-full pulse-ring"></div>
              <div className="absolute inset-0 bg-green-100 rounded-full flex items-center justify-center scale-pop">
                <svg className="w-14 h-14" viewBox="0 0 100 100">
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
          </div>
          
          <h1 className="text-3xl font-bold text-green-600 mb-2">Success! 🎉</h1>
          <p className="text-gray-700 mb-4 text-lg">Your homework has been submitted!</p>
          
          {/* Details Section */}
          <div className="bg-green-50 rounded-lg p-4 mb-6 text-left space-y-3 border border-green-200">
            <div className="flex items-center gap-3">
              <i className="fas fa-book text-green-600 text-lg w-6"></i>
              <div>
                <p className="text-xs text-gray-600">Subject</p>
                <p className="text-sm font-bold text-gray-800">{subject || 'Homework'}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <i className="fas fa-image text-green-600 text-lg w-6"></i>
              <div>
                <p className="text-xs text-gray-600">Type</p>
                <p className="text-sm font-bold text-gray-800">Image</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <i className="fas fa-clock text-green-600 text-lg w-6"></i>
              <div>
                <p className="text-xs text-gray-600">Status</p>
                <p className="text-sm font-bold text-gray-800">Submitted Successfully</p>
              </div>
            </div>
          </div>

          {/* Message */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 text-left space-y-3">
            <p className="text-sm text-blue-900">
              <i className="fas fa-info-circle text-blue-600 mr-2"></i>
              <strong>What's Next?</strong><br/>
              A tutor will review your homework and send you feedback via WhatsApp shortly.
            </p>
            
            <div className="bg-white rounded-lg p-3 border border-blue-100">
              <p className="text-xs font-semibold text-gray-700 flex items-center gap-2 mb-2">
                <i className="fas fa-check-circle text-green-600"></i>
                Confirmation Message Sent
              </p>
              <p className="text-xs text-gray-600">
                ✓ A confirmation message has been sent to your WhatsApp with submission details.
              </p>
            </div>
          </div>

          {/* Auto-close countdown */}
          <style>{`
            @keyframes countdown-pulse {
              0%, 100% { opacity: 0.6; }
              50% { opacity: 1; }
            }
            .countdown-pulse {
              animation: countdown-pulse 1s ease-in-out infinite;
            }
          `}</style>
          <p className="text-sm text-gray-500 mb-4 countdown-pulse">
            This page will close in <strong>{countdown}</strong> second{countdown !== 1 ? 's' : ''}...
          </p>
          
          <button
            onClick={() => window.close()}
            className="w-full px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-bold transition flex items-center justify-center gap-2"
          >
            <i className="fas fa-times"></i> Close Now
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-blue-100 py-6 px-4 safe-area">
      {/* Mobile Safe Area */}
      <style>{`
        body {
          padding-top: max(12px, env(safe-area-inset-top));
          padding-bottom: max(12px, env(safe-area-inset-bottom));
        }
        .safe-area {
          padding-top: max(12px, env(safe-area-inset-top));
          padding-bottom: max(12px, env(safe-area-inset-bottom));
        }
        @keyframes pulse-icon {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.1); }
        }
        .pulse-icon {
          animation: pulse-icon 2s ease-in-out infinite;
        }
        @keyframes float-up {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-8px); }
        }
        .float-up {
          animation: float-up 2s ease-in-out infinite;
        }
        @keyframes spin-smooth {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .spin-smooth {
          animation: spin-smooth 1s linear infinite;
        }
      `}</style>

      <div className="max-w-lg mx-auto">
        {/* Header */}
        <div className="bg-white rounded-t-2xl shadow-lg p-6 text-center border-b-4 border-blue-600 mb-0">
          <i className="fas fa-camera text-5xl text-blue-600 mb-4 block pulse-icon"></i>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">📸 Upload Homework</h1>
          {subject && (
            <div className="inline-block bg-blue-100 rounded-full px-4 py-2">
              <div className="flex items-center justify-center gap-2 text-gray-700">
                <i className="fas fa-book text-blue-600"></i>
                <span><strong>{subject}</strong></span>
              </div>
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="bg-white p-6 shadow-lg space-y-6">
          {/* Instructions */}
          <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded">
            <h2 className="font-bold text-gray-900 mb-3 text-sm">📝 Instructions:</h2>
            <ul className="text-sm text-gray-700 space-y-2">
              <li className="flex items-start gap-2">
                <i className="fas fa-check text-green-600 mt-1 flex-shrink-0"></i>
                <span>Take a clear, readable photo of your homework</span>
              </li>
              <li className="flex items-start gap-2">
                <i className="fas fa-check text-green-600 mt-1 flex-shrink-0"></i>
                <span>Landscape orientation works best</span>
              </li>
              <li className="flex items-start gap-2">
                <i className="fas fa-check text-green-600 mt-1 flex-shrink-0"></i>
                <span>File size must be less than 10MB</span>
              </li>
              <li className="flex items-start gap-2">
                <i className="fas fa-check text-green-600 mt-1 flex-shrink-0"></i>
                <span>Supported: JPG, PNG, and other image formats</span>
              </li>
            </ul>
          </div>

          {/* File Input Area */}
          <div className="space-y-3">
            <label className="block">
              <div className="border-2 border-dashed border-blue-300 rounded-2xl p-8 text-center cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition duration-200 active:bg-blue-100">
                <input
                  type="file"
                  accept="image/*"
                  capture="environment"
                  onChange={handleFileSelect}
                  disabled={state.uploading}
                  className="hidden"
                />
                <i className="fas fa-cloud-upload-alt text-5xl text-blue-400 mb-3 block float-up"></i>
                <p className="text-gray-800 font-bold mb-1 text-lg">Tap to upload image</p>
                <p className="text-sm text-gray-600">or click to choose from gallery</p>
                <p className="text-xs text-gray-500 mt-3 flex items-center justify-center gap-1">
                  <i className="fas fa-image"></i> JPG, PNG • Max 10MB
                </p>
              </div>
            </label>
          </div>

          {/* File Preview */}
          {preview && (
            <div className="space-y-3 bg-gray-50 p-4 rounded-xl border-2 border-green-300">
              <p className="text-sm font-bold text-gray-800">📸 Preview:</p>
              <div className="bg-white rounded-lg p-2 flex items-center justify-center">
                <img
                  src={preview}
                  alt="Preview"
                  className="max-w-full max-h-80 rounded-lg object-contain"
                />
              </div>
              
              {/* File Details */}
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between p-3 bg-white rounded-lg">
                  <div className="flex items-center gap-2 flex-1">
                    <i className="fas fa-file-image text-blue-600"></i>
                    <div className="min-w-0 flex-1">
                      <p className="font-medium text-gray-800 truncate">{state.fileName}</p>
                      <p className="text-xs text-gray-600">{state.fileSize}</p>
                    </div>
                  </div>
                  <i className="fas fa-check-circle text-green-600 text-lg"></i>
                </div>
              </div>
            </div>
          )}

          {/* Error Message */}
          {state.error && (
            <div className="bg-red-50 border-l-4 border-red-600 p-4 rounded">
              <p className="text-sm text-red-700 font-medium">
                <i className="fas fa-exclamation-circle mr-2"></i>
                {state.error}
              </p>
            </div>
          )}

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={!selectedFile || state.uploading}
            className={`w-full py-4 rounded-xl font-bold text-white text-lg transition duration-200 relative overflow-hidden flex items-center justify-center gap-2 shadow-lg ${
              !selectedFile || state.uploading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 active:from-blue-800 active:to-blue-900'
            }`}
          >
            {/* Progress bar background */}
            {state.uploading && (
              <div
                className="absolute inset-0 bg-blue-800 transition-all duration-300"
                style={{ width: `${state.uploadProgress}%` }}
              />
            )}
            
            {/* Button content */}
            <div className="relative flex items-center justify-center w-full">
              {state.uploading ? (
                <>
                  <i className="fas fa-spinner mr-2 spin-smooth"></i>
                  <span>Uploading {state.uploadProgress}%</span>
                </>
              ) : (
                <>
                  <i className="fas fa-upload"></i>
                  <span>Upload Image</span>
                </>
              )}
            </div>
          </button>
        </div>

        {/* Footer Info */}
        <div className="bg-white rounded-b-2xl shadow-lg p-4 text-center border-t border-gray-100">
          <p className="text-xs text-gray-600 flex items-center justify-center gap-2">
            <i className="fas fa-shield-alt text-blue-600"></i>
            Your image is secure and only visible to your tutor
          </p>
        </div>
      </div>
    </div>
  );
}
