"use client"

import { useState, useEffect, useMemo } from "react"
import { useAuth } from "@/features/auth/hooks/useAuth"
import { useClientWebSocketSLA } from "@/features/sla/hooks/useClientWebSocketSLA"
import { useSLAData } from "@/features/sla/hooks/useSLAData"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Progress } from "@/components/ui/progress"
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  Cpu, 
  Database, 
  Filter,
  HardDrive, 
  Monitor, 
  RefreshCw, 
  Search,
  TrendingUp,
  TrendingDown,
  Users, 
  Zap,
  ChevronLeft,
  ChevronRight,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Wifi,
  WifiOff
} from "lucide-react"
import { format } from "date-fns"

type SortOrder = 'asc' | 'desc'
type SortField = 'metric_type' | 'value' | 'status' | 'measured_at'

export default function MetricsPage() {
  const { user } = useAuth()
  
  // Use WebSocket for real-time system health updates
  const { 
    systemHealth,
    isLoading: wsLoading, 
    error: wsError, 
    lastUpdated, 
    refreshData: wsRefreshData,
    isConnected: wsConnected,
    connectionInfo
  } = useClientWebSocketSLA(true)
  
  // Use traditional API for detailed metrics
  const { 
    metrics = [],
    isLoading: metricsLoading,
    error: metricsError,
    fetchMetrics,
    refreshData: metricsRefreshData
  } = useSLAData(false, 0)

  // Pagination and filtering state
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(12)
  const [statusFilter, setStatusFilter] = useState<'all' | 'healthy' | 'warning' | 'critical'>('all')
  const [metricTypeFilter, setMetricTypeFilter] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [sortField, setSortField] = useState<SortField>('measured_at')
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc')

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
              You need super admin privileges to access metrics.
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Load metrics on mount
  useEffect(() => {
    fetchMetrics()
  }, [fetchMetrics])

  // Get unique metric types for filtering
  const metricTypes = useMemo(() => {
    const types = Array.from(new Set(metrics.map(m => m.metric_type)))
    return types.sort()
  }, [metrics])

  // Calculate filtered, searched and sorted metrics
  const filteredMetrics = useMemo(() => {
    let filtered = [...metrics]
    
    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter(metric => metric.status === statusFilter)
    }
    
    // Filter by metric type
    if (metricTypeFilter !== 'all') {
      filtered = filtered.filter(metric => metric.metric_type === metricTypeFilter)
    }
    
    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(metric => 
        metric.metric_type.toLowerCase().includes(query) ||
        metric.id.toLowerCase().includes(query)
      )
    }
    
    // Sort metrics
    filtered.sort((a, b) => {
      let aValue: any
      let bValue: any
      
      switch (sortField) {
        case 'measured_at':
          aValue = new Date(a.measured_at).getTime()
          bValue = new Date(b.measured_at).getTime()
          break
        case 'value':
          aValue = a.value
          bValue = b.value
          break
        case 'status':
          // Critical < Warning < Healthy
          const statusOrder = { critical: 0, warning: 1, healthy: 2 }
          aValue = statusOrder[a.status as keyof typeof statusOrder] ?? 3
          bValue = statusOrder[b.status as keyof typeof statusOrder] ?? 3
          break
        case 'metric_type':
          aValue = a.metric_type.toLowerCase()
          bValue = b.metric_type.toLowerCase()
          break
        default:
          return 0
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1
      } else {
        return aValue < bValue ? 1 : -1
      }
    })
    
    return filtered
  }, [metrics, statusFilter, metricTypeFilter, searchQuery, sortField, sortOrder])

  const paginatedMetrics = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize
    const endIndex = startIndex + pageSize
    return filteredMetrics.slice(startIndex, endIndex)
  }, [filteredMetrics, currentPage, pageSize])

  const totalPages = Math.ceil(filteredMetrics.length / pageSize)

  // Reset to first page when filter or search changes
  useEffect(() => {
    setCurrentPage(1)
  }, [statusFilter, metricTypeFilter, searchQuery, sortField, sortOrder])

  // Calculate metric statistics
  const totalMetrics = metrics.length
  const healthyMetrics = metrics.filter(m => m.status === 'healthy').length
  const warningMetrics = metrics.filter(m => m.status === 'warning').length
  const criticalMetrics = metrics.filter(m => m.status === 'critical').length

  const handleRefresh = async () => {
    await Promise.all([
      wsRefreshData(),
      metricsRefreshData()
    ])
  }

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortOrder('desc')
    }
  }

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) {
      return <ArrowUpDown className="h-4 w-4" />
    }
    return sortOrder === 'asc' ? <ArrowUp className="h-4 w-4" /> : <ArrowDown className="h-4 w-4" />
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

  const getProgressColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-500'
      case 'warning': return 'bg-yellow-500'
      case 'critical': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const formatMetricValue = (value: number, unit: string) => {
    if (unit === '%') {
      return `${value.toFixed(1)}%`
    } else if (unit === 'ms') {
      return `${Math.round(value)}ms`
    } else if (unit === 'count') {
      return value.toString()
    }
    return `${value} ${unit}`
  }

  const isLoading = wsLoading || metricsLoading
  const error = wsError || metricsError

  return (
    <div className="flex-1 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">System Metrics</h2>
          <p className="text-muted-foreground">
            Detailed performance metrics and monitoring data
          </p>
        </div>
        <div className="flex items-center space-x-4">
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
            onClick={handleRefresh}
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

      {/* Current System Health Overview */}
      {systemHealth && (
        <Card>
          <CardHeader>
            <CardTitle>Current System Health</CardTitle>
            <CardDescription>
              Real-time system performance overview
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Cpu className="h-4 w-4" />
                  <span className="text-sm font-medium">CPU Usage</span>
                </div>
                <div className="space-y-1">
                  <div className="text-lg font-bold">
                    {systemHealth.metrics_summary?.cpu_usage?.toFixed(1) || 'N/A'}%
                  </div>
                  <Progress 
                    value={systemHealth.metrics_summary?.cpu_usage || 0} 
                    className="h-2"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Monitor className="h-4 w-4" />
                  <span className="text-sm font-medium">Memory</span>
                </div>
                <div className="space-y-1">
                  <div className="text-lg font-bold">
                    {systemHealth.metrics_summary?.memory_usage?.toFixed(1) || 'N/A'}%
                  </div>
                  <Progress 
                    value={systemHealth.metrics_summary?.memory_usage || 0} 
                    className="h-2"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <HardDrive className="h-4 w-4" />
                  <span className="text-sm font-medium">Disk</span>
                </div>
                <div className="space-y-1">
                  <div className="text-lg font-bold">
                    {systemHealth.metrics_summary?.disk_usage?.toFixed(1) || 'N/A'}%
                  </div>
                  <Progress 
                    value={systemHealth.metrics_summary?.disk_usage || 0} 
                    className="h-2"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Database className="h-4 w-4" />
                  <span className="text-sm font-medium">DB Response</span>
                </div>
                <div className="space-y-1">
                  <div className="text-lg font-bold">
                    {systemHealth.metrics_summary?.database_response_time?.toFixed(0) || 'N/A'}ms
                  </div>
                  <div className="text-xs text-muted-foreground">Response time</div>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4" />
                  <span className="text-sm font-medium">Uptime</span>
                </div>
                <div className="space-y-1">
                  <div className="text-lg font-bold">
                    {systemHealth.uptime_percentage?.toFixed(2) || 'N/A'}%
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {systemHealth.uptime_duration || 'N/A'}
                  </div>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4" />
                  <span className="text-sm font-medium">Active Users</span>
                </div>
                <div className="space-y-1">
                  <div className="text-lg font-bold">
                    {systemHealth.metrics_summary?.active_users || 'N/A'}
                  </div>
                  <div className="text-xs text-muted-foreground">24h active</div>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4" />
                  <span className="text-sm font-medium">DB Connections</span>
                </div>
                <div className="space-y-1">
                  <div className="text-lg font-bold">
                    {systemHealth.metrics_summary?.database_connections || 'N/A'}
                  </div>
                  <div className="text-xs text-muted-foreground">Active connections</div>
                </div>
              </div>
            </div>
            
            {/* Uptime Information Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 pt-4 border-t">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  <span className="text-sm font-medium">System Uptime</span>
                </div>
                <div className="space-y-1">
                  <div className="text-lg font-bold">
                    {systemHealth.uptime_duration || 'N/A'}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {systemHealth.uptime_percentage?.toFixed(2) || '0.00'}% uptime
                  </div>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4" />
                  <span className="text-sm font-medium">Overall Health</span>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <div className="text-lg font-bold">
                      {systemHealth.health_percentage?.toFixed(2) || '0.00'}%
                    </div>
                    <Badge variant={
                      systemHealth.overall_status === 'healthy' ? 'default' :
                      systemHealth.overall_status === 'warning' ? 'secondary' : 'destructive'
                    }>
                      {systemHealth.overall_status}
                    </Badge>
                  </div>
                  <div className="text-xs text-muted-foreground">System health score</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Metrics Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Metrics</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalMetrics}</div>
            <p className="text-xs text-muted-foreground">Monitored metrics</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Healthy</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{healthyMetrics}</div>
            <p className="text-xs text-muted-foreground">Within normal range</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Warning</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{warningMetrics}</div>
            <p className="text-xs text-muted-foreground">Need attention</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Critical</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{criticalMetrics}</div>
            <p className="text-xs text-muted-foreground">Require immediate action</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters & Search
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search metrics by type or ID..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Select value={statusFilter} onValueChange={(value: any) => setStatusFilter(value)}>
                <SelectTrigger className="w-[140px]">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="healthy">Healthy</SelectItem>
                  <SelectItem value="warning">Warning</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                </SelectContent>
              </Select>
              <Select value={metricTypeFilter} onValueChange={setMetricTypeFilter}>
                <SelectTrigger className="w-[160px]">
                  <SelectValue placeholder="Metric Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  {metricTypes.map(type => (
                    <SelectItem key={type} value={type}>
                      {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select value={pageSize.toString()} onValueChange={(value) => setPageSize(parseInt(value))}>
                <SelectTrigger className="w-[100px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="6">6 per page</SelectItem>
                  <SelectItem value="12">12 per page</SelectItem>
                  <SelectItem value="24">24 per page</SelectItem>
                  <SelectItem value="48">48 per page</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Metrics Grid */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Metrics Details</CardTitle>
              <CardDescription>
                Showing {filteredMetrics.length} of {totalMetrics} metrics
              </CardDescription>
            </div>
            <div className="text-sm text-muted-foreground">
              Page {currentPage} of {totalPages}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : filteredMetrics.length === 0 ? (
            <div className="text-center py-8">
              <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">No metrics found</h3>
              <p className="text-muted-foreground">
                {searchQuery || statusFilter !== 'all' || metricTypeFilter !== 'all'
                  ? 'Try adjusting your filters or search terms.'
                  : 'No metrics are currently available.'}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Sort Controls */}
              <div className="flex items-center gap-2 text-sm">
                <span className="text-muted-foreground">Sort by:</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort('metric_type')}
                  className="h-auto p-1"
                >
                  Type {getSortIcon('metric_type')}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort('value')}
                  className="h-auto p-1"
                >
                  Value {getSortIcon('value')}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort('status')}
                  className="h-auto p-1"
                >
                  Status {getSortIcon('status')}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort('measured_at')}
                  className="h-auto p-1"
                >
                  Time {getSortIcon('measured_at')}
                </Button>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {paginatedMetrics.map((metric) => (
                  <Card key={metric.id} className="transition-shadow hover:shadow-md">
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {getMetricIcon(metric.metric_type)}
                          <CardTitle className="text-base">
                            {metric.metric_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </CardTitle>
                        </div>
                        <Badge variant={getStatusBadgeVariant(metric.status)}>
                          {metric.status}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div>
                        <div className="text-2xl font-bold">
                          {formatMetricValue(metric.value, metric.unit)}
                        </div>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <span>Thresholds:</span>
                          <span className="text-yellow-600">⚠ {metric.threshold_warning}{metric.unit}</span>
                          <span className="text-red-600">🚨 {metric.threshold_critical}{metric.unit}</span>
                        </div>
                      </div>
                      
                      {metric.unit === '%' && (
                        <div className="space-y-1">
                          <Progress 
                            value={Math.min(metric.value, 100)} 
                            className="h-2"
                          />
                          <div className="flex justify-between text-xs text-muted-foreground">
                            <span>0%</span>
                            <span>100%</span>
                          </div>
                        </div>
                      )}
                      
                      <div className="text-xs text-muted-foreground">
                        <div>Measured: {format(new Date(metric.measured_at), 'MMM dd, HH:mm:ss')}</div>
                        <div>ID: {metric.id.slice(0, 8)}...</div>
                      </div>
                      
                      {metric.additional_data && Object.keys(metric.additional_data).length > 0 && (
                        <details className="text-xs">
                          <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
                            Additional Data
                          </summary>
                          <pre className="mt-2 p-2 bg-muted rounded text-xs overflow-auto">
                            {JSON.stringify(metric.additional_data, null, 2)}
                          </pre>
                        </details>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-6">
              <div className="text-sm text-muted-foreground">
                Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, filteredMetrics.length)} of {filteredMetrics.length} results
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  <ChevronLeft className="h-4 w-4" />
                  Previous
                </Button>
                <div className="flex items-center space-x-1">
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    const pageNum = Math.max(1, Math.min(totalPages - 4, currentPage - 2)) + i
                    return (
                      <Button
                        key={pageNum}
                        variant={currentPage === pageNum ? "default" : "outline"}
                        size="sm"
                        onClick={() => setCurrentPage(pageNum)}
                        className="w-8 h-8 p-0"
                      >
                        {pageNum}
                      </Button>
                    )
                  })}
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={currentPage === totalPages}
                >
                  Next
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
