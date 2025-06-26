"use client"

import { useState, useEffect, useMemo } from "react"
import { useAuth } from "@/features/auth/hooks/useAuth"
import { useClientWebSocketSLA } from "@/features/sla/hooks/useClientWebSocketSLA"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  Filter,
  RefreshCw, 
  Search,
  ChevronLeft,
  ChevronRight,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Wifi,
  WifiOff,
  Zap
} from "lucide-react"
import { format } from "date-fns"

type SortOrder = 'asc' | 'desc'
type SortField = 'triggered_at' | 'alert_type' | 'title' | 'acknowledged'

export default function AlertsPage() {
  const { user } = useAuth()
  
  // Use WebSocket for real-time updates
  const { 
    alerts, 
    isLoading, 
    error, 
    lastUpdated, 
    acknowledgeAlert: wsAcknowledgeAlert,
    refreshData,
    isConnected: wsConnected,
    connectionInfo
  } = useClientWebSocketSLA(true)
  
  const [acknowledgingAlerts, setAcknowledgingAlerts] = useState<Set<string>>(new Set())

  // Pagination and filtering state
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [alertFilter, setAlertFilter] = useState<'all' | 'critical' | 'warning' | 'acknowledged' | 'unacknowledged'>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [sortField, setSortField] = useState<SortField>('triggered_at')
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
              You need super admin privileges to access alerts.
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Calculate filtered, searched and sorted alerts
  const filteredAlerts = useMemo(() => {
    let filtered = [...alerts]
    
    // Filter by alert type or acknowledgment status
    if (alertFilter === 'critical') {
      filtered = filtered.filter(alert => alert.alert_type === 'critical')
    } else if (alertFilter === 'warning') {
      filtered = filtered.filter(alert => alert.alert_type === 'warning')
    } else if (alertFilter === 'acknowledged') {
      filtered = filtered.filter(alert => alert.acknowledged)
    } else if (alertFilter === 'unacknowledged') {
      filtered = filtered.filter(alert => !alert.acknowledged)
    }
    
    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(alert => 
        alert.title.toLowerCase().includes(query) ||
        alert.message.toLowerCase().includes(query) ||
        alert.metric_type.toLowerCase().includes(query)
      )
    }
    
    // Sort alerts - ensure new alerts appear at the top by default
    filtered.sort((a, b) => {
      let aValue: any
      let bValue: any
      
      switch (sortField) {
        case 'triggered_at':
          aValue = new Date(a.triggered_at).getTime()
          bValue = new Date(b.triggered_at).getTime()
          break
        case 'alert_type':
          // Critical comes before warning
          aValue = a.alert_type === 'critical' ? 0 : 1
          bValue = b.alert_type === 'critical' ? 0 : 1
          break
        case 'title':
          aValue = a.title.toLowerCase()
          bValue = b.title.toLowerCase()
          break
        case 'acknowledged':
          aValue = a.acknowledged ? 1 : 0
          bValue = b.acknowledged ? 1 : 0
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
    
    // For default sort by triggered_at desc, ensure newest alerts are first
    if (sortField === 'triggered_at' && sortOrder === 'desc') {
      // Double-check the sort to ensure newest first
      filtered.sort((a, b) => new Date(b.triggered_at).getTime() - new Date(a.triggered_at).getTime())
    }
    
    return filtered
  }, [alerts, alertFilter, searchQuery, sortField, sortOrder])

  const paginatedAlerts = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize
    const endIndex = startIndex + pageSize
    return filteredAlerts.slice(startIndex, endIndex)
  }, [filteredAlerts, currentPage, pageSize])

  const totalPages = Math.ceil(filteredAlerts.length / pageSize)

  // Reset to first page when filter or search changes
  useEffect(() => {
    setCurrentPage(1)
  }, [alertFilter, searchQuery, sortField, sortOrder])

  // Calculate alert statistics
  const totalAlerts = alerts.length
  const criticalAlerts = alerts.filter(alert => alert.alert_type === 'critical').length
  const warningAlerts = alerts.filter(alert => alert.alert_type === 'warning').length
  const acknowledgedAlerts = alerts.filter(alert => alert.acknowledged).length
  const unacknowledgedAlerts = alerts.filter(alert => !alert.acknowledged).length

  const handleAcknowledgeAlert = async (alertId: string) => {
    const alert = alerts.find(a => a.id === alertId)
    if (!alert || alert.acknowledged) return

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

  const getAlertTypeIcon = (alertType: string) => {
    switch (alertType) {
      case 'critical': return <AlertTriangle className="h-4 w-4 text-red-500" />
      case 'warning': return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      default: return <AlertTriangle className="h-4 w-4 text-gray-500" />
    }
  }

  const getAlertTypeBadgeVariant = (alertType: string) => {
    switch (alertType) {
      case 'critical': return 'destructive' as const
      case 'warning': return 'secondary' as const
      default: return 'outline' as const
    }
  }

  return (
    <div className="flex-1 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">System Alerts</h2>
          <p className="text-muted-foreground">
            Monitor and manage system alerts and warnings
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

      {/* Alert Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalAlerts}</div>
            <p className="text-xs text-muted-foreground">All alerts</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Critical</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{criticalAlerts}</div>
            <p className="text-xs text-muted-foreground">Require immediate attention</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Warning</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{warningAlerts}</div>
            <p className="text-xs text-muted-foreground">Need monitoring</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Acknowledged</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{acknowledgedAlerts}</div>
            <p className="text-xs text-muted-foreground">Already reviewed</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending</CardTitle>
            <Clock className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{unacknowledgedAlerts}</div>
            <p className="text-xs text-muted-foreground">Need attention</p>
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
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search alerts by title, message, or metric type..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Select value={alertFilter} onValueChange={(value: any) => setAlertFilter(value)}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Filter by type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Alerts</SelectItem>
                  <SelectItem value="critical">Critical Only</SelectItem>
                  <SelectItem value="warning">Warning Only</SelectItem>
                  <SelectItem value="acknowledged">Acknowledged</SelectItem>
                  <SelectItem value="unacknowledged">Unacknowledged</SelectItem>
                </SelectContent>
              </Select>
              <Select value={pageSize.toString()} onValueChange={(value) => setPageSize(parseInt(value))}>
                <SelectTrigger className="w-[100px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="5">5 per page</SelectItem>
                  <SelectItem value="10">10 per page</SelectItem>
                  <SelectItem value="20">20 per page</SelectItem>
                  <SelectItem value="50">50 per page</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Alerts Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Alerts</CardTitle>
              <CardDescription>
                Showing {filteredAlerts.length} of {totalAlerts} alerts
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
          ) : filteredAlerts.length === 0 ? (
            <div className="text-center py-8">
              <AlertTriangle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">No alerts found</h3>
              <p className="text-muted-foreground">
                {searchQuery || alertFilter !== 'all' 
                  ? 'Try adjusting your filters or search terms.'
                  : 'No alerts are currently active.'}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {/* Table Header */}
              <div className="grid grid-cols-12 gap-4 p-3 bg-muted/50 rounded-lg font-medium text-sm">
                <div className="col-span-1 flex items-center">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort('alert_type')}
                    className="h-auto p-0 font-medium"
                  >
                    Type {getSortIcon('alert_type')}
                  </Button>
                </div>
                <div className="col-span-4 flex items-center">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort('title')}
                    className="h-auto p-0 font-medium"
                  >
                    Alert {getSortIcon('title')}
                  </Button>
                </div>
                <div className="col-span-2 flex items-center">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort('triggered_at')}
                    className="h-auto p-0 font-medium"
                  >
                    Time {getSortIcon('triggered_at')}
                  </Button>
                </div>
                <div className="col-span-2 flex items-center">
                  Value
                </div>
                <div className="col-span-2 flex items-center">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort('acknowledged')}
                    className="h-auto p-0 font-medium"
                  >
                    Status {getSortIcon('acknowledged')}
                  </Button>
                </div>
                <div className="col-span-1">
                  Action
                </div>
              </div>

              {/* Table Rows */}
              {paginatedAlerts.map((alert, index) => {
                // Check if alert is new (within last 5 minutes)
                const isNewAlert = new Date().getTime() - new Date(alert.triggered_at).getTime() < 5 * 60 * 1000
                
                return (
                  <div
                    key={alert.id}
                    className={`grid grid-cols-12 gap-4 p-3 border rounded-lg hover:bg-muted/30 transition-colors ${
                      isNewAlert ? 'bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800' : ''
                    }`}
                  >
                    <div className="col-span-1 flex items-center">
                      <div className="flex items-center gap-2">
                        {isNewAlert && (
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" title="New alert" />
                        )}
                        <Badge variant={getAlertTypeBadgeVariant(alert.alert_type)}>
                          {alert.alert_type}
                        </Badge>
                      </div>
                    </div>
                    <div className="col-span-4 flex items-start gap-3">
                      {getAlertTypeIcon(alert.alert_type)}
                      <div className="min-w-0 flex-1">
                        <p className={`font-medium truncate ${isNewAlert ? 'text-blue-900 dark:text-blue-100' : ''}`}>
                          {alert.title}
                          {isNewAlert && <span className="ml-2 text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-1 py-0.5 rounded">NEW</span>}
                        </p>
                        <p className="text-sm text-muted-foreground line-clamp-2">
                          {alert.message}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Metric: {alert.metric_type.replace('_', ' ')}
                        </p>
                      </div>
                    </div>
                    <div className="col-span-2 flex items-center">
                      <div className="text-sm">
                        <p className="font-medium">
                          {format(new Date(alert.triggered_at), 'MMM dd, HH:mm')}
                        </p>
                        <p className="text-muted-foreground">
                          {format(new Date(alert.triggered_at), 'yyyy')}
                        </p>
                        {isNewAlert && (
                          <p className="text-xs text-blue-600 dark:text-blue-400 flex items-center gap-1">
                            <Zap className="h-3 w-3" />
                            Just now
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="col-span-2 flex items-center">
                      <div className="text-sm">
                        <p className="font-medium">{alert.current_value}</p>
                        <p className="text-muted-foreground">vs {alert.threshold_value}</p>
                      </div>
                    </div>
                    <div className="col-span-2 flex items-center">
                      {alert.acknowledged ? (
                        <Badge variant="default" className="bg-green-100 text-green-800">
                          <CheckCircle2 className="h-3 w-3 mr-1" />
                          Acknowledged
                        </Badge>
                      ) : (
                        <Badge variant="secondary">
                          <Clock className="h-3 w-3 mr-1" />
                          Pending
                        </Badge>
                      )}
                    </div>
                    <div className="col-span-1 flex items-center">
                      {!alert.acknowledged && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAcknowledgeAlert(alert.id)}
                          disabled={acknowledgingAlerts.has(alert.id)}
                          className="text-xs"
                        >
                          {acknowledgingAlerts.has(alert.id) ? '...' : 'ACK'}
                        </Button>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-6">
              <div className="text-sm text-muted-foreground">
                Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, filteredAlerts.length)} of {filteredAlerts.length} results
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
