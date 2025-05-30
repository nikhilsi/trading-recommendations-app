// frontend/src/services/api.js
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with defaults
const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// API methods organized by feature
export const marketApi = {
  scan: (params) => api.get('/api/market/scan', { params }),
};

export const recommendationsApi = {
  get: (params) => api.get('/api/recommendations', { params }),
};

export const watchlistApi = {
  get: () => api.get('/api/watchlist'),
  add: (symbol) => api.post('/api/watchlist', { symbol }),
  remove: (symbol) => api.delete(`/api/watchlist/${symbol}`),
};

export const statsApi = {
  get: () => api.get('/api/stats'),
};

export default api;