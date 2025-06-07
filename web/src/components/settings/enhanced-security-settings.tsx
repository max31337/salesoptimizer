"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  tokenRevocationService, 
  type Session, 
  type RevokedSession,
  type SessionsResponse,
  type RevokedSessionsResponse,
  type GroupedSessionsResponse,
  type GroupedRevokedSessionsResponse
} from "@/features/auth/services/token-revocation-service"
import { useAuth } from "@/features/auth/hooks/useAuth"
import { 
  Smartphone, 
  Monitor, 
  LogOut, 
  Shield, 
  Clock, 
  MapPin,
  AlertTriangle,
  Loader2,
  ChevronLeft,
  ChevronRight,
  Users,
  Globe,
  List,
  Layers
} from "lucide-react"
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "@/components/ui/alert-dialog"

interface PaginationState {
  page: number
  pageSize: number
  totalPages: number
  totalCount: number
}

type ViewMode = 'list' | 'device' | 'ip'
type SessionData = SessionsResponse | GroupedSessionsResponse
type RevokedSessionData = RevokedSessionsResponse | GroupedRevokedSessionsResponse

export function EnhancedSecuritySettings() {
  const [activeSessions, setActiveSessions] = useState<Session[]>([])
  const [groupedActiveSessions, setGroupedActiveSessions] = useState<Record<string, Session[]>>({})
  const [revokedSessions, setRevokedSessions] = useState<RevokedSession[]>([])
  const [groupedRevokedSessions, setGroupedRevokedSessions] = useState<Record<string, RevokedSession[]>>({})
  
  const [activeTab, setActiveTab] = useState("active")
  const [viewMode, setViewMode] = useState<ViewMode>('list')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  
  const [activeSessionsPagination, setActiveSessionsPagination] = useState<PaginationState>({
    page: 1,
    pageSize: 10,
    totalPages: 0,
    totalCount: 0
  })
  const [revokedSessionsPagination, setRevokedSessionsPagination] = useState<PaginationState>({
    page: 1,
    pageSize: 10,
    totalPages: 0,
    totalCount: 0
  })
  
  const { logout } = useAuth()
  useEffect(() => {
    loadSessions()
  }, [activeTab, viewMode])

  const loadSessions = async () => {
    // Always reset to page 1 when viewMode changes to avoid pagination issues
    if (activeTab === "active") {
      await loadActiveSessions(1)
    } else {
      await loadRevokedSessions(1)
    }
  }

  const loadActiveSessions = async (page: number = 1) => {
    try {
      setIsLoading(true)
      setError("")
      
      let response: SessionData
      
      if (viewMode === 'list') {
        response = await tokenRevocationService.getActiveSessions(page, activeSessionsPagination.pageSize)
        const sessionResponse = response as SessionsResponse
        setActiveSessions(sessionResponse.sessions)
        setGroupedActiveSessions({})
        setActiveSessionsPagination({
          page: sessionResponse.page,
          pageSize: sessionResponse.page_size,
          totalPages: sessionResponse.total_pages,
          totalCount: sessionResponse.total_count
        })
      } else {
        const groupBy = viewMode === 'device' ? 'device' : 'ip'
        response = await tokenRevocationService.getActiveSessions(page, activeSessionsPagination.pageSize, groupBy)
        const groupedResponse = response as GroupedSessionsResponse
        setActiveSessions([])
        setGroupedActiveSessions(groupedResponse.grouped_sessions)
        setActiveSessionsPagination({
          page: groupedResponse.page,
          pageSize: groupedResponse.page_size,
          totalPages: groupedResponse.total_pages,
          totalCount: groupedResponse.total_sessions
        })
      }
    } catch (err: any) {
      console.error('Failed to load active sessions:', err)
      const errorMessage = err?.message || err?.detail || 'Failed to load active sessions'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const loadRevokedSessions = async (page: number = 1) => {
    try {
      setIsLoading(true)
      setError("")
      
      let response: RevokedSessionData
      
      if (viewMode === 'list') {
        response = await tokenRevocationService.getRevokedSessions(page, revokedSessionsPagination.pageSize)
        const sessionResponse = response as RevokedSessionsResponse
        setRevokedSessions(sessionResponse.sessions)
        setGroupedRevokedSessions({})
        setRevokedSessionsPagination({
          page: sessionResponse.page,
          pageSize: sessionResponse.page_size,
          totalPages: sessionResponse.total_pages,
          totalCount: sessionResponse.total_count
        })
      } else {
        const groupBy = viewMode === 'device' ? 'device' : 'ip'
        response = await tokenRevocationService.getRevokedSessions(page, revokedSessionsPagination.pageSize, groupBy)
        const groupedResponse = response as GroupedRevokedSessionsResponse
        setRevokedSessions([])
        setGroupedRevokedSessions(groupedResponse.grouped_sessions)
        setRevokedSessionsPagination({
          page: groupedResponse.page,
          pageSize: groupedResponse.page_size,
          totalPages: groupedResponse.total_pages,
          totalCount: groupedResponse.total_sessions
        })
      }
    } catch (err: any) {
      console.error('Failed to load revoked sessions:', err)
      const errorMessage = err?.message || err?.detail || 'Failed to load revoked sessions'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogoutAllDevices = async () => {
    try {
      setActionLoading("logout-all")
      const result = await tokenRevocationService.logoutAllDevices(true)
      
      if (result.success) {
        setSuccess("Successfully logged out from all devices")
        // This will trigger a full app logout
        await logout()
      } else {
        setError(result.message || "Failed to logout from all devices")
      }
    } catch (err: any) {
      console.error('Failed to logout from all devices:', err)
      setError(err?.message || "Failed to logout from all devices")
    } finally {
      setActionLoading(null)
    }
  }

  const handleLogoutCurrentDevice = async () => {
    try {
      setActionLoading("logout-current")
      const result = await tokenRevocationService.logoutCurrentDevice()
      
      if (result.success) {
        setSuccess("Successfully logged out from current device")
        // This will trigger a full app logout
        await logout()
      } else {
        setError(result.message || "Failed to logout from current device")
      }
    } catch (err: any) {
      console.error('Failed to logout from current device:', err)
      setError(err?.message || "Failed to logout from current device")
    } finally {
      setActionLoading(null)
    }
  }

  const handleRevokeSession = async (sessionId: string) => {
    try {
      setActionLoading(sessionId)
      const result = await tokenRevocationService.revokeSessionById(sessionId)
      
      if (result.success) {
        setSuccess("Session revoked successfully")
        await loadSessions() // Reload sessions
      } else {
        setError(result.message || "Failed to revoke session")
      }
    } catch (err: any) {
      console.error('Failed to revoke session:', err)
      setError(err?.message || "Failed to revoke session")
    } finally {
      setActionLoading(null)
    }
  }

  const getDeviceIcon = (deviceInfo: string, userAgent: string) => {
    const deviceInfoLower = deviceInfo?.toLowerCase() || ''
    const userAgentLower = userAgent?.toLowerCase() || ''
    
    if (deviceInfoLower.includes('mobile') || deviceInfoLower.includes('android') || deviceInfoLower.includes('iphone') ||
        userAgentLower.includes('mobile') || userAgentLower.includes('android') || userAgentLower.includes('iphone')) {
      return <Smartphone className="h-4 w-4" />
    }
    return <Monitor className="h-4 w-4" />
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const renderSessionCard = (session: Session | RevokedSession) => {
    const isRevoked = 'revoked_at' in session
    
    return (
      <Card key={session.id} className="mb-3">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {getDeviceIcon(session.device_info, session.user_agent)}
              <div>
                <div className="font-medium">
                  {session.device_info || "Unknown Device"}
                  {session.is_current && (
                    <Badge variant="secondary" className="ml-2">Current</Badge>
                  )}
                </div>
                <div className="text-sm text-muted-foreground flex items-center space-x-4">
                  <span className="flex items-center">
                    <MapPin className="h-3 w-3 mr-1" />
                    {session.ip_address || "Unknown IP"}
                  </span>
                  <span className="flex items-center">
                    <Clock className="h-3 w-3 mr-1" />
                    {formatDate(session.created_at)}
                  </span>
                  {isRevoked && 'revoked_at' in session && (
                    <span className="flex items-center text-red-600">
                      <AlertTriangle className="h-3 w-3 mr-1" />
                      Revoked: {formatDate(session.revoked_at)}
                    </span>
                  )}
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  {session.user_agent || "Unknown Browser"}
                </div>
              </div>
            </div>
            {!isRevoked && !session.is_current && (
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button 
                    variant="outline" 
                    size="sm"
                    disabled={actionLoading === session.id}
                  >
                    {actionLoading === session.id ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <LogOut className="h-4 w-4" />
                    )}
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Revoke Session</AlertDialogTitle>
                    <AlertDialogDescription>
                      Are you sure you want to revoke this session? The user will be logged out from this device.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction onClick={() => handleRevokeSession(session.id)}>
                      Revoke Session
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            )}
          </div>
        </CardContent>
      </Card>
    )
  }

  const renderGroupedSessions = (groupedSessions: Record<string, Session[]> | Record<string, RevokedSession[]>) => {
    return Object.entries(groupedSessions).map(([groupKey, sessions]) => (
      <Card key={groupKey} className="mb-4">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center space-x-2">
            {viewMode === 'device' ? (
              <Users className="h-5 w-5" />
            ) : (
              <Globe className="h-5 w-5" />
            )}
            <span>{groupKey}</span>
            <Badge variant="outline">{sessions.length} session{sessions.length !== 1 ? 's' : ''}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="space-y-2">
            {sessions.map((session: Session | RevokedSession) => renderSessionCard(session))}
          </div>
        </CardContent>
      </Card>
    ))
  }

  const renderPagination = () => {
    const pagination = activeTab === "active" ? activeSessionsPagination : revokedSessionsPagination
    const loadPage = activeTab === "active" ? loadActiveSessions : loadRevokedSessions
    
    if (pagination.totalPages <= 1) return null
    
    return (
      <div className="flex items-center justify-between mt-4">
        <div className="text-sm text-muted-foreground">
          Page {pagination.page} of {pagination.totalPages} ({pagination.totalCount} total)
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => loadPage(pagination.page - 1)}
            disabled={pagination.page <= 1 || isLoading}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => loadPage(pagination.page + 1)}
            disabled={pagination.page >= pagination.totalPages || isLoading}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    )
  }

  const ViewModeButton = ({ mode, icon: Icon, label }: { mode: ViewMode, icon: any, label: string }) => (
    <Button
      variant={viewMode === mode ? "default" : "outline"}
      size="sm"
      onClick={() => setViewMode(mode)}
      className="flex items-center space-x-2"
      disabled={isLoading}
    >
      <Icon className="h-4 w-4" />
      <span>{label}</span>
    </Button>
  )

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Security Settings</h2>
        <p className="text-muted-foreground">
          Manage your account security and active sessions
        </p>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert>
          <Shield className="h-4 w-4" />
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Manage your sessions across all devices
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button 
                  variant="destructive" 
                  className="flex-1"
                  disabled={actionLoading === "logout-all"}
                >
                  {actionLoading === "logout-all" ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <LogOut className="h-4 w-4 mr-2" />
                  )}
                  Logout All Devices
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Logout from all devices?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This will end all active sessions across all your devices. You'll need to log in again on each device.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={handleLogoutAllDevices}>
                    Logout All Devices
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>

            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button 
                  variant="outline" 
                  className="flex-1"
                  disabled={actionLoading === "logout-current"}
                >
                  {actionLoading === "logout-current" ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <LogOut className="h-4 w-4 mr-2" />
                  )}
                  Logout Current Device
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Logout from current device?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This will end your session on this device only. You'll need to log in again.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={handleLogoutCurrentDevice}>
                    Logout Current Device
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </CardContent>
      </Card>

      {/* Sessions Management */}
      <Card>
        <CardHeader>
          <CardTitle>Sessions Management</CardTitle>
          <CardDescription>
            View and manage your active and revoked sessions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Enhanced View Mode Controls */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between space-y-4 sm:space-y-0">
              <h3 className="text-lg font-medium">View Options</h3>
              <div className="flex items-center space-x-2">
                <ViewModeButton mode="list" icon={List} label="List View" />
                <ViewModeButton mode="device" icon={Users} label="Group by Device" />
                <ViewModeButton mode="ip" icon={Globe} label="Group by IP" />
              </div>
            </div>

            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="active" className="flex items-center space-x-2">
                  <Shield className="h-4 w-4" />
                  <span>Active Sessions</span>
                </TabsTrigger>
                <TabsTrigger value="revoked" className="flex items-center space-x-2">
                  <AlertTriangle className="h-4 w-4" />
                  <span>Revoked Sessions</span>
                </TabsTrigger>
              </TabsList>

              <TabsContent value="active" className="space-y-4">
                {isLoading ? (
                  <div className="flex items-center justify-center p-8">
                    <Loader2 className="h-8 w-8 animate-spin" />
                    <span className="ml-2">Loading sessions...</span>
                  </div>
                ) : viewMode === 'list' ? (
                  <div className="space-y-3">
                    {activeSessions.length === 0 ? (
                      <div className="text-center p-8 text-muted-foreground">
                        No active sessions found
                      </div>
                    ) : (
                      activeSessions.map(renderSessionCard)
                    )}
                  </div>
                ) : (
                  <div className="space-y-4">
                    {Object.keys(groupedActiveSessions).length === 0 ? (
                      <div className="text-center p-8 text-muted-foreground">
                        No active sessions found
                      </div>
                    ) : (
                      renderGroupedSessions(groupedActiveSessions)
                    )}
                  </div>
                )}
                {renderPagination()}
              </TabsContent>

              <TabsContent value="revoked" className="space-y-4">
                {isLoading ? (
                  <div className="flex items-center justify-center p-8">
                    <Loader2 className="h-8 w-8 animate-spin" />
                    <span className="ml-2">Loading sessions...</span>
                  </div>
                ) : viewMode === 'list' ? (
                  <div className="space-y-3">
                    {revokedSessions.length === 0 ? (
                      <div className="text-center p-8 text-muted-foreground">
                        No revoked sessions found
                      </div>
                    ) : (
                      revokedSessions.map(renderSessionCard)
                    )}
                  </div>
                ) : (
                  <div className="space-y-4">
                    {Object.keys(groupedRevokedSessions).length === 0 ? (
                      <div className="text-center p-8 text-muted-foreground">
                        No revoked sessions found
                      </div>
                    ) : (
                      renderGroupedSessions(groupedRevokedSessions)
                    )}
                  </div>
                )}
                {renderPagination()}
              </TabsContent>
            </Tabs>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
