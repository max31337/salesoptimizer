"use client"

import { useAuth } from '@/features/auth/hooks/useAuth'
import { useRouter } from 'next/navigation'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { AlertTriangle } from "lucide-react"

export function SessionExpiredModal() {
  const { showSessionExpiredModal, dismissSessionExpiredModal } = useAuth()
  const router = useRouter()

  const handleLoginRedirect = () => {
    dismissSessionExpiredModal()
    router.push('/login')
  }

  const handleStayOnPage = () => {
    dismissSessionExpiredModal()
  }

  return (
    <Dialog open={showSessionExpiredModal} onOpenChange={dismissSessionExpiredModal}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-orange-100 dark:bg-orange-900/20">
            <AlertTriangle className="h-6 w-6 text-orange-600 dark:text-orange-400" />
          </div>
          <DialogTitle className="text-center">Session Expired</DialogTitle>
          <DialogDescription className="text-center">
            Your session has expired. Please sign in again to continue using the application.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="sm:justify-center space-x-2">
          <Button variant="outline" onClick={handleStayOnPage}>
            Stay on Page
          </Button>
          <Button onClick={handleLoginRedirect} className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
            Sign In
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}