import React, { useEffect, useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/store/auth-store'
import { useRouter } from 'next/navigation'

interface SessionExpiredDialogProps {
  open: boolean
  onClose: () => void
}

export function SessionExpiredDialog({ open, onClose }: SessionExpiredDialogProps) {
  const { logout, refreshAuth, setSessionExpired } = useAuthStore()
  const router = useRouter()
  const [isRefreshing, setIsRefreshing] = useState(false)

  const handleRefresh = async () => {
    setIsRefreshing(true)
    try {
      const success = await refreshAuth()
      if (success) {
        setSessionExpired(false)
        onClose()
      } else {
        handleLogout()
      }
    } catch (error) {
      console.error('Refresh failed:', error)
      handleLogout()
    } finally {
      setIsRefreshing(false)
    }
  }

  const handleLogout = async () => {
    await logout()
    onClose()
    router.push('/auth/login')
  }

  return (
    <Dialog open={open} onOpenChange={() => {}}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <span className="text-amber-500">⚠️</span>
            Session Expired
          </DialogTitle>
          <DialogDescription>
            Your session has expired for security reasons. Would you like to refresh your session or log in again?
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="flex gap-2 sm:justify-between">
          <Button
            variant="outline"
            onClick={handleLogout}
            disabled={isRefreshing}
          >
            Log In Again
          </Button>
          <Button
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            {isRefreshing ? 'Refreshing...' : 'Refresh Session'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// Hook to handle session expiry events
export function useSessionExpiry() {
  const { sessionExpired, setSessionExpired } = useAuthStore()
  const [showDialog, setShowDialog] = useState(false)

  useEffect(() => {
    const handleSessionExpired = () => {
      setSessionExpired(true)
      setShowDialog(true)
    }

    // Listen for session expiry events from the API client
    window.addEventListener('session-expired', handleSessionExpired)

    return () => {
      window.removeEventListener('session-expired', handleSessionExpired)
    }
  }, [setSessionExpired])

  useEffect(() => {
    if (sessionExpired) {
      setShowDialog(true)
    }
  }, [sessionExpired])

  const handleClose = () => {
    setShowDialog(false)
    setSessionExpired(false)
  }

  return {
    showSessionExpiredDialog: showDialog,
    closeSessionExpiredDialog: handleClose,
  }
}
