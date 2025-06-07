"use client"

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { CheckCircle, Clock, Info } from "lucide-react"

interface ProfileUpdateModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  type: 'success' | 'pending' | 'error'
  message: string
  onContinue?: () => void
}

export function ProfileUpdateModal({ 
  open, 
  onOpenChange, 
  type, 
  message,
  onContinue 
}: ProfileUpdateModalProps) {
  const handleContinue = () => {
    if (onContinue) {
      onContinue()
    }
    onOpenChange(false)
  }

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className="h-6 w-6 text-green-600" />
      case 'pending':
        return <Clock className="h-6 w-6 text-yellow-600" />
      case 'error':
        return <Info className="h-6 w-6 text-red-600" />
      default:
        return <Info className="h-6 w-6" />
    }
  }

  const getTitle = () => {
    switch (type) {
      case 'success':
        return 'Profile Updated Successfully'
      case 'pending':
        return 'Profile Update Under Review'
      case 'error':
        return 'Update Failed'
      default:
        return 'Profile Update'
    }
  }

  const getVariant = () => {
    switch (type) {
      case 'error':
        return 'destructive' as const
      default:
        return 'default' as const
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {getIcon()}
            {getTitle()}
          </DialogTitle>
          <DialogDescription>
            {type === 'pending' && (
              "Your profile update has been submitted and is now under review by your organization administrator."
            )}
            {type === 'success' && (
              "Your profile has been updated successfully."
            )}
            {type === 'error' && (
              "There was an error updating your profile. Please try again."
            )}
          </DialogDescription>        </DialogHeader>
        
        <Alert variant={getVariant()}>
          {getIcon()}
          <AlertDescription>
            {message}
          </AlertDescription>
        </Alert>

        <div className="flex justify-end gap-2">
          <Button onClick={handleContinue}>
            {type === 'error' ? 'Try Again' : 'Continue'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
