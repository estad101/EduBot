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

interface BotTemplate {
  id: number;
  template_name: string;
  template_content: string;
  variables: string[];
  menu_items?: string[];
  is_default: boolean;
}

interface EditingTemplate extends BotTemplate {
  // For tracking edits
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
  const [templates, setTemplates] = useState<BotTemplate[]>([]);
  const [loadingTemplates, setLoadingTemplates] = useState(false);
  const [editingTemplateId, setEditingTemplateId] = useState<number | null>(null);
  const [editingTemplate, setEditingTemplate] = useState<EditingTemplate | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [templateMenuId, setTemplateMenuId] = useState<number | null>(null);

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

  // Fetch templates from bot_message_templates table
  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        setLoadingTemplates(true);
        const response = await apiClient.getTemplates();
        
        if (response.status === 'success' && response.data?.templates) {
          setTemplates(response.data.templates);
        }
      } catch (err: any) {
        console.error('Failed to fetch templates:', err.message);
      } finally {
        setLoadingTemplates(false);
      }
    };

    fetchTemplates();
  }, []);

  const openEditModal = (template: BotTemplate) => {
    setEditingTemplate({ ...template });
    setEditingTemplateId(template.id);
    setShowEditModal(true);
    setTemplateMenuId(null);
  };

  const closeEditModal = () => {
    setShowEditModal(false);
    setEditingTemplate(null);
    setEditingTemplateId(null);
  };

  const saveTemplateChanges = async () => {
    if (!editingTemplate) return;

    // Validate template
    if (!editingTemplate.template_name.trim()) {
      setError('Template name is required');
      return;
    }
    if (!editingTemplate.template_content.trim()) {
      setError('Template content is required');
      return;
    }
    
    try {
      setIsSaving(true);
      setError(null);
      const response = await apiClient.updateTemplate(editingTemplate.id, {
        template_name: editingTemplate.template_name.trim(),
        template_content: editingTemplate.template_content.trim(),
        variables: editingTemplate.variables || [],
        menu_items: editingTemplate.menu_items || [],
        is_default: editingTemplate.is_default
      });
      
      if (response.status === 'success') {
        setSuccess('Template updated successfully!');
        setTemplates(templates.map(t => t.id === editingTemplate.id ? editingTemplate : t));
        closeEditModal();
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(response.message || 'Failed to update template');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to update template');
    } finally {
      setIsSaving(false);
    }
  };

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
    
    // Don't save settings if templates tab is active
    if (activeTab === 'templates') {
      return;
    }
    
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
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-8 px-4 md:px-8">
        <div className="max-w-6xl mx-auto">
          
          {/* Header Section */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2 flex items-center gap-3">
              <i className="fas fa-cog text-blue-600 text-3xl"></i>
              Admin Settings
            </h1>
            <p className="text-gray-600 text-lg">Manage your bot configuration, integrations, and templates</p>
          </div>

          {/* Alerts Section */}
          <div className="space-y-4 mb-8">
            {success && (
              <div className="bg-green-50 border-l-4 border-green-500 rounded-lg p-4 flex items-start gap-4 shadow-sm">
                <i className="fas fa-check-circle text-green-600 text-2xl flex-shrink-0 mt-1"></i>
                <div className="flex-1">
                  <h3 className="font-bold text-green-900 text-lg">Success!</h3>
                  <p className="text-green-700 mt-1">{success}</p>
                </div>
                <button onClick={() => setSuccess(null)} className="text-green-600 hover:text-green-800">
                  <i className="fas fa-times text-xl"></i>
                </button>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-4 flex items-start gap-4 shadow-sm">
                <i className="fas fa-exclamation-circle text-red-600 text-2xl flex-shrink-0 mt-1"></i>
                <div className="flex-1">
                  <h3 className="font-bold text-red-900 text-lg">Error</h3>
                  <p className="text-red-700 mt-1">{error}</p>
                </div>
                <button onClick={() => setError(null)} className="text-red-600 hover:text-red-800">
                  <i className="fas fa-times text-xl"></i>
                </button>
              </div>
            )}

            {isDirty && (
              <div className="bg-amber-50 border-l-4 border-amber-500 rounded-lg p-4 flex items-start gap-4 shadow-sm">
                <i className="fas fa-exclamation-triangle text-amber-600 text-2xl flex-shrink-0 mt-1"></i>
                <div className="flex-1">
                  <h3 className="font-bold text-amber-900 text-lg">Unsaved Changes</h3>
                  <p className="text-amber-700 mt-1">You have made changes that haven't been saved yet.</p>
                </div>
              </div>
            )}
          </div>

          {/* Confirmation Dialog */}
          {showConfirmDialog && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
              <div className="bg-white rounded-xl shadow-2xl max-w-sm w-full animate-in fade-in duration-200">
                <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4 rounded-t-xl">
                  <h3 className="text-xl font-bold text-white flex items-center gap-2">
                    <i className="fas fa-shield-alt"></i>
                    Confirm Changes
                  </h3>
                </div>
                <div className="p-6">
                  <p className="text-gray-700 text-base leading-relaxed">
                    You're about to save changes to your production configuration. Make sure everything is correct before proceeding.
                  </p>
                </div>
                <div className="bg-gray-50 px-6 py-4 rounded-b-xl flex gap-3 justify-end border-t">
                  <button
                    onClick={() => setShowConfirmDialog(false)}
                    className="px-5 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={confirmSave}
                    className="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium flex items-center gap-2 disabled:opacity-50"
                    disabled={isSaving}
                  >
                    {isSaving && <i className="fas fa-spinner fa-spin"></i>}
                    {isSaving ? 'Saving...' : 'Save Settings'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Tab Navigation - Horizontal Scrollable */}
          <div className="bg-white rounded-xl shadow-sm mb-8 overflow-hidden">
            <div className="overflow-x-auto">
              <div className="flex border-b border-gray-200 min-w-max md:min-w-full">
                <TabButton
                  icon="fas fa-cog"
                  label="Bot Config"
                  active={activeTab === 'bot'}
                  onClick={() => setActiveTab('bot')}
                  color="purple"
                />
                <TabButton
                  icon="fas fa-comments"
                  label="WhatsApp"
                  active={activeTab === 'whatsapp'}
                  onClick={() => setActiveTab('whatsapp')}
                  color="green"
                />
                <TabButton
                  icon="fas fa-credit-card"
                  label="Paystack"
                  active={activeTab === 'paystack'}
                  onClick={() => setActiveTab('paystack')}
                  color="blue"
                />
                <TabButton
                  icon="fas fa-database"
                  label="Database"
                  active={activeTab === 'database'}
                  onClick={() => setActiveTab('database')}
                  color="orange"
                />
                <TabButton
                  icon="fas fa-file-alt"
                  label="Templates"
                  active={activeTab === 'templates'}
                  onClick={() => setActiveTab('templates')}
                  color="cyan"
                />
              </div>
            </div>
          </div>

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

        {/* Settings Form */}
        <form onSubmit={handleSave} className="space-y-6">

          {/* Bot Configuration Tab */}
          {activeTab === 'bot' && (
            <div className="bg-white rounded-xl shadow-sm p-8 md:p-10 animate-in fade-in duration-300">
              <div className="mb-8 pb-6 border-b border-gray-200">
                <h2 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                    <i className="fas fa-cog text-purple-600 text-xl"></i>
                  </div>
                  Bot Configuration
                </h2>
                <p className="text-gray-600 text-lg">Configure how your chatbot appears and responds to users</p>
              </div>

              <div className="space-y-6">
                {/* Bot Name */}
                <div className="p-5 bg-gradient-to-br from-purple-50 to-transparent rounded-lg border border-purple-100">
                  <label className="block text-sm font-bold text-gray-800 mb-3 uppercase tracking-wide">
                    <i className="fas fa-heading mr-2 text-purple-600"></i>Bot Name
                  </label>
                  <input
                    type="text"
                    name="bot_name"
                    value={settings.bot_name || ''}
                    onChange={handleInputChange}
                    placeholder="e.g., EduBot"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition text-base"
                  />
                  <p className="text-xs text-gray-600 mt-2 flex items-center gap-1">
                    <i className="fas fa-info-circle"></i>
                    The name used in all bot responses and greetings
                  </p>
                </div>

                {/* Welcome Template */}
                <div className="p-5 bg-gradient-to-br from-yellow-50 to-transparent rounded-lg border border-yellow-100">
                  <label className="block text-sm font-bold text-gray-800 mb-3 uppercase tracking-wide">
                    <i className="fas fa-star mr-2 text-yellow-500"></i>Welcome Template
                  </label>
                  <textarea
                    name="template_welcome"
                    value={settings.template_welcome || ''}
                    onChange={handleInputChange}
                    placeholder="Enter welcome message template..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent transition font-mono text-sm h-28"
                  />
                  <p className="text-xs text-gray-600 mt-2 flex items-center gap-1">
                    <i className="fas fa-info-circle"></i>
                    Message shown when user first interacts. Use {'{'}name{'}'} for user name and {'{'}bot_name{'}'} for bot name
                  </p>
                </div>

                {/* Greeting Template */}
                <div className="p-5 bg-gradient-to-br from-blue-50 to-transparent rounded-lg border border-blue-100">
                  <label className="block text-sm font-bold text-gray-800 mb-3 uppercase tracking-wide">
                    <i className="fas fa-handshake mr-2 text-blue-500"></i>Greeting Template
                  </label>
                  <textarea
                    name="template_greeting"
                    value={settings.template_greeting || ''}
                    onChange={handleInputChange}
                    placeholder="Enter greeting template..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition font-mono text-sm h-24"
                  />
                  <p className="text-xs text-gray-600 mt-2 flex items-center gap-1">
                    <i className="fas fa-info-circle"></i>
                    General greeting message for returning users
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* WhatsApp Configuration Tab */}
          {activeTab === 'whatsapp' && (
            <div className="bg-white rounded-xl shadow-sm p-8 md:p-10 animate-in fade-in duration-300">
              <div className="mb-8 pb-6 border-b border-gray-200">
                <h2 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <i className="fas fa-comments text-green-600 text-xl"></i>
                  </div>
                  WhatsApp Configuration
                </h2>
                <p className="text-gray-600 text-lg">Set up your WhatsApp Cloud API credentials for messaging</p>
              </div>

              <div className="space-y-6">
                {/* API Key */}
                <div className="p-5 bg-gradient-to-br from-green-50 to-transparent rounded-lg border border-green-100">
                  <label className="block text-sm font-bold text-gray-800 mb-3 uppercase tracking-wide">
                    <i className="fas fa-key mr-2 text-green-600"></i>API Key / Access Token
                  </label>
                  <div className="flex gap-2">
                    <input
                      type={showTokens ? 'text' : 'password'}
                      name="whatsapp_api_key"
                      value={settings.whatsapp_api_key || ''}
                      onChange={handleInputChange}
                      placeholder="Enter your WhatsApp API key..."
                      className={`flex-1 px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition text-base ${
                        validationErrors.whatsapp_api_key ? 'border-red-500 bg-red-50' : 'border-gray-300'
                      }`}
                    />
                    <button
                      type="button"
                      onClick={() => setShowTokens(!showTokens)}
                      className="px-4 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition font-semibold"
                    >
                      <i className={`fas ${showTokens ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                    </button>
                  </div>
                  {validationErrors.whatsapp_api_key && (
                    <p className="text-xs text-red-600 mt-2 flex items-center gap-1">
                      <i className="fas fa-exclamation-circle"></i>
                      {validationErrors.whatsapp_api_key}
                    </p>
                  )}
                  <p className="text-xs text-gray-600 mt-2 flex items-center gap-1">
                    <i className="fas fa-info-circle"></i>
                    Get this from WhatsApp Cloud API dashboard
                  </p>
                </div>

                {/* Phone Number ID */}
                <div className="p-5 bg-gradient-to-br from-green-50 to-transparent rounded-lg border border-green-100">
                  <label className="block text-sm font-bold text-gray-800 mb-3 uppercase tracking-wide">
                    <i className="fas fa-phone mr-2 text-green-600"></i>Phone Number ID
                  </label>
                  <input
                    type="text"
                    name="whatsapp_phone_number_id"
                    value={settings.whatsapp_phone_number_id || ''}
                    onChange={handleInputChange}
                    placeholder="Enter phone number ID..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition text-base"
                  />
                  <p className="text-xs text-gray-600 mt-2 flex items-center gap-1">
                    <i className="fas fa-info-circle"></i>
                    Your WhatsApp business phone number ID
                  </p>
                </div>

                {/* Business Account ID */}
                <div className="p-6 bg-gradient-to-br from-green-50 to-transparent rounded-xl border border-green-100">
                  <label className="block text-sm font-bold text-gray-800 mb-3 uppercase tracking-wide">
                    <i className="fas fa-briefcase mr-2 text-green-600"></i>Business Account ID
                  </label>
                  <input
                    type="text"
                    name="whatsapp_business_account_id"
                    value={settings.whatsapp_business_account_id || ''}
                    onChange={handleInputChange}
                    placeholder="Enter business account ID..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition"
                  />
                  <p className="text-xs text-gray-600 mt-3 flex items-center gap-1">
                    <i className="fas fa-info-circle"></i>Your WhatsApp Business Account ID
                  </p>
                </div>

                {/* Phone Number */}
                <div className="p-6 bg-gradient-to-br from-green-50 to-transparent rounded-xl border border-green-100">
                  <label className="block text-sm font-bold text-gray-800 mb-3 uppercase tracking-wide">
                    <i className="fas fa-phone-alt mr-2 text-green-600"></i>Bot Phone Number
                  </label>
                  <input
                    type="tel"
                    name="whatsapp_phone_number"
                    value={settings.whatsapp_phone_number || ''}
                    onChange={handleInputChange}
                    placeholder="+234..."
                    className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition ${
                      validationErrors.whatsapp_phone_number ? 'border-red-500 bg-red-50' : 'border-gray-300'
                    }`}
                  />
                  {validationErrors.whatsapp_phone_number && (
                    <p className="text-xs text-red-600 mt-3 font-medium flex items-center gap-1">
                      <i className="fas fa-exclamation-circle"></i> {validationErrors.whatsapp_phone_number}
                    </p>
                  )}
                  <p className="text-xs text-gray-600 mt-3 flex items-center gap-1">
                    <i className="fas fa-info-circle"></i> Phone number in format +1234567890
                  </p>
                </div>

                {/* Webhook Token */}
                <div className="p-6 bg-gradient-to-br from-green-50 to-transparent rounded-xl border border-green-100">
                  <label className="block text-sm font-bold text-gray-800 mb-3 uppercase tracking-wide">
                    <i className="fas fa-shield-alt mr-2 text-green-600"></i>Webhook Token
                  </label>
                  <div className="flex gap-2">
                    <input
                      type={showTokens ? 'text' : 'password'}
                      name="whatsapp_webhook_token"
                      value={settings.whatsapp_webhook_token || ''}
                      onChange={handleInputChange}
                      placeholder="Enter webhook verification token..."
                      className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition"
                    />
                    <button
                      type="button"
                      onClick={() => setShowTokens(!showTokens)}
                      className="px-4 py-3 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition font-medium"
                    >
                      <i className={`fas ${showTokens ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                    </button>
                  </div>
                  <p className="text-xs text-gray-600 mt-3 flex items-center gap-1">
                    <i className="fas fa-info-circle"></i> Used to verify webhook requests from WhatsApp
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Paystack Configuration Tab */}
          {activeTab === 'paystack' && (
            <div className="bg-gradient-to-br from-blue-50 via-white to-transparent rounded-xl shadow-sm p-8 animate-in fade-in duration-300">
              <div className="flex items-start gap-4 mb-8 pb-6 border-b border-blue-100">
                <div className="w-14 h-14 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <i className="fas fa-credit-card text-blue-600 text-2xl"></i>
                </div>
                <div>
                  <h2 className="text-3xl font-bold text-gray-900">Payment Gateway</h2>
                  <p className="text-gray-600 mt-1">Configure your Paystack payment processing credentials</p>
                </div>
              </div>

              <div className="space-y-6">
                {/* Public Key */}
                <div className="p-6 bg-gradient-to-br from-blue-50 to-transparent rounded-xl border border-blue-100">
                  <label className="block text-sm font-bold text-gray-800 mb-3 uppercase tracking-wide">
                    <i className="fas fa-lock-open mr-2 text-blue-600"></i>Public Key
                  </label>
                  <div className="flex gap-2">
                    <input
                      type={showTokens ? 'text' : 'password'}
                      name="paystack_public_key"
                      value={settings.paystack_public_key || ''}
                      onChange={handleInputChange}
                      placeholder="pk_live_..."
                      className={`flex-1 px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition font-mono text-sm ${
                        validationErrors.paystack_public_key ? 'border-red-500 bg-red-50' : 'border-gray-300'
                      }`}
                    />
                    <button
                      type="button"
                      onClick={() => setShowTokens(!showTokens)}
                      className="px-4 py-3 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition font-medium"
                    >
                      <i className={`fas ${showTokens ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                    </button>
                  </div>
                  {validationErrors.paystack_public_key && (
                    <p className="text-xs text-red-600 mt-3 font-medium flex items-center gap-1">
                      <i className="fas fa-exclamation-circle"></i> {validationErrors.paystack_public_key}
                    </p>
                  )}
                  <p className="text-xs text-gray-600 mt-3 flex items-center gap-1">
                    <i className="fas fa-info-circle"></i> Public key from your Paystack dashboard
                  </p>
                </div>

                {/* Secret Key */}
                <div className="p-6 bg-gradient-to-br from-blue-50 to-transparent rounded-xl border border-blue-100">
                  <label className="block text-sm font-bold text-gray-800 mb-3 uppercase tracking-wide">
                    <i className="fas fa-lock mr-2 text-blue-600"></i>Secret Key
                  </label>
                  <div className="flex gap-2">
                    <input
                      type={showTokens ? 'text' : 'password'}
                      name="paystack_secret_key"
                      value={settings.paystack_secret_key || ''}
                      onChange={handleInputChange}
                      placeholder="sk_live_..."
                      className={`flex-1 px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition font-mono text-sm ${
                        validationErrors.paystack_secret_key ? 'border-red-500 bg-red-50' : 'border-gray-300'
                      }`}
                    />
                    <button
                      type="button"
                      onClick={() => setShowTokens(!showTokens)}
                      className="px-4 py-3 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition font-medium"
                    >
                      <i className={`fas ${showTokens ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                    </button>
                  </div>
                  {validationErrors.paystack_secret_key && (
                    <p className="text-xs text-red-600 mt-3 font-medium flex items-center gap-1">
                      <i className="fas fa-exclamation-circle"></i> {validationErrors.paystack_secret_key}
                    </p>
                  )}
                  <p className="text-xs text-gray-600 mt-3 flex items-center gap-1">
                    <i className="fas fa-info-circle"></i> Keep this secret! Used for secure server-side transactions
                  </p>
                </div>

                {/* Webhook Secret */}
                <div className="p-6 bg-gradient-to-br from-blue-50 to-transparent rounded-xl border border-blue-100">
                  <label className="block text-sm font-bold text-gray-800 mb-3 uppercase tracking-wide">
                    <i className="fas fa-key mr-2 text-blue-600"></i>Webhook Secret
                  </label>
                  <div className="flex gap-2">
                    <input
                      type={showTokens ? 'text' : 'password'}
                      name="paystack_webhook_secret"
                      value={settings.paystack_webhook_secret || ''}
                      onChange={handleInputChange}
                      placeholder="Enter webhook secret..."
                      className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition font-mono text-sm"
                    />
                    <button
                      type="button"
                      onClick={() => setShowTokens(!showTokens)}
                      className="px-4 py-3 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition font-medium"
                    >
                      <i className={`fas ${showTokens ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                    </button>
                  </div>
                  <p className="text-xs text-gray-600 mt-3 flex items-center gap-1">
                    <i className="fas fa-info-circle"></i> Used to verify webhook signatures from Paystack
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Database Configuration Tab */}
          {activeTab === 'database' && (
            <div className="bg-gradient-to-br from-orange-50 via-white to-transparent rounded-xl shadow-sm p-8 animate-in fade-in duration-300">
              <div className="flex items-start gap-4 mb-8 pb-6 border-b border-orange-100">
                <div className="w-14 h-14 bg-orange-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <i className="fas fa-database text-orange-600 text-2xl"></i>
                </div>
                <div>
                  <h2 className="text-3xl font-bold text-gray-900">Database Connection</h2>
                  <p className="text-gray-600 mt-1">Configure your MySQL database connection string</p>
                </div>
              </div>

              <div className="space-y-6">
                {/* Database URL */}
                <div className="p-6 bg-gradient-to-br from-orange-50 to-transparent rounded-xl border border-orange-100">
                  <label className="block text-sm font-bold text-gray-800 mb-3 uppercase tracking-wide">
                    <i className="fas fa-link mr-2 text-orange-600"></i>Database URL
                  </label>
                  <div className="flex gap-2">
                    <input
                      type={showTokens ? 'text' : 'password'}
                      name="database_url"
                      value={settings.database_url || ''}
                      onChange={handleInputChange}
                      placeholder="mysql+pymysql://user:pass@host/database"
                      className={`flex-1 px-4 py-3 border rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent transition font-mono text-sm ${
                        validationErrors.database_url ? 'border-red-500 bg-red-50' : 'border-gray-300'
                      }`}
                    />
                    <button
                      type="button"
                      onClick={() => setShowTokens(!showTokens)}
                      className="px-4 py-3 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 transition font-medium"
                    >
                      <i className={`fas ${showTokens ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                    </button>
                  </div>
                  {validationErrors.database_url && (
                    <p className="text-xs text-red-600 mt-3 font-medium flex items-center gap-1">
                      <i className="fas fa-exclamation-circle"></i> {validationErrors.database_url}
                    </p>
                  )}
                  <p className="text-xs text-gray-600 mt-3 flex items-center gap-1">
                    <i className="fas fa-info-circle"></i> Format: mysql+pymysql://user:password@host:port/database
                  </p>
                </div>

                {/* Connection Status */}
                <div className="p-6 bg-gradient-to-br from-green-50 to-transparent rounded-xl border border-green-100">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                    <div>
                      <p className="text-sm font-semibold text-gray-800">Connection Status</p>
                      <p className="text-xs text-gray-600 mt-1">Using Railway MySQL database</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Templates Tab */}
          {activeTab === 'templates' && (
            <div className="bg-gradient-to-br from-cyan-50 via-white to-transparent rounded-xl shadow-sm p-8 animate-in fade-in duration-300">
              <div className="flex items-start gap-4 mb-8 pb-6 border-b border-cyan-100">
                <div className="w-14 h-14 bg-cyan-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <i className="fas fa-file-alt text-cyan-600 text-2xl"></i>
                </div>
                <div>
                  <h2 className="text-3xl font-bold text-gray-900">Bot Message Templates</h2>
                  <p className="text-gray-600 mt-1">Manage and edit message templates stored in the database</p>
                </div>
              </div>

              {loadingTemplates ? (
                <div className="flex justify-center items-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600"></div>
                  <span className="ml-3 text-gray-600">Loading templates...</span>
                </div>
              ) : templates.length === 0 ? (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
                  <i className="fas fa-inbox text-yellow-600 text-3xl mb-3"></i>
                  <p className="text-gray-600">No templates found in the database.</p>
                  <p className="text-sm text-gray-500 mt-2">Templates will appear here once they are seeded or created.</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Summary Stats */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-cyan-50 border border-cyan-200 rounded-xl p-6">
                      <p className="text-sm text-cyan-600 font-semibold flex items-center gap-2">
                        <i className="fas fa-list-check"></i>Total Templates
                      </p>
                      <p className="text-3xl font-bold text-cyan-900 mt-2">{templates.length}</p>
                    </div>
                    <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
                      <p className="text-sm text-blue-600 font-semibold flex items-center gap-2">
                        <i className="fas fa-star"></i>Default Templates
                      </p>
                      <p className="text-3xl font-bold text-blue-900 mt-2">{templates.filter(t => t.is_default).length}</p>
                    </div>
                    <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-6">
                      <p className="text-sm text-indigo-600 font-semibold flex items-center gap-2">
                        <i className="fas fa-pencil-alt"></i>Custom Templates
                      </p>
                      <p className="text-3xl font-bold text-indigo-900 mt-2">{templates.filter(t => !t.is_default).length}</p>
                    </div>
                  </div>

                  {/* Templates List - No Scrolling */}
                  <div className="space-y-4">
                    {templates.map((template) => (
                      <div key={template.id} className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all">
                        <div className="flex justify-between items-start mb-4">
                          <div className="flex-1">
                            <h3 className="font-bold text-lg text-gray-900 flex items-center gap-2">
                              <i className="fas fa-tag text-cyan-600"></i>
                              {template.template_name}
                              {template.is_default && (
                                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-yellow-100 text-yellow-800">
                                  ⭐ Default
                                </span>
                              )}
                            </h3>
                            <p className="text-xs text-gray-500 mt-2">Template ID: <code className="bg-gray-100 px-2 py-1 rounded font-mono">{template.id}</code></p>
                          </div>
                          {/* Template Menu */}
                          <div className="relative">
                            <button
                              onClick={() => setTemplateMenuId(templateMenuId === template.id ? null : template.id)}
                              className="p-2 hover:bg-gray-100 rounded-lg transition text-gray-600 font-bold text-lg"
                              title="Template actions menu"
                            >
                              <i className="fas fa-ellipsis-v"></i>
                            </button>
                            {templateMenuId === template.id && (
                              <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-300 rounded-lg shadow-xl z-50">
                                <button
                                  onClick={() => openEditModal(template)}
                                  className="w-full text-left px-4 py-3 hover:bg-blue-50 text-blue-600 font-bold flex items-center gap-2 border-b transition"
                                >
                                  <i className="fas fa-edit text-lg"></i>Edit Template
                                </button>
                                <button
                                  onClick={() => {
                                    alert('Duplicate functionality coming soon');
                                    setTemplateMenuId(null);
                                  }}
                                  className="w-full text-left px-4 py-3 hover:bg-green-50 text-green-600 font-bold flex items-center gap-2 border-b transition"
                                >
                                  <i className="fas fa-copy text-lg"></i>Duplicate
                                </button>
                                <button
                                  onClick={() => {
                                    if (window.confirm(`Delete template "${template.template_name}"? This action cannot be undone.`)) {
                                      alert('Delete functionality coming soon');
                                    }
                                    setTemplateMenuId(null);
                                  }}
                                  className="w-full text-left px-4 py-3 hover:bg-red-50 text-red-600 font-bold flex items-center gap-2 transition"
                                >
                                  <i className="fas fa-trash text-lg"></i>Delete
                                </button>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Template Content - Better Display */}
                        <div className="mb-4">
                          <p className="text-xs font-bold text-gray-700 mb-2 flex items-center gap-1">
                            <i className="fas fa-align-left text-cyan-600"></i>CONTENT
                          </p>
                          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 font-mono text-sm text-gray-700 whitespace-pre-wrap break-words">
                            {template.template_content}
                          </div>
                        </div>

                        {/* Menu Items - Display */}
                        {template.menu_items && template.menu_items.length > 0 && (
                          <div className="mb-4">
                            <p className="text-xs font-bold text-gray-700 mb-2 flex items-center gap-1">
                              <i className="fas fa-bars text-orange-600"></i>MENU BUTTONS
                            </p>
                            <div className="space-y-2">
                              {template.menu_items.map((item, idx) => (
                                <div key={idx} className="bg-orange-50 border border-orange-200 rounded-lg p-3 flex items-center gap-2">
                                  <i className="fas fa-button text-orange-600"></i>
                                  <span className="text-sm font-mono text-gray-700">{item}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Variables - Better Display */}
                        {template.variables && template.variables.length > 0 && (
                          <div>
                            <p className="text-xs font-bold text-gray-700 mb-2 flex items-center gap-1">
                              <i className="fas fa-code text-purple-600"></i>VARIABLES
                            </p>
                            <div className="flex flex-wrap gap-2">
                              {template.variables.map((variable, idx) => (
                                <span key={idx} className="inline-block bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-xs font-bold font-mono border border-purple-200">
                                  {typeof variable === 'string' ? variable : JSON.stringify(variable)}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Edit Template Modal */}
          {showEditModal && editingTemplate && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60] p-4">
              <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[95vh] overflow-y-auto">
                <div className="sticky top-0 z-10 bg-gradient-to-r from-cyan-50 to-cyan-100 border-b border-cyan-200 p-6 flex justify-between items-center">
                  <h3 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                    <div className="w-10 h-10 bg-cyan-600 rounded-lg flex items-center justify-center">
                      <i className="fas fa-edit text-white"></i>
                    </div>
                    Edit Template
                  </h3>
                  <button
                    type="button"
                    onClick={closeEditModal}
                    className="text-gray-600 hover:text-gray-800 text-3xl font-bold transition"
                  >
                    ×
                  </button>
                </div>

                <div className="p-8 space-y-6">
                  {/* Template Name */}
                  <div>
                    <label className="block text-sm font-bold text-gray-800 mb-3 uppercase tracking-wide">
                      <i className="fas fa-tag text-cyan-600 mr-2"></i>Template Name
                    </label>
                    <input
                      type="text"
                      value={editingTemplate.template_name}
                      onChange={(e) => setEditingTemplate({ ...editingTemplate, template_name: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition"
                      placeholder="e.g., greeting_welcome_new_user"
                    />
                    <p className="text-xs text-gray-600 mt-2 flex items-center gap-1">
                      <i className="fas fa-info-circle"></i> Use descriptive names with underscores
                    </p>
                  </div>

                  {/* Template Content */}
                  <div>
                    <label className="block text-sm font-bold text-gray-800 mb-3 uppercase tracking-wide">
                      <i className="fas fa-align-left text-cyan-600 mr-2"></i>Template Content
                    </label>
                    <textarea
                      value={editingTemplate.template_content}
                      onChange={(e) => setEditingTemplate({ ...editingTemplate, template_content: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent font-mono text-sm transition"
                      placeholder="Enter template content with variables like {user_name}, {bot_name}, etc."
                      rows={8}
                    />
                    <p className="text-xs text-gray-600 mt-2 flex items-center gap-1">
                      <i className="fas fa-info-circle"></i> Use curly braces for variables: {'{variable_name}'}
                    </p>
                  </div>

                  {/* Menu Items Management */}
                  <div>
                    <label className="block text-sm font-bold text-gray-800 mb-3 uppercase tracking-wide">
                      <i className="fas fa-bars text-orange-600 mr-2"></i>Menu Buttons (Optional)
                    </label>
                    <div className="space-y-3 mb-4 p-4 bg-orange-50 rounded-lg border border-orange-100 min-h-20">
                      {editingTemplate.menu_items && editingTemplate.menu_items.length > 0 ? (
                        editingTemplate.menu_items.map((item, idx) => (
                          <div key={idx} className="flex gap-2 items-center bg-white border border-orange-200 rounded-lg p-3">
                            <div className="flex-1">
                              <input
                                type="text"
                                value={item}
                                onChange={(e) => {
                                  const newMenuItems = [...(editingTemplate.menu_items || [])];
                                  newMenuItems[idx] = e.target.value;
                                  setEditingTemplate({ ...editingTemplate, menu_items: newMenuItems });
                                }}
                                placeholder="Button text"
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm"
                              />
                            </div>
                            <button
                              onClick={() => {
                                setEditingTemplate({
                                  ...editingTemplate,
                                  menu_items: editingTemplate.menu_items?.filter((_, i) => i !== idx) || []
                                });
                              }}
                              className="px-3 py-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition font-bold"
                              title="Remove menu button"
                            >
                              <i className="fas fa-trash"></i>
                            </button>
                          </div>
                        ))
                      ) : (
                        <span className="text-gray-500 text-sm italic">No menu buttons added yet</span>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        id="menuButtonInput"
                        placeholder="Add new menu button (e.g., Click Here, Learn More, etc.)"
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && e.currentTarget.value.trim()) {
                            const buttonText = e.currentTarget.value.trim();
                            setEditingTemplate({
                              ...editingTemplate,
                              menu_items: [...(editingTemplate.menu_items || []), buttonText]
                            });
                            e.currentTarget.value = '';
                            e.currentTarget.focus();
                          }
                        }}
                        className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm transition"
                      />
                      <button
                        type="button"
                        onClick={() => {
                          const input = document.getElementById('menuButtonInput') as HTMLInputElement;
                          if (input?.value.trim()) {
                            const buttonText = input.value.trim();
                            setEditingTemplate({
                              ...editingTemplate,
                              menu_items: [...(editingTemplate.menu_items || []), buttonText]
                            });
                            input.value = '';
                            input.focus();
                          }
                        }}
                        className="px-4 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition font-bold flex items-center gap-2"
                        title="Add menu button"
                      >
                        <i className="fas fa-plus"></i>Add
                      </button>
                    </div>
                    <p className="text-xs text-gray-600 mt-2 flex items-center gap-1">
                      <i className="fas fa-info-circle"></i> Add menu buttons that will appear below the message (optional)
                    </p>
                  </div>

                  {/* Variables Management */}
                  <div>
                    <label className="block text-sm font-bold text-gray-800 mb-3 uppercase tracking-wide">
                      <i className="fas fa-code text-purple-600 mr-2"></i>Variables
                    </label>
                    <div className="flex flex-wrap gap-2 mb-4 p-4 bg-purple-50 rounded-lg border border-purple-100 min-h-16">
                      {editingTemplate.variables && editingTemplate.variables.length > 0 ? (
                        editingTemplate.variables.map((variable, idx) => (
                          <span key={idx} className="inline-flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-full text-sm font-bold font-mono">
                            {'{' + variable + '}'}
                            <button
                              onClick={() => {
                                setEditingTemplate({
                                  ...editingTemplate,
                                  variables: editingTemplate.variables?.filter((_, i) => i !== idx) || []
                                });
                              }}
                              className="hover:bg-purple-700 rounded-full w-6 h-6 flex items-center justify-center transition"
                              title="Remove variable"
                            >
                              ×
                            </button>
                          </span>
                        ))
                      ) : (
                        <span className="text-gray-500 text-sm italic">No variables added yet</span>
                      )}
                    </div>
                    <input
                      type="text"
                      placeholder="Enter variable name and press Enter (e.g., user_name)"
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && e.currentTarget.value.trim()) {
                          const varName = e.currentTarget.value.trim();
                          if (!editingTemplate.variables?.includes(varName)) {
                            setEditingTemplate({
                              ...editingTemplate,
                              variables: [...(editingTemplate.variables || []), varName]
                            });
                          }
                          e.currentTarget.value = '';
                        }
                      }}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm transition"
                    />
                    <p className="text-xs text-gray-600 mt-2 flex items-center gap-1">
                      <i className="fas fa-info-circle"></i> Add variables that will be used in the template content
                    </p>
                  </div>

                  {/* Is Default Toggle */}
                  <div className="flex items-center gap-4 p-5 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200 rounded-xl">
                    <input
                      type="checkbox"
                      checked={editingTemplate.is_default}
                      onChange={(e) => setEditingTemplate({ ...editingTemplate, is_default: e.target.checked })}
                      className="w-6 h-6 text-yellow-600 rounded focus:ring-2 cursor-pointer"
                    />
                    <label className="flex-1 text-sm font-bold text-gray-900 cursor-pointer flex items-center gap-2">
                      <i className="fas fa-star text-yellow-600 text-lg"></i>Mark as Default Template
                    </label>
                  </div>
                </div>

                {/* Modal Footer */}
                <div className="sticky bottom-0 z-10 bg-gradient-to-r from-gray-50 to-gray-100 border-t border-gray-200 px-8 py-6 flex gap-3 justify-end">
                  <button
                    type="button"
                    onClick={closeEditModal}
                    className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-200 transition font-bold flex items-center gap-2"
                  >
                    <i className="fas fa-times"></i>Cancel
                  </button>
                  <button
                    type="button"
                    onClick={saveTemplateChanges}
                    disabled={isSaving}
                    className="px-6 py-3 bg-gradient-to-r from-cyan-600 to-cyan-700 text-white rounded-lg hover:from-cyan-700 hover:to-cyan-800 transition font-bold disabled:opacity-50 flex items-center gap-2 shadow-lg"
                  >
                    {isSaving ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                        Saving...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-save"></i>Save Changes
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Save Button */}
          {activeTab !== 'templates' && (
          <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-2xl">
            <div className="max-w-6xl mx-auto px-4 md:px-8 py-4 flex gap-3 justify-end items-center">
              {isDirty && (
                <p className="text-sm text-amber-700 mr-auto">
                  <i className="fas fa-exclamation-circle mr-2"></i>
                  You have unsaved changes
                </p>
              )}
              <button
                type="button"
                onClick={() => {
                  setSettings(originalSettings);
                  setValidationErrors({});
                }}
                className="px-6 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={!isDirty}
              >
                <i className="fas fa-times mr-2"></i>Discard
              </button>
              <button
                type="submit"
                className="px-8 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg hover:shadow-xl"
                disabled={!isDirty || isSaving}
              >
                {isSaving ? (
                  <>
                    <i className="fas fa-spinner fa-spin"></i>
                    Saving...
                  </>
                ) : (
                  <>
                    <i className="fas fa-save"></i>
                    Save All Settings
                  </>
                )}
              </button>
            </div>
          </div>
          )}

          {/* Padding for fixed button */}
          <div className="h-24"></div>
        </form>
      </div>
    </div>
    </Layout>
  );
}

// Helper Tab Button Component
function TabButton({
  icon,
  label,
  active,
  onClick,
  color,
}: {
  icon: string;
  label: string;
  active: boolean;
  onClick: () => void;
  color: string;
}) {
  const colorMap: Record<string, string> = {
    purple: 'text-purple-600 border-purple-600 bg-purple-50 hover:bg-purple-100',
    green: 'text-green-600 border-green-600 bg-green-50 hover:bg-green-100',
    blue: 'text-blue-600 border-blue-600 bg-blue-50 hover:bg-blue-100',
    orange: 'text-orange-600 border-orange-600 bg-orange-50 hover:bg-orange-100',
    cyan: 'text-cyan-600 border-cyan-600 bg-cyan-50 hover:bg-cyan-100',
  };

  return (
    <button
      onClick={onClick}
      className={`flex-1 min-w-max py-4 px-6 font-semibold border-b-2 transition text-lg flex items-center justify-center gap-2 whitespace-nowrap ${
        active
          ? `${colorMap[color]} border-b-2 shadow-sm`
          : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
      }`}
    >
      <i className={`${icon} text-xl`}></i>
      {label}
    </button>
  );
}
