'use client';

import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface NotificationPreferences {
  phone_number: string;
  homework_submitted: boolean;
  homework_reviewed: boolean;
  chat_messages: boolean;
  subscription_alerts: boolean;
  account_updates: boolean;
  system_alerts: boolean;
  prefer_whatsapp: boolean;
  prefer_email: boolean;
  quiet_hours_enabled: boolean;
  quiet_hours_start?: string;
  quiet_hours_end?: string;
  batch_notifications: boolean;
}

export default function NotificationPreferences() {
  const [phone, setPhone] = useState('');
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const fetchPreferences = async (phoneNumber: string) => {
    if (!phoneNumber.trim()) return;

    setLoading(true);
    try {
      const response = await axios.get(
        `${API_URL}/api/notifications/preferences?phone_number=${phoneNumber}`
      );

      if (response.data.status === 'success') {
        setPreferences(response.data.data);
        setMessage('');
      }
    } catch (error) {
      console.error('Error fetching preferences:', error);
      setMessage('Failed to load preferences');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchPreferences(phone);
  };

  const savePreferences = async () => {
    if (!phone.trim() || !preferences) return;

    setSaving(true);
    try {
      const payload = {
        homework_submitted: preferences.homework_submitted,
        homework_reviewed: preferences.homework_reviewed,
        chat_messages: preferences.chat_messages,
        subscription_alerts: preferences.subscription_alerts,
        account_updates: preferences.account_updates,
        system_alerts: preferences.system_alerts,
        prefer_whatsapp: preferences.prefer_whatsapp,
        prefer_email: preferences.prefer_email,
        quiet_hours_enabled: preferences.quiet_hours_enabled,
        quiet_hours_start: preferences.quiet_hours_start,
        quiet_hours_end: preferences.quiet_hours_end,
        batch_notifications: preferences.batch_notifications,
      };

      const response = await axios.post(
        `${API_URL}/api/notifications/preferences?phone_number=${phone}`,
        payload
      );

      if (response.data.status === 'success') {
        setMessage('✓ Preferences saved successfully!');
        setTimeout(() => setMessage(''), 3000);
      }
    } catch (error) {
      console.error('Error saving preferences:', error);
      setMessage('Failed to save preferences');
    } finally {
      setSaving(false);
    }
  };

  const togglePreference = (key: keyof NotificationPreferences) => {
    if (preferences && typeof preferences[key] === 'boolean') {
      setPreferences({
        ...preferences,
        [key]: !preferences[key],
      });
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">⚙️ Notification Preferences</h2>

      {/* Search Form */}
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-4">
          <input
            type="text"
            placeholder="Enter phone number (e.g., +1234567890)"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            type="submit"
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
          >
            Load
          </button>
        </div>
      </form>

      {message && (
        <div className={`mb-4 p-4 rounded-lg ${
          message.includes('✓')
            ? 'bg-green-100 text-green-800'
            : 'bg-red-100 text-red-800'
        }`}>
          {message}
        </div>
      )}

      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading...</div>
      ) : preferences ? (
        <div className="space-y-6">
          {/* Notification Types */}
          <section>
            <h3 className="text-lg font-bold text-gray-800 mb-4">
              📬 Notification Types
            </h3>
            <div className="space-y-3 bg-gray-50 p-4 rounded-lg">
              {[
                {
                  key: 'homework_submitted',
                  label: '📝 Homework Submitted',
                  desc: 'When homework is submitted',
                },
                {
                  key: 'homework_reviewed',
                  label: '✅ Homework Reviewed',
                  desc: 'When homework gets feedback',
                },
                {
                  key: 'chat_messages',
                  label: '💬 Chat Messages',
                  desc: 'New chat support messages',
                },
                {
                  key: 'subscription_alerts',
                  label: '🎉 Subscription Alerts',
                  desc: 'Subscription changes and expirations',
                },
                {
                  key: 'account_updates',
                  label: '👤 Account Updates',
                  desc: 'Profile and account changes',
                },
                {
                  key: 'system_alerts',
                  label: '⚠️ System Alerts',
                  desc: 'Important system notifications',
                },
              ].map((item) => (
                <label
                  key={item.key}
                  className="flex items-center gap-3 cursor-pointer p-2 hover:bg-white rounded transition"
                >
                  <input
                    type="checkbox"
                    checked={
                      preferences[
                        item.key as keyof NotificationPreferences
                      ] as boolean
                    }
                    onChange={() =>
                      togglePreference(
                        item.key as keyof NotificationPreferences
                      )
                    }
                    className="w-5 h-5 text-blue-500"
                  />
                  <div>
                    <div className="font-semibold text-gray-800">
                      {item.label}
                    </div>
                    <div className="text-sm text-gray-600">{item.desc}</div>
                  </div>
                </label>
              ))}
            </div>
          </section>

          {/* Communication Channels */}
          <section>
            <h3 className="text-lg font-bold text-gray-800 mb-4">
              📱 Communication Channels
            </h3>
            <div className="space-y-3 bg-gray-50 p-4 rounded-lg">
              {[
                {
                  key: 'prefer_whatsapp',
                  label: '💬 WhatsApp',
                  desc: 'Receive notifications via WhatsApp',
                },
                {
                  key: 'prefer_email',
                  label: '📧 Email',
                  desc: 'Receive notifications via email',
                },
              ].map((item) => (
                <label
                  key={item.key}
                  className="flex items-center gap-3 cursor-pointer p-2 hover:bg-white rounded transition"
                >
                  <input
                    type="checkbox"
                    checked={
                      preferences[
                        item.key as keyof NotificationPreferences
                      ] as boolean
                    }
                    onChange={() =>
                      togglePreference(
                        item.key as keyof NotificationPreferences
                      )
                    }
                    className="w-5 h-5 text-blue-500"
                  />
                  <div>
                    <div className="font-semibold text-gray-800">
                      {item.label}
                    </div>
                    <div className="text-sm text-gray-600">{item.desc}</div>
                  </div>
                </label>
              ))}
            </div>
          </section>

          {/* Quiet Hours */}
          <section>
            <h3 className="text-lg font-bold text-gray-800 mb-4">
              🌙 Quiet Hours
            </h3>
            <div className="bg-gray-50 p-4 rounded-lg space-y-4">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.quiet_hours_enabled}
                  onChange={() =>
                    togglePreference('quiet_hours_enabled')
                  }
                  className="w-5 h-5 text-blue-500"
                />
                <div>
                  <div className="font-semibold text-gray-800">
                    Enable Quiet Hours
                  </div>
                  <div className="text-sm text-gray-600">
                    No notifications during quiet hours
                  </div>
                </div>
              </label>

              {preferences.quiet_hours_enabled && (
                <div className="flex gap-4 ml-8">
                  <div className="flex-1">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Start Time (HH:MM)
                    </label>
                    <input
                      type="time"
                      value={preferences.quiet_hours_start || '22:00'}
                      onChange={(e) =>
                        setPreferences({
                          ...preferences,
                          quiet_hours_start: e.target.value,
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div className="flex-1">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      End Time (HH:MM)
                    </label>
                    <input
                      type="time"
                      value={preferences.quiet_hours_end || '08:00'}
                      onChange={(e) =>
                        setPreferences({
                          ...preferences,
                          quiet_hours_end: e.target.value,
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                </div>
              )}
            </div>
          </section>

          {/* Other Options */}
          <section>
            <h3 className="text-lg font-bold text-gray-800 mb-4">
              📨 Other Options
            </h3>
            <div className="bg-gray-50 p-4 rounded-lg">
              <label className="flex items-center gap-3 cursor-pointer p-2 hover:bg-white rounded transition">
                <input
                  type="checkbox"
                  checked={preferences.batch_notifications}
                  onChange={() =>
                    togglePreference('batch_notifications')
                  }
                  className="w-5 h-5 text-blue-500"
                />
                <div>
                  <div className="font-semibold text-gray-800">
                    Batch Notifications
                  </div>
                  <div className="text-sm text-gray-600">
                    Receive notifications in batches instead of individually
                  </div>
                </div>
              </label>
            </div>
          </section>

          {/* Save Button */}
          <div className="flex gap-4">
            <button
              onClick={savePreferences}
              disabled={saving}
              className="flex-1 px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition disabled:bg-gray-400"
            >
              {saving ? 'Saving...' : '💾 Save Preferences'}
            </button>
          </div>

          {/* Info Box */}
          <div className="bg-blue-50 p-4 rounded-lg border-l-4 border-blue-500">
            <p className="text-sm text-gray-700">
              <strong>ℹ️ Note:</strong> Quiet hours work based on the server time.
              For example, 22:00-08:00 means no notifications between 10 PM and 8
              AM. The system respects your preferences and will skip notifications
              during quiet hours unless they're marked as urgent.
            </p>
          </div>
        </div>
      ) : phone ? (
        <div className="text-center py-8 text-gray-500">
          No preferences found. Click Load to create default preferences.
        </div>
      ) : null}
    </div>
  );
}
