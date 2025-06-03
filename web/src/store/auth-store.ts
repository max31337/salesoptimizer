import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import Cookies from 'js-cookie'
import { User, AuthState, LoginRequest, LoginResponse } from '@/types/auth'
import api from '@/lib/api'

interface AuthStore extends AuthState {
  login: (credentials: LoginRequest) => Promise<void>
  logout: () => void
  setUser: (user: User | null) => void
  setLoading: (loading: boolean) => void
  checkAuth: () => Promise<void>
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (credentials: LoginRequest) => {
        try {
          set({ isLoading: true })
          
          const response = await api.post<LoginResponse>('/api/v1/auth/login', credentials)
          const { access_token, refresh_token, user } = response.data

          // Store tokens in cookies
          Cookies.set('access_token', access_token, { expires: 1 }) // 1 day
          Cookies.set('refresh_token', refresh_token, { expires: 7 }) // 7 days

          set({
            user,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: () => {
        Cookies.remove('access_token')
        Cookies.remove('refresh_token')
        set({
          user: null,
          isAuthenticated: false,
          isLoading: false,
        })
      },

      setUser: (user: User | null) => {
        set({
          user,
          isAuthenticated: !!user,
        })
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading })
      },

      checkAuth: async () => {
        const token = Cookies.get('access_token')
        if (!token) {
          set({ user: null, isAuthenticated: false })
          return
        }

        try {
          set({ isLoading: true })
          const response = await api.get<User>('/api/v1/auth/me')
          set({
            user: response.data,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error) {
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
          })
          Cookies.remove('access_token')
          Cookies.remove('refresh_token')
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)