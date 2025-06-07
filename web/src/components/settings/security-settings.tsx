"use client"

import React, { useState, useEffect } from "react"
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
  MoreHorizontal,
  List,
  Users,
  Globe
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

export function SecuritySettings() {
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
    totalCount: 0  })
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

  const handleLogoutCurrentDevice = async () => {
    try {
      setActionLoading('current')
      setError("")
      setSuccess("")
      
      await tokenRevocationService.logoutCurrentDevice()
      setSuccess('Successfully logged out from current device')
      
      // Logout the user from the app
      await logout()
    } catch (err: any) {
      console.error('Failed to logout current device:', err)
      const errorMessage = err?.message || err?.detail || 'Failed to logout from current device'
      setError(errorMessage)
    } finally {
      setActionLoading(null)
    }
  }

  const handleLogoutAllDevices = async () => {
    try {
      setActionLoading('all')
      setError("")
      setSuccess("")
      
      await tokenRevocationService.logoutAllDevices(true)
      setSuccess('Successfully logged out from all devices')
      
      // Logout the user from the app
      await logout()
    } catch (err: any) {
      console.error('Failed to logout all devices:', err)
      const errorMessage = err?.message || err?.detail || 'Failed to logout from all devices'
      setError(errorMessage)
    } finally {
      setActionLoading(null)
    }
  }
  const handleRevokeSession = async (sessionId: string) => {
    try {
      setActionLoading(sessionId)
      setError("")
      setSuccess("")
      
      await tokenRevocationService.revokeSessionById(sessionId)
      setSuccess('Session revoked successfully')
      
      // Reload active sessions to update the list
      await loadActiveSessions(activeSessionsPagination.page)
      // Load revoked sessions to update that list too
      await loadRevokedSessions(revokedSessionsPagination.page)
    } catch (err: any) {
      console.error('Failed to revoke session:', err)
      const errorMessage = err?.message || err?.detail || 'Failed to revoke session'
      setError(errorMessage)
    } finally {
      setActionLoading(null)
    }
  }

  const handleActivePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= activeSessionsPagination.totalPages) {
      loadActiveSessions(newPage)
    }
  }

  const handleRevokedPageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= revokedSessionsPagination.totalPages) {
      loadRevokedSessions(newPage)
    }
  }

  const getDeviceIcon = (userAgent: string) => {
    if (!userAgent) return <Monitor className="h-4 w-4" />
    
    if (userAgent.toLowerCase().includes('mobile') || userAgent.toLowerCase().includes('android') || userAgent.toLowerCase().includes('iphone')) {
      return <Smartphone className="h-4 w-4" />
    }
    return <Monitor className="h-4 w-4" />
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const formatUserAgent = (userAgent: string) => {
    // Extract browser and OS info from user agent
    if (!userAgent) return 'Unknown Browser'
    
    if (userAgent.includes('Chrome')) {
      if (userAgent.includes('Windows')) return 'Chrome on Windows'
      if (userAgent.includes('Mac')) return 'Chrome on macOS'
      if (userAgent.includes('Linux')) return 'Chrome on Linux'
      return 'Chrome Browser'
    }
    if (userAgent.includes('Firefox')) return 'Firefox Browser'
    if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) return 'Safari Browser'
    if (userAgent.includes('Edge')) return 'Microsoft Edge'
    return 'Unknown Browser'
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-foreground mb-2">Security Settings</h2>
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
        <Alert className="border-green-200 bg-green-50 text-green-800 dark:border-green-800 dark:bg-green-950 dark:text-green-200">
          <Shield className="h-4 w-4" />
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Quick Security Actions
          </CardTitle>
          <CardDescription>
            Logout from devices to secure your account
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="outline" className="flex items-center gap-2">
                  <LogOut className="h-4 w-4" />
                  {actionLoading === 'current' && <Loader2 className="h-4 w-4 animate-spin" />}
                  Logout Current Device
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Logout from Current Device?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This will sign you out of this device only. You'll need to sign in again to continue using the application.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction 
                    onClick={handleLogoutCurrentDevice}
                    disabled={actionLoading === 'current'}
                  >
                    {actionLoading === 'current' ? 'Logging out...' : 'Logout'}
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>

            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="destructive" className="flex items-center gap-2">
                  <LogOut className="h-4 w-4" />
                  {actionLoading === 'all' && <Loader2 className="h-4 w-4 animate-spin" />}
                  Logout All Devices
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Logout from All Devices?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This will sign you out of ALL devices including this one. You'll need to sign in again on each device to continue using the application.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction 
                    onClick={handleLogoutAllDevices}
                    disabled={actionLoading === 'all'}
                    className="bg-red-600 hover:bg-red-700"
                  >
                    {actionLoading === 'all' ? 'Logging out...' : 'Logout All'}
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </CardContent>
      </Card>      {/* Sessions Management with Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="active" className="flex items-center gap-2">
            <Monitor className="h-4 w-4" />
            Active Sessions
            {activeSessionsPagination.totalCount > 0 && (
              <Badge variant="secondary" className="ml-1">
                {activeSessionsPagination.totalCount}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="revoked" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Revoked Sessions
            {revokedSessionsPagination.totalCount > 0 && (
              <Badge variant="secondary" className="ml-1">
                {revokedSessionsPagination.totalCount}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="active">
          <Card>            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Monitor className="h-5 w-5" />
                Active Sessions
              </CardTitle>
              <CardDescription>
                Manage devices that are currently signed into your account
              </CardDescription>
              
              {/* View Mode Selector */}
              <div className="flex flex-wrap gap-2 mt-4">
                <Button
                  variant={viewMode === 'list' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setViewMode('list')}
                  className="flex items-center gap-2"
                >
                  <List className="h-4 w-4" />
                  List View
                </Button>
                <Button
                  variant={viewMode === 'device' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setViewMode('device')}
                  className="flex items-center gap-2"
                >
                  <Monitor className="h-4 w-4" />
                  Group by Device
                </Button>
                <Button
                  variant={viewMode === 'ip' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setViewMode('ip')}
                  className="flex items-center gap-2"
                >
                  <Globe className="h-4 w-4" />
                  Group by IP
                </Button>
              </div>
            </CardHeader>
            <CardContent>              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin" />
                  <span className="ml-2">Loading sessions...</span>
                </div>
              ) : viewMode === 'list' ? (
                // List View
                activeSessions.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    No active sessions found
                  </div>
                ) : (
                  <>
                    <div className="space-y-4">
                      {activeSessions.map((session) => (
                        <div
                          key={session.id}
                          className="flex items-center justify-between p-4 border rounded-lg bg-card"
                        >
                          <div className="flex items-center space-x-4">
                            <div className="p-2 bg-muted rounded-lg">
                              {getDeviceIcon(session.user_agent)}
                            </div>
                            <div className="space-y-1">
                              <div className="flex items-center gap-2">
                                <span className="font-medium">
                                  {formatUserAgent(session.user_agent)}
                                </span>
                                {session.is_current && (
                                  <Badge variant="secondary" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                                    Current Device
                                  </Badge>
                                )}
                              </div>
                              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                <div className="flex items-center gap-1">
                                  <MapPin className="h-3 w-3" />
                                  {session.ip_address}
                                </div>
                                <div className="flex items-center gap-1">
                                  <Clock className="h-3 w-3" />
                                  Last used: {formatDate(session.last_used_at)}
                                </div>
                              </div>
                            </div>
                          </div>
                          {!session.is_current && (
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
                                  {actionLoading === session.id ? 'Revoking...' : 'Revoke'}
                                </Button>
                              </AlertDialogTrigger>
                              <AlertDialogContent>
                                <AlertDialogHeader>
                                  <AlertDialogTitle>Revoke Session?</AlertDialogTitle>
                                  <AlertDialogDescription>
                                    This will sign out the device "{formatUserAgent(session.user_agent)}" 
                                    from IP {session.ip_address}. This action cannot be undone.
                                  </AlertDialogDescription>
                                </AlertDialogHeader>
                                <AlertDialogFooter>
                                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                                  <AlertDialogAction 
                                    onClick={() => handleRevokeSession(session.id)}
                                    disabled={actionLoading === session.id}
                                  >
                                    {actionLoading === session.id ? 'Revoking...' : 'Revoke Session'}
                                  </AlertDialogAction>
                                </AlertDialogFooter>
                              </AlertDialogContent>
                            </AlertDialog>
                          )}
                        </div>
                      ))}
                    </div>
                  </>
                )
              ) : (
                // Grouped View
                Object.keys(groupedActiveSessions).length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    No active sessions found
                  </div>
                ) : (
                  <div className="space-y-6">
                    {Object.entries(groupedActiveSessions).map(([groupKey, sessions]) => (
                      <div key={groupKey} className="space-y-3">
                        <div className="flex items-center gap-2 pb-2 border-b">
                          <div className="p-2 bg-muted rounded-lg">
                            {viewMode === 'device' ? (
                              getDeviceIcon(sessions[0]?.user_agent || '')
                            ) : (
                              <Globe className="h-4 w-4" />
                            )}
                          </div>
                          <div>
                            <h3 className="font-semibold text-lg">
                              {viewMode === 'device' ? formatUserAgent(groupKey) : groupKey}
                            </h3>
                            <p className="text-sm text-muted-foreground">
                              {sessions.length} session{sessions.length !== 1 ? 's' : ''}
                            </p>
                          </div>
                        </div>
                        <div className="space-y-3 ml-6">
                          {sessions.map((session) => (
                            <div
                              key={session.id}
                              className="flex items-center justify-between p-3 border rounded-lg bg-card/50"
                            >
                              <div className="space-y-1">
                                <div className="flex items-center gap-2">
                                  <span className="font-medium text-sm">
                                    {viewMode === 'device' ? session.ip_address : formatUserAgent(session.user_agent)}
                                  </span>
                                  {session.is_current && (
                                    <Badge variant="secondary" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                                      Current Device
                                    </Badge>
                                  )}
                                </div>
                                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                                  <div className="flex items-center gap-1">
                                    <Clock className="h-3 w-3" />
                                    Last used: {formatDate(session.last_used_at)}
                                  </div>
                                </div>
                              </div>
                              {!session.is_current && (
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
                                      {actionLoading === session.id ? 'Revoking...' : 'Revoke'}
                                    </Button>
                                  </AlertDialogTrigger>
                                  <AlertDialogContent>
                                    <AlertDialogHeader>
                                      <AlertDialogTitle>Revoke Session?</AlertDialogTitle>
                                      <AlertDialogDescription>
                                        This will sign out the device "{formatUserAgent(session.user_agent)}" 
                                        from IP {session.ip_address}. This action cannot be undone.
                                      </AlertDialogDescription>
                                    </AlertDialogHeader>
                                    <AlertDialogFooter>
                                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                                      <AlertDialogAction 
                                        onClick={() => handleRevokeSession(session.id)}
                                        disabled={actionLoading === session.id}
                                      >
                                        {actionLoading === session.id ? 'Revoking...' : 'Revoke Session'}
                                      </AlertDialogAction>
                                    </AlertDialogFooter>
                                  </AlertDialogContent>
                                </AlertDialog>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )
              )}              
              {/* Pagination for Active Sessions */}
              {activeSessionsPagination.totalPages > 1 && (
                <div className="flex items-center justify-between mt-6 pt-4 border-t">
                  <div className="text-sm text-muted-foreground">
                    Showing {(activeSessionsPagination.page - 1) * activeSessionsPagination.pageSize + 1} to{' '}
                    {Math.min(activeSessionsPagination.page * activeSessionsPagination.pageSize, activeSessionsPagination.totalCount)} of{' '}
                    {activeSessionsPagination.totalCount} sessions
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleActivePageChange(activeSessionsPagination.page - 1)}
                      disabled={activeSessionsPagination.page <= 1}
                    >
                      <ChevronLeft className="h-4 w-4" />
                      Previous
                    </Button>
                    <div className="flex items-center space-x-1">
                      {Array.from({ length: activeSessionsPagination.totalPages }, (_, i) => i + 1)
                        .filter(page => 
                          page === 1 || 
                          page === activeSessionsPagination.totalPages || 
                          Math.abs(page - activeSessionsPagination.page) <= 1
                        )
                        .map((page, index, array) => (
                          <div key={page} className="flex items-center">
                            {index > 0 && array[index - 1] !== page - 1 && (
                              <span className="px-2 text-muted-foreground">
                                <MoreHorizontal className="h-4 w-4" />
                              </span>
                            )}
                            <Button
                              variant={page === activeSessionsPagination.page ? "default" : "outline"}
                              size="sm"
                              onClick={() => handleActivePageChange(page)}
                              className="min-w-[2.5rem]"
                            >
                              {page}
                            </Button>
                          </div>
                        ))}
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleActivePageChange(activeSessionsPagination.page + 1)}
                      disabled={activeSessionsPagination.page >= activeSessionsPagination.totalPages}
                    >
                      Next
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="revoked">
          <Card>            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Revoked Sessions
              </CardTitle>
              <CardDescription>
                Sessions that have been logged out or revoked
              </CardDescription>
              
              {/* View Mode Selector */}
              <div className="flex flex-wrap gap-2 mt-4">
                <Button
                  variant={viewMode === 'list' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setViewMode('list')}
                  className="flex items-center gap-2"
                >
                  <List className="h-4 w-4" />
                  List View
                </Button>
                <Button
                  variant={viewMode === 'device' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setViewMode('device')}
                  className="flex items-center gap-2"
                >
                  <Monitor className="h-4 w-4" />
                  Group by Device
                </Button>
                <Button
                  variant={viewMode === 'ip' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setViewMode('ip')}
                  className="flex items-center gap-2"
                >
                  <Globe className="h-4 w-4" />
                  Group by IP
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin" />
                  <span className="ml-2">Loading revoked sessions...</span>
                </div>
              ) : viewMode === 'list' ? (
                revokedSessions.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    No revoked sessions found
                  </div>
                ) : (
                  <>
                    <div className="space-y-4">
                      {revokedSessions.map((session) => (
                        <div
                          key={session.id}
                          className="flex items-center justify-between p-4 border rounded-lg bg-card opacity-75"
                        >
                          <div className="flex items-center space-x-4">
                            <div className="p-2 bg-muted rounded-lg">
                              {getDeviceIcon(session.user_agent)}
                            </div>
                            <div className="space-y-1">
                              <div className="flex items-center gap-2">
                                <span className="font-medium">
                                  {formatUserAgent(session.user_agent)}
                                </span>
                                <Badge variant="destructive">
                                  Revoked
                                </Badge>
                              </div>
                              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                <div className="flex items-center gap-1">
                                  <MapPin className="h-3 w-3" />
                                  {session.ip_address}
                                </div>
                                <div className="flex items-center gap-1">
                                  <Clock className="h-3 w-3" />
                                  Created: {formatDate(session.created_at)}
                                </div>
                                <div className="flex items-center gap-1">
                                  <Clock className="h-3 w-3" />
                                  Revoked: {formatDate(session.revoked_at)}
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                    
                    {/* Pagination for Revoked Sessions */}
                    {revokedSessionsPagination.totalPages > 1 && (
                      <div className="flex items-center justify-between mt-6 pt-4 border-t">
                        <div className="text-sm text-muted-foreground">
                          Showing {(revokedSessionsPagination.page - 1) * revokedSessionsPagination.pageSize + 1} to{' '}
                          {Math.min(revokedSessionsPagination.page * revokedSessionsPagination.pageSize, revokedSessionsPagination.totalCount)} of{' '}
                          {revokedSessionsPagination.totalCount} sessions
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleRevokedPageChange(revokedSessionsPagination.page - 1)}
                            disabled={revokedSessionsPagination.page <= 1}
                          >
                            <ChevronLeft className="h-4 w-4" />
                            Previous
                          </Button>
                          <div className="flex items-center space-x-1">
                            {Array.from({ length: revokedSessionsPagination.totalPages }, (_, i) => i + 1)
                              .filter(page => 
                                page === 1 || 
                                page === revokedSessionsPagination.totalPages || 
                                Math.abs(page - revokedSessionsPagination.page) <= 1
                              )
                              .map((page, index, array) => (
                                <div key={page} className="flex items-center">
                                  {index > 0 && array[index - 1] !== page - 1 && (
                                    <span className="px-2 text-muted-foreground">
                                      <MoreHorizontal className="h-4 w-4" />
                                    </span>
                                  )}
                                  <Button
                                    variant={page === revokedSessionsPagination.page ? "default" : "outline"}
                                    size="sm"
                                    onClick={() => handleRevokedPageChange(page)}
                                    className="min-w-[2.5rem]"
                                  >
                                    {page}
                                  </Button>
                                </div>
                              ))}
                          </div>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleRevokedPageChange(revokedSessionsPagination.page + 1)}
                            disabled={revokedSessionsPagination.page >= revokedSessionsPagination.totalPages}
                          >
                            Next
                            <ChevronRight className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    )}
                  </>
                )
              ) : (
                // Grouped View for Revoked Sessions
                Object.keys(groupedRevokedSessions).length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    No revoked sessions found
                  </div>
                ) : (
                  <div className="space-y-6">
                    {Object.entries(groupedRevokedSessions).map(([groupKey, sessions]) => (
                      <div key={groupKey} className="space-y-3">
                        <div className="flex items-center gap-2 pb-2 border-b">
                          <div className="p-2 bg-muted rounded-lg">
                            {viewMode === 'device' ? (
                              getDeviceIcon(sessions[0]?.user_agent || '')
                            ) : (
                              <Globe className="h-4 w-4" />
                            )}
                          </div>
                          <div>
                            <h3 className="font-semibold text-lg">
                              {viewMode === 'device' ? formatUserAgent(groupKey) : groupKey}
                            </h3>
                            <p className="text-sm text-muted-foreground">
                              {sessions.length} session{sessions.length !== 1 ? 's' : ''}
                            </p>
                          </div>
                        </div>
                        <div className="space-y-3 ml-6">
                          {sessions.map((session) => (
                            <div
                              key={session.id}
                              className="flex items-center justify-between p-3 border rounded-lg bg-card/50 opacity-75"
                            >
                              <div className="space-y-1">
                                <div className="flex items-center gap-2">
                                  <span className="font-medium text-sm">
                                    {viewMode === 'device' ? session.ip_address : formatUserAgent(session.user_agent)}
                                  </span>
                                  <Badge variant="destructive">
                                    Revoked
                                  </Badge>
                                </div>
                                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                                  <div className="flex items-center gap-1">
                                    <Clock className="h-3 w-3" />
                                    Created: {formatDate(session.created_at)}
                                  </div>
                                  <div className="flex items-center gap-1">
                                    <Clock className="h-3 w-3" />
                                    Revoked: {formatDate(session.revoked_at)}
                                  </div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )
              )}

              {/* Pagination for Revoked Sessions */}
              {revokedSessionsPagination.totalPages > 1 && (
                <div className="flex items-center justify-between mt-6 pt-4 border-t">
                  <div className="text-sm text-muted-foreground">
                    Showing {(revokedSessionsPagination.page - 1) * revokedSessionsPagination.pageSize + 1} to{' '}
                    {Math.min(revokedSessionsPagination.page * revokedSessionsPagination.pageSize, revokedSessionsPagination.totalCount)} of{' '}
                    {revokedSessionsPagination.totalCount} sessions
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleRevokedPageChange(revokedSessionsPagination.page - 1)}
                      disabled={revokedSessionsPagination.page <= 1}
                    >
                      <ChevronLeft className="h-4 w-4" />
                      Previous
                    </Button>
                    <div className="flex items-center space-x-1">
                      {Array.from({ length: revokedSessionsPagination.totalPages }, (_, i) => i + 1)
                        .filter(page => 
                          page === 1 || 
                          page === revokedSessionsPagination.totalPages || 
                          Math.abs(page - revokedSessionsPagination.page) <= 1
                        )
                        .map((page, index, array) => (
                          <div key={page} className="flex items-center">
                            {index > 0 && array[index - 1] !== page - 1 && (
                              <span className="px-2 text-muted-foreground">
                                <MoreHorizontal className="h-4 w-4" />
                              </span>
                            )}
                            <Button
                              variant={page === revokedSessionsPagination.page ? "default" : "outline"}
                              size="sm"
                              onClick={() => handleRevokedPageChange(page)}
                              className="min-w-[2.5rem]"
                            >
                              {page}
                            </Button>
                          </div>
                        ))}
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleRevokedPageChange(revokedSessionsPagination.page + 1)}
                      disabled={revokedSessionsPagination.page >= revokedSessionsPagination.totalPages}
                    >
                      Next
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
