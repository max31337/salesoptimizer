"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { tokenRevocationService } from "@/features/auth/services/token-revocation-service"
import { useAuth } from "@/features/auth/hooks/useAuth"
import { 
  Smartphone, 
  Monitor, 
  LogOut, 
  Shield, 
  Clock, 
  MapPin,
  AlertTriangle,
  Loader2
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

interface Session {
  id: string
  device_info: string
  ip_address: string
  user_agent: string
  created_at: string
  last_used_at: string
  is_current: boolean
}

export function SecuritySettings() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const { logout } = useAuth()

  useEffect(() => {
    loadSessions()
  }, [])
  const loadSessions = async () => {
    try {
      setIsLoading(true)
      setError("")
      const response = await tokenRevocationService.getActiveSessions()
      setSessions(response.sessions)
    } catch (err: any) {
      console.error('Failed to load sessions:', err)
      const errorMessage = err?.message || err?.detail || 'Failed to load active sessions'
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
      
      // Reload sessions to update the list
      await loadSessions()
    } catch (err: any) {
      console.error('Failed to revoke session:', err)
      const errorMessage = err?.message || err?.detail || 'Failed to revoke session'
      setError(errorMessage)
    } finally {
      setActionLoading(null)
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
      </Card>

      {/* Active Sessions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Monitor className="h-5 w-5" />
            Active Sessions
          </CardTitle>
          <CardDescription>
            Manage devices that are currently signed into your account
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin" />
              <span className="ml-2">Loading sessions...</span>
            </div>
          ) : sessions.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No active sessions found
            </div>
          ) : (
            <div className="space-y-4">
              {sessions.map((session) => (
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
          )}
        </CardContent>
      </Card>
    </div>
  )
}
