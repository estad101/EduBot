'use client';

import { useEffect, useState, useRef } from 'react';
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
  sender_type: 'user' | 'bot' | 'admin';
  message_type: string;
}

interface ChatSupportSession {
  phone_number: string;
  is_active: boolean;
  started_at: string;
  admin_name?: string;
  message_count: number;
}

export default function ConversationsPage() {
  const router = useRouter();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedPhone, setSelectedPhone] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [messageInput, setMessageInput] = useState('');
  const [sendingMessage, setSendingMessage] = useState(false);
  const [isChatSupport, setIsChatSupport] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [chatSession, setChatSession] = useState<ChatSupportSession | null>(null);
  const [activatingChat, setActivatingChat] = useState(false);
  const [endingChat, setEndingChat] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<number>(Date.now());

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Fetch conversations on mount and periodically
  useEffect(() => {
    fetchConversations();
    const interval = setInterval(fetchConversations, 8000); // Refresh every 8 seconds
    return () => clearInterval(interval);
  }, [router]);

  // Fetch messages when selected phone changes
  useEffect(() => {
    if (selectedPhone) {
      fetchMessages();
      const interval = setInterval(fetchMessages, 4000); // Refresh every 4 seconds
      return () => clearInterval(interval);
    }
    return undefined;
  }, [selectedPhone]);

  const fetchConversations = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      if (!token) {
        router.push('/login');
        return;
      }

      const response = await apiClient.get('/api/admin/conversations');
      if (response.status === 'success') {
        setConversations(response.data || []);
        setError(null);
      }
    } catch (err: any) {
      console.error('Failed to fetch conversations:', err);
      setError(err.message || 'Failed to load conversations');
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async () => {
    if (!selectedPhone) return;

    try {
      setRefreshing(true);
      const response = await apiClient.get(`/api/admin/conversations/${selectedPhone}/messages`);
      if (response.status === 'success') {
        setMessages(response.data || []);
      }

      // Check if this is a chat support conversation
      const conv = conversations.find(c => c.phone_number === selectedPhone);
      setIsChatSupport(conv?.is_chat_support || false);
      setChatSession({
        phone_number: selectedPhone,
        is_active: conv?.is_chat_support || false,
        started_at: new Date().toISOString(),
        message_count: conv?.message_count || 0
      });
    } catch (err: any) {
      console.error('Failed to fetch messages:', err);
    } finally {
      setRefreshing(false);
      setLastRefresh(Date.now());
    }
  };

  const handleStartChatSupport = async () => {
    if (!selectedPhone) return;

    setActivatingChat(true);
    try {
      const response = await apiClient.post(
        `/api/admin/conversations/${selectedPhone}/chat-support/start`,
        { admin_message: 'Chat support session started. How can I help you today?' }
      );

      if (response.status === 'success') {
        setIsChatSupport(true);
        setError(null);
        fetchMessages();
        fetchConversations();
      } else {
        setError(response.message || 'Failed to start chat support');
      }
    } catch (err: any) {
      setError(err.message || 'Error starting chat support');
      console.error('Error:', err);
    } finally {
      setActivatingChat(false);
    }
  };

  const handleSendMessage = async () => {
    if (!messageInput.trim() || !selectedPhone || !isChatSupport) return;

    const messageText = messageInput.trim();
    setSendingMessage(true);
    
    try {
      const response = await apiClient.post(
        `/api/admin/conversations/${selectedPhone}/chat-support/send`,
        { message: messageText, sender_type: 'admin' }
      );

      if (response.status === 'success') {
        setMessageInput('');
        setError(null);
        await fetchMessages();
      } else {
        setError(response.message || 'Failed to send message');
      }
    } catch (err: any) {
      setError(err.message || 'Error sending message');
      console.error('Error:', err);
    } finally {
      setSendingMessage(false);
    }
  };

  const handleEndChat = async () => {
    if (!selectedPhone || !isChatSupport) return;

    const confirm = window.confirm(
      'Are you sure you want to end this chat support session? The user will be notified.'
    );
    if (!confirm) return;

    setEndingChat(true);
    try {
      const response = await apiClient.post(
        `/api/admin/conversations/${selectedPhone}/chat-support/end`,
        { 
          admin_message: 'Thank you for contacting us. This chat support session has been closed.',
          ended_by: 'admin'
        }
      );

      if (response.status === 'success') {
        setIsChatSupport(false);
        setMessageInput('');
        setError(null);
        setChatSession(null);
        await fetchMessages();
        await fetchConversations();
        alert('✓ Chat support session ended successfully');
      } else {
        setError(response.message || 'Failed to end chat');
      }
    } catch (err: any) {
      setError(err.message || 'Error ending chat');
      console.error('Error:', err);
    } finally {
      setEndingChat(false);
    }
  };

  // Format timestamp
  const formatTime = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
      });
    } catch {
      return '';
    }
  };

  // Format message content
  const MessageContent = ({ text, senderType }: { text: string; senderType: string }) => {
    const cleanText = text.replace(/\*\*/g, '').replace(/\*/g, '');
    const lines = cleanText.split('\n');
    
    return (
      <div className="break-words whitespace-pre-wrap">
        {lines.map((line, idx) => {
          if (line.trim().startsWith('•')) {
            const commandText = line.trim().substring(1).trim();
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
        <div className={`${showChat ? 'hidden md:flex' : 'flex'} md:col-span-1 bg-white rounded-lg shadow overflow-hidden flex flex-col border border-gray-200`}>
          <div className="bg-gradient-to-r from-green-600 to-green-700 text-white p-4">
            <h2 className="text-base sm:text-lg font-bold flex items-center gap-2">
              <i className="fab fa-whatsapp"></i>Chat Support
            </h2>
            <p className="text-green-100 text-xs sm:text-sm">{conversations.length} active conversations</p>
          </div>

          <div className="overflow-y-auto flex-1">
            {conversations.length === 0 ? (
              <div className="p-6 text-center text-gray-500">
                <i className="fas fa-inbox text-3xl mb-2 text-gray-300"></i>
                <p className="text-sm font-medium">No conversations</p>
                <p className="text-xs text-gray-400 mt-1">Messages will appear here</p>
              </div>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.phone_number}
                  onClick={() => {
                    setSelectedPhone(conv.phone_number);
                    setShowChat(true);
                  }}
                  className={`p-3 sm:p-4 border-b cursor-pointer transition hover:bg-gray-50 ${
                    selectedPhone === conv.phone_number
                      ? 'bg-green-50 border-l-4 border-green-600'
                      : ''
                  }`}
                >
                  <div className="flex justify-between items-start gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <p className="font-bold text-gray-800 text-sm truncate">
                          {conv.student_name || 'Unknown'}
                        </p>
                        {conv.is_chat_support && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded-full font-semibold">
                            <i className="fas fa-comments text-xs"></i>
                            Chat
                          </span>
                        )}
                      </div>
                      <p className="text-xs sm:text-sm text-gray-600 truncate mt-1">{conv.last_message}</p>
                      <p className="text-xs text-gray-400 mt-1">
                        {new Date(conv.last_message_time).toLocaleString()}
                      </p>
                    </div>
                    {conv.is_active && (
                      <span className="inline-block w-3 h-3 bg-green-500 rounded-full flex-shrink-0 mt-1 animate-pulse"></span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Chat View */}
        <div className={`${showChat ? 'flex' : 'hidden'} md:flex md:col-span-2 bg-white rounded-lg shadow overflow-hidden flex flex-col border border-gray-200`}>
          {selectedPhone ? (
            <>
              {/* Chat Header */}
              <div className="bg-gradient-to-r from-green-600 to-green-700 text-white p-3 sm:p-4 flex justify-between items-center gap-2 border-b border-green-800">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setShowChat(false)}
                      className="md:hidden p-2 hover:bg-green-700 rounded transition"
                      title="Back"
                    >
                      <i className="fas fa-arrow-left"></i>
                    </button>
                    <div className="min-w-0">
                      <p className="font-bold text-sm sm:text-base truncate">
                        {conversations.find((c) => c.phone_number === selectedPhone)?.student_name || selectedPhone}
                      </p>
                      <p className="text-green-100 text-xs flex items-center gap-1">
                        {conversations.find((c) => c.phone_number === selectedPhone)?.is_active ? (
                          <>
                            <span className="inline-block w-2 h-2 bg-green-400 rounded-full"></span>
                            Active
                          </>
                        ) : (
                          'Offline'
                        )}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="flex gap-1 sm:gap-2 flex-shrink-0">
                  {isChatSupport && (
                    <span className="text-xs bg-blue-500 px-2 py-1 rounded whitespace-nowrap">
                      💬 Chat Active
                    </span>
                  )}
                </div>
              </div>

              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-3 sm:p-4 space-y-3 bg-gray-50">
                {messages.length === 0 ? (
                  <div className="flex items-center justify-center h-full text-gray-400">
                    <div className="text-center">
                      <i className="fab fa-whatsapp text-4xl sm:text-6xl mb-4 text-gray-200"></i>
                      <p className="text-sm">No messages yet</p>
                      {!isChatSupport && (
                        <p className="text-xs text-gray-400 mt-1">Start chat to begin</p>
                      )}
                    </div>
                  </div>
                ) : (
                  <>
                    {messages.map((msg) => (
                      <div
                        key={msg.id}
                        className={`flex ${msg.sender_type === 'user' ? 'justify-start' : 'justify-end'}`}
                      >
                        <div
                          className={`max-w-xs sm:max-w-md px-3 sm:px-4 py-2.5 rounded-lg text-sm ${
                            msg.sender_type === 'user'
                              ? 'bg-white border border-gray-200 text-gray-800 rounded-tl-none'
                              : msg.sender_type === 'admin'
                              ? 'bg-blue-600 text-white rounded-tr-none'
                              : 'bg-green-600 text-white rounded-tr-none'
                          }`}
                        >
                          {msg.sender_type === 'admin' && (
                            <p className="text-xs font-semibold text-blue-100 mb-1">You</p>
                          )}
                          <MessageContent text={msg.text} senderType={msg.sender_type} />
                          <p
                            className={`text-xs mt-1.5 font-medium ${
                              msg.sender_type === 'user'
                                ? 'text-gray-400'
                                : 'text-blue-100'
                            }`}
                          >
                            {formatTime(msg.timestamp)}
                          </p>
                        </div>
                      </div>
                    ))}
                    <div ref={messagesEndRef} />
                  </>
                )}
              </div>

              {/* Input Area */}
              <div className="p-3 sm:p-4 border-t bg-white space-y-2 sm:space-y-3">
                {isChatSupport ? (
                  <>
                    <div className="flex items-center gap-2 sm:gap-3">
                      <input
                        type="text"
                        placeholder="Type your message..."
                        value={messageInput}
                        onChange={(e) => setMessageInput(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            handleSendMessage();
                          }
                        }}
                        disabled={sendingMessage || refreshing}
                        autoFocus
                        className="flex-1 px-3 sm:px-4 py-2.5 text-sm border border-gray-300 rounded-full bg-white focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100"
                      />
                      <button
                        onClick={handleSendMessage}
                        disabled={sendingMessage || !messageInput.trim() || refreshing}
                        className="bg-green-600 hover:bg-green-700 disabled:bg-gray-300 text-white rounded-full p-2.5 font-medium transition flex-shrink-0 disabled:cursor-not-allowed"
                        title="Send message"
                      >
                        {sendingMessage ? (
                          <i className="fas fa-spinner fa-spin text-sm"></i>
                        ) : (
                          <i className="fas fa-paper-plane text-sm"></i>
                        )}
                      </button>
                    </div>

                    <div className="flex gap-2">
                      <button
                        onClick={handleEndChat}
                        disabled={endingChat}
                        className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-300 text-white px-3 sm:px-4 py-2 rounded text-sm font-medium transition disabled:cursor-not-allowed"
                      >
                        {endingChat ? (
                          <><i className="fas fa-spinner fa-spin mr-2"></i>Ending...</>
                        ) : (
                          <><i className="fas fa-times mr-2"></i>End Chat</>
                        )}
                      </button>
                      <button
                        onClick={fetchMessages}
                        disabled={refreshing}
                        className="px-3 py-2 border border-gray-300 rounded text-sm font-medium transition hover:bg-gray-50 disabled:bg-gray-100"
                        title="Refresh messages"
                      >
                        <i className={`fas fa-redo ${refreshing ? 'fa-spin' : ''}`}></i>
                      </button>
                    </div>

                    <div className="bg-green-50 border border-green-200 rounded-lg p-2 text-xs text-green-700 flex items-center gap-2">
                      <i className="fas fa-check-circle flex-shrink-0"></i>
                      <span>Chat support active • You can send and receive messages</span>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="flex items-center gap-2 sm:gap-3">
                      <input
                        type="text"
                        placeholder="Start chat to send messages..."
                        disabled
                        className="flex-1 px-3 sm:px-4 py-2.5 text-sm border border-gray-300 rounded-full bg-gray-100 text-gray-500"
                      />
                      <button
                        disabled
                        className="bg-gray-300 text-white rounded-full p-2.5 font-medium flex-shrink-0 cursor-not-allowed"
                      >
                        <i className="fas fa-paper-plane text-sm"></i>
                      </button>
                    </div>

                    <button
                      onClick={handleStartChatSupport}
                      disabled={activatingChat}
                      className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white px-3 sm:px-4 py-2.5 rounded text-sm font-medium transition disabled:cursor-not-allowed"
                    >
                      {activatingChat ? (
                        <><i className="fas fa-spinner fa-spin mr-2"></i>Starting...</>
                      ) : (
                        <><i className="fas fa-comments mr-2"></i>Start Chat Support</>
                      )}
                    </button>

                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-2 text-xs text-blue-700 flex items-center gap-2">
                      <i className="fas fa-info-circle flex-shrink-0"></i>
                      <span>Click "Start Chat Support" to begin live messaging</span>
                    </div>
                  </>
                )}
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-400">
              <div className="text-center px-4">
                <i className="fab fa-whatsapp text-4xl sm:text-6xl mb-4 text-gray-200"></i>
                <p className="text-sm font-medium">Select a conversation</p>
                <p className="text-xs text-gray-400 mt-1">Choose from the list to view and manage chat</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="fixed bottom-6 right-6 bg-red-600 text-white rounded-lg shadow-lg p-4 max-w-sm">
          <div className="flex items-start gap-3">
            <i className="fas fa-exclamation-circle text-lg flex-shrink-0 mt-0.5"></i>
            <div>
              <p className="font-medium text-sm">{error}</p>
              <button
                onClick={() => setError(null)}
                className="text-xs mt-2 opacity-80 hover:opacity-100 underline"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}
