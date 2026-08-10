import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

const client = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 120000, // 2 min — Ollama can be slow locally
});

// Response interceptor — normalize errors for UI consumption
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!error.response) {
      return Promise.reject(new Error('Unable to connect to the workforce service. Please ensure the backend is running.'));
    }
    const detail = error.response?.data?.detail || error.response?.statusText || 'An unexpected error occurred.';
    return Promise.reject(new Error(detail));
  }
);

export default client;
