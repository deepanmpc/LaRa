import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useAuthStore = create(
    persist(
        (set) => ({
            token: null,
            role: null,
            isAuthenticated: false,
            login: (token, role) => set({ token, role, isAuthenticated: true }),
            logout: () => set({ token: null, role: null, isAuthenticated: false }),
        }),
        {
            name: 'lara-auth-storage', // saves to localStorage
        }
    )
);
