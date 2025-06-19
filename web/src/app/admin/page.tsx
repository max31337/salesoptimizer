"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { InviteOrgAdminModal } from "@/components/admin/invite-org-admin-modal"
import { useAuth } from "@/features/auth/hooks/useAuth"
import { useSLAData } from "@/features/sla/hooks/useSLAData"
import { ThemeToggle } from "@/components/ui/theme-toggle"
import { UserAvatar } from "@/components/ui/user-avatar"
import { Building, Users, Activity, UserPlus, Settings, FileText, LogOut, User as UserIcon, Monitor, AlertTriangle, Loader2 } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import Link from "next/link"
import { createFullName } from "@/utils/nameParser"

export default function SuperAdminDashboard() {  
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false)
  const [isLoggingOut, setIsLoggingOut] = useState(false)
  const { user, logout } = useAuth()
  const { systemHealth, alerts, isLoading: slaLoading } = useSLAData(true, 30000)
  
  // Calculate real-time alert counts from the alerts array
  const activeAlertsCount = alerts.length
  const unacknowledgedAlertsCount = alerts.filter(alert => !alert.acknowledged).length
  
  const handleLogout = async () => {
    if (isLoggingOut) return
    
    setIsLoggingOut(true)
    try {
      await logout()
    } catch (error) {
      console.error('Logout failed:', error)
    } finally {
      setIsLoggingOut(false)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card shadow-sm border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Super Admin Dashboard</h1>
              <p className="mt-1 text-sm text-muted-foreground">
                Welcome back, {user?.first_name || user?.email}
              </p>
            </div>
              <div className="flex items-center space-x-4">
              <Badge variant="secondary" className="bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300">
                Super Admin
              </Badge>
              
              <Button 
                variant="outline" 
                size="sm" 
                className="flex items-center gap-2"
                asChild
              >
                <Link href="/admin/sla-monitoring">
                  <Monitor className="h-4 w-4" />
                  SLA Monitoring
                </Link>
              </Button>
              
              <ThemeToggle />
              
              {/* User Profile Dropdown */}
              <DropdownMenu>                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                    <UserAvatar 
                      user={user} 
                      className="h-10 w-10" 
                      fallbackClassName="bg-purple-100 dark:bg-purple-900/50 text-purple-800 dark:text-purple-300"
                    />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">                      <p className="text-sm font-medium leading-none">
                        {user?.first_name && user?.last_name 
                          ? createFullName(user.first_name, user.last_name)
                          : user?.email}
                      </p>
                      <p className="text-xs leading-none text-muted-foreground">
                        {user?.email}
                      </p>
                    </div>
                  </DropdownMenuLabel>                  <DropdownMenuSeparator />
                  <DropdownMenuItem className="cursor-pointer" asChild>
                    <Link href="/profile">
                      <UserIcon className="mr-2 h-4 w-4" />
                      <span>Profile</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem className="cursor-pointer" asChild>
                    <Link href="/settings">
                      <Settings className="mr-2 h-4 w-4" />
                      <span>Settings</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem 
                    className="cursor-pointer text-red-600 dark:text-red-400 focus:text-red-600 dark:focus:text-red-400"
                    onClick={handleLogout}
                    disabled={isLoggingOut}
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>{isLoggingOut ? 'Signing out...' : 'Sign out'}</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card className="bg-card border-border">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-card-foreground">Organizations</CardTitle>
                <Building className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-card-foreground">24</div>
                <p className="text-xs text-muted-foreground">
                  +3 from last month
                </p>
              </CardContent>
            </Card>

            <Card className="bg-card border-border">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-card-foreground">Active Users</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-card-foreground">1,247</div>
                <p className="text-xs text-muted-foreground">
                  +12% from last month
                </p>
              </CardContent>
            </Card>            <Card className="bg-card border-border">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-card-foreground">System Health</CardTitle>
                <div className="flex items-center gap-2">
                  {slaLoading && <Loader2 className="h-3 w-3 animate-spin text-muted-foreground" />}
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <div className={`text-2xl font-bold ${
                    systemHealth?.overall_status === 'healthy' 
                      ? 'text-green-600 dark:text-green-400'
                      : systemHealth?.overall_status === 'warning'
                      ? 'text-yellow-600 dark:text-yellow-400'
                      : 'text-red-600 dark:text-red-400'
                  }`}>
                    {systemHealth 
                      ? `${systemHealth.healthy_metrics}/${systemHealth.total_metrics}`
                      : '---'
                    }
                  </div>
                  <Badge 
                    variant={
                      systemHealth?.overall_status === 'healthy' 
                        ? 'default'
                        : systemHealth?.overall_status === 'warning'
                        ? 'secondary'
                        : 'destructive'
                    }
                    className="text-xs"
                  >
                    {systemHealth?.overall_status || 'Unknown'}
                  </Badge>
                </div>                <div className="flex items-center gap-1 mt-1">
                  <p className="text-xs text-muted-foreground">
                    {activeAlertsCount > 0 ? `${activeAlertsCount} alerts` : 'No alerts'}
                  </p>
                  {unacknowledgedAlertsCount > 0 && (
                    <>
                      <span className="text-xs text-muted-foreground">•</span>
                      <div className="flex items-center gap-1">
                        <AlertTriangle className="h-3 w-3 text-orange-500" />
                        <span className="text-xs text-orange-600 dark:text-orange-400">
                          {unacknowledgedAlertsCount} unack.
                        </span>
                      </div>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <Card className="mb-8 bg-card border-border">
            <CardHeader>
              <CardTitle className="text-card-foreground">Quick Actions</CardTitle>
              <CardDescription className="text-muted-foreground">
                Common administrative tasks
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-4">
                <Button 
                  onClick={() => setIsInviteModalOpen(true)}
                  className="flex items-center gap-2"
                >
                  <UserPlus className="h-4 w-4" />
                  Invite Organization Admin
                </Button>
                
                <Button variant="outline" className="flex items-center gap-2">
                  <Settings className="h-4 w-4" />
                  System Settings
                </Button>
                
                <Button variant="outline" className="flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  View Audit Logs
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-card-foreground">Recent Activity</CardTitle>
              <CardDescription className="text-muted-foreground">
                Latest system events and user activities
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center space-x-4">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-card-foreground">New organization created</p>
                    <p className="text-xs text-muted-foreground">Acme Corp - 2 hours ago</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-card-foreground">Organization admin invited</p>
                    <p className="text-xs text-muted-foreground">admin@techstart.com - 4 hours ago</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-card-foreground">System maintenance completed</p>
                    <p className="text-xs text-muted-foreground">Database optimization - 6 hours ago</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Invite Modal */}
      <InviteOrgAdminModal 
        open={isInviteModalOpen}
        onOpenChange={setIsInviteModalOpen}
      />
    </div>
  )
}