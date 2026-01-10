'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '../components/Layout';
import MessageManagementTab from '../components/MessageManagementTab';
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
  const [isTesting, setIsTesting] = useState(false);
  const [activeTab, setActiveTab] = useState<'whatsapp' | 'paystack' | 'database' | 'bot' | 'messages'>('bot');
  const [testPhoneNumber, setTestPhoneNumber] = useState('+2348109508833');
  const [isTestingSendToNumber, setIsTestingSendToNumber] = useState(false);
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

  // Validation functions
  const validatePhoneNumber = (phone: string): boolean => {
    if (!phone) return true;
    const phoneRegex = /^\+?[1-9]\d{1,14}$/;
    return phoneRegex.test(phone.replace(/\D/g, ''));
  };

  const validateTokenFormat = (token: string, prefix: string): boolean => {
    if (!token) return true;
    return token.length > 10 && (prefix === '' || token.startsWith(prefix));
  };

  const validateSettings = (): boolean => {
    const errors: ValidationError = {};

    if (activeTab === 'whatsapp') {
      if (settings.whatsapp_phone_number && !validatePhoneNumber(settings.whatsapp_phone_number)) {
        errors.whatsapp_phone_number = 'Invalid phone number format';
      }
      if (settings.whatsapp_api_key && !validateTokenFormat(settings.whatsapp_api_key, 'EAA')) {
        errors.whatsapp_api_key = 'Invalid API token format (should start with EAA)';
      }
      if (settings.whatsapp_phone_number_id && !/^\d+$/.test(settings.whatsapp_phone_number_id)) {
        errors.whatsapp_phone_number_id = 'Phone Number ID should be numeric';
      }
      if (settings.whatsapp_business_account_id && !/^\d+$/.test(settings.whatsapp_business_account_id)) {
        errors.whatsapp_business_account_id = 'Business Account ID should be numeric';
      }
    }

    if (activeTab === 'paystack') {
      if (settings.paystack_public_key && !validateTokenFormat(settings.paystack_public_key, 'pk_')) {
        errors.paystack_public_key = 'Invalid public key format (should start with pk_)';
      }
      if (settings.paystack_secret_key && !validateTokenFormat(settings.paystack_secret_key, 'sk_')) {
        errors.paystack_secret_key = 'Invalid secret key format (should start with sk_)';
      }
    }

    if (activeTab === 'database') {
      if (settings.database_url && !settings.database_url.includes('://')) {
        errors.database_url = 'Invalid database URL format';
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSettingChange = (key: string, value: string) => {
    // For sensitive tokens, trim whitespace automatically
    let trimmedValue = value;
    if (key.includes('key') || key.includes('token') || key.includes('secret')) {
      trimmedValue = value.trim();
    }
    
    setSettings((prev) => ({
      ...prev,
      [key]: trimmedValue,
    }));
    // Clear validation error for this field when user starts editing
    if (validationErrors[key]) {
      setValidationErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[key];
        return newErrors;
      });
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateSettings()) {
      setError('Please fix the validation errors below');
      return;
    }

    setShowConfirmDialog(true);
  };

  const confirmSave = async () => {
    setShowConfirmDialog(false);
    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      const cleanedSettings = Object.fromEntries(
        Object.entries(settings).filter(([_, v]) => v !== undefined)
      ) as Record<string, string>;
      
      console.log('Saving settings:', cleanedSettings);
      const response = await apiClient.updateSettings(cleanedSettings);
      console.log('Save response:', response);
      
      if (response.status === 'success') {
        setOriginalSettings(settings);
        setSuccess('Settings saved successfully');
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(response.message || 'Failed to save settings');
      }
    } catch (err: any) {
      console.error('Save error:', err);
      const errorMsg = err.response?.data?.message || err.message || 'Failed to save settings. Check network connection.';
      setError(errorMsg);
    } finally {
      setIsSaving(false);
    }
  };

  const handleSendTestMessage = async () => {
    if (!testPhoneNumber || !validatePhoneNumber(testPhoneNumber)) {
      setError('Invalid phone number format');
      return;
    }

    setError(null);
    setSuccess(null);
    setIsTestingSendToNumber(true);

    try {
      const response = await apiClient.testWhatsAppMessage(testPhoneNumber, 'Test message from WhatsApp chatbot admin settings. If you receive this, your configuration is working correctly!');

      if (response && response.status === 'success') {
        setSuccess(`Test message sent successfully to ${testPhoneNumber}`);
        setTimeout(() => setSuccess(null), 5000);
      } else {
        setError(response?.message || 'Failed to send test message');
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || err.message || 'Failed to send test message';
      setError(errorMsg);
    } finally {
      setIsTestingSendToNumber(false);
    }
  };

  const maskToken = (token?: string): string => {
    if (!token) return '';
    if (token.length <= 10) return token;
    return token.substring(0, 5) + '*'.repeat(token.length - 10) + token.substring(token.length - 5);
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
              onClick={() => setActiveTab('messages')}
              className={`flex-1 py-4 px-6 font-medium border-b-2 transition ${
                activeTab === 'messages'
                  ? 'border-pink-600 text-pink-600 bg-pink-50'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <i className="fas fa-message mr-2"></i>Messages
            </button>
          </div>
        </div>

        {/* Messages Management Tab - Outside Form */}
        {activeTab === 'messages' && (
          <MessageManagementTab />
        )}

        {/* Settings Form */}
        {activeTab !== 'messages' && (
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
                    value={settings.bot_name || ''}
                    onChange={(e) => handleSettingChange('bot_name', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition"
                    placeholder="EduBot"
                  />
                  <p className="text-xs text-gray-500 mt-2">The name used in all bot responses and greetings. This will appear in welcome messages, status updates, and all automated responses.</p>
                  
                  {/* Preview */}
                  <div className="mt-4 p-4 bg-purple-50 border border-purple-200 rounded-lg">
                    <p className="text-xs font-semibold text-purple-900 mb-2">Preview:</p>
                    <div className="bg-white rounded p-3 border border-purple-100">
                      <p className="text-sm text-gray-700">
                        👋 John, welcome to <span className="font-semibold text-purple-600">{settings.bot_name || 'EduBot'}</span>!
                      </p>
                    </div>
                  </div>
                </div>

                {/* Save Button for Bot Config */}
                <div className="flex gap-3 pt-4 border-t border-gray-200">
                  <button
                    type="submit"
                    disabled={!isDirty || isSaving}
                    className={`px-6 py-2 rounded-lg font-medium transition flex items-center gap-2 ${
                      !isDirty || isSaving
                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        : 'bg-purple-600 text-white hover:bg-purple-700'
                    }`}
                  >
                    <i className={`fas ${isSaving ? 'fa-spinner fa-spin' : 'fa-save'}`}></i>
                    {isSaving ? 'Saving...' : 'Save Settings'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* WhatsApp Configuration Tab */}
          {activeTab === 'whatsapp' && (
            <div className="bg-white rounded-lg shadow p-8 animate-in fade-in duration-300">
              <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center">
                <i className="fas fa-comments text-green-600 mr-3"></i>WhatsApp Cloud API
              </h2>
              <p className="text-gray-600 mb-6">Configure your WhatsApp Business Account credentials for the chatbot</p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Business Account ID */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-id-card mr-2 text-green-600"></i>Business Account ID
                  </label>
                  <input
                    type="text"
                    value={settings.whatsapp_business_account_id || ''}
                    onChange={(e) => handleSettingChange('whatsapp_business_account_id', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500 transition"
                    placeholder="1516305056071819"
                  />
                  <p className="text-xs text-gray-500 mt-1">Your WhatsApp Business Account ID</p>
                </div>

                {/* Phone Number ID */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-phone mr-2 text-green-600"></i>Phone Number ID
                  </label>
                  <input
                    type="text"
                    value={settings.whatsapp_phone_number_id || ''}
                    onChange={(e) => handleSettingChange('whatsapp_phone_number_id', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500 transition"
                    placeholder="797467203457022"
                  />
                  <p className="text-xs text-gray-500 mt-1">Your WhatsApp Phone Number ID</p>
                </div>

                {/* Phone Number */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-mobile-alt mr-2 text-green-600"></i>Phone Number
                  </label>
                  <input
                    type="tel"
                    value={settings.whatsapp_phone_number || ''}
                    onChange={(e) => handleSettingChange('whatsapp_phone_number', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500 transition"
                    placeholder="+15551610271"
                  />
                  <p className="text-xs text-gray-500 mt-1">Your WhatsApp phone number with country code</p>
                </div>

                {/* API Key */}
                <div className="md:col-span-2">
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-key mr-2 text-green-600"></i>API Access Token
                  </label>
                  <div className="flex items-center gap-2">
                    <input
                      type={showTokens ? "text" : "password"}
                      value={settings.whatsapp_api_key || ''}
                      onChange={(e) => handleSettingChange('whatsapp_api_key', e.target.value)}
                      className={`flex-1 px-4 py-3 border rounded-lg focus:outline-none focus:ring-1 transition font-mono text-sm ${
                        validationErrors.whatsapp_api_key
                          ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
                          : 'border-gray-300 focus:border-green-500 focus:ring-green-500'
                      }`}
                      placeholder="EAA..."
                    />
                    <button
                      type="button"
                      onClick={() => setShowTokens(!showTokens)}
                      className="px-3 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition text-gray-600"
                      title={showTokens ? "Hide tokens" : "Show tokens"}
                    >
                      <i className={`fas ${showTokens ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                    </button>
                  </div>
                  {validationErrors.whatsapp_api_key ? (
                    <p className="text-xs text-red-600 mt-1 flex items-center">
                      <i className="fas fa-exclamation-circle mr-1"></i>
                      {validationErrors.whatsapp_api_key}
                    </p>
                  ) : (
                    <p className="text-xs text-gray-500 mt-1">Your WhatsApp Cloud API access token (starts with EAA...)</p>
                  )}
                  <p className="text-xs text-yellow-600 mt-2 font-semibold">⚠️ Make sure the token is valid and not expired</p>
                </div>

                {/* Webhook Token */}
                <div className="md:col-span-2">
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-shield-alt mr-2 text-green-600"></i>Webhook Verification Token
                  </label>
                  <div className="flex items-center gap-2">
                    <input
                      type={showTokens ? "text" : "password"}
                      value={settings.whatsapp_webhook_token || ''}
                      onChange={(e) => handleSettingChange('whatsapp_webhook_token', e.target.value)}
                      className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500 transition font-mono text-sm"
                      placeholder="your_webhook_token_here"
                    />
                    <button
                      type="button"
                      onClick={() => setShowTokens(!showTokens)}
                      className="px-3 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition text-gray-600"
                      title={showTokens ? "Hide tokens" : "Show tokens"}
                    >
                      <i className={`fas ${showTokens ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Secret token for verifying WhatsApp webhooks</p>
                </div>
              </div>

              {/* WhatsApp Info Box */}
              <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-sm text-green-800">
                  <i className="fas fa-info-circle mr-2"></i>
                  <strong>Note:</strong> Get these credentials from your WhatsApp Business Account Settings in the Meta Business Suite
                </p>
              </div>

              {/* Send Test Message to Custom Number Section */}
              <div className="mt-8 border-t pt-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <i className="fas fa-phone text-green-600 mr-2"></i>
                  Send Test WhatsApp to Specific Number
                </h3>
                
                <div className="flex gap-3">
                  <div className="flex-1">
                    <input
                      type="tel"
                      value={testPhoneNumber}
                      onChange={(e) => setTestPhoneNumber(e.target.value)}
                      className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-1 transition ${
                        testPhoneNumber && !validatePhoneNumber(testPhoneNumber)
                          ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
                          : 'border-gray-300 focus:border-green-500 focus:ring-green-500'
                      }`}
                      placeholder="+2348109508833"
                    />
                    {testPhoneNumber && !validatePhoneNumber(testPhoneNumber) ? (
                      <p className="text-xs text-red-600 mt-1 flex items-center">
                        <i className="fas fa-exclamation-circle mr-1"></i>
                        Invalid phone number format. Use format: +1234567890
                      </p>
                    ) : (
                      <p className="text-xs text-gray-500 mt-1">Phone number with country code (e.g., +2348109508833)</p>
                    )}
                  </div>
                </div>

                <button
                  type="button"
                  onClick={handleSendTestMessage}
                  disabled={isTestingSendToNumber || !testPhoneNumber || !validatePhoneNumber(testPhoneNumber)}
                  className="w-full mt-3 px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium flex items-center justify-center"
                >
                  {isTestingSendToNumber ? (
                    <>
                      <i className="fas fa-spinner fa-spin mr-2"></i>
                      Sending...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-paper-plane mr-2"></i>
                      Send Test Message
                    </>
                  )}
                </button>
                <p className="text-xs text-gray-500 mt-2 text-center">
                  Sends a test message to the specified number
                </p>
              </div>
            </div>
          )}

          {/* Paystack Configuration Tab */}
          {activeTab === 'paystack' && (
            <div className="bg-white rounded-lg shadow p-8 animate-in fade-in duration-300">
              <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center">
                <i className="fas fa-credit-card text-blue-600 mr-3"></i>Paystack Payment Gateway
              </h2>
              <p className="text-gray-600 mb-6">Configure your Paystack account for payment processing</p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Public Key */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-lock-open mr-2 text-blue-600"></i>Public Key
                  </label>
                  <div className="flex items-center gap-2">
                    <input
                      type={showTokens ? "text" : "password"}
                      value={settings.paystack_public_key || ''}
                      onChange={(e) => handleSettingChange('paystack_public_key', e.target.value)}
                      className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition font-mono text-sm"
                      placeholder="pk_live_..."
                    />
                    <button
                      type="button"
                      onClick={() => setShowTokens(!showTokens)}
                      className="px-3 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition text-gray-600"
                      title={showTokens ? "Hide tokens" : "Show tokens"}
                    >
                      <i className={`fas ${showTokens ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Public key from your Paystack account</p>
                </div>

                {/* Secret Key */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-lock mr-2 text-blue-600"></i>Secret Key
                  </label>
                  <div className="flex items-center gap-2">
                    <input
                      type={showTokens ? "text" : "password"}
                      value={settings.paystack_secret_key || ''}
                      onChange={(e) => handleSettingChange('paystack_secret_key', e.target.value)}
                      className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition font-mono text-sm"
                      placeholder="sk_live_..."
                    />
                    <button
                      type="button"
                      onClick={() => setShowTokens(!showTokens)}
                      className="px-3 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition text-gray-600"
                      title={showTokens ? "Hide tokens" : "Show tokens"}
                    >
                      <i className={`fas ${showTokens ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Secret key from your Paystack account</p>
                </div>

                {/* Webhook Secret */}
                <div className="md:col-span-2">
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <i className="fas fa-shield-alt mr-2 text-blue-600"></i>Webhook Secret
                  </label>
                  <div className="flex items-center gap-2">
                    <input
                      type={showTokens ? "text" : "password"}
                      value={settings.paystack_webhook_secret || ''}
                      onChange={(e) => handleSettingChange('paystack_webhook_secret', e.target.value)}
                      className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition font-mono text-sm"
                      placeholder="sk_test_..."
                    />
                    <button
                      type="button"
                      onClick={() => setShowTokens(!showTokens)}
                      className="px-3 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition text-gray-600"
                      title={showTokens ? "Hide tokens" : "Show tokens"}
                    >
                      <i className={`fas ${showTokens ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Webhook secret for verifying Paystack events</p>
                </div>
              </div>

              {/* Paystack Info Box */}
              <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-800">
                  <i className="fas fa-info-circle mr-2"></i>
                  <strong>Note:</strong> Find these keys in your Paystack Dashboard under Settings &gt; API Keys &amp; Webhooks
                </p>
              </div>
            </div>
          )}

          {/* Database Configuration Tab */}
          {activeTab === 'database' && (
            <div className="bg-white rounded-lg shadow p-8 animate-in fade-in duration-300">
              <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center">
                <i className="fas fa-database text-orange-600 mr-3"></i>Database Connection
              </h2>
              <p className="text-gray-600 mb-6">Configure your database connection settings</p>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  <i className="fas fa-server mr-2 text-orange-600"></i>Database URL
                </label>
                <textarea
                  value={settings.database_url || ''}
                  onChange={(e) => handleSettingChange('database_url', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500 transition font-mono text-sm h-24"
                  placeholder="mysql+pymysql://user:password@localhost:3306/database_name"
                />
                <p className="text-xs text-gray-500 mt-1">Your database connection string</p>
              </div>

              {/* Database Info Box */}
              <div className="mt-6 bg-orange-50 border border-orange-200 rounded-lg p-4">
                <p className="text-sm text-orange-800 mb-3">
                  <i className="fas fa-info-circle mr-2"></i>
                  <strong>Connection Format:</strong>
                </p>
                <code className="block bg-white border border-orange-100 rounded p-3 text-xs font-mono text-orange-900 overflow-x-auto">
                  mysql+pymysql://username:password@host:port/database
                </code>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="bg-white rounded-lg shadow p-6 flex gap-4 justify-end">
            <button
              type="button"
              onClick={() => {
                setSettings(originalSettings);
                setValidationErrors({});
              }}
              disabled={!isDirty || isSaving}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium flex items-center"
            >
              <i className="fas fa-undo mr-2"></i>
              Reset
            </button>
            <button
              type="submit"
              disabled={isSaving || !isDirty || Object.keys(validationErrors).length > 0}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium flex items-center"
            >
              {isSaving ? (
                <>
                  <i className="fas fa-spinner fa-spin mr-2"></i>
                  Saving...
                </>
              ) : (
                <>
                  <i className="fas fa-save mr-2"></i>
                  Save Settings
                </>
              )}
            </button>
          </div>
        </form>
        )}
      </div>
    </Layout>
  );
}
