"use client"

import { useState, useEffect } from "react"
import { useAuth } from "@/features/auth/hooks/useAuth"
import { profileService, type Organization } from "@/features/profile/services/profile-service"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { UserAvatar } from "@/components/ui/user-avatar"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { 
  User, 
  Mail, 
  Phone, 
  Building, 
  Calendar, 
  Settings,
  ArrowLeft,
  Users,
  Shield,
  AlertTriangle,
  Loader2
} from "lucide-react"
import Link from "next/link"
import { format } from "date-fns"

export default function ProfilePage() {
  const { user, isLoading: authLoading } = useAuth()
  const [organization, setOrganization] = useState<Organization | null>(null)
  const [isLoadingOrg, setIsLoadingOrg] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchOrganization = async () => {
      if (!user?.tenant_id) {
        setIsLoadingOrg(false)
        return
      }

      try {
        const response = await profileService.getOrganization()
        setOrganization(response.organization)
      } catch (err: any) {
        console.error('Failed to fetch organization:', err)
        setError('Failed to load organization information')
      } finally {
        setIsLoadingOrg(false)
      }
    }

    if (user) {
      fetchOrganization()
    }
  }, [user])

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

  const getRoleBadgeVariant = (role: string) => {
    switch (role) {
      case 'super_admin':
        return 'default'
      case 'org_admin':
        return 'secondary'
      case 'manager':
        return 'outline'
      default:
        return 'outline'
    }
  }

  if (authLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center gap-2">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Loading profile...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header with back button */}
      <header className="bg-card shadow-sm border-b border-border">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4 py-6">
            <Button variant="ghost" size="sm" asChild>
              <Link href={user?.role === 'super_admin' ? '/admin' : '/dashboard'}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Link>
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-foreground">Profile</h1>
              <p className="text-sm text-muted-foreground">
                View your profile information and details
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="space-y-6">
          {/* Profile Header Card */}
          <Card className="overflow-hidden">
            {/* Cover Background */}
            <div className="h-32 bg-gradient-to-r from-blue-600 to-purple-600"></div>
            
            {/* Profile Content */}
            <CardContent className="relative px-6 pb-6">
              {/* Profile Picture - Positioned to overlap cover */}
              <div className="absolute -top-16 left-6">
                <UserAvatar 
                  user={user} 
                  className="h-32 w-32 border-4 border-background shadow-lg" 
                  fallbackClassName="text-3xl bg-white text-blue-600"
                />
              </div>
              
              {/* Edit Profile Button */}
              <div className="flex justify-end pt-4">
                <Button variant="outline" size="sm" asChild>
                  <Link href="/settings/profile">
                    <Settings className="h-4 w-4 mr-2" />
                    Edit Profile
                  </Link>
                </Button>
              </div>

              {/* User Info */}
              <div className="mt-8 ml-40">
                <div className="space-y-4">
                  <div>
                    <h2 className="text-3xl font-bold text-foreground">
                      {user.first_name && user.last_name 
                        ? `${user.first_name} ${user.last_name}` 
                        : user.email}
                    </h2>
                    <p className="text-lg text-muted-foreground">
                      {user.email}
                    </p>
                  </div>

                  {/* Role Badge */}
                  <div className="flex items-center gap-2">
                    <Badge variant={getRoleBadgeVariant(user.role)} className="flex items-center gap-1">
                      <Shield className="h-3 w-3" />
                      {getRoleDisplayName(user.role)}
                    </Badge>
                  </div>

                  {/* Bio */}
                  {user.bio && (
                    <div className="max-w-2xl">
                      <p className="text-foreground leading-relaxed">
                        {user.bio}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Information Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Contact Information */}
            <Card>
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Contact Information
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-sm text-muted-foreground">Email</p>
                      <p className="text-foreground">{user.email}</p>
                    </div>
                  </div>
                  
                  {user.phone && (
                    <div className="flex items-center gap-3">
                      <Phone className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <p className="text-sm text-muted-foreground">Phone</p>
                        <p className="text-foreground">{user.phone}</p>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Organization Information */}
            <Card>
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
                  <Building className="h-5 w-5" />
                  Organization
                </h3>
                {isLoadingOrg ? (
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm text-muted-foreground">Loading...</span>
                  </div>
                ) : organization ? (
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <Users className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <p className="text-sm text-muted-foreground">Organization</p>
                        <p className="text-foreground font-medium">{organization.name}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      <Shield className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <p className="text-sm text-muted-foreground">Subscription</p>
                        <Badge variant="outline" className="capitalize">
                          {organization.subscription_tier}
                        </Badge>
                      </div>
                    </div>

                    {organization.created_at && (
                      <div className="flex items-center gap-3">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <p className="text-sm text-muted-foreground">Member Since</p>
                          <p className="text-foreground">
                            {format(new Date(organization.created_at), 'MMMM d, yyyy')}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-muted-foreground">No organization information available</p>
                )}
              </CardContent>
            </Card>

            {/* Account Details */}
            <Card className="md:col-span-2">
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Account Details
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <p className="text-sm text-muted-foreground">User ID</p>
                    <p className="text-foreground font-mono text-sm">{user.id}</p>
                  </div>
                  
                  <div>
                    <p className="text-sm text-muted-foreground">Role</p>
                    <p className="text-foreground">{getRoleDisplayName(user.role)}</p>
                  </div>
                  
                  {user.tenant_id && (
                    <div>
                      <p className="text-sm text-muted-foreground">Organization ID</p>
                      <p className="text-foreground font-mono text-sm">{user.tenant_id}</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
