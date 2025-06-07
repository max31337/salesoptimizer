"use client"

import { useState, useRef, useEffect } from "react"
import { useAuth } from "@/features/auth/hooks/useAuth"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { ProfileUpdateModal } from "@/components/modals/profile-update-modal"
import { UserAvatar } from "@/components/ui/user-avatar"
import { profileService, type ProfileUpdateRequest } from "@/features/profile/services/profile-service"
import { User, Mail, Phone, Building, Upload, Trash2, Loader2, AlertTriangle } from "lucide-react"

export default function ProfileSettingsPage() {
  const { user, refreshUser } = useAuth()
  const fileInputRef = useRef<HTMLInputElement>(null)    // Form state
  const [formData, setFormData] = useState({
    email: user?.email || '',
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    phone: user?.phone || '',
    bio: user?.bio || ''
  })
    // UI state
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isUploadingPhoto, setIsUploadingPhoto] = useState(false)
  const [isDeletingPhoto, setIsDeletingPhoto] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const getRoleDisplayName = (role: string) => {
    switch (role) {
      case 'super_admin':
        return 'System Administrator'
      case 'org_admin':
        return 'Organization Administrator'
      case 'manager':
        return 'Manager'
      case 'member':
        return 'Member'
      default:
        return role
    }
  }

  // Admin check
  const isAdmin = user?.role === 'super_admin' || user?.role === 'org_admin'

  // Modal state
  const [modalOpen, setModalOpen] = useState(false)
  const [modalType, setModalType] = useState<'success' | 'pending' | 'error'>('success')
  const [modalMessage, setModalMessage] = useState('')  // Update form data when user data changes
  useEffect(() => {
    if (user) {
      setFormData({
        email: user.email || '',
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone: user.phone || '',
        bio: user.bio || ''
      })
    }
  }, [user])

  const handleInputChange = (field: keyof ProfileUpdateRequest, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear messages when user starts typing
    if (error) setError('')
    if (success) setSuccess('')
  }
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError('')
    setSuccess('')

    try {
      // Only send fields that have changed
      const changedFields: ProfileUpdateRequest = {}
      
      // Check email change (only for admins)
      if (isAdmin && formData.email !== (user?.email || '')) {
        changedFields.email = formData.email
      }
      
      if (formData.first_name !== (user?.first_name || '')) {
        changedFields.first_name = formData.first_name
      }
      if (formData.last_name !== (user?.last_name || '')) {
        changedFields.last_name = formData.last_name
      }      if (formData.phone !== (user?.phone || '')) {
        changedFields.phone = formData.phone
      }
      if (formData.bio !== (user?.bio || '')) {
        changedFields.bio = formData.bio
      }

      // If no changes, show message
      if (Object.keys(changedFields).length === 0) {
        setError('No changes detected')
        return
      }

      const response = await profileService.updateProfile(changedFields)

      if (profileService.isPendingResponse(response)) {
        // Show pending approval modal
        setModalType('pending')
        setModalMessage(response.message)
        setModalOpen(true)
      } else {
        // Show success modal and refresh user data
        setModalType('success')
        setModalMessage(response.message)
        setModalOpen(true)
        
        // Refresh user data in auth context
        await refreshUser()
      }
    } catch (err: any) {
      console.error('Profile update failed:', err)
      setModalType('error')
      setModalMessage(err.message || 'Failed to update profile')
      setModalOpen(true)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handlePhotoUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please select a valid image file')
      return
    }

    // Validate file size (2MB limit)
    if (file.size > 2 * 1024 * 1024) {
      setError('File size must be less than 2MB')
      return
    }

    setIsUploadingPhoto(true)
    setError('')

    try {
      await profileService.uploadProfilePicture(file)
      setSuccess('Profile picture uploaded successfully')
      
      // Refresh user data to get new profile picture URL
      await refreshUser()
    } catch (err: any) {
      console.error('Photo upload failed:', err)
      setError(err.message || 'Failed to upload photo')
    } finally {
      setIsUploadingPhoto(false)
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handlePhotoDelete = async () => {
    setIsDeletingPhoto(true)
    setError('')

    try {
      await profileService.deleteProfilePicture()
      setSuccess('Profile picture removed successfully')
      
      // Refresh user data
      await refreshUser()
    } catch (err: any) {
      console.error('Photo deletion failed:', err)
      setError(err.message || 'Failed to remove photo')
    } finally {
      setIsDeletingPhoto(false)
    }  }
  
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-foreground mb-2">Profile Settings</h2>
        <p className="text-muted-foreground">
          Manage your personal information and account details
        </p>
      </div>

      {/* Error/Success Messages */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert>
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      {/* Profile Photo */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Profile Photo
          </CardTitle>
          <CardDescription>
            Update your profile picture (JPG, PNG or GIF. Max size 2MB)
          </CardDescription>
        </CardHeader>        <CardContent className="flex items-center gap-4">
          <UserAvatar 
            user={user} 
            className="h-20 w-20" 
            fallbackClassName="text-lg"
          />
          <div className="flex gap-2">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handlePhotoUpload}
              className="hidden"
            />
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploadingPhoto}
            >
              {isUploadingPhoto ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4 mr-2" />
                  Upload Photo
                </>
              )}
            </Button>
            {user?.profile_picture_url && (
              <Button 
                variant="outline" 
                size="sm"
                onClick={handlePhotoDelete}
                disabled={isDeletingPhoto}
              >
                {isDeletingPhoto ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Removing...
                  </>
                ) : (
                  <>
                    <Trash2 className="h-4 w-4 mr-2" />
                    Remove
                  </>
                )}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>      {/* Personal Information */}
      <Card>
        <CardHeader>
          <CardTitle>Personal Information</CardTitle>
          <CardDescription>
            Update your personal details
            {!isAdmin && (
              <span className="block text-yellow-600 dark:text-yellow-400 mt-1">
                Profile updates require approval from your organization administrator
              </span>
            )}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="firstName">First Name</Label>
                <Input
                  id="firstName"
                  value={formData.first_name}
                  onChange={(e) => handleInputChange('first_name', e.target.value)}
                  placeholder="Enter your first name"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="lastName">Last Name</Label>
                <Input
                  id="lastName"
                  value={formData.last_name}
                  onChange={(e) => handleInputChange('last_name', e.target.value)}
                  placeholder="Enter your last name"
                />
              </div>
            </div>            <div className="space-y-2">
              <Label htmlFor="email" className="flex items-center gap-2">
                <Mail className="h-4 w-4" />
                Email Address
              </Label>
              <Input
                id="email"
                type="email"
                value={isAdmin ? formData.email : (user?.email || '')}
                onChange={(e) => handleInputChange('email', e.target.value)}
                placeholder="Enter your email"
                disabled={!isAdmin}
              />
              <p className="text-xs text-muted-foreground">
                {isAdmin 
                  ? "As an admin, you can update your email address directly."
                  : "Email cannot be changed. Contact support if you need to update it."
                }
              </p>
            </div>            <div className="space-y-2">
              <Label htmlFor="phone" className="flex items-center gap-2">
                <Phone className="h-4 w-4" />
                Phone Number
              </Label>
              <Input
                id="phone"
                type="tel"
                value={formData.phone}
                onChange={(e) => handleInputChange('phone', e.target.value)}
                placeholder="Enter your phone number"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="bio">Bio</Label>
              <Textarea
                id="bio"
                value={formData.bio}
                onChange={(e) => handleInputChange('bio', e.target.value)}
                placeholder="Tell us about yourself... (optional, max 1000 characters)"
                maxLength={1000}
                rows={4}
              />
              <p className="text-xs text-muted-foreground">
                {formData.bio.length}/1000 characters
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="role" className="flex items-center gap-2">
                <Building className="h-4 w-4" />
                Role
              </Label>              <Input
                id="role"
                value={getRoleDisplayName(user?.role || '')}
                disabled
              />              <p className="text-xs text-muted-foreground">
                {user?.role === 'super_admin' 
                  ? "System-wide admin role cannot be changed."
                  : user?.role === 'org_admin'
                  ? "System Admin can only update your Organization role."
                  : "Role is assigned by your organization administrator."
                }
              </p>
            </div>

            <div className="flex justify-end">
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  'Save Changes'
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Profile Update Modal */}
      <ProfileUpdateModal
        open={modalOpen}
        onOpenChange={setModalOpen}
        type={modalType}
        message={modalMessage}
      />
    </div>
  )
}
