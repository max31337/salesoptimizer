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
    if (!isLoading) {
      if (!isAuthenticated) {
        router.push('/login')
        return
      }
      
      if (user?.role !== 'super_admin') {
        router.push('/dashboard') // Redirect non-super admins
        return
      }
    }
  }, [user, isLoading, isAuthenticated, router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (!isAuthenticated || user?.role !== 'super_admin') {
    return null // Will redirect in useEffect
  }

  return <>{children}</>
}