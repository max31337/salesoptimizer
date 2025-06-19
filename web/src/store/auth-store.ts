import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import Cookies from 'js-cookie'
import { User, AuthState, LoginRequest, LoginResponse } from '@/types/auth'
import { apiClient } from '@/lib/api'

interface AuthStore extends AuthState {
  login: (credentials: LoginRequest) => Promise<void>
  logout: () => Promise<void>
  setUser: (user: User | null) => void
  setLoading: (loading: boolean) => void
  checkAuth: () => Promise<void>
  refreshAuth: () => Promise<boolean>
  sessionExpired: boolean
  setSessionExpired: (expired: boolean) => void
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      sessionExpired: false,

      login: async (credentials: LoginRequest) => {
        try {
          set({ isLoading: true, sessionExpired: false })
          
          const formData = new URLSearchParams()
          formData.append('username', credentials.emailOrUsername)
          formData.append('password', credentials.password)

          const response = await apiClient.postForm<LoginResponse>('/auth/login', formData)
          const { user } = response

          // Mark as logged in for auth persistence
          localStorage.setItem('salesoptimizer_was_logged_in', 'true')

          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            sessionExpired: false,
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },      logout: async () => {
        try {
          // Call logout endpoint to revoke tokens on server
          await apiClient.post('/auth/logout', {})
        } catch (error) {
          console.error('Server logout failed:', error)
        } finally {
          // Dispatch logout event for WebSocket cleanup
          if (typeof window !== 'undefined') {
            const event = new CustomEvent('auth-logout')
            window.dispatchEvent(event)
          }
          
          // Close WebSocket connection before clearing user state
          try {
            const { slaWebSocketClient } = await import('@/lib/websocket')
            slaWebSocketClient.disconnect()
            console.log('🔌 WebSocket disconnected on logout')
          } catch (error) {
            console.warn('Failed to disconnect WebSocket on logout:', error)
          }
          
          // Clear local state regardless of server response
          Cookies.remove('access_token')
          Cookies.remove('refresh_token')
          localStorage.removeItem('salesoptimizer_was_logged_in')
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            sessionExpired: false,
          })
        }
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

      setSessionExpired: (expired: boolean) => {
        set({ sessionExpired: expired })
      },

      refreshAuth: async () => {
        try {
          // The API client will automatically handle token refresh
          const response = await apiClient.get<User>('/auth/me')
          set({
            user: response,
            isAuthenticated: true,
            sessionExpired: false,
          })
          return true
        } catch (error) {
          console.error('Auth refresh failed:', error)
          set({
            user: null,
            isAuthenticated: false,
            sessionExpired: true,
          })
          return false
        }
      },      checkAuth: async () => {
        // Don't auto-logout on page refresh if user was previously logged in
        const wasLoggedIn = localStorage.getItem('salesoptimizer_was_logged_in') === 'true'
        const hasRefreshToken = document.cookie.split(';').some(cookie => 
          cookie.trim().startsWith('refresh_token=')
        )

        if (!wasLoggedIn || !hasRefreshToken) {
          set({ user: null, isAuthenticated: false })
          return
        }

        try {
          set({ isLoading: true })
          const response = await apiClient.get<User>('/auth/me')
          set({
            user: response,
            isAuthenticated: true,
            isLoading: false,
            sessionExpired: false,
          })
        } catch (error) {
          console.error('Auth check failed:', error)
          // Only clear auth state if it's a definitive failure, not a network issue
          if (error instanceof Error && (error.message.includes('401') || error.message.includes('Unauthorized'))) {
            set({
              user: null,
              isAuthenticated: false,
              sessionExpired: true,
            })
            localStorage.removeItem('salesoptimizer_was_logged_in')
          }
          set({ isLoading: false })
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