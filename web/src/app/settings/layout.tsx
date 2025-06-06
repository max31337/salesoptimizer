"use client"

import { useAuth } from "@/features/auth/hooks/useAuth"
import { useRouter } from "next/navigation"
import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { 
  User, 
  Shield, 
  Bell, 
  Settings, 
  ArrowLeft,
  Building,
  Users
} from "lucide-react"

const settingsNavigation = [
  {
    name: "Profile",
    href: "/settings/profile",
    icon: User,
    description: "Manage your personal information"
  },
  {
    name: "Security",
    href: "/settings/security",
    icon: Shield,
    description: "Manage sessions and security settings"
  },
  {
    name: "Notifications",
    href: "/settings/notifications", 
    icon: Bell,
    description: "Configure notification preferences"
  },
  {
    name: "General",
    href: "/settings/general",
    icon: Settings,
    description: "Application preferences and settings"
  }
]

// Add organization settings for admins
const organizationNavigation = [
  {
    name: "Organization",
    href: "/settings/organization",
    icon: Building,
    description: "Manage organization settings"
  },
  {
    name: "Team Management",
    href: "/settings/team",
    icon: Users,
    description: "Manage team members and roles"
  }
]

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { user, isLoading, isAuthenticated } = useAuth()
  const router = useRouter()
  const pathname = usePathname()
  const [hasCheckedAccess, setHasCheckedAccess] = useState(false)

  useEffect(() => {
    if (!isLoading && !hasCheckedAccess) {
      setHasCheckedAccess(true)
      
      if (!isAuthenticated) {
        router.push('/login')
        return
      }
    }
  }, [user, isLoading, isAuthenticated, router, hasCheckedAccess])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-lg text-muted-foreground">Redirecting to login...</p>
        </div>
      </div>
    )
  }

  const isAdmin = user?.role === 'super_admin' || user?.role === 'org_admin'
  const allNavigation = [...settingsNavigation, ...(isAdmin ? organizationNavigation : [])]

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card shadow-sm border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" asChild>
                <Link href={user?.role === 'super_admin' ? '/admin' : '/dashboard'}>
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Dashboard
                </Link>
              </Button>
              <div>
                <h1 className="text-3xl font-bold text-foreground">Settings</h1>
                <p className="mt-1 text-sm text-muted-foreground">
                  Manage your account and application preferences
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar Navigation */}
          <div className="lg:col-span-1">
            <Card className="p-4">
              <nav className="space-y-2">
                {allNavigation.map((item) => {
                  const isActive = pathname === item.href
                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                        isActive 
                          ? "bg-primary text-primary-foreground" 
                          : "text-muted-foreground hover:text-foreground hover:bg-muted"
                      )}
                    >
                      <item.icon className="h-4 w-4" />
                      <div>
                        <div>{item.name}</div>
                        <div className={cn(
                          "text-xs",
                          isActive ? "text-primary-foreground/80" : "text-muted-foreground"
                        )}>
                          {item.description}
                        </div>
                      </div>
                    </Link>
                  )
                })}
              </nav>
            </Card>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            <Card className="p-6">
              {children}
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
