"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"
import { ProfilePictureCacheManager } from "@/utils/profile-picture-cache"

interface UserAvatarProps {
  user: {
    id?: string
    profile_picture_url?: string | null
    first_name?: string | null
    last_name?: string | null
    email?: string | null
  } | null
  className?: string
  fallbackClassName?: string
  forceRefresh?: boolean // For when we know the picture was just updated
}

export function UserAvatar({ user, className, fallbackClassName, forceRefresh = false }: UserAvatarProps) {
  const getUserInitials = (user: any) => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase()
    }
    if (user?.email) {
      return user.email.substring(0, 2).toUpperCase()
    }
    return 'U'
  }

  const getProfilePictureUrl = (profilePictureUrl?: string | null) => {
    if (!profilePictureUrl || !user?.id) {
      return undefined
    }
    
    return ProfilePictureCacheManager.getCachedProfilePictureUrl(
      user.id,
      profilePictureUrl,
      forceRefresh
    )
  }

  const profilePictureUrl = getProfilePictureUrl(user?.profile_picture_url)

  return (
    <Avatar className={className}>
      {profilePictureUrl && (
        <AvatarImage 
          src={profilePictureUrl} 
          alt={user?.email || 'User'}
        />
      )}
      <AvatarFallback className={cn("bg-muted", fallbackClassName)}>
        {getUserInitials(user)}
      </AvatarFallback>
    </Avatar>
  )
}
