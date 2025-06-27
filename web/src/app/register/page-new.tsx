"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function RegisterPage() {
  const router = useRouter()
  
  useEffect(() => {
    // Redirect to landing page with signup section
    router.replace('/#signup')
  }, [router])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <p className="text-muted-foreground">Redirecting to signup...</p>
      </div>
    </div>
  )
}
