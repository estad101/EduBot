'use client';

import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Notification {
  id: number;
  type: string;
  priority: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
  read_at?: string;
  related_entity?: {
    type: string;
    id: string;
  };
}

interface NotificationStats {
  total: number;
  unread: number;
  by_type: {
    [key: string]: number;
  };
}

export default function NotificationsPanel() {
  const [phone, setPhone] = useState('');
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [stats, setStats] = useState<NotificationStats | null>(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<'all' | 'unread'>('all');
  const [selectedType, setSelectedType] = useState<string>('');

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const fetchNotifications = async (phoneNumber: string) => {
    if (!phoneNumber.trim()) return;
    
    setLoading(true);
    try {
      const params = new URLSearchParams({
        phone_number: phoneNumber,
        limit: '50',
        unread_only: filter === 'unread' ? 'true' : 'false',
      });
      
      if (selectedType) {
        params.append('notification_type', selectedType);
      }

      const response = await axios.get(
        `${API_URL}/api/notifications/?${params}`
      );
      
      if (response.data.status === 'success') {
        setNotifications(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async (phoneNumber: string) => {
    if (!phoneNumber.trim()) return;
    
    try {
      const response = await axios.get(
        `${API_URL}/api/notifications/stats?phone_number=${phoneNumber}`
      );
      
      if (response.data.status === 'success') {
        setStats(response.data.data);
      }

      const countResponse = await axios.get(
        `${API_URL}/api/notifications/unread-count?phone_number=${phoneNumber}`
      );
      
      if (countResponse.data.status === 'success') {
        setUnreadCount(countResponse.data.data.unread_count);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const markAsRead = async (notificationId: number) => {
    try {
      await axios.post(
        `${API_URL}/api/notifications/${notificationId}/mark-as-read`
      );
      
      // Refresh notifications
      if (phone) {
        fetchNotifications(phone);
        fetchStats(phone);
      }
    } catch (error) {
      console.error('Error marking as read:', error);
    }
  };

  const markAllAsRead = async () => {
    if (!phone.trim()) return;
    
    try {
      await axios.post(
        `${API_URL}/api/notifications/mark-all-as-read?phone_number=${phone}`
      );
      
      fetchNotifications(phone);
      fetchStats(phone);
    } catch (error) {
      console.error('Error marking all as read:', error);
    }
  };

  const deleteNotification = async (notificationId: number) => {
    try {
      await axios.delete(
        `${API_URL}/api/notifications/${notificationId}`
      );
      
      if (phone) {
        fetchNotifications(phone);
        fetchStats(phone);
      }
    } catch (error) {
      console.error('Error deleting notification:', error);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchNotifications(phone);
    fetchStats(phone);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-100 text-red-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'normal':
        return 'bg-blue-100 text-blue-800';
      case 'low':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeIcon = (type: string) => {
    const icons: { [key: string]: string } = {
      homework_submitted: '📝',
      homework_reviewed: '✅',
      chat_message: '💬',
      chat_support_started: '🎯',
      registration_complete: '👋',
      subscription_activated: '🎉',
      subscription_expiring: '⏰',
      payment_confirmed: '💳',
      account_updated: '👤',
      system_alert: '⚠️',
    };
    return icons[type] || '📬';
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">📬 Notifications</h2>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
            <div className="text-gray-600">Total Notifications</div>
          </div>
          <div className="bg-red-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-red-600">{stats.unread}</div>
            <div className="text-gray-600">Unread</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {Object.keys(stats.by_type).length}
            </div>
            <div className="text-gray-600">Types</div>
          </div>
        </div>
      )}

      {/* Search Form */}
      <form onSubmit={handleSearch} className="mb-6 space-y-4">
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
            Search
          </button>
        </div>

        {/* Filters */}
        <div className="flex gap-4 items-center">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as 'all' | 'unread')}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value="all">All Notifications</option>
            <option value="unread">Unread Only</option>
          </select>

          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value="">All Types</option>
            <option value="homework_submitted">Homework Submitted</option>
            <option value="homework_reviewed">Homework Reviewed</option>
            <option value="chat_message">Chat Message</option>
            <option value="chat_support_started">Chat Started</option>
            <option value="registration_complete">Registration</option>
            <option value="subscription_activated">Subscription Active</option>
            <option value="payment_confirmed">Payment Confirmed</option>
            <option value="system_alert">System Alert</option>
          </select>

          {unreadCount > 0 && (
            <button
              onClick={markAllAsRead}
              type="button"
              className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition"
            >
              Mark All as Read
            </button>
          )}
        </div>
      </form>

      {/* Notifications List */}
      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-8 text-gray-500">Loading...</div>
        ) : notifications.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No notifications found
          </div>
        ) : (
          notifications.map((notification) => (
            <div
              key={notification.id}
              className={`border rounded-lg p-4 transition ${
                notification.is_read
                  ? 'bg-gray-50 border-gray-200'
                  : 'bg-white border-blue-200 border-l-4'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl">
                      {getTypeIcon(notification.type)}
                    </span>
                    <h3 className="font-bold text-gray-800">
                      {notification.title}
                    </h3>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-semibold ${getPriorityColor(
                        notification.priority
                      )}`}
                    >
                      {notification.priority.toUpperCase()}
                    </span>
                  </div>

                  <p className="text-gray-600 text-sm mb-2">
                    {notification.message}
                  </p>

                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>
                      📅{' '}
                      {new Date(notification.created_at).toLocaleString()}
                    </span>
                    {notification.is_read && notification.read_at && (
                      <span>
                        ✓ Read{' '}
                        {new Date(notification.read_at).toLocaleString()}
                      </span>
                    )}
                    {notification.related_entity && (
                      <span>
                        🔗 {notification.related_entity.type} (
                        {notification.related_entity.id})
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex gap-2 ml-4">
                  {!notification.is_read && (
                    <button
                      onClick={() => markAsRead(notification.id)}
                      className="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition text-sm"
                    >
                      Mark Read
                    </button>
                  )}
                  <button
                    onClick={() => deleteNotification(notification.id)}
                    className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 transition text-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Legend */}
      <div className="mt-8 pt-4 border-t border-gray-200">
        <h4 className="font-bold text-gray-800 mb-3">Notification Types:</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm text-gray-600">
          <div>📝 Homework Submitted</div>
          <div>✅ Homework Reviewed</div>
          <div>💬 Chat Message</div>
          <div>🎯 Chat Support</div>
          <div>👋 Registration</div>
          <div>🎉 Subscription Active</div>
          <div>⏰ Subscription Expiring</div>
          <div>💳 Payment Confirmed</div>
        </div>
      </div>
    </div>
  );
}
