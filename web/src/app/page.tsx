"use client"

import { useAuth } from '@/features/auth/hooks/useAuth'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function HomePage() {
  const { isAuthenticated, user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated && user) {
        // Redirect based on role
        if (user.role === 'super_admin') {
          router.push('/admin')
        } else {
          router.push('/dashboard')
        }
      } else {
        router.push('/login')
      }
    }
  }, [isAuthenticated, user, isLoading, router])

  // Show loading while determining auth state
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
    </div>
  )
}