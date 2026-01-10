'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '../components/Layout';
import { apiClient } from '../lib/api-client';

interface SettingsData {
  whatsapp_api_key?: string;
  whatsapp_phone_number_id?: string;
  whatsapp_webhook_token?: string;
  whatsapp_business_account_id?: string;
  whatsapp_phone_number?: string;
  paystack_public_key?: string;
  paystack_secret_key?: string;
  paystack_webhook_secret?: string;
  database_url?: string;
  bot_name?: string;
  template_welcome?: string;
  template_status?: string;
  template_greeting?: string;
  template_help?: string;
  template_faq?: string;
  template_error?: string;
  [key: string]: string | undefined;
}

interface ValidationError {
  [key: string]: string;
}

export default function SettingsPage() {
  const router = useRouter();
  const [settings, setSettings] = useState<SettingsData>({});
  const [originalSettings, setOriginalSettings] = useState<SettingsData>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<'whatsapp' | 'paystack' | 'database' | 'bot' | 'templates'>('bot');
  const [validationErrors, setValidationErrors] = useState<ValidationError>({});
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [showTokens, setShowTokens] = useState(false);

  const isDirty = JSON.stringify(settings) !== JSON.stringify(originalSettings);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('admin_token');
        if (!token) {
          router.push('/login');
          return;
        }

        const response = await apiClient.getSettings();
        if (response.status === 'success') {
          const settingsData = response.data || {};
          setSettings(settingsData);
          setOriginalSettings(settingsData);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load settings');
      } finally {
        setLoading(false);
      }
    };

    fetchSettings();
  }, [router]);

  const validatePhoneNumber = (phone: string): boolean => {
    return /^\+\d{1,15}$/.test(phone);
  };

  const validateSettings = (): boolean => {
    const errors: ValidationError = {};

    if (activeTab === 'whatsapp') {
      if (settings.whatsapp_api_key && settings.whatsapp_api_key.length < 20) {
        errors.whatsapp_api_key = 'API key must be at least 20 characters';
      }
      if (settings.whatsapp_phone_number && !validatePhoneNumber(settings.whatsapp_phone_number)) {
        errors.whatsapp_phone_number = 'Phone number must be in format +1234567890';
      }
    }

    if (activeTab === 'paystack') {
      if (settings.paystack_public_key && settings.paystack_public_key.length < 20) {
        errors.paystack_public_key = 'Public key must be at least 20 characters';
      }
      if (settings.paystack_secret_key && settings.paystack_secret_key.length < 20) {
        errors.paystack_secret_key = 'Secret key must be at least 20 characters';
      }
    }

    if (activeTab === 'database') {
      if (settings.database_url && !settings.database_url.startsWith('mysql://') && !settings.database_url.startsWith('mysql+pymysql://')) {
        errors.database_url = 'Invalid database URL format';
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateSettings()) {
      setError('Please fix the validation errors below');
      return;
    }

    setError(null);
    setSuccess(null);
    setShowConfirmDialog(true);
  };

  const confirmSave = async () => {
    setShowConfirmDialog(false);
    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      const cleanedSettings = Object.fromEntries(
        Object.entries(settings).filter(([_, v]) => v !== undefined && v !== '')
      ) as Record<string, string>;
      
      console.log('Saving settings:', cleanedSettings);
      const response = await apiClient.updateSettings(cleanedSettings);
      console.log('Save response:', response);
      
      if (response.status === 'success') {
        setOriginalSettings(settings);
        setSuccess('Settings saved successfully ✅');
        setTimeout(() => setSuccess(null), 5000);
      } else {
        setError(response.message || 'Failed to save settings');
      }
    } catch (err: any) {
      console.error('Save error:', err);
      const errorMsg = err.response?.data?.message || err.message || 'Failed to save settings. Check network connection.';
      setError(`Error: ${errorMsg}`);
    } finally {
      setIsSaving(false);
    }
  };

  const maskToken = (token?: string): string => {
    if (!token) return '';
    if (token.length <= 10) return token;
    return token.substring(0, 5) + '*'.repeat(token.length - 10) + token.substring(token.length - 5);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setSettings((prev) => ({
      ...prev,
      [name]: value
    }));
    // Clear error for this field
    if (validationErrors[name]) {
      setValidationErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <i className="fas fa-spinner fa-spin text-4xl text-blue-600 mb-4"></i>
            <p className="text-gray-600">Loading settings...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-4xl">
        {/* Confirmation Dialog */}
        {showConfirmDialog && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-lg p-6 max-w-sm">
              <h3 className="text-lg font-bold text-gray-900 mb-2 flex items-center">
                <i className="fas fa-exclamation-triangle text-yellow-500 mr-2"></i>
                Confirm Changes
              </h3>
              <p className="text-gray-700 mb-6">Are you sure you want to save these settings? This will update your production configuration.</p>
              <div className="flex gap-3 justify-end">
                <button
                  onClick={() => setShowConfirmDialog(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmSave}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                  disabled={isSaving}
                >
                  {isSaving ? 'Saving...' : 'Save Settings'}
                </button>
              </div>
            </div>
          </div>
        )}

        {success && (
          <div className="bg-green-50 border-l-4 border-green-500 rounded-lg p-4 mb-6 flex items-start">
            <i className="fas fa-check-circle text-green-600 text-xl mr-3 mt-0.5"></i>
            <div>
              <h3 className="font-semibold text-green-900">Success</h3>
              <p className="text-sm text-green-700 mt-1">{success}</p>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-4 mb-6 flex items-start">
            <i className="fas fa-exclamation-circle text-red-600 text-xl mr-3 mt-0.5"></i>
            <div>
              <h3 className="font-semibold text-red-900">Error</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        )}

        {isDirty && (
          <div className="bg-yellow-50 border-l-4 border-yellow-400 rounded-lg p-4 mb-6 flex items-start">
            <i className="fas fa-info-circle text-yellow-600 text-xl mr-3 mt-0.5"></i>
            <div>
              <h3 className="font-semibold text-yellow-900">Unsaved Changes</h3>
              <p className="text-sm text-yellow-700 mt-1">You have unsaved changes. Click "Save Settings" to apply them.</p>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="flex border-b border-gray-200 flex-wrap">
            <button
              onClick={() => setActiveTab('bot')}
              className={`flex-1 min-w-max py-4 px-6 font-medium border-b-2 transition ${
                activeTab === 'bot'
                  ? 'border-purple-600 text-purple-600 bg-purple-50'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <i className="fas fa-robot mr-2"></i>Bot Config
            </button>
            <button
              onClick={() => setActiveTab('whatsapp')}
              className={`flex-1 min-w-max py-4 px-6 font-medium border-b-2 transition ${
                activeTab === 'whatsapp'
                  ? 'border-green-600 text-green-600 bg-green-50'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <i className="fas fa-comments mr-2"></i>WhatsApp
            </button>
            <button
              onClick={() => setActiveTab('paystack')}
              className={`flex-1 py-4 px-6 font-medium border-b-2 transition ${
                activeTab === 'paystack'
                  ? 'border-blue-600 text-blue-600 bg-blue-50'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <i className="fas fa-credit-card mr-2"></i>Paystack
            </button>
            <button
              onClick={() => setActiveTab('database')}
              className={`flex-1 py-4 px-6 font-medium border-b-2 transition ${
                activeTab === 'database'
                  ? 'border-orange-600 text-orange-600 bg-orange-50'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <i className="fas fa-database mr-2"></i>Database
            </button>
            <button
              onClick={() => setActiveTab('templates')}
              className={`flex-1 py-4 px-6 font-medium border-b-2 transition ${
                activeTab === 'templates'
                  ? 'border-cyan-600 text-cyan-600 bg-cyan-50'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <i className="fas fa-file-alt mr-2"></i>Templates
            </button>
          </div>
        </div>

        {/* Settings Form */}
        <form onSubmit={handleSave} className="space-y-6">

          {/* Bot Configuration Tab */}
          {activeTab === 'bot' && (
            <div className="bg-white rounded-lg shadow p-8 animate-in fade-in duration-300">
              <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center">
                <i className="fas fa-robot text-purple-600 mr-3"></i>Bot Configuration
              </h2>
              <p className="text-gray-600 mb-6">Configure how your chatbot appears and responds to users</p>

              <div className="space-y-6">
                {/* Bot Name */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-heading mr-2 text-purple-600"></i>Bot Name
                  </label>
                  <input
                    type="text"
                    name="bot_name"
                    value={settings.bot_name || ''}
                    onChange={handleInputChange}
                    placeholder="e.g., EduBot"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
                  />
                  <p className="text-xs text-gray-500 mt-2">The name used in all bot responses and greetings.</p>
                </div>

                {/* Welcome Template */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-star mr-2 text-yellow-500"></i>Welcome Template
                  </label>
                  <textarea
                    name="template_welcome"
                    value={settings.template_welcome || ''}
                    onChange={handleInputChange}
                    placeholder="Enter welcome message template..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition font-mono text-sm h-24"
                  />
                  <p className="text-xs text-gray-500 mt-2">Message shown when user first interacts. Use {'{'}name{'}'} for user name and {'{'}bot_name{'}'} for bot name.</p>
                </div>

                {/* Greeting Template */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-handshake mr-2 text-blue-500"></i>Greeting Template
                  </label>
                  <textarea
                    name="template_greeting"
                    value={settings.template_greeting || ''}
                    onChange={handleInputChange}
                    placeholder="Enter greeting template..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition font-mono text-sm h-20"
                  />
                  <p className="text-xs text-gray-500 mt-2">General greeting message for returning users.</p>
                </div>
              </div>
            </div>
          )}

          {/* WhatsApp Configuration Tab */}
          {activeTab === 'whatsapp' && (
            <div className="bg-white rounded-lg shadow p-8 animate-in fade-in duration-300">
              <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center">
                <i className="fas fa-comments text-green-600 mr-3"></i>WhatsApp Configuration
              </h2>
              <p className="text-gray-600 mb-6">Set up your WhatsApp Cloud API credentials</p>

              <div className="space-y-6">
                {/* API Key */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-key mr-2 text-green-600"></i>API Key
                  </label>
                  <div className="flex gap-2">
                    <input
                      type={showTokens ? 'text' : 'password'}
                      name="whatsapp_api_key"
                      value={settings.whatsapp_api_key || ''}
                      onChange={handleInputChange}
                      placeholder="Enter your WhatsApp API key..."
                      className={`flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition ${
                        validationErrors.whatsapp_api_key ? 'border-red-500' : 'border-gray-300'
                      }`}
                    />
                    <button
                      type="button"
                      onClick={() => setShowTokens(!showTokens)}
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
                    >
                      <i className={`fas ${showTokens ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                    </button>
                  </div>
                  {validationErrors.whatsapp_api_key && (
                    <p className="text-xs text-red-600 mt-2">{validationErrors.whatsapp_api_key}</p>
                  )}
                  <p className="text-xs text-gray-500 mt-2">Get this from WhatsApp Cloud API dashboard</p>
                </div>

                {/* Phone Number ID */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-phone mr-2 text-green-600"></i>Phone Number ID
                  </label>
                  <input
                    type="text"
                    name="whatsapp_phone_number_id"
                    value={settings.whatsapp_phone_number_id || ''}
                    onChange={handleInputChange}
                    placeholder="Enter phone number ID..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition"
                  />
                  <p className="text-xs text-gray-500 mt-2">Your WhatsApp business phone number ID</p>
                </div>

                {/* Business Account ID */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-briefcase mr-2 text-green-600"></i>Business Account ID
                  </label>
                  <input
                    type="text"
                    name="whatsapp_business_account_id"
                    value={settings.whatsapp_business_account_id || ''}
                    onChange={handleInputChange}
                    placeholder="Enter business account ID..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition"
                  />
                  <p className="text-xs text-gray-500 mt-2">Your WhatsApp Business Account ID</p>
                </div>

                {/* Phone Number */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-phone-alt mr-2 text-green-600"></i>Bot Phone Number
                  </label>
                  <input
                    type="tel"
                    name="whatsapp_phone_number"
                    value={settings.whatsapp_phone_number || ''}
                    onChange={handleInputChange}
                    placeholder="+234..."
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition ${
                      validationErrors.whatsapp_phone_number ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {validationErrors.whatsapp_phone_number && (
                    <p className="text-xs text-red-600 mt-2">{validationErrors.whatsapp_phone_number}</p>
                  )}
                  <p className="text-xs text-gray-500 mt-2">Phone number in format +1234567890</p>
                </div>

                {/* Webhook Token */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-shield-alt mr-2 text-green-600"></i>Webhook Token
                  </label>
                  <input
                    type={showTokens ? 'text' : 'password'}
                    name="whatsapp_webhook_token"
                    value={settings.whatsapp_webhook_token || ''}
                    onChange={handleInputChange}
                    placeholder="Enter webhook verification token..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition"
                  />
                  <p className="text-xs text-gray-500 mt-2">Used to verify webhook requests from WhatsApp</p>
                </div>
              </div>
            </div>
          )}

          {/* Paystack Configuration Tab */}
          {activeTab === 'paystack' && (
            <div className="bg-white rounded-lg shadow p-8 animate-in fade-in duration-300">
              <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center">
                <i className="fas fa-credit-card text-blue-600 mr-3"></i>Paystack Configuration
              </h2>
              <p className="text-gray-600 mb-6">Set up your Paystack payment gateway credentials</p>

              <div className="space-y-6">
                {/* Public Key */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-lock-open mr-2 text-blue-600"></i>Public Key
                  </label>
                  <div className="flex gap-2">
                    <input
                      type={showTokens ? 'text' : 'password'}
                      name="paystack_public_key"
                      value={settings.paystack_public_key || ''}
                      onChange={handleInputChange}
                      placeholder="pk_live_..."
                      className={`flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition ${
                        validationErrors.paystack_public_key ? 'border-red-500' : 'border-gray-300'
                      }`}
                    />
                    <button
                      type="button"
                      onClick={() => setShowTokens(!showTokens)}
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
                    >
                      <i className={`fas ${showTokens ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                    </button>
                  </div>
                  {validationErrors.paystack_public_key && (
                    <p className="text-xs text-red-600 mt-2">{validationErrors.paystack_public_key}</p>
                  )}
                  <p className="text-xs text-gray-500 mt-2">Found in your Paystack dashboard settings</p>
                </div>

                {/* Secret Key */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-lock mr-2 text-blue-600"></i>Secret Key
                  </label>
                  <div className="flex gap-2">
                    <input
                      type={showTokens ? 'text' : 'password'}
                      name="paystack_secret_key"
                      value={settings.paystack_secret_key || ''}
                      onChange={handleInputChange}
                      placeholder="sk_live_..."
                      className={`flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition ${
                        validationErrors.paystack_secret_key ? 'border-red-500' : 'border-gray-300'
                      }`}
                    />
                    <button
                      type="button"
                      onClick={() => setShowTokens(!showTokens)}
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
                    >
                      <i className={`fas ${showTokens ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                    </button>
                  </div>
                  {validationErrors.paystack_secret_key && (
                    <p className="text-xs text-red-600 mt-2">{validationErrors.paystack_secret_key}</p>
                  )}
                  <p className="text-xs text-gray-500 mt-2">Keep this secret! Used for server-side transactions</p>
                </div>

                {/* Webhook Secret */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-webhook mr-2 text-blue-600"></i>Webhook Secret
                  </label>
                  <input
                    type={showTokens ? 'text' : 'password'}
                    name="paystack_webhook_secret"
                    value={settings.paystack_webhook_secret || ''}
                    onChange={handleInputChange}
                    placeholder="Enter webhook secret..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  />
                  <p className="text-xs text-gray-500 mt-2">Verify webhook signatures from Paystack</p>
                </div>
              </div>
            </div>
          )}

          {/* Database Configuration Tab */}
          {activeTab === 'database' && (
            <div className="bg-white rounded-lg shadow p-8 animate-in fade-in duration-300">
              <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center">
                <i className="fas fa-database text-orange-600 mr-3"></i>Database Configuration
              </h2>
              <p className="text-gray-600 mb-6">Database connection settings</p>

              <div className="space-y-6">
                {/* Database URL */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-link mr-2 text-orange-600"></i>Database URL
                  </label>
                  <div className="flex gap-2">
                    <input
                      type={showTokens ? 'text' : 'password'}
                      name="database_url"
                      value={settings.database_url || ''}
                      onChange={handleInputChange}
                      placeholder="mysql+pymysql://user:pass@host/database"
                      className={`flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent transition font-mono text-sm ${
                        validationErrors.database_url ? 'border-red-500' : 'border-gray-300'
                      }`}
                    />
                    <button
                      type="button"
                      onClick={() => setShowTokens(!showTokens)}
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
                    >
                      <i className={`fas ${showTokens ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                    </button>
                  </div>
                  {validationErrors.database_url && (
                    <p className="text-xs text-red-600 mt-2">{validationErrors.database_url}</p>
                  )}
                  <p className="text-xs text-gray-500 mt-2">MySQL connection string. Format: mysql+pymysql://user:password@host:port/database</p>
                </div>
              </div>
            </div>
          )}

          {/* Templates Tab */}
          {activeTab === 'templates' && (
            <div className="bg-white rounded-lg shadow p-8 animate-in fade-in duration-300">
              <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center">
                <i className="fas fa-file-alt text-cyan-600 mr-3"></i>Message Templates
              </h2>
              <p className="text-gray-600 mb-6">Pre-configured response templates</p>

              <div className="space-y-6">
                {/* Help Template */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-question-circle mr-2 text-cyan-600"></i>Help Template
                  </label>
                  <textarea
                    name="template_help"
                    value={settings.template_help || ''}
                    onChange={handleInputChange}
                    placeholder="Enter help template..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition font-mono text-sm h-24"
                  />
                  <p className="text-xs text-gray-500 mt-2">Help and features information</p>
                </div>

                {/* FAQ Template */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-lightbulb mr-2 text-cyan-600"></i>FAQ Template
                  </label>
                  <textarea
                    name="template_faq"
                    value={settings.template_faq || ''}
                    onChange={handleInputChange}
                    placeholder="Enter FAQ template..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition font-mono text-sm h-20"
                  />
                  <p className="text-xs text-gray-500 mt-2">Frequently asked questions template</p>
                </div>

                {/* Status Template */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-info-circle mr-2 text-cyan-600"></i>Status Template
                  </label>
                  <textarea
                    name="template_status"
                    value={settings.template_status || ''}
                    onChange={handleInputChange}
                    placeholder="Enter status template..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition font-mono text-sm h-20"
                  />
                  <p className="text-xs text-gray-500 mt-2">User status and registration status template</p>
                </div>

                {/* Error Template */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-exclamation-circle mr-2 text-cyan-600"></i>Error Template
                  </label>
                  <textarea
                    name="template_error"
                    value={settings.template_error || ''}
                    onChange={handleInputChange}
                    placeholder="Enter error template..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition font-mono text-sm h-20"
                  />
                  <p className="text-xs text-gray-500 mt-2">Error message template</p>
                </div>
              </div>
            </div>
          )}

          {/* Save Button */}
          <div className="flex gap-3 justify-end sticky bottom-6">
            <button
              type="button"
              onClick={() => {
                setSettings(originalSettings);
                setValidationErrors({});
              }}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-semibold disabled:opacity-50"
              disabled={!isDirty}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold disabled:opacity-50 flex items-center gap-2"
              disabled={!isDirty || isSaving}
            >
              <i className="fas fa-save"></i>
              {isSaving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </form>
      </div>
    </Layout>
  );
}
