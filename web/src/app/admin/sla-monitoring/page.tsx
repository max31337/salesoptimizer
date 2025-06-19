"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { useSLAData } from "@/features/sla/hooks/useSLAData"
import { 
  ArrowLeft, 
  RefreshCw, 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Monitor,
  Loader2,
  Database,
  Cpu,
  HardDrive,
  Users,
  Zap
} from "lucide-react"
import Link from "next/link"
import { format } from "date-fns"
import { type SLAAlert } from "@/features/sla/services/sla-service"

export default function SLAMonitoringPage() {
  const { 
    systemHealth, 
    alerts, 
    metrics, 
    isLoading, 
    error, 
    lastUpdated, 
    acknowledgeAlert, 
    refreshData   } = useSLAData(true, 30000)
  
  const [acknowledgingAlerts, setAcknowledgingAlerts] = useState<Set<string>>(new Set())

  // Calculate real-time alert counts from the alerts array
  const activeAlertsCount = alerts.length
  const unacknowledgedAlertsCount = alerts.filter(alert => !alert.acknowledged).length

  const handleAcknowledgeAlert = async (alertId: string) => {
    setAcknowledgingAlerts(prev => new Set([...Array.from(prev), alertId]))
    try {
      await acknowledgeAlert(alertId)
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
      case 'healthy': return 'text-green-600 dark:text-green-400'
      case 'warning': return 'text-yellow-600 dark:text-yellow-400'
      case 'critical': return 'text-red-600 dark:text-red-400'
      default: return 'text-gray-600 dark:text-gray-400'
    }
  }

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'healthy': return 'default' as const
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
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card shadow-sm border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" asChild>
                <Link href="/admin">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Dashboard
                </Link>
              </Button>
              <div>
                <h1 className="text-3xl font-bold text-foreground">SLA Monitoring</h1>
                <p className="mt-1 text-sm text-muted-foreground">
                  Real-time system health and performance monitoring
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
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
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {error && (
            <Alert className="mb-6">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* System Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Overall Status</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <Badge variant={getStatusBadgeVariant(systemHealth?.overall_status || 'unknown')}>
                    {systemHealth?.overall_status || 'Unknown'}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  System health status
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Metrics</CardTitle>
                <Monitor className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {systemHealth ? `${systemHealth.healthy_metrics}/${systemHealth.total_metrics}` : '---'}
                </div>
                <p className="text-xs text-muted-foreground">
                  Healthy metrics
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>              
              <CardContent>
                <div className="text-2xl font-bold">
                  {activeAlertsCount}
                </div>
                <p className="text-xs text-muted-foreground">
                  Requires attention
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Unacknowledged</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>              <CardContent>
                <div className="text-2xl font-bold text-orange-600">
                  {unacknowledgedAlertsCount}
                </div>
                <p className="text-xs text-muted-foreground">
                  Pending acknowledgment
                </p>
              </CardContent>
            </Card>          </div>

          {/* Uptime Overview */}
          {systemHealth?.uptime_percentage !== undefined && (
            <Card className="mb-8">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  System Uptime
                </CardTitle>
                <CardDescription>System availability and uptime statistics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600 dark:text-green-400 mb-1">
                      {systemHealth.uptime_percentage.toFixed(2)}%
                    </div>
                    <p className="text-sm text-muted-foreground">Uptime (24h)</p>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-lg font-medium text-card-foreground mb-1">
                      {systemHealth.uptime_duration || 'N/A'}
                    </div>
                    <p className="text-sm text-muted-foreground">Current Uptime</p>
                  </div>
                  
                  <div className="text-center">
                    <Badge variant={
                      systemHealth.uptime_status === 'operational' ? 'default' :
                      systemHealth.uptime_status === 'degraded' ? 'secondary' : 'destructive'
                    }>
                      {systemHealth.uptime_status}
                    </Badge>
                    <p className="text-sm text-muted-foreground mt-1">Status</p>
                  </div>
                </div>
                
                {systemHealth.system_start_time && (
                  <div className="mt-4 pt-4 border-t">
                    <p className="text-xs text-muted-foreground">
                      System started: {new Date(systemHealth.system_start_time).toLocaleString()}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Metrics Overview */}
          {systemHealth?.metrics_summary && (
            <Card className="mb-8">
              <CardHeader>
                <CardTitle>Key Metrics</CardTitle>
                <CardDescription>Current system performance indicators</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                  <div className="flex items-center gap-3 p-3 rounded-lg border">
                    <Cpu className="h-5 w-5 text-blue-500" />
                    <div>
                      <p className="text-sm font-medium">CPU Usage</p>
                      <p className="text-lg font-bold">{systemHealth.metrics_summary.cpu_usage.toFixed(1)}%</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3 p-3 rounded-lg border">
                    <Monitor className="h-5 w-5 text-green-500" />
                    <div>
                      <p className="text-sm font-medium">Memory</p>
                      <p className="text-lg font-bold">{systemHealth.metrics_summary.memory_usage.toFixed(1)}%</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3 p-3 rounded-lg border">
                    <HardDrive className="h-5 w-5 text-purple-500" />
                    <div>
                      <p className="text-sm font-medium">Disk</p>
                      <p className="text-lg font-bold">{systemHealth.metrics_summary.disk_usage.toFixed(1)}%</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3 p-3 rounded-lg border">
                    <Database className="h-5 w-5 text-orange-500" />
                    <div>
                      <p className="text-sm font-medium">DB Response</p>
                      <p className="text-lg font-bold">{systemHealth.metrics_summary.database_response_time.toFixed(0)}ms</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3 p-3 rounded-lg border">
                    <Users className="h-5 w-5 text-indigo-500" />
                    <div>
                      <p className="text-sm font-medium">Active Users</p>
                      <p className="text-lg font-bold">{systemHealth.metrics_summary.active_users}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3 p-3 rounded-lg border">
                    <Zap className="h-5 w-5 text-yellow-500" />
                    <div>
                      <p className="text-sm font-medium">DB Connections</p>
                      <p className="text-lg font-bold">{systemHealth.metrics_summary.database_connections}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Active Alerts */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" />
                  Active Alerts ({alerts.length})
                </CardTitle>
                <CardDescription>System alerts requiring attention</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="h-6 w-6 animate-spin" />
                  </div>
                ) : alerts.length === 0 ? (
                  <div className="flex items-center justify-center py-8 text-muted-foreground">
                    <CheckCircle className="h-6 w-6 mr-2" />
                    No active alerts
                  </div>
                ) : (
                  <div className="space-y-4">
                    {alerts.map((alert: SLAAlert) => (
                      <div key={alert.id} className="border rounded-lg p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              {getAlertTypeIcon(alert.alert_type)}
                              <span className="font-medium">{alert.title}</span>
                              <Badge variant={alert.alert_type === 'critical' ? 'destructive' : 'secondary'}>
                                {alert.alert_type}
                              </Badge>
                            </div>
                            <p className="text-sm text-muted-foreground mb-2">{alert.message}</p>
                            <div className="flex items-center gap-4 text-xs text-muted-foreground">
                              <span>Metric: {alert.metric_type}</span>
                              <span>Value: {alert.current_value}</span>
                              <span>Threshold: {alert.threshold_value}</span>
                              <span>Triggered: {format(new Date(alert.triggered_at), 'HH:mm:ss')}</span>
                            </div>
                          </div>
                          <div className="ml-4">
                            {alert.acknowledged ? (
                              <div className="text-center">
                                <Badge variant="outline" className="mb-1">
                                  Acknowledged
                                </Badge>
                                <p className="text-xs text-muted-foreground">
                                  {alert.acknowledged_at && format(new Date(alert.acknowledged_at), 'HH:mm:ss')}
                                </p>
                              </div>
                            ) : (
                              <Button
                                size="sm"
                                onClick={() => handleAcknowledgeAlert(alert.id)}
                                disabled={acknowledgingAlerts.has(alert.id)}
                              >
                                {acknowledgingAlerts.has(alert.id) ? (
                                  <Loader2 className="h-3 w-3 animate-spin mr-1" />
                                ) : (
                                  <CheckCircle className="h-3 w-3 mr-1" />
                                )}
                                Acknowledge
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Recent Metrics */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Recent Metrics ({metrics.length})
                </CardTitle>
                <CardDescription>Latest performance measurements</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="h-6 w-6 animate-spin" />
                  </div>
                ) : metrics.length === 0 ? (
                  <div className="flex items-center justify-center py-8 text-muted-foreground">
                    No metrics available
                  </div>
                ) : (
                  <div className="space-y-3">
                    {metrics.slice(0, 10).map((metric) => (
                      <div key={metric.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-3">
                          {getMetricIcon(metric.metric_type)}
                          <div>
                            <p className="font-medium text-sm">{metric.metric_type.replace('_', ' ')}</p>
                            <p className="text-xs text-muted-foreground">
                              {format(new Date(metric.measured_at), 'HH:mm:ss')}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="flex items-center gap-2">
                            <span className="font-bold">{metric.value.toFixed(1)}{metric.unit}</span>
                            <Badge variant={getStatusBadgeVariant(metric.status)}>
                              {metric.status}
                            </Badge>
                          </div>
                          <p className="text-xs text-muted-foreground">
                            Warn: {metric.threshold_warning} | Crit: {metric.threshold_critical}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
