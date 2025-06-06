"use client"

import { useAuth } from "@/features/auth/hooks/useAuth"
import { useRouter } from "next/navigation"
import { useEffect } from "react"

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { user, isLoading, isAuthenticated } = useAuth()
  const router = useRouter()

  useEffect(() => {
    // Only perform checks when loading is complete
    if (!isLoading) {
      if (!isAuthenticated) {
        console.log('Admin layout: User not authenticated, redirecting to login')
        router.push('/login')
        return
      }
      
      if (user?.role !== 'super_admin') {
        console.log('Admin layout: User not super admin, redirecting to dashboard')
        router.push('/dashboard')
        return
      }
      
      console.log('Admin layout: Access granted for super admin')
    }
  }, [user, isLoading, isAuthenticated, router])

  // Show loading while authentication is being checked
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  // Show loading while redirect is happening
  if (!isAuthenticated || user?.role !== 'super_admin') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Checking access...</p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}