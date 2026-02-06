import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  refreshToken: () => api.post('/auth/refresh'),
};

// Conversations API
export const conversationsAPI = {
  getList: (params) => api.get('/conversations', { params }),
  create: (data) => api.post('/conversations', data),
  getDetail: (id) => api.get(`/conversations/${id}`),
  update: (id, data) => api.put(`/conversations/${id}`, data),
  delete: (id) => api.delete(`/conversations/${id}`),
};

// Messages API
export const messagesAPI = {
  getList: (conversationId, params) =>
    api.get(`/conversations/${conversationId}/messages`, { params }),
  send: (conversationId, data) =>
    api.post(`/conversations/${conversationId}/messages`, data),
  sendStream: async (conversationId, content, onChunk, onComplete, onError) => {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}/messages/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ content, stream: true }),
    });

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let hasError = false;
    let hasCompleted = false;

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('event: ')) {
            const event = line.slice(7).trim();
            if (event === 'complete') {
              hasCompleted = true;
            }
            continue;
          }
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            try {
              const parsed = JSON.parse(data);
              if (parsed.content && onChunk) {
                onChunk(parsed.content);
              } else if (parsed.message_id && onComplete) {
                hasCompleted = true;
                onComplete(parsed);
              } else if (parsed.message && onError) {
                onError(parsed.message);
                hasError = true;
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e, data);
            }
          }
        }
      }

      // If stream ended without error but no complete event, trigger completion
      if (!hasError && !hasCompleted && onComplete) {
        onComplete({ message_id: null, created_at: new Date().toISOString() });
      }
    } catch (error) {
      console.error('Stream error:', error);
      if (onError && !hasError) {
        onError(error.message);
      }
    }

    return !hasError;
  },
  delete: (messageId) => api.delete(`/messages/${messageId}`),
};

// Organize API
export const organizeAPI = {
  toDocument: (data) => api.post('/organize/to-document', data),
  getSuggestions: (conversationId) =>
    api.post(`/organize/suggestions?conversation_id=${conversationId}`),
};

// Documents API
export const documentsAPI = {
  getList: (params) => api.get('/documents', { params }),
  getDetail: (id) => api.get(`/documents/${id}`),
  create: (data) => api.post('/documents', data),
  update: (id, data) => api.put(`/documents/${id}`, data),
  delete: (id) => api.delete(`/documents/${id}`),
  search: (params) => api.get('/documents/search', { params }),
};

// Tasks API
export const tasksAPI = {
  getList: (params) => api.get('/tasks', { params }),
  getDetail: (id) => api.get(`/tasks/${id}`),
  create: (data) => api.post('/tasks', data),
  update: (id, data) => api.put(`/tasks/${id}`, data),
  complete: (id) => api.post(`/tasks/${id}/complete`),
  delete: (id) => api.delete(`/tasks/${id}`),
  sendReminder: (id) => api.post(`/tasks/${id}/send-reminder`),
};

// Users API
export const usersAPI = {
  getMe: () => api.get('/users/me'),
  updateMe: (data) => api.put('/users/me', data),
  changePassword: (data) => api.post('/users/change-password', data),
  updateEmailSettings: (data) => api.put('/users/email-settings', data),
};

// AI API
export const aiAPI = {
  getModels: () => api.get('/ai/models'),
  setDefaultModel: (data) => api.put('/ai/models/default', data),
};

export default api;
