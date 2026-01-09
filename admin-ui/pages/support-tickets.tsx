'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import Layout from '../components/Layout';
import { apiClient } from '../lib/api-client';

interface SupportMessage {
  id: number;
  ticket_id: number;
  sender_type: string;
  sender_name: string;
  message: string;
  created_at: string;
}

interface SupportTicket {
  id: number;
  phone_number: string;
  sender_name: string;
  issue_description: string;
  status: string;
  priority: string;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
  messages: SupportMessage[];
}

export default function SupportTicketsPage() {
  const router = useRouter();
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [selectedTicket, setSelectedTicket] = useState<SupportTicket | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newMessage, setNewMessage] = useState('');
  const [sendingMessage, setSendingMessage] = useState(false);

  const fetchTickets = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      if (!token) {
        router.push('/login');
        return;
      }

      const response = await apiClient.getOpenSupportTickets(0, 50);
      // Handle both response structures
      if (response.tickets) {
        // Response has tickets array
        setTickets(response.tickets);
      } else if (Array.isArray(response)) {
        // Response is directly an array
        setTickets(response);
      } else if (response.data && Array.isArray(response.data)) {
        // Response has data property with array
        setTickets(response.data);
      } else {
        setTickets([]);
      }
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load support tickets');
      console.error('Error fetching tickets:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTickets();
    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchTickets, 10000);
    return () => clearInterval(interval);
  }, [router]);

  const handleSelectTicket = async (ticket: SupportTicket) => {
    try {
      const response = await apiClient.getSupportTicket(ticket.id);
      // Handle different response structures
      if (response.id) {
        // Response is the ticket directly
        setSelectedTicket(response);
      } else if (response.data && response.data.id) {
        // Response has data property
        setSelectedTicket(response.data);
      }
      setNewMessage('');
    } catch (err) {
      console.error('Error loading ticket:', err);
      setError('Failed to load ticket details');
    }
  };

  const handleSendMessage = async () => {
    if (!selectedTicket || !newMessage.trim()) return;

    try {
      setSendingMessage(true);
      const response = await apiClient.addSupportMessage(selectedTicket.id, newMessage.trim());
      
      setNewMessage('');
      // Refresh the selected ticket regardless of response structure
      const ticketResponse = await apiClient.getSupportTicket(selectedTicket.id);
      if (ticketResponse.id) {
        setSelectedTicket(ticketResponse);
      } else if (ticketResponse.data && ticketResponse.data.id) {
        setSelectedTicket(ticketResponse.data);
      }
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message');
    } finally {
      setSendingMessage(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <i className="fas fa-spinner fa-spin text-4xl text-blue-600 mb-4"></i>
            <p className="text-gray-600">Loading support tickets...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-200px)]">
        {/* Tickets List */}
        <div className="lg:col-span-1 bg-white rounded-lg shadow overflow-hidden flex flex-col">
          <div className="bg-yellow-600 text-white p-4">
            <h2 className="text-lg font-bold">
              <i className="fas fa-ticket-alt mr-2"></i>Support Tickets
            </h2>
            <p className="text-yellow-100 text-sm mt-1">
              {tickets.length} open ticket{tickets.length !== 1 ? 's' : ''}
            </p>
          </div>

          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4">
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}

          <div className="flex-1 overflow-y-auto divide-y">
            {tickets.length === 0 ? (
              <div className="p-6 text-center text-gray-500">
                <i className="fas fa-inbox text-4xl mb-4 block opacity-30"></i>
                <p>No open support tickets</p>
              </div>
            ) : (
              tickets.map((ticket) => (
                <button
                  key={ticket.id}
                  onClick={() => handleSelectTicket(ticket)}
                  className={`w-full text-left p-4 hover:bg-gray-50 transition ${
                    selectedTicket?.id === ticket.id ? 'bg-yellow-50 border-l-4 border-yellow-600' : ''
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate">{ticket.sender_name || 'Anonymous'}</p>
                      <p className="text-xs text-gray-600 mt-1 line-clamp-2">{ticket.issue_description}</p>
                      <p className="text-xs text-gray-400 mt-2">
                        {new Date(ticket.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs font-semibold whitespace-nowrap ${
                      ticket.priority === 'HIGH' ? 'bg-red-100 text-red-800' :
                      ticket.priority === 'URGENT' ? 'bg-red-200 text-red-900' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {ticket.priority}
                    </span>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Ticket Detail */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow overflow-hidden flex flex-col">
          {selectedTicket ? (
            <>
              {/* Header */}
              <div className="bg-gradient-to-r from-yellow-600 to-yellow-700 text-white p-6 border-b">
                <div className="flex justify-between items-start gap-4">
                  <div>
                    <h3 className="text-2xl font-bold">Ticket #{selectedTicket.id}</h3>
                    <p className="text-yellow-100 text-sm mt-2">
                      <i className="fas fa-phone mr-2"></i>{selectedTicket.phone_number}
                    </p>
                  </div>
                  <span className={`px-4 py-2 rounded-lg font-semibold text-sm ${
                    selectedTicket.status === 'OPEN' ? 'bg-yellow-100 text-yellow-800' :
                    selectedTicket.status === 'IN_PROGRESS' ? 'bg-blue-100 text-blue-800' :
                    selectedTicket.status === 'RESOLVED' ? 'bg-green-100 text-green-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {selectedTicket.status}
                  </span>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
                <div className="space-y-4">
                  {selectedTicket.messages.length === 0 ? (
                    <p className="text-center text-gray-500 py-8">No messages yet</p>
                  ) : (
                    selectedTicket.messages.map((msg) => (
                      <div key={msg.id} className={`flex ${msg.sender_type === 'admin' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-lg ${
                          msg.sender_type === 'admin'
                            ? 'bg-yellow-600 text-white rounded-br-none'
                            : 'bg-white text-gray-900 border border-gray-200 rounded-bl-none'
                        }`}>
                          {msg.sender_type === 'user' && (
                            <p className="text-xs font-semibold mb-1 opacity-75">
                              {msg.sender_name}
                            </p>
                          )}
                          <p className="text-sm whitespace-pre-wrap break-words">{msg.message}</p>
                          <p className={`text-xs mt-2 ${
                            msg.sender_type === 'admin' ? 'text-yellow-100' : 'text-gray-500'
                          }`}>
                            {new Date(msg.created_at).toLocaleTimeString('en-US', {
                              hour: '2-digit',
                              minute: '2-digit',
                              hour12: true
                            })}
                          </p>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Message Input */}
              <div className="border-t bg-white p-4">
                <div className="flex gap-2">
                  <textarea
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && e.ctrlKey) {
                        handleSendMessage();
                      }
                    }}
                    placeholder="Type your response... (Ctrl+Enter to send)"
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-600 resize-none"
                    rows={3}
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={!newMessage.trim() || sendingMessage}
                    className="px-4 py-3 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-300 text-white rounded-lg font-medium transition"
                  >
                    <i className={`fas ${sendingMessage ? 'fa-spinner fa-spin' : 'fa-paper-plane'} mr-2`}></i>
                    Send
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-400">
              <div className="text-center">
                <i className="fas fa-ticket-alt text-6xl mb-4 opacity-20"></i>
                <p>Select a support ticket to view and respond</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
