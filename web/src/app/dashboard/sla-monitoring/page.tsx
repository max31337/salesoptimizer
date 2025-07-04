"use client"

import { useState, useEffect, useMemo } from "react"
import Link from "next/link"
import { useAuth } from "@/features/auth/hooks/useAuth"
import { useClientWebSocketSLA } from "@/features/sla/hooks/useClientWebSocketSLA"
import { useSLAData } from "@/features/sla/hooks/useSLAData"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  Cpu, 
  Database, 
  HardDrive, 
  Monitor, 
  RefreshCw, 
  Users, 
  Zap 
} from "lucide-react"
import { format } from "date-fns"

export default function SLAMonitoringPage() {
  const { user } = useAuth()
  
  // Use WebSocket for real-time updates
  const { 
    systemHealth, 
    alerts, 
    isLoading, 
    error, 
    lastUpdated, 
    acknowledgeAlert: wsAcknowledgeAlert,
    refreshData,
    isConnected: wsConnected,
    connectionInfo
  } = useClientWebSocketSLA(true)
  
  // Keep the old hook as fallback for metrics and manual refresh
  const { 
    metrics = [],
    refreshData: fallbackRefresh 
  } = useSLAData(false, 0)
  
  const [acknowledgingAlerts, setAcknowledgingAlerts] = useState<Set<string>>(new Set())

  // Pagination and filtering state
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [alertFilter, setAlertFilter] = useState<'all' | 'critical' | 'warning'>('all')

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
              You need super admin privileges to access SLA monitoring.
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Calculate filtered and paginated alerts
  const filteredAlerts = useMemo(() => {
    let filtered = [...alerts]
    
    // Filter by alert type
    if (alertFilter !== 'all') {
      filtered = filtered.filter(alert => alert.alert_type === alertFilter)
    }
    
    // Sort by triggered_at (newest first) to ensure new alerts appear at the top
    filtered.sort((a, b) => new Date(b.triggered_at).getTime() - new Date(a.triggered_at).getTime())
    
    return filtered
  }, [alerts, alertFilter])

  const paginatedAlerts = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize
    const endIndex = startIndex + pageSize
    return filteredAlerts.slice(startIndex, endIndex)
  }, [filteredAlerts, currentPage, pageSize])

  const totalPages = Math.ceil(filteredAlerts.length / pageSize)

  // Reset to first page when filter changes
  useEffect(() => {
    setCurrentPage(1)
  }, [alertFilter])

  // Calculate real-time alert counts from the alerts array
  const activeAlertsCount = alerts.length
  const unacknowledgedAlertsCount = alerts.filter(alert => !alert.acknowledged).length
  const criticalAlertsCount = alerts.filter(alert => alert.alert_type === 'critical').length
  const warningAlertsCount = alerts.filter(alert => alert.alert_type === 'warning').length

  const handleAcknowledgeAlert = async (alertId: string) => {
    // Check if alert is already acknowledged
    const alert = alerts.find(a => a.id === alertId)
    if (!alert) {
      console.warn('Alert not found:', alertId)
      return
    }
    
    if (alert.acknowledged) {
      console.warn('Alert already acknowledged:', alertId)
      return
    }

    setAcknowledgingAlerts(prev => new Set([...Array.from(prev), alertId]))
    try {
      await wsAcknowledgeAlert(alertId)
    } catch (error) {
      console.error('Failed to acknowledge alert:', error)
    } finally {
      setAcknowledgingAlerts(prev => {
        const newSet = new Set(prev)
        newSet.delete(alertId)
        return newSet
      })
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': 
      case 'operational': // Add operational as a healthy state
        return 'text-green-600 dark:text-green-400'
      case 'warning': return 'text-yellow-600 dark:text-yellow-400'
      case 'critical': return 'text-red-600 dark:text-red-400'
      default: return 'text-gray-600 dark:text-gray-400'
    }
  }

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'healthy': 
      case 'operational': // Add operational as a healthy state
        return 'default' as const
      case 'warning': return 'secondary' as const
      case 'critical': return 'destructive' as const
      default: return 'outline' as const
    }
  }

  const getMetricIcon = (metricType: string) => {
    switch (metricType) {
      case 'cpu_usage': return <Cpu className="h-4 w-4" />
      case 'memory_usage': return <Monitor className="h-4 w-4" />
      case 'disk_usage': return <HardDrive className="h-4 w-4" />
      case 'database_response_time': return <Database className="h-4 w-4" />
      case 'active_users': return <Users className="h-4 w-4" />
      case 'database_connections': return <Zap className="h-4 w-4" />
      case 'uptime': return <Activity className="h-4 w-4" />
      default: return <Activity className="h-4 w-4" />
    }
  }

  const getAlertTypeIcon = (alertType: string) => {
    switch (alertType) {
      case 'critical': return <AlertTriangle className="h-4 w-4 text-red-500" />
      case 'warning': return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      default: return <AlertTriangle className="h-4 w-4 text-gray-500" />
    }
  }

  return (
    <div className="flex-1 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">SLA Monitoring</h2>
          <p className="text-muted-foreground">
            Real-time system health and performance monitoring
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <div className="flex items-center gap-2 justify-end">
              <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <p className="text-xs text-muted-foreground">
                {wsConnected ? 'Real-time' : 'Offline'}
                {connectionInfo && ` (${connectionInfo.active_connections} clients)`}
              </p>
            </div>
            <p className="text-xs text-muted-foreground">Last updated</p>
            <p className="text-sm font-medium">
              {lastUpdated ? format(lastUpdated, 'HH:mm:ss') : '---'}
            </p>
          </div>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={refreshData}
            disabled={isLoading}
            className="flex items-center gap-2"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Status</CardTitle>
            <div className={`w-2 h-2 rounded-full ${
              systemHealth?.overall_status === 'healthy' ? 'bg-green-500' :
              systemHealth?.overall_status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
            }`} />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? '...' : systemHealth?.overall_status || 'Unknown'}
            </div>
            <p className="text-xs text-muted-foreground">
              {isLoading ? 'Loading...' : `${systemHealth?.healthy_metrics || 0}/${systemHealth?.total_metrics || 0} metrics healthy`}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Uptime</CardTitle>
            <div className="flex items-center gap-2">
              {isLoading ? (
                <div className="w-2 h-2 rounded-full bg-gray-300 animate-pulse" />
              ) : (
                <div className={`w-2 h-2 rounded-full ${
                  (systemHealth?.uptime_status === 'healthy' || systemHealth?.uptime_status === 'operational') ? 'bg-green-500' :
                  systemHealth?.uptime_status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                }`} />
              )}
              <Activity className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <div className="text-2xl font-bold">
                {isLoading ? '...' : `${systemHealth?.uptime_percentage?.toFixed(2) || '0.00'}%`}
              </div>
              <Badge variant={getStatusBadgeVariant(systemHealth?.uptime_status || 'unknown')}>
                {systemHealth?.uptime_status || 'Unknown'}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              {systemHealth?.uptime_duration || 'N/A'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activeAlertsCount}</div>
            <p className="text-xs text-muted-foreground">
              {unacknowledgedAlertsCount} unacknowledged
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Health Score</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? '...' : `${(systemHealth?.health_percentage || 0).toFixed(2)}%`}
            </div>
            <p className="text-xs text-muted-foreground">
              Overall system health
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Alerts */}
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
                <Link href="/dashboard/sla-monitoring/alerts" className="flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4" />
                  View All Alerts
                </Link>
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {paginatedAlerts.slice(0, 5).map((alert) => (
                <div
                  key={alert.id}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    {getAlertTypeIcon(alert.alert_type)}
                    <div>
                      <p className="font-medium">{alert.title}</p>
                      <p className="text-sm text-muted-foreground">
                        {alert.message}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {format(new Date(alert.triggered_at), 'PPp')}
                      </p>
                    </div>
                  </div>
                  {!alert.acknowledged && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleAcknowledgeAlert(alert.id)}
                      disabled={acknowledgingAlerts.has(alert.id)}
                    >
                      {acknowledgingAlerts.has(alert.id) ? 'Acknowledging...' : 'Acknowledge'}
                    </Button>
                  )}
                </div>
              ))}
            </div>
            {alerts.length > 5 && (
              <div className="mt-4 text-center">
                <Button asChild variant="ghost" size="sm">
                  <Link href="/dashboard/sla-monitoring/alerts">
                    View {alerts.length - 5} more alerts
                  </Link>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* System Metrics */}
      {systemHealth && (
        <Card>
          <CardHeader>
            <CardTitle>System Metrics</CardTitle>
            <CardDescription>
              Current system performance indicators
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Cpu className="h-4 w-4" />
                  <span className="text-sm font-medium">CPU Usage</span>
                </div>
                <div className="text-2xl font-bold">
                  {systemHealth.metrics_summary?.cpu_usage?.toFixed(1) || 'N/A'}%
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Monitor className="h-4 w-4" />
                  <span className="text-sm font-medium">Memory Usage</span>
                </div>
                <div className="text-2xl font-bold">
                  {systemHealth.metrics_summary?.memory_usage?.toFixed(1) || 'N/A'}%
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <HardDrive className="h-4 w-4" />
                  <span className="text-sm font-medium">Disk Usage</span>
                </div>
                <div className="text-2xl font-bold">
                  {systemHealth.metrics_summary?.disk_usage?.toFixed(1) || 'N/A'}%
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Database className="h-4 w-4" />
                  <span className="text-sm font-medium">DB Response</span>
                </div>
                <div className="text-2xl font-bold">
                  {systemHealth.metrics_summary?.database_response_time?.toFixed(0) || 'N/A'}ms
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4" />
                  <span className="text-sm font-medium">Active Users</span>
                </div>
                <div className="text-2xl font-bold">
                  {systemHealth.metrics_summary?.active_users || 'N/A'}
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4" />
                  <span className="text-sm font-medium">DB Connections</span>
                </div>
                <div className="text-2xl font-bold">
                  {systemHealth.metrics_summary?.database_connections || 'N/A'}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
