import axios from 'axios';

// In production, use the full URL from env (VITE_API_BASE_URL).
// In dev, fall back to '/api' so the Vite proxy routes to backend.
const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

const api = axios.create({
    baseURL: API_BASE,
    headers: {
        'Content-Type': 'application/json',
    },
});


// Attach JWT before every request
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('lara_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Handle 401 globally - clear auth and redirect
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401 || error.response?.status === 403) {
            localStorage.removeItem('lara_token');
            localStorage.removeItem('lara_user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default api;
