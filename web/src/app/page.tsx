"use client"

import { useAuth } from '@/features/auth/hooks/useAuth'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { LandingPage } from '@/components/landing/landing-page'

export default function HomePage() {
  const { isAuthenticated, user, isLoading } = useAuth()
  const router = useRouter()
  const [showLanding, setShowLanding] = useState(false)

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated && user) {
        // Redirect authenticated users based on role
        if (user.role === 'super_admin') {
          router.push('/admin')
        } else {
          router.push('/dashboard')
        }
      } else {
        // Show landing page for unauthenticated users
        setShowLanding(true)
      }
    }
  }, [isAuthenticated, user, isLoading, router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (showLanding) {
    return <LandingPage />
  }

  // Show loading while redirecting authenticated users
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
    </div>
  )
}