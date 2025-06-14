import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: async (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await api.post('/auth/login', formData);
    return response.data;
  },

  register: async (username, email, password) => {
    const response = await api.post('/auth/register', {
      username,
      email,
      password,
    });
    return response.data;
  },

  getProfile: async () => {
    const response = await api.get('/auth/profile');
    return response.data;
  },
};

export const productAPI = {
  search: async (query, filters) => {
    const response = await api.get('/products/search', {
      params: { q: query, ...filters },
    });
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/products/${id}`);
    return response.data;
  },

  getCategories: async () => {
    const response = await api.get('/products/categories');
    return response.data;
  },

  getBrands: async () => {
    const response = await api.get('/products/brands');
    return response.data;
  },

  getFeatured: async () => {
    const response = await api.get('/products/featured');
    return response.data;
  },

  getTrending: async () => {
    const response = await api.get('/products/trending');
    return response.data;
  },
};

export const chatAPI = {
  sendMessage: async (message, sessionId) => {
    const response = await api.post('/chat/message', {
      message,
      session_id: sessionId,
    });
    return response.data;
  },

  getSession: async (sessionId) => {
    const response = await api.get(`/chat/session/${sessionId}`);
    return response.data;
  },

  getSessions: async () => {
    const response = await api.get('/chat/sessions');
    return response.data;
  },
};
