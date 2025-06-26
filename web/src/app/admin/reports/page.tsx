"use client"

import { useState, useEffect } from "react"
import { useAuth } from "@/features/auth/hooks/useAuth"
import { slaService } from "@/features/sla/services/sla-service"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { 
  Activity, 
  AlertTriangle, 
  BarChart3,
  Calendar,
  CheckCircle2, 
  Clock, 
  Database, 
  Download,
  FileText,
  Monitor, 
  RefreshCw, 
  TrendingDown,
  TrendingUp,
  Users
} from "lucide-react"
import { format, subDays, subHours, subMonths } from "date-fns"

interface ReportData {
  period: string
  uptime_percentage: number
  avg_response_time: number
  total_alerts: number
  critical_alerts: number
  warning_alerts: number
  resolved_alerts: number
  system_events: number
  user_activity: number
  performance_score: number
}

interface SystemMetrics {
  avg_cpu_usage: number
  avg_memory_usage: number
  avg_disk_usage: number
  peak_cpu_usage: number
  peak_memory_usage: number
  peak_disk_usage: number
}

export default function ReportsPage() {
  const { user } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedPeriod, setSelectedPeriod] = useState<'24h' | '7d' | '30d' | '90d'>('30d')
  const [reportData, setReportData] = useState<ReportData | null>(null)
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null)
  const [isGeneratingReport, setIsGeneratingReport] = useState(false)

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
              You need super admin privileges to access reports.
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  const fetchReportData = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      // For now, we'll generate mock data based on the selected period
      // In a real implementation, this would call the backend API
      const mockData: ReportData = {
        period: selectedPeriod,
        uptime_percentage: 99.8 - Math.random() * 0.5,
        avg_response_time: 120 + Math.random() * 80,
        total_alerts: Math.floor(Math.random() * 50) + 10,
        critical_alerts: Math.floor(Math.random() * 5),
        warning_alerts: Math.floor(Math.random() * 15) + 5,
        resolved_alerts: Math.floor(Math.random() * 40) + 30,
        system_events: Math.floor(Math.random() * 200) + 100,
        user_activity: Math.floor(Math.random() * 1000) + 500,
        performance_score: 85 + Math.random() * 10
      }

      const mockMetrics: SystemMetrics = {
        avg_cpu_usage: 45 + Math.random() * 20,
        avg_memory_usage: 60 + Math.random() * 20,
        avg_disk_usage: 30 + Math.random() * 20,
        peak_cpu_usage: 70 + Math.random() * 25,
        peak_memory_usage: 80 + Math.random() * 15,
        peak_disk_usage: 50 + Math.random() * 30
      }

      setReportData(mockData)
      setSystemMetrics(mockMetrics)
    } catch (err) {
      setError('Failed to fetch report data')
      console.error('Error fetching report data:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const generateReport = async () => {
    setIsGeneratingReport(true)
    try {
      // Simulate report generation
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // In a real implementation, this would trigger a backend report generation
      // and potentially download a PDF or Excel file
      const reportContent = `
SalesOptimizer System Report - ${selectedPeriod.toUpperCase()}
Generated: ${format(new Date(), 'yyyy-MM-dd HH:mm:ss')}

=== SYSTEM HEALTH OVERVIEW ===
Uptime: ${reportData?.uptime_percentage.toFixed(2)}%
Average Response Time: ${reportData?.avg_response_time.toFixed(0)}ms
Performance Score: ${reportData?.performance_score.toFixed(1)}%

=== ALERTS SUMMARY ===
Total Alerts: ${reportData?.total_alerts}
Critical: ${reportData?.critical_alerts}
Warning: ${reportData?.warning_alerts}
Resolved: ${reportData?.resolved_alerts}

=== SYSTEM METRICS ===
Average CPU Usage: ${systemMetrics?.avg_cpu_usage.toFixed(1)}%
Average Memory Usage: ${systemMetrics?.avg_memory_usage.toFixed(1)}%
Average Disk Usage: ${systemMetrics?.avg_disk_usage.toFixed(1)}%

Peak CPU Usage: ${systemMetrics?.peak_cpu_usage.toFixed(1)}%
Peak Memory Usage: ${systemMetrics?.peak_memory_usage.toFixed(1)}%
Peak Disk Usage: ${systemMetrics?.peak_disk_usage.toFixed(1)}%

=== ACTIVITY SUMMARY ===
System Events: ${reportData?.system_events}
User Activity Events: ${reportData?.user_activity}
      `

      // Create and download the report as a text file
      const blob = new Blob([reportContent], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `salesoptimizer-report-${selectedPeriod}-${format(new Date(), 'yyyy-MM-dd')}.txt`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (err) {
      setError('Failed to generate report')
    } finally {
      setIsGeneratingReport(false)
    }
  }

  useEffect(() => {
    fetchReportData()
  }, [selectedPeriod])

  const getPeriodLabel = (period: string) => {
    switch (period) {
      case '24h': return 'Last 24 Hours'
      case '7d': return 'Last 7 Days'
      case '30d': return 'Last 30 Days'
      case '90d': return 'Last 90 Days'
      default: return period
    }
  }

  return (
    <div className="flex-1 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">System Reports</h2>
          <p className="text-muted-foreground">
            Comprehensive system health and performance reports
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Select
            value={selectedPeriod}
            onValueChange={(value: '24h' | '7d' | '30d' | '90d') => setSelectedPeriod(value)}
          >
            <SelectTrigger className="w-[160px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="24h">Last 24 Hours</SelectItem>
              <SelectItem value="7d">Last 7 Days</SelectItem>
              <SelectItem value="30d">Last 30 Days</SelectItem>
              <SelectItem value="90d">Last 90 Days</SelectItem>
            </SelectContent>
          </Select>
          
          <Button
            onClick={fetchReportData}
            disabled={isLoading}
            variant="outline"
            className="flex items-center gap-2"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          
          <Button
            onClick={generateReport}
            disabled={isGeneratingReport || !reportData}
            className="flex items-center gap-2"
          >
            <Download className={`h-4 w-4 ${isGeneratingReport ? 'animate-spin' : ''}`} />
            {isGeneratingReport ? 'Generating...' : 'Download Report'}
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {reportData && (
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="alerts">Alerts</TabsTrigger>
            <TabsTrigger value="activity">Activity</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Overview Stats */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">System Uptime</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{reportData.uptime_percentage.toFixed(2)}%</div>
                  <p className="text-xs text-muted-foreground">
                    {getPeriodLabel(selectedPeriod)}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
                  <Clock className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{reportData.avg_response_time.toFixed(0)}ms</div>
                  <p className="text-xs text-muted-foreground">
                    API response time
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Alerts</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{reportData.total_alerts}</div>
                  <p className="text-xs text-muted-foreground">
                    {reportData.critical_alerts} critical, {reportData.warning_alerts} warning
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Performance Score</CardTitle>
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{reportData.performance_score.toFixed(1)}%</div>
                  <p className="text-xs text-muted-foreground">
                    Overall system performance
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* System Health Summary */}
            <Card>
              <CardHeader>
                <CardTitle>System Health Summary</CardTitle>
                <CardDescription>
                  Key metrics for {getPeriodLabel(selectedPeriod).toLowerCase()}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">System Uptime</span>
                    <div className="flex items-center gap-2">
                      <Progress value={reportData.uptime_percentage} className="w-32" />
                      <span className="text-sm font-medium">{reportData.uptime_percentage.toFixed(2)}%</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Performance Score</span>
                    <div className="flex items-center gap-2">
                      <Progress value={reportData.performance_score} className="w-32" />
                      <span className="text-sm font-medium">{reportData.performance_score.toFixed(1)}%</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Alert Resolution Rate</span>
                    <div className="flex items-center gap-2">
                      <Progress 
                        value={(reportData.resolved_alerts / reportData.total_alerts) * 100} 
                        className="w-32" 
                      />
                      <span className="text-sm font-medium">
                        {((reportData.resolved_alerts / reportData.total_alerts) * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="performance" className="space-y-6">
            {systemMetrics && (
              <>
                {/* Performance Metrics */}
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm font-medium">CPU Usage</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Average</span>
                        <span className="font-medium">{systemMetrics.avg_cpu_usage.toFixed(1)}%</span>
                      </div>
                      <Progress value={systemMetrics.avg_cpu_usage} className="h-2" />
                      <div className="flex justify-between text-sm">
                        <span>Peak</span>
                        <span className="font-medium">{systemMetrics.peak_cpu_usage.toFixed(1)}%</span>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm font-medium">Memory Usage</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Average</span>
                        <span className="font-medium">{systemMetrics.avg_memory_usage.toFixed(1)}%</span>
                      </div>
                      <Progress value={systemMetrics.avg_memory_usage} className="h-2" />
                      <div className="flex justify-between text-sm">
                        <span>Peak</span>
                        <span className="font-medium">{systemMetrics.peak_memory_usage.toFixed(1)}%</span>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm font-medium">Disk Usage</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Average</span>
                        <span className="font-medium">{systemMetrics.avg_disk_usage.toFixed(1)}%</span>
                      </div>
                      <Progress value={systemMetrics.avg_disk_usage} className="h-2" />
                      <div className="flex justify-between text-sm">
                        <span>Peak</span>
                        <span className="font-medium">{systemMetrics.peak_disk_usage.toFixed(1)}%</span>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Performance Trends */}
                <Card>
                  <CardHeader>
                    <CardTitle>Performance Trends</CardTitle>
                    <CardDescription>
                      Resource utilization patterns for {getPeriodLabel(selectedPeriod).toLowerCase()}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center gap-3">
                          <TrendingUp className="h-5 w-5 text-green-500" />
                          <div>
                            <p className="font-medium">CPU Performance</p>
                            <p className="text-sm text-muted-foreground">
                              Stable usage with occasional spikes during peak hours
                            </p>
                          </div>
                        </div>
                        <Badge variant="secondary">Optimal</Badge>
                      </div>
                      
                      <div className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center gap-3">
                          <TrendingUp className="h-5 w-5 text-blue-500" />
                          <div>
                            <p className="font-medium">Memory Efficiency</p>
                            <p className="text-sm text-muted-foreground">
                              Consistent usage patterns with good garbage collection
                            </p>
                          </div>
                        </div>
                        <Badge variant="secondary">Good</Badge>
                      </div>
                      
                      <div className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center gap-3">
                          <TrendingDown className="h-5 w-5 text-orange-500" />
                          <div>
                            <p className="font-medium">Disk I/O</p>
                            <p className="text-sm text-muted-foreground">
                              Moderate usage with room for optimization
                            </p>
                          </div>
                        </div>
                        <Badge variant="outline">Monitor</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>

          <TabsContent value="alerts" className="space-y-6">
            {/* Alert Statistics */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Critical Alerts</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-red-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-red-600">{reportData.critical_alerts}</div>
                  <p className="text-xs text-muted-foreground">
                    Require immediate attention
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Warning Alerts</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-yellow-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-yellow-600">{reportData.warning_alerts}</div>
                  <p className="text-xs text-muted-foreground">
                    Need monitoring
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Resolved Alerts</CardTitle>
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">{reportData.resolved_alerts}</div>
                  <p className="text-xs text-muted-foreground">
                    Successfully resolved
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Resolution Rate</CardTitle>
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {((reportData.resolved_alerts / reportData.total_alerts) * 100).toFixed(1)}%
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Alert resolution efficiency
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Alert Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle>Alert Breakdown</CardTitle>
                <CardDescription>
                  Detailed analysis of alerts for {getPeriodLabel(selectedPeriod).toLowerCase()}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Total Alerts Generated</span>
                    <span className="text-sm font-medium">{reportData.total_alerts}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Critical (High Priority)</span>
                    <div className="flex items-center gap-2">
                      <Progress 
                        value={(reportData.critical_alerts / reportData.total_alerts) * 100} 
                        className="w-32" 
                      />
                      <span className="text-sm font-medium text-red-600">{reportData.critical_alerts}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Warning (Medium Priority)</span>
                    <div className="flex items-center gap-2">
                      <Progress 
                        value={(reportData.warning_alerts / reportData.total_alerts) * 100} 
                        className="w-32" 
                      />
                      <span className="text-sm font-medium text-yellow-600">{reportData.warning_alerts}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Successfully Resolved</span>
                    <div className="flex items-center gap-2">
                      <Progress 
                        value={(reportData.resolved_alerts / reportData.total_alerts) * 100} 
                        className="w-32" 
                      />
                      <span className="text-sm font-medium text-green-600">{reportData.resolved_alerts}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="activity" className="space-y-6">
            {/* Activity Statistics */}
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">System Events</CardTitle>
                  <Monitor className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{reportData.system_events.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground">
                    Internal system activities
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">User Activity</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{reportData.user_activity.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground">
                    User interactions and requests
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Activity Summary */}
            <Card>
              <CardHeader>
                <CardTitle>Activity Summary</CardTitle>
                <CardDescription>
                  System and user activity overview for {getPeriodLabel(selectedPeriod).toLowerCase()}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="space-y-2">
                    <h4 className="font-medium">System Activities</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div className="flex justify-between">
                        <span>Database Operations</span>
                        <span className="font-medium">{Math.floor(reportData.system_events * 0.4).toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>API Requests</span>
                        <span className="font-medium">{Math.floor(reportData.system_events * 0.3).toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Background Tasks</span>
                        <span className="font-medium">{Math.floor(reportData.system_events * 0.2).toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Monitoring Events</span>
                        <span className="font-medium">{Math.floor(reportData.system_events * 0.1).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <h4 className="font-medium">User Activities</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div className="flex justify-between">
                        <span>Login Sessions</span>
                        <span className="font-medium">{Math.floor(reportData.user_activity * 0.1).toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Page Views</span>
                        <span className="font-medium">{Math.floor(reportData.user_activity * 0.5).toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Data Updates</span>
                        <span className="font-medium">{Math.floor(reportData.user_activity * 0.2).toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>File Operations</span>
                        <span className="font-medium">{Math.floor(reportData.user_activity * 0.2).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}
