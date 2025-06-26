"use client"

import { useState, useEffect } from "react"
import { useAuth } from "@/features/auth/hooks/useAuth"
import { profileService, type Organization } from "@/features/profile/services/profile-service"
import { useClientWebSocketSLA } from "@/features/sla/hooks/useClientWebSocketSLA"
import { InviteOrgAdminModal } from "@/components/admin/invite-org-admin-modal"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Separator } from "@/components/ui/separator"
import { 
  User, 
  Building, 
  Activity, 
  Settings, 
  Users,
  TrendingUp,
  BarChart3,
  Target,
  Clock,
  CheckCircle2,
  AlertCircle,
  Loader2,
  UserPlus,
  Monitor,
  AlertTriangle,
  RefreshCw,
  Shield
} from "lucide-react"
import Link from "next/link"
import { createFullName } from "@/utils/nameParser"

export default function DashboardPage() {
  const { user } = useAuth()
  const [organization, setOrganization] = useState<Organization | null>(null)
  const [isLoadingOrg, setIsLoadingOrg] = useState(true)
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false)

  // For super admin - use WebSocket SLA data
  const { 
    systemHealth, 
    alerts, 
    isLoading: slaLoading, 
    isConnected: wsConnected,
    lastUpdated 
  } = useClientWebSocketSLA()

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
      } finally {
        setIsLoadingOrg(false)
      }
    }

    if (user) {
      fetchOrganization()
    }
  }, [user])

  const getOrganizationName = () => {
    if (isLoadingOrg) return "Loading..."
    if (organization) return organization.name
    return "No organization"
  }

  const isAdmin = user?.role === 'super_admin' || user?.role === 'org_admin'
  const isSuperAdmin = user?.role === 'super_admin'

  // Calculate real-time alert counts for super admin
  const activeAlertsCount = alerts.length
  const unacknowledgedAlertsCount = alerts.filter(alert => !alert.acknowledged).length

  return (
    <div className="flex-1 space-y-6">
      {/* Welcome Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">
            {isSuperAdmin ? 'Super Admin Dashboard' : `Welcome back, ${user ? createFullName(user.first_name || '', user.last_name || '') : 'User'}!`}
          </h2>
          <p className="text-muted-foreground">
            {isSuperAdmin 
              ? 'Monitor and manage the entire SalesOptimizer platform'
              : "Here's what's happening with your sales activities today."
            }
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant={user?.role === 'super_admin' ? 'destructive' : 'secondary'}>
            {user?.role === 'super_admin' ? 'Super Admin' : 
             user?.role === 'org_admin' ? 'Organization Admin' : 'User'}
          </Badge>
          
          {/* WebSocket Connection Status for Super Admin */}
          {isSuperAdmin && (
            <div className="flex items-center gap-2 text-sm">
              <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-muted-foreground">
                {wsConnected ? 'Live Data' : 'Disconnected'}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Super Admin Stats Cards */}
      {isSuperAdmin && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Organizations</CardTitle>
              <Building className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">24</div>
              <p className="text-xs text-muted-foreground">
                +3 from last month
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">1,247</div>
              <p className="text-xs text-muted-foreground">
                +12% from last month
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">System Uptime</CardTitle>
              <div className="flex items-center gap-2">
                {slaLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                ) : (
                  <div className={`w-2 h-2 rounded-full ${
                    systemHealth?.uptime_status === 'healthy' ? 'bg-green-500' :
                    systemHealth?.uptime_status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                  }`} />
                )}
                <Activity className="h-4 w-4 text-muted-foreground" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <div className="text-2xl font-bold">
                  {slaLoading ? '...' : `${systemHealth?.uptime_percentage?.toFixed(2) || '0.00'}%`}
                </div>
                <Badge variant={
                  systemHealth?.uptime_status === 'healthy' ? 'default' :
                  systemHealth?.uptime_status === 'warning' ? 'secondary' : 'destructive'
                }>
                  {systemHealth?.uptime_status || 'unknown'}
                </Badge>
              </div>
              <div className="flex items-center justify-between mt-1">
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">
                    {systemHealth?.uptime_duration ? `Running: ${systemHealth.uptime_duration}` : 'Last 30 days'}
                  </p>
                  {lastUpdated && (
                    <p className="text-xs text-muted-foreground">
                      Updated {new Date(lastUpdated).toLocaleTimeString()}
                    </p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">System Health</CardTitle>
              <div className="flex items-center gap-2">
                {slaLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                ) : (
                  <div className={`w-2 h-2 rounded-full ${
                    systemHealth?.overall_status === 'healthy' ? 'bg-green-500' :
                    systemHealth?.overall_status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                  }`} />
                )}
                <Monitor className="h-4 w-4 text-muted-foreground" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <div className="text-2xl font-bold">
                  {slaLoading ? '...' : `${systemHealth?.health_percentage?.toFixed(2) || '0.00'}%`}
                </div>
                <Badge variant={
                  systemHealth?.overall_status === 'healthy' ? 'default' :
                  systemHealth?.overall_status === 'warning' ? 'secondary' : 'destructive'
                }>
                  {systemHealth?.overall_status || 'unknown'}
                </Badge>
              </div>
              <div className="flex items-center gap-1 mt-1">
                <p className="text-xs text-muted-foreground">
                  {unacknowledgedAlertsCount > 0 ? `${unacknowledgedAlertsCount} alerts` : 'All systems operational'}
                </p>
                {unacknowledgedAlertsCount > 0 && (
                  <AlertTriangle className="h-3 w-3 text-yellow-500" />
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Regular User Stats Cards */}
      {!isSuperAdmin && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Profile Status</CardTitle>
              <User className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">Complete</div>
              <p className="text-xs text-muted-foreground">
                Profile setup status
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Organization</CardTitle>
              <Building className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold truncate">{getOrganizationName()}</div>
              <p className="text-xs text-muted-foreground">
                Current organization
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Activity Status</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">Active</div>
              <p className="text-xs text-muted-foreground">
                Account status
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Role</CardTitle>
              <Settings className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {user?.role === 'org_admin' ? 'Org Admin' : 
                 user?.role === 'sales_manager' ? 'Manager' : 'Rep'}
              </div>
              <p className="text-xs text-muted-foreground">
                Your current role
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Super Admin Quick Actions */}
      {isSuperAdmin && (
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Common administrative tasks for platform management
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
              
              <Button 
                variant="outline" 
                className="flex items-center gap-2"
                onClick={() => window.location.href = '/dashboard/sla-monitoring'}
              >
                <Monitor className="h-4 w-4" />
                SLA Monitoring
              </Button>
              
              <Button variant="outline" className="flex items-center gap-2">
                <Settings className="h-4 w-4" />
                System Settings
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Admin Content for Org Admins */}
      {isAdmin && !isSuperAdmin && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">—</div>
              <p className="text-xs text-muted-foreground">
                Active users in organization
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Performance</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">—</div>
              <p className="text-xs text-muted-foreground">
                Team performance
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Analytics</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">—</div>
              <p className="text-xs text-muted-foreground">
                Data insights
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Goals</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">—</div>
              <p className="text-xs text-muted-foreground">
                Monthly targets
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        {/* Activity Overview */}
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>
              {isSuperAdmin ? 'System Activity' : 'Recent Activity'}
            </CardTitle>
            <CardDescription>
              {isSuperAdmin 
                ? 'Latest platform events and system activities'
                : 'Your recent actions and updates'
              }
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {isSuperAdmin ? (
              <>
                <div className="flex items-center space-x-4">
                  <Monitor className="h-4 w-4 text-blue-600" />
                  <div className="flex-1 space-y-1">
                    <div className="text-sm font-medium">System monitoring active</div>
                    <div className="text-xs text-muted-foreground">
                      Real-time data collection enabled
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Live
                  </div>
                </div>
                
                {unacknowledgedAlertsCount > 0 && (
                  <div className="flex items-center space-x-4">
                    <AlertTriangle className="h-4 w-4 text-yellow-600" />
                    <div className="flex-1 space-y-1">
                      <div className="text-sm font-medium">
                        {unacknowledgedAlertsCount} unacknowledged alert{unacknowledgedAlertsCount !== 1 ? 's' : ''}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        Requires attention
                      </div>
                    </div>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => window.location.href = '/dashboard/sla-monitoring'}
                    >
                      View Details
                    </Button>
                  </div>
                )}
                
                <div className="flex items-center space-x-4">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <div className="flex-1 space-y-1">
                    <div className="text-sm font-medium">Platform operational</div>
                    <div className="text-xs text-muted-foreground">
                      All core services running normally
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Now
                  </div>
                </div>
              </>
            ) : (
              <>
                <div className="flex items-center space-x-4">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <div className="flex-1 space-y-1">
                    <div className="text-sm font-medium">Profile updated successfully</div>
                    <div className="text-xs text-muted-foreground">
                      Your account information is up to date
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Just now
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <Clock className="h-4 w-4 text-blue-600" />
                  <div className="flex-1 space-y-1">
                    <div className="text-sm font-medium">Welcome to SalesOptimizer</div>
                    <div className="text-xs text-muted-foreground">
                      Start exploring your dashboard features
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Today
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Account/System Overview */}
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>
              {isSuperAdmin ? 'System Overview' : 'Account Overview'}
            </CardTitle>
            <CardDescription>
              {isSuperAdmin 
                ? 'Platform health and status information'
                : 'Your account information'
              }
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {isSuperAdmin ? (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">System Status</span>
                  <Badge variant={
                    systemHealth?.overall_status === 'healthy' ? 'default' :
                    systemHealth?.overall_status === 'warning' ? 'secondary' : 'destructive'
                  }>
                    {systemHealth?.overall_status || 'Unknown'}
                  </Badge>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Uptime</span>
                  <span className="font-medium">
                    {systemHealth?.uptime_percentage?.toFixed(2) || '0.00'}%
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Running Since</span>
                  <span className="font-medium text-xs">
                    {systemHealth?.uptime_duration || 'Unknown'}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Health Score</span>
                  <span className="font-medium">
                    {systemHealth?.health_percentage?.toFixed(2) || '0.00'}%
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Active Alerts</span>
                  <span className={`font-medium ${activeAlertsCount > 0 ? 'text-yellow-600' : 'text-green-600'}`}>
                    {activeAlertsCount}
                  </span>
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Name</span>
                  <span className="font-medium">
                    {user ? createFullName(user.first_name || '', user.last_name || '') : 'User'}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Email</span>
                  <span className="font-medium">{user?.email}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Organization</span>
                  <span className="font-medium">{getOrganizationName()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Role</span>
                  <Badge variant="secondary">
                    {user?.role === 'org_admin' ? 'Org Admin' : 
                     user?.role === 'sales_manager' ? 'Manager' : 'Rep'}
                  </Badge>
                </div>
              </div>
            )}

            <div className="pt-4 space-y-2">
              <Button variant="outline" size="sm" className="w-full" asChild>
                <Link href="/settings">
                  <Settings className="h-4 w-4 mr-2" />
                  {isSuperAdmin ? 'System Settings' : 'Account Settings'}
                </Link>
              </Button>
              
              {isSuperAdmin && (
                <Button variant="outline" size="sm" className="w-full" asChild>
                  <Link href="/admin/sla-monitoring">
                    <Monitor className="h-4 w-4 mr-2" />
                    SLA Monitoring
                  </Link>
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Invite Modal for Super Admin */}
      {isSuperAdmin && (
        <InviteOrgAdminModal 
          open={isInviteModalOpen}
          onOpenChange={setIsInviteModalOpen}
        />
      )}
    </div>
  )
}
