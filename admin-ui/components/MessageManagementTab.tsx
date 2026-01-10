import React, { useState, useEffect } from 'react';
import { apiClient } from '../lib/api-client';

interface MenuItem {
  id: string;
  label: string;
  action: string;
  emoji?: string;
  description?: string;
}

interface BotMessage {
  id: number;
  message_key: string;
  message_type: string;
  context: string;
  content: string;
  has_menu: boolean;
  menu_items: MenuItem[];
  next_states: string[];
  is_active: boolean;
  description: string;
  variables: string[];
}

interface WorkflowNode {
  id: string;
  label: string;
  type: string;
  context: string;
}

interface WorkflowEdge {
  from: string;
  to: string;
  trigger: string;
  condition?: string;
  description?: string;
}

const MessageManagementTab: React.FC = () => {
  const [messages, setMessages] = useState<BotMessage[]>([]);
  const [diagram, setDiagram] = useState<{ nodes: WorkflowNode[]; edges: WorkflowEdge[] } | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'list' | 'create' | 'workflow'>('list');
  const [selectedMessage, setSelectedMessage] = useState<BotMessage | null>(null);
  const [editMode, setEditMode] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    message_key: '',
    message_type: 'prompt',
    context: 'IDLE',
    content: '',
    has_menu: false,
    menu_items: [] as MenuItem[],
    next_states: [] as string[],
    description: ''
  });

  useEffect(() => {
    fetchMessages();
    fetchWorkflowDiagram();
  }, []);

  const fetchMessages = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/api/messages/list');
      if (response.data?.data?.messages) {
        setMessages(response.data.data.messages);
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchWorkflowDiagram = async () => {
    try {
      const response = await apiClient.get('/api/messages/workflow/diagram');
      if (response.data?.data) {
        setDiagram(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching workflow:', error);
    }
  };

  const handleSaveMessage = async () => {
    try {
      if (editMode && selectedMessage) {
        await apiClient.put(`/api/messages/${selectedMessage.message_key}/update`, formData);
      } else {
        await apiClient.post('/api/messages/create', formData);
      }
      fetchMessages();
      resetForm();
      setActiveTab('list');
    } catch (error) {
      console.error('Error saving message:', error);
    }
  };

  const handleDeleteMessage = async (messageKey: string) => {
    if (confirm('Are you sure you want to delete this message?')) {
      try {
        await apiClient.delete(`/api/messages/${messageKey}`);
        fetchMessages();
      } catch (error) {
        console.error('Error deleting message:', error);
      }
    }
  };

  const handleEditMessage = (message: BotMessage) => {
    setSelectedMessage(message);
    setFormData({
      message_key: message.message_key,
      message_type: message.message_type,
      context: message.context,
      content: message.content,
      has_menu: message.has_menu,
      menu_items: message.menu_items || [],
      next_states: message.next_states || [],
      description: message.description
    });
    setEditMode(true);
    setActiveTab('create');
  };

  const resetForm = () => {
    setFormData({
      message_key: '',
      message_type: 'prompt',
      context: 'IDLE',
      content: '',
      has_menu: false,
      menu_items: [],
      next_states: [],
      description: ''
    });
    setSelectedMessage(null);
    setEditMode(false);
  };

  const addMenuItem = () => {
    setFormData({
      ...formData,
      menu_items: [...formData.menu_items, { id: '', label: '', action: '' }]
    });
  };

  const updateMenuItem = (index: number, field: string, value: string) => {
    const newItems = [...formData.menu_items];
    newItems[index] = { ...newItems[index], [field]: value };
    setFormData({ ...formData, menu_items: newItems });
  };

  const removeMenuItem = (index: number) => {
    setFormData({
      ...formData,
      menu_items: formData.menu_items.filter((_, i) => i !== index)
    });
  };

  const getMessageTypeColor = (type: string) => {
    const colors: { [key: string]: string } = {
      greeting: 'bg-green-100 text-green-800',
      prompt: 'bg-blue-100 text-blue-800',
      confirmation: 'bg-purple-100 text-purple-800',
      menu: 'bg-yellow-100 text-yellow-800',
      error: 'bg-red-100 text-red-800',
      info: 'bg-gray-100 text-gray-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="flex gap-4 border-b">
        <button
          onClick={() => setActiveTab('list')}
          className={`px-4 py-2 ${activeTab === 'list' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600'}`}
        >
          📋 Messages List
        </button>
        <button
          onClick={() => { resetForm(); setActiveTab('create'); }}
          className={`px-4 py-2 ${activeTab === 'create' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600'}`}
        >
          ✏️ {editMode ? 'Edit' : 'Create'} Message
        </button>
        <button
          onClick={() => setActiveTab('workflow')}
          className={`px-4 py-2 ${activeTab === 'workflow' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600'}`}
        >
          🔄 Workflow Diagram
        </button>
      </div>

      {/* Messages List Tab */}
      {activeTab === 'list' && (
        <div className="space-y-4">
          <h2 className="text-2xl font-bold">Bot Messages</h2>
          {loading ? (
            <p>Loading messages...</p>
          ) : (
            <div className="space-y-3">
              {messages.length === 0 ? (
                <p className="text-gray-500">No messages found</p>
              ) : (
                messages.map((msg) => (
                  <div key={msg.id} className="border rounded-lg p-4 hover:shadow-lg transition">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1">
                        <h3 className="font-bold text-lg">{msg.message_key}</h3>
                        <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${getMessageTypeColor(msg.message_type)}`}>
                          {msg.message_type}
                        </span>
                        <span className="ml-2 text-xs text-gray-600">[{msg.context}]</span>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleEditMessage(msg)}
                          className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteMessage(msg.message_key)}
                          className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                        >
                          Delete
                        </button>
                        <button
                          className={`px-3 py-1 rounded ${msg.is_active ? 'bg-green-500 text-white' : 'bg-gray-300'}`}
                        >
                          {msg.is_active ? 'Active' : 'Inactive'}
                        </button>
                      </div>
                    </div>
                    <p className="text-gray-700 mb-2 whitespace-pre-wrap">{msg.content.substring(0, 100)}...</p>
                    {msg.has_menu && msg.menu_items?.length > 0 && (
                      <div className="mt-2">
                        <p className="text-xs font-semibold text-gray-600">Menu Items ({msg.menu_items.length}):</p>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {msg.menu_items.map((item) => (
                            <span key={item.id} className="text-xs bg-gray-200 px-2 py-1 rounded">
                              {item.emoji} {item.label}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      )}

      {/* Create/Edit Message Tab */}
      {activeTab === 'create' && (
        <div className="space-y-4">
          <h2 className="text-2xl font-bold">{editMode ? 'Edit' : 'Create'} Message</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold mb-2">Message Key</label>
              <input
                type="text"
                value={formData.message_key}
                onChange={(e) => setFormData({ ...formData, message_key: e.target.value })}
                disabled={editMode}
                placeholder="e.g., registration_name_prompt"
                className="w-full border rounded px-3 py-2 disabled:bg-gray-100"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Message Type</label>
              <select
                value={formData.message_type}
                onChange={(e) => setFormData({ ...formData, message_type: e.target.value })}
                className="w-full border rounded px-3 py-2"
              >
                <option>greeting</option>
                <option>prompt</option>
                <option>confirmation</option>
                <option>menu</option>
                <option>error</option>
                <option>info</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Context (State)</label>
              <input
                type="text"
                value={formData.context}
                onChange={(e) => setFormData({ ...formData, context: e.target.value })}
                placeholder="e.g., REGISTERING_NAME"
                className="w-full border rounded px-3 py-2"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2">Message Content</label>
            <textarea
              value={formData.content}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              rows={6}
              placeholder="Message text (use {full_name}, {bot_name}, etc. for variables)"
              className="w-full border rounded px-3 py-2 font-mono text-sm"
            />
            <p className="text-xs text-gray-600 mt-2">Preview:</p>
            <div className="bg-gray-100 p-3 rounded whitespace-pre-wrap text-sm">{formData.content}</div>
          </div>

          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.has_menu}
                onChange={(e) => setFormData({ ...formData, has_menu: e.target.checked })}
              />
              <span>This message has menu buttons</span>
            </label>
          </div>

          {formData.has_menu && (
            <div className="border-l-4 border-blue-500 pl-4 py-2">
              <h3 className="font-semibold mb-3">Menu Items</h3>
              <div className="space-y-3">
                {formData.menu_items.map((item, idx) => (
                  <div key={idx} className="border rounded p-3 bg-gray-50">
                    <div className="grid grid-cols-3 gap-2">
                      <input
                        type="text"
                        placeholder="ID"
                        value={item.id}
                        onChange={(e) => updateMenuItem(idx, 'id', e.target.value)}
                        className="border rounded px-2 py-1 text-sm"
                      />
                      <input
                        type="text"
                        placeholder="Label (e.g., 📝 Homework)"
                        value={item.label}
                        onChange={(e) => updateMenuItem(idx, 'label', e.target.value)}
                        className="border rounded px-2 py-1 text-sm"
                      />
                      <input
                        type="text"
                        placeholder="Action"
                        value={item.action}
                        onChange={(e) => updateMenuItem(idx, 'action', e.target.value)}
                        className="border rounded px-2 py-1 text-sm"
                      />
                    </div>
                    <div className="mt-2 flex gap-2">
                      <input
                        type="text"
                        placeholder="Description (optional)"
                        value={item.description || ''}
                        onChange={(e) => updateMenuItem(idx, 'description', e.target.value)}
                        className="flex-1 border rounded px-2 py-1 text-sm"
                      />
                      <button
                        onClick={() => removeMenuItem(idx)}
                        className="px-2 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              <button
                onClick={addMenuItem}
                className="mt-3 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
              >
                + Add Menu Item
              </button>
            </div>
          )}

          <div>
            <label className="block text-sm font-semibold mb-2">Description</label>
            <input
              type="text"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="What is this message for?"
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleSaveMessage}
              className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 font-semibold"
            >
              {editMode ? 'Update Message' : 'Create Message'}
            </button>
            <button
              onClick={resetForm}
              className="px-6 py-2 bg-gray-400 text-white rounded hover:bg-gray-500 font-semibold"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Workflow Diagram Tab */}
      {activeTab === 'workflow' && (
        <div className="space-y-4">
          <h2 className="text-2xl font-bold">Message Workflow Diagram</h2>
          {diagram ? (
            <div className="border rounded-lg p-4 bg-white">
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <h3 className="font-semibold mb-3">Messages ({diagram.nodes.length})</h3>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {diagram.nodes.map((node) => (
                      <div key={node.id} className={`p-2 rounded text-sm ${getMessageTypeColor(node.type)}`}>
                        <strong>{node.label}</strong>
                        <br />
                        <span className="text-xs">[{node.context}]</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h3 className="font-semibold mb-3">Workflows ({diagram.edges.length})</h3>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {diagram.edges.map((edge, idx) => (
                      <div key={idx} className="p-2 rounded text-sm bg-gray-100 border-l-2 border-blue-500">
                        <strong>{edge.from}</strong>
                        <br />
                        <span className="text-xs text-gray-600">↓ ({edge.trigger})</span>
                        <br />
                        <strong>{edge.to}</strong>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-4">
                💡 For advanced visualization with graph rendering, use external tools like Mermaid or Vis.js
              </p>
            </div>
          ) : (
            <p>Loading workflow diagram...</p>
          )}
        </div>
      )}
    </div>
  );
};

export default MessageManagementTab;
