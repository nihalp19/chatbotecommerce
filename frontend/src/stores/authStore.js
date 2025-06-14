import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authAPI } from '../services/api';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      loading: true,
      isAuthenticated: false,

      login: async (username, password) => {
        try {
          const response = await authAPI.login(username, password);
          localStorage.setItem('token', response.access_token);
          set({ 
            user: response.user, 
            isAuthenticated: true,
            loading: false 
          });
          return true;
        } catch (error) {
          set({ loading: false });
          return false;
        }
      },

      register: async (username, email, password) => {
        try {
          const response = await authAPI.register(username, email, password);
          localStorage.setItem('token', response.access_token);
          set({ 
            user: response.user, 
            isAuthenticated: true,
            loading: false 
          });
          return true;
        } catch (error) {
          set({ loading: false });
          return false;
        }
      },

      logout: () => {
        localStorage.removeItem('token');
        set({ 
          user: null, 
          isAuthenticated: false,
          loading: false 
        });
      },

      checkAuthStatus: async () => {
        try {
          const token = localStorage.getItem('token');
          if (token) {
            const userData = await authAPI.getProfile();
            set({ 
              user: userData, 
              isAuthenticated: true,
              loading: false 
            });
          } else {
            set({ loading: false });
          }
        } catch (error) {
          localStorage.removeItem('token');
          set({ 
            user: null, 
            isAuthenticated: false,
            loading: false 
          });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        user: state.user,
        isAuthenticated: state.isAuthenticated 
      }),
    }
  )
);
