"use client"

import { useRouter } from "next/navigation"
import { useEffect } from "react"

export default function SettingsPage() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to security settings by default
    router.replace('/settings/security')
  }, [router])

  return (
    <div className="flex items-center justify-center py-8">
      <div className="text-center">
        <p className="text-muted-foreground">Redirecting to settings...</p>
      </div>
    </div>
  )
}
