"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useRouter } from 'next/navigation'

interface User {
  id: string
  email: string
  role: string
  first_name?: string
  last_name?: string
  tenant_id?: string
  full_name?: string
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (credentials: { emailOrUsername: string; password: string }) => Promise<{ user: User; access_token: string }>
  logout: () => Promise<void>
  isAuthenticated: boolean
  getToken: () => string | null
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  // Check for existing token on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const userData = localStorage.getItem('user_data')
    
    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData)
        setUser(parsedUser)
      } catch (error) {
        console.error('Failed to parse user data:', error)
        // Clear invalid data
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user_data')
      }
    }
    
    setIsLoading(false)
  }, [])

  const login = async (credentials: { emailOrUsername: string; password: string }) => {
    setIsLoading(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: credentials.emailOrUsername, // Backend expects 'username' field
          password: credentials.password,
        }),
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Login failed' }))
        throw new Error(error.detail || 'Login failed')
      }

      const data = await response.json()
      
      const user: User = {
        id: data.user_id,
        email: data.email,
        role: data.role,
        first_name: data.full_name.split(' ')[0] || '',
        last_name: data.full_name.split(' ').slice(1).join(' ') || '',
        tenant_id: data.tenant_id
      }

      // Store tokens and user data
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      localStorage.setItem('user_data', JSON.stringify(user))
      
      setUser(user)

      return {
        user,
        access_token: data.access_token
      }
    } catch (error) {
      console.error('Login error:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    setIsLoading(true)
    try {
      // Call backend logout endpoint if it exists
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/logout`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          })
        } catch (error) {
          console.error('Backend logout failed:', error)
          // Continue with local cleanup even if backend fails
        }
      }

      // Clear all authentication data from localStorage
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_data')

      // Clear user state
      setUser(null)
      
      // Redirect to landing page
      router.push('/')
    } catch (error) {
      console.error('Logout error:', error)
      // Even if something fails, clear local state and redirect
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_data')
      setUser(null)
      router.push('/')
    } finally {
      setIsLoading(false)
    }
  }

  const getToken = () => {
    return localStorage.getItem('access_token')
  }

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    logout,
    isAuthenticated: !!user,
    getToken
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}