"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"

interface UserAvatarProps {
  user: {
    profile_picture_url?: string | null
    first_name?: string | null
    last_name?: string | null
    email?: string | null
  } | null
  className?: string
  fallbackClassName?: string
}

export function UserAvatar({ user, className, fallbackClassName }: UserAvatarProps) {
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
    if (!profilePictureUrl) {
      return undefined
    }
    
    // If it's a full URL, return as is
    if (profilePictureUrl.startsWith('http')) {
      return `${profilePictureUrl}?t=${Date.now()}`
    }
    
    // If it's a relative path, prepend API URL and add cache busting
    return `${process.env.NEXT_PUBLIC_API_URL}${profilePictureUrl}?t=${Date.now()}`
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
