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
  is_chat_support?: boolean;
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
  const [messageInput, setMessageInput] = useState('');
  const [sendingMessage, setSendingMessage] = useState(false);
  const [isChatSupport, setIsChatSupport] = useState(false);
  const [showChat, setShowChat] = useState(false);

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
    
    // Check if this is a chat support conversation
    const conv = conversations.find(c => c.phone_number === selectedPhone);
    setIsChatSupport(conv?.is_chat_support || false);
    
    const interval = setInterval(fetchMessages, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, [selectedPhone, conversations]);

  const handleSendMessage = async () => {
    if (!messageInput.trim() || !selectedPhone) return;

    setSendingMessage(true);
    try {
      const response = await apiClient.post(
        `/api/admin/conversations/${selectedPhone}/chat-support/send`,
        { message: messageInput }
      );

      if (response.status === 'success') {
        setMessageInput('');
        // Refresh messages
        const messagesResponse = await apiClient.get(
          `/api/admin/conversations/${selectedPhone}/messages`
        );
        if (messagesResponse.status === 'success') {
          setMessages(messagesResponse.data);
        }
      } else {
        setError(response.message || 'Failed to send message');
      }
    } catch (err: any) {
      setError(err.message || 'Error sending message');
    } finally {
      setSendingMessage(false);
    }
  };

  const handleEndChat = async () => {
    if (!selectedPhone) return;

    if (!window.confirm('Are you sure you want to end this chat support session?')) return;

    try {
      const response = await apiClient.post(
        `/api/admin/conversations/${selectedPhone}/chat-support/end`,
        { message: 'Chat support session has been ended by admin.' }
      );

      if (response.status === 'success') {
        setIsChatSupport(false);
        setMessageInput('');
        setError(null);
        // Refresh conversations
        const convResponse = await apiClient.get('/api/admin/conversations');
        if (convResponse.status === 'success') {
          setConversations(convResponse.data);
        }
      } else {
        setError(response.message || 'Failed to end chat');
      }
    } catch (err: any) {
      setError(err.message || 'Error ending chat');
    }
  };

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
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 h-[calc(100vh-200px)]">
        {/* Conversations List */}
        <div className={`${showChat ? 'hidden md:flex' : 'flex'} md:col-span-1 bg-white rounded-lg shadow overflow-hidden flex flex-col`}>
          <div className="bg-green-600 text-white p-4">
            <h2 className="text-base sm:text-lg font-bold">
              <i className="fab fa-whatsapp mr-2"></i>Messages
            </h2>
            <p className="text-green-100 text-xs sm:text-sm">{conversations.length} conversations</p>
          </div>

          <div className="overflow-y-auto flex-1">
            {conversations.length === 0 ? (
              <div className="p-6 text-center text-gray-500">
                <p className="text-sm">No conversations yet</p>
              </div>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.phone_number}
                  onClick={() => {
                    setSelectedPhone(conv.phone_number);
                    setShowChat(true);
                  }}
                  className={`p-3 sm:p-4 border-b cursor-pointer transition ${
                    selectedPhone === conv.phone_number
                      ? 'bg-green-50 border-l-4 border-green-600'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="flex justify-between items-start gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <p className="font-bold text-gray-800 text-sm sm:text-base truncate">
                          {conv.student_name || conv.phone_number}
                        </p>
                        {conv.is_chat_support && (
                          <span className="inline-block px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded font-semibold">
                            💬
                          </span>
                        )}
                        {conv.type === 'student' && (
                          <span className="inline-block px-2 py-0.5 bg-green-100 text-green-800 text-xs rounded">
                            S
                          </span>
                        )}
                        {conv.type === 'lead' && (
                          <span className="inline-block px-2 py-0.5 bg-yellow-100 text-yellow-800 text-xs rounded">
                            L
                          </span>
                        )}
                      </div>
                      <p className="text-xs sm:text-sm text-gray-600 truncate">{conv.last_message}</p>
                    </div>
                    {conv.is_active && (
                      <span className="inline-block w-2.5 h-2.5 bg-green-500 rounded-full flex-shrink-0 mt-1"></span>
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
        <div className={`${showChat ? 'flex' : 'hidden'} md:flex md:col-span-2 bg-white rounded-lg shadow overflow-hidden flex flex-col`}>
          {selectedPhone ? (
            <>
              {/* Chat Header */}
              <div className="bg-green-600 text-white p-3 sm:p-4 flex justify-between items-center gap-2 sm:gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setShowChat(false)}
                      className="md:hidden p-1 hover:bg-green-700 rounded transition"
                    >
                      <i className="fas fa-arrow-left text-lg"></i>
                    </button>
                    <div className="min-w-0">
                      <p className="font-bold text-sm sm:text-base truncate">
                        {conversations.find((c) => c.phone_number === selectedPhone)?.student_name ||
                          selectedPhone}
                      </p>
                      <p className="text-green-100 text-xs">
                        {conversations.find((c) => c.phone_number === selectedPhone)?.is_active
                          ? 'Active now'
                          : 'Offline'}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="flex gap-1 sm:gap-2 flex-shrink-0">
                  <button className="p-2 hover:bg-green-700 rounded-full transition hidden sm:block">
                    <i className="fas fa-phone"></i>
                  </button>
                  <button className="p-2 hover:bg-green-700 rounded-full transition hidden sm:block">
                    <i className="fas fa-video"></i>
                  </button>
                  <button className="p-2 hover:bg-green-700 rounded-full transition">
                    <i className="fas fa-info-circle"></i>
                  </button>
                </div>
              </div>

              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-3 sm:p-4 bg-gradient-to-b from-gray-50 to-white">
                {messages.length === 0 ? (
                  <div className="flex items-center justify-center h-full text-gray-400">
                    <div className="text-center">
                      <i className="fab fa-whatsapp text-4xl sm:text-6xl mb-4 text-green-200"></i>
                      <p className="text-sm">No messages yet</p>
                    </div>
                  </div>
                ) : (
                  messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`mb-2 sm:mb-3 flex ${msg.sender_type === 'user' ? 'justify-start' : 'justify-end'}`}
                    >
                      <div
                        className={`max-w-xs sm:max-w-sm px-3 sm:px-4 py-2 rounded-lg text-sm ${
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
              <div className="p-3 sm:p-4 border-t bg-gray-50 space-y-2 sm:space-y-3">
                {isChatSupport ? (
                  <>
                    <div className="flex items-center gap-2 sm:gap-3">
                      <button className="text-green-600 hover:text-green-700 text-lg sm:text-xl flex-shrink-0">
                        <i className="fas fa-plus-circle"></i>
                      </button>
                      <input
                        type="text"
                        placeholder="Type message..."
                        value={messageInput}
                        onChange={(e) => setMessageInput(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            handleSendMessage();
                          }
                        }}
                        disabled={sendingMessage}
                        className="flex-1 px-3 sm:px-4 py-2 text-sm border border-gray-300 rounded-full bg-white focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                      <button
                        onClick={handleSendMessage}
                        disabled={sendingMessage || !messageInput.trim()}
                        className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-full p-2 font-medium transition flex-shrink-0"
                      >
                        {sendingMessage ? (
                          <i className="fas fa-spinner fa-spin text-sm"></i>
                        ) : (
                          <i className="fas fa-paper-plane text-sm"></i>
                        )}
                      </button>
                    </div>
                    <button
                      onClick={handleEndChat}
                      className="w-full bg-red-600 hover:bg-red-700 text-white px-3 sm:px-4 py-2 rounded text-sm sm:text-base font-medium transition"
                    >
                      <i className="fas fa-times mr-2"></i>End Chat
                    </button>
                    <p className="text-xs text-green-700">
                      ✓ Chat support is active - You can send and receive messages
                    </p>
                  </>
                ) : (
                  <>
                    <div className="flex items-center gap-2 sm:gap-3">
                      <button className="text-green-600 hover:text-green-700 text-lg sm:text-xl flex-shrink-0">
                        <i className="fas fa-plus-circle"></i>
                      </button>
                      <input
                        type="text"
                        placeholder="Read-only..."
                        disabled
                        className="flex-1 px-3 sm:px-4 py-2 text-sm border border-gray-300 rounded-full bg-white"
                      />
                      <button className="text-green-600 hover:text-green-700 text-lg sm:text-xl flex-shrink-0">
                        <i className="fas fa-microphone"></i>
                      </button>
                    </div>
                    <p className="text-xs text-gray-500">
                      Messages are read-only - Not in active chat support
                    </p>
                  </>
                )}
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-400">
              <div className="text-center px-4">
                <i className="fab fa-whatsapp text-4xl sm:text-6xl mb-4 text-gray-300"></i>
                <p className="text-sm">Select a conversation to view messages</p>
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
