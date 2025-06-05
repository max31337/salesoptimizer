"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api'

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
  login: (credentials: { emailOrUsername: string; password: string }) => Promise<{ user: User }>
  logout: () => Promise<void>
  isAuthenticated: boolean
  checkAuth: () => Promise<void>
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

  // Check authentication status on mount
  const checkAuth = async () => {
    try {
      const userData = await apiClient.get<{
        user_id: string
        email: string
        role: string
        full_name: string
        tenant_id?: string
      }>('/auth/me')
      
      const user: User = {
        id: userData.user_id,
        email: userData.email,
        role: userData.role,
        full_name: userData.full_name,
        first_name: userData.full_name.split(' ')[0] || '',
        last_name: userData.full_name.split(' ').slice(1).join(' ') || '',
        tenant_id: userData.tenant_id
      }
      
      setUser(user)
    } catch (error) {
      // User not authenticated or token expired
      setUser(null)
    }
  }

  useEffect(() => {
    const initAuth = async () => {
      setIsLoading(true)
      await checkAuth()
      setIsLoading(false)
    }
    
    initAuth()
  }, [])

  const login = async (credentials: { emailOrUsername: string; password: string }) => {
    setIsLoading(true)
    try {
      const formData = new URLSearchParams({
        username: credentials.emailOrUsername,
        password: credentials.password,
      })

      const data = await apiClient.postForm<{
        user_id: string
        email: string
        role: string
        full_name: string
        tenant_id?: string
      }>('/auth/login', formData)
      
      const user: User = {
        id: data.user_id,
        email: data.email,
        role: data.role,
        full_name: data.full_name,
        first_name: data.full_name.split(' ')[0] || '',
        last_name: data.full_name.split(' ').slice(1).join(' ') || '',
        tenant_id: data.tenant_id
      }
      
      setUser(user)
      return { user }
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
      await apiClient.post('/auth/logout', {})
      setUser(null)
      router.push('/')
    } catch (error) {
      console.error('Logout error:', error)
      // Clear local state even if backend fails
      setUser(null)
      router.push('/')
    } finally {
      setIsLoading(false)
    }
  }

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    logout,
    isAuthenticated: !!user,
    checkAuth
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}