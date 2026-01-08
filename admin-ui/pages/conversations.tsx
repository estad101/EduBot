'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '../components/Layout';
import { apiClient } from '../lib/api-client';

interface Conversation {
  phone_number: string;
  student_name?: string;
  last_message: string;
  last_message_time: string;
  message_count: number;
  is_active: boolean;
  type?: 'student' | 'lead' | 'memory';
}

interface Message {
  id: string;
  phone_number: string;
  text: string;
  timestamp: string;
  sender_type: 'user' | 'bot';
  message_type: string;
}

export default function ConversationsPage() {
  const router = useRouter();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedPhone, setSelectedPhone] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('admin_token');
        if (!token) {
          router.push('/login');
          return;
        }

        const response = await apiClient.get('/api/admin/conversations');
        if (response.status === 'success') {
          setConversations(response.data);
          if (response.data.length > 0) {
            setSelectedPhone(response.data[0].phone_number);
          }
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load conversations');
      } finally {
        setLoading(false);
      }
    };

    fetchConversations();
    const interval = setInterval(fetchConversations, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, [router]);

  useEffect(() => {
    const fetchMessages = async () => {
      if (!selectedPhone) return;

      try {
        const response = await apiClient.get(`/api/admin/conversations/${selectedPhone}/messages`);
        if (response.status === 'success') {
          setMessages(response.data);
        }
      } catch (err: any) {
        console.error('Failed to load messages:', err);
      }
    };

    fetchMessages();
    const interval = setInterval(fetchMessages, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, [selectedPhone]);

  // Component to format message text
  const MessageContent = ({ text }: { text: string }) => {
    // Remove asterisks and process commands
    const cleanText = text.replace(/\*\*/g, '').replace(/\*/g, '');
    
    // Split by newlines
    const lines = cleanText.split('\n');
    
    return (
      <div className="break-words whitespace-pre-wrap">
        {lines.map((line, idx) => {
          // Check if line is a command (starts with •)
          if (line.trim().startsWith('•')) {
            const commandText = line.trim().substring(1).trim();
            // Extract command in quotes or parentheses
            const match = commandText.match(/['"](.*?)['"]|^\**(.*?)\**/);
            if (match && (match[1] || match[2])) {
              const command = (match[1] || match[2]).toUpperCase();
              const rest = commandText.replace(match[0], '').trim();
              return (
                <div key={idx} className="my-1">
                  <strong>{command}</strong> {rest}
                </div>
              );
            }
          }
          return <div key={idx}>{line}</div>;
        })}
      </div>
    );
  };

  if (loading && conversations.length === 0) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <i className="fas fa-spinner fa-spin text-4xl text-green-600 mb-4"></i>
            <p className="text-gray-600">Loading conversations...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-200px)]">
        {/* Conversations List */}
        <div className="lg:col-span-1 bg-white rounded-lg shadow overflow-hidden flex flex-col">
          <div className="bg-green-600 text-white p-4">
            <h2 className="text-lg font-bold">
              <i className="fab fa-whatsapp mr-2"></i>Messages
            </h2>
            <p className="text-green-100 text-sm">{conversations.length} conversations</p>
          </div>

          <div className="overflow-y-auto flex-1">
            {conversations.length === 0 ? (
              <div className="p-6 text-center text-gray-500">
                <p>No conversations yet</p>
              </div>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.phone_number}
                  onClick={() => setSelectedPhone(conv.phone_number)}
                  className={`p-4 border-b cursor-pointer transition ${
                    selectedPhone === conv.phone_number
                      ? 'bg-green-50 border-l-4 border-green-600'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="font-bold text-gray-800">
                          {conv.student_name || conv.phone_number}
                        </p>
                        {conv.type === 'student' && (
                          <span className="inline-block px-2 py-1 bg-green-100 text-green-800 text-xs rounded font-semibold">
                            Student
                          </span>
                        )}
                        {conv.type === 'lead' && (
                          <span className="inline-block px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded font-semibold">
                            Lead
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 truncate">{conv.last_message}</p>
                    </div>
                    {conv.is_active && (
                      <span className="inline-block w-3 h-3 bg-green-500 rounded-full ml-2 mt-1"></span>
                    )}
                  </div>
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(conv.last_message_time).toLocaleString()}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Chat View */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow overflow-hidden flex flex-col">
          {selectedPhone ? (
            <>
              {/* Chat Header */}
              <div className="bg-green-600 text-white p-4 flex justify-between items-center">
                <div>
                  <p className="font-bold">
                    {conversations.find((c) => c.phone_number === selectedPhone)?.student_name ||
                      selectedPhone}
                  </p>
                  <p className="text-green-100 text-sm">
                    {conversations.find((c) => c.phone_number === selectedPhone)?.is_active
                      ? 'Active now'
                      : 'Offline'}
                  </p>
                </div>
                <div className="flex space-x-2">
                  <button className="p-2 hover:bg-green-700 rounded-full transition">
                    <i className="fas fa-phone"></i>
                  </button>
                  <button className="p-2 hover:bg-green-700 rounded-full transition">
                    <i className="fas fa-video"></i>
                  </button>
                  <button className="p-2 hover:bg-green-700 rounded-full transition">
                    <i className="fas fa-info-circle"></i>
                  </button>
                </div>
              </div>

              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-4 bg-gradient-to-b from-gray-50 to-white">
                {messages.length === 0 ? (
                  <div className="flex items-center justify-center h-full text-gray-400">
                    <div className="text-center">
                      <i className="fab fa-whatsapp text-6xl mb-4 text-green-200"></i>
                      <p>No messages yet</p>
                    </div>
                  </div>
                ) : (
                  messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`mb-3 flex ${msg.sender_type === 'user' ? 'justify-start' : 'justify-end'}`}
                    >
                      <div
                        className={`max-w-xs px-4 py-2 rounded-lg ${
                          msg.sender_type === 'user'
                            ? 'bg-white border border-gray-200 text-gray-800'
                            : 'bg-green-600 text-white rounded-br-none'
                        }`}
                      >
                        <MessageContent text={msg.text} />
                        <p
                          className={`text-xs mt-1 ${
                            msg.sender_type === 'user' ? 'text-gray-400' : 'text-green-100'
                          }`}
                        >
                          {new Date(msg.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Message Input */}
              <div className="p-4 border-t bg-gray-50">
                <div className="flex items-center space-x-3">
                  <button className="text-green-600 hover:text-green-700 text-xl">
                    <i className="fas fa-plus-circle"></i>
                  </button>
                  <input
                    type="text"
                    placeholder="Type a message..."
                    disabled
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-full bg-white"
                  />
                  <button className="text-green-600 hover:text-green-700 text-xl">
                    <i className="fas fa-microphone"></i>
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Messages are read-only for admin dashboard
                </p>
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-400">
              <div className="text-center">
                <i className="fab fa-whatsapp text-6xl mb-4 text-gray-300"></i>
                <p>Select a conversation to view messages</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-4 mt-6">
          <p className="text-red-700">{error}</p>
        </div>
      )}
    </Layout>
  );
}
