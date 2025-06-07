"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { getNameComponents } from '@/utils/nameParser'

interface User {
  id: string
  email: string
  role: string
  first_name?: string
  last_name?: string
  tenant_id?: string
  full_name?: string
  phone?: string
  profile_picture_url?: string
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (credentials: { emailOrUsername: string; password: string }) => Promise<{ user: User }>
  logout: () => Promise<void>
  isAuthenticated: boolean
  checkAuth: () => Promise<void>
  refreshUser: () => Promise<void>
  showSessionExpiredModal: boolean
  dismissSessionExpiredModal: () => void
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
  const [isLoading, setIsLoading] = useState(true) // Start as true to prevent premature redirects
  const [hasInitialized, setHasInitialized] = useState(false)
  const [showSessionExpiredModal, setShowSessionExpiredModal] = useState(false)
  const router = useRouter()

  // Check if we have any indication of being logged in
  const hasAuthIndicators = () => {
    if (typeof window === 'undefined') return false
    
    // Check for cookies or localStorage indicators
    return document.cookie.includes('access_token') || 
           localStorage.getItem('salesoptimizer_was_logged_in') === 'true'
  }

  // Check authentication status only when we think user might be logged in
  const checkAuth = async () => {
    console.log('🔍 Checking auth state...')
    
    // Don't check if we have no indicators of being logged in
    if (!hasAuthIndicators()) {
      console.log('❌ No auth indicators found, user not logged in')
      setUser(null)
      setIsLoading(false)
      setHasInitialized(true)
      return
    }

    console.log('✅ Auth indicators found, verifying with server...')
    setIsLoading(true)
    try {      const userData = await apiClient.get<{
        user_id: string
        email: string
        role: string
        full_name: string
        tenant_id?: string
        first_name?: string
        last_name?: string
        phone?: string
        profile_picture_url?: string      }>('/auth/me')
      
      const nameComponents = getNameComponents({
        first_name: userData.first_name,
        last_name: userData.last_name,
        full_name: userData.full_name
      })

      const user: User = {
        id: userData.user_id,
        email: userData.email,
        role: userData.role,
        full_name: userData.full_name,
        first_name: nameComponents.first_name,
        last_name: nameComponents.last_name,
        tenant_id: userData.tenant_id,
        phone: userData.phone,
        profile_picture_url: userData.profile_picture_url
      }
      
      console.log('✅ Auth check successful, user:', user.email, 'role:', user.role)
      setUser(user)
      // Mark that user was logged in
      localStorage.setItem('salesoptimizer_was_logged_in', 'true')
    } catch (error) {
      console.log('❌ Auth check failed - user not authenticated')
      setUser(null)
      
      // If we had indicators but auth failed, show session expired modal
      if (hasAuthIndicators()) {
        setShowSessionExpiredModal(true)
        // Clear the login indicator
        localStorage.removeItem('salesoptimizer_was_logged_in')
      }
    } finally {
      setIsLoading(false)
      setHasInitialized(true)
    }
  }
  // Only run auth check on mount if we have indicators
  useEffect(() => {
    if (!hasInitialized) {
      checkAuth()
    }

    // Listen for session expired events from API client
    const handleSessionExpired = () => {
      setShowSessionExpiredModal(true)
      setUser(null)
    }

    if (typeof window !== 'undefined') {
      window.addEventListener('session-expired', handleSessionExpired)
      return () => {
        window.removeEventListener('session-expired', handleSessionExpired)
      }
    }
  }, [hasInitialized])

  const login = async (credentials: { emailOrUsername: string; password: string }) => {
    setIsLoading(true)
    try {      const formData = new URLSearchParams({
        username: credentials.emailOrUsername,
        password: credentials.password,
      })

      const data = await apiClient.postForm<{
        user_id: string
        email: string
        role: string
        full_name: string
        tenant_id?: string
        first_name?: string
        last_name?: string
        phone?: string
        profile_picture_url?: string
      }>('/auth/login', formData)
        const nameComponents = getNameComponents({
        first_name: data.first_name,
        last_name: data.last_name,
        full_name: data.full_name
      })

      const user: User = {
        id: data.user_id,
        email: data.email,
        role: data.role,
        full_name: data.full_name,
        first_name: nameComponents.first_name,
        last_name: nameComponents.last_name,
        tenant_id: data.tenant_id,
        phone: data.phone,
        profile_picture_url: data.profile_picture_url
      }
      
      setUser(user)
      // Mark that user is logged in
      localStorage.setItem('salesoptimizer_was_logged_in', 'true')
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
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setUser(null)
      // Clear the login indicator
      localStorage.removeItem('salesoptimizer_was_logged_in')
      setIsLoading(false)
      router.push('/')
    }
  }
  const dismissSessionExpiredModal = () => {
    setShowSessionExpiredModal(false)
  }

  const refreshUser = async () => {
    try {
      const userData = await apiClient.get<{
        user_id: string
        email: string
        role: string
        full_name: string
        tenant_id?: string
        first_name?: string
        last_name?: string
        phone?: string
        profile_picture_url?: string      }>('/auth/me')
      
      const nameComponents = getNameComponents({
        first_name: userData.first_name,
        last_name: userData.last_name,
        full_name: userData.full_name
      })

      const user: User = {
        id: userData.user_id,
        email: userData.email,
        role: userData.role,
        full_name: userData.full_name,
        first_name: nameComponents.first_name,
        last_name: nameComponents.last_name,
        tenant_id: userData.tenant_id,
        phone: userData.phone,
        profile_picture_url: userData.profile_picture_url
      }
      
      setUser(user)
    } catch (error) {
      console.error('Failed to refresh user data:', error)
      throw error
    }
  }
  const value: AuthContextType = {
    user,
    isLoading,
    login,
    logout,
    isAuthenticated: !!user,
    checkAuth,
    refreshUser,
    showSessionExpiredModal,
    dismissSessionExpiredModal
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}