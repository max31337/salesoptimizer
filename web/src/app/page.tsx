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
    // Only run redirect logic after auth has been checked
    if (!isLoading) {
      if (isAuthenticated && user) {
        // Redirect all authenticated users to dashboard
        console.log('HomePage: Redirecting authenticated user to dashboard')
        router.push('/dashboard')
      } else {
        // Show landing page for unauthenticated users
        console.log('HomePage: Showing landing page for unauthenticated user')
        setShowLanding(true)
      }
    }
  }, [isAuthenticated, user, isLoading, router])

  // Show loading only when actively checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  // Show landing page for unauthenticated users
  if (showLanding) {
    return <LandingPage />
  }

  // Show loading while redirecting authenticated users
  if (isAuthenticated && user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Redirecting...</p>
        </div>
      </div>
    )
  }

  // Fallback loading state
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
    </div>
  )
}