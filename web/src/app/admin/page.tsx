"use client"

import { useState } from "react"
import { useAuth } from "@/features/auth/hooks/useAuth"
import { useClientWebSocketSLA } from "@/features/sla/hooks/useClientWebSocketSLA"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  Monitor, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Activity,
  Settings,
  Users,
  Database,
  Loader2,
  Wifi,
  WifiOff
} from "lucide-react"
import Link from "next/link"
import { format } from "date-fns"

export default function SuperAdminPage() {
  const { user } = useAuth()
  
  // Use WebSocket SLA data for real-time monitoring
  const { 
    systemHealth, 
    alerts, 
    isLoading: slaLoading, 
    isConnected: wsConnected,
    lastUpdated 
  } = useClientWebSocketSLA()
  // Check if user is super admin
  if (user?.role !== 'super_admin') {
    return (
      <div className="flex-1 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-center">Access Denied</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-center text-muted-foreground">
              You need super admin privileges to access this area.
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Calculate alert statistics
  const activeAlertsCount = alerts.length
  const unacknowledgedAlertsCount = alerts.filter(alert => !alert.acknowledged).length
  const criticalAlertsCount = alerts.filter(alert => alert.alert_type === 'critical').length
  const warningAlertsCount = alerts.filter(alert => alert.alert_type === 'warning').length

  const handleLogout = async () => {
    // Logout functionality moved to sidebar
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
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="flex items-center gap-2 justify-end">
                  <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  <p className="text-xs text-muted-foreground flex items-center gap-1">
                    {wsConnected ? (
                      <>
                        <Wifi className="h-3 w-3" />
                        Real-time
                      </>
                    ) : (
                      <>
                        <WifiOff className="h-3 w-3" />
                        Offline
                      </>
                    )}
                  </p>
                </div>
                <p className="text-xs text-muted-foreground">Last updated</p>
                <p className="text-sm font-medium">
                  {lastUpdated ? format(lastUpdated, 'HH:mm:ss') : '---'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          
          {/* System Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">System Status</CardTitle>
                <div className="flex items-center gap-2">
                  {slaLoading && !systemHealth && <Loader2 className="h-3 w-3 animate-spin text-muted-foreground" />}
                  <Monitor className="h-4 w-4 text-muted-foreground" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <div className={`text-2xl font-bold ${
                    systemHealth?.overall_status === 'healthy' 
                      ? 'text-green-600 dark:text-green-400'
                      : systemHealth?.overall_status === 'warning'
                      ? 'text-yellow-600 dark:text-yellow-400'
                      : systemHealth?.overall_status === 'critical'
                      ? 'text-red-600 dark:text-red-400'
                      : 'text-muted-foreground'
                  }`}>
                    {systemHealth 
                      ? `${systemHealth.healthy_metrics}/${systemHealth.total_metrics}`
                      : slaLoading ? '---' : 'N/A'
                    }
                  </div>
                  <Badge 
                    variant={
                      systemHealth?.overall_status === 'healthy' 
                        ? 'default'
                        : systemHealth?.overall_status === 'warning'
                        ? 'secondary'
                        : systemHealth?.overall_status === 'critical'
                        ? 'destructive'
                        : 'outline'
                    }
                    className="text-xs"
                  >
                    {systemHealth?.overall_status || (slaLoading ? 'Loading...' : 'Unknown')}
                  </Badge>
                </div>
                <div className="flex items-center gap-1 mt-1">
                  <p className="text-xs text-muted-foreground">
                    {activeAlertsCount > 0 ? `${activeAlertsCount} alerts` : 'No alerts'}
                  </p>
                  {unacknowledgedAlertsCount > 0 && (
                    <>
                      <span className="text-xs text-muted-foreground">•</span>
                      <div className="flex items-center gap-1">
                        <AlertTriangle className="h-3 w-3 text-orange-500" />
                        <span className="text-xs text-orange-600 dark:text-orange-400">
                          {unacknowledgedAlertsCount} unacknowledged
                        </span>
                      </div>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Health Score</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {slaLoading ? '...' : `${systemHealth?.health_percentage?.toFixed(2) || '0.00'}%`}
                </div>
                <p className="text-xs text-muted-foreground">
                  Overall system health
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Critical Alerts</CardTitle>
                <AlertTriangle className="h-4 w-4 text-red-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {criticalAlertsCount}
                </div>
                <p className="text-xs text-muted-foreground">
                  Require immediate action
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Warning Alerts</CardTitle>
                <AlertTriangle className="h-4 w-4 text-yellow-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-yellow-600">
                  {warningAlertsCount}
                </div>
                <p className="text-xs text-muted-foreground">
                  Need monitoring
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <Card className="hover:shadow-md transition-shadow">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-red-500" />
                  System Alerts
                </CardTitle>
                <CardDescription>
                  Monitor and manage system alerts in real-time
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold">{activeAlertsCount}</div>
                    <p className="text-sm text-muted-foreground">Active alerts</p>
                  </div>
                  <Button asChild>
                    <Link href="/admin/alerts">
                      View Alerts
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="hover:shadow-md transition-shadow">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5 text-blue-500" />
                  System Metrics
                </CardTitle>
                <CardDescription>
                  View detailed performance metrics and analytics
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold">
                      {systemHealth?.total_metrics || 0}
                    </div>
                    <p className="text-sm text-muted-foreground">Monitored metrics</p>
                  </div>
                  <Button asChild variant="outline">
                    <Link href="/admin/metrics">
                      View Metrics
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="hover:shadow-md transition-shadow">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Monitor className="h-5 w-5 text-green-500" />
                  SLA Monitoring
                </CardTitle>
                <CardDescription>
                  Comprehensive system health and SLA monitoring
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold">
                      {systemHealth?.uptime_percentage?.toFixed(1) || '0.0'}%
                    </div>
                    <p className="text-sm text-muted-foreground">Uptime (24h)</p>
                  </div>
                  <Button asChild variant="outline">
                    <Link href="/dashboard/sla-monitoring">
                      View SLA
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Alerts Preview */}
          {alerts.length > 0 && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Recent Alerts</CardTitle>
                    <CardDescription>
                      Latest system alerts and warnings
                    </CardDescription>
                  </div>
                  <Button asChild variant="outline" size="sm">
                    <Link href="/admin/alerts" className="flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4" />
                      View All Alerts
                    </Link>
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {alerts.slice(0, 5).map((alert) => (
                    <div key={alert.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <AlertTriangle className={`h-4 w-4 ${
                          alert.alert_type === 'critical' ? 'text-red-500' : 'text-yellow-500'
                        }`} />
                        <div>
                          <p className="font-medium text-sm">{alert.title}</p>
                          <p className="text-xs text-muted-foreground">
                            {format(new Date(alert.triggered_at), 'MMM dd, HH:mm')}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={alert.alert_type === 'critical' ? 'destructive' : 'secondary'}>
                          {alert.alert_type}
                        </Badge>
                        {alert.acknowledged ? (
                          <Badge variant="default" className="bg-green-100 text-green-800">
                            <CheckCircle className="h-3 w-3 mr-1" />
                            ACK
                          </Badge>
                        ) : (
                          <Badge variant="secondary">
                            <Clock className="h-3 w-3 mr-1" />
                            Pending
                          </Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

        </div>
      </main>
    </div>
  )
}
