import api from './api';

export const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    const data = response.data;
    localStorage.setItem('lara_token', data.token);
    localStorage.setItem('lara_user', JSON.stringify({
        name: data.userName,
        email: data.email,
        role: data.role,
        status: data.status,
    }));
    return data;
};

export const register = async (payload) => {
    const response = await api.post('/auth/register', payload);
    const data = response.data;
    localStorage.setItem('lara_token', data.token);
    localStorage.setItem('lara_user', JSON.stringify({
        name: data.userName,
        email: data.email,
        role: data.role,
        status: data.status,
    }));
    return data;
};

export const logout = () => {
    localStorage.removeItem('lara_token');
    localStorage.removeItem('lara_user');
};

export const getStoredUser = () => {
    try {
        return JSON.parse(localStorage.getItem('lara_user'));
    } catch {
        return null;
    }
};

export const getToken = () => localStorage.getItem('lara_token');
export const isAuthenticated = () => !!getToken();
