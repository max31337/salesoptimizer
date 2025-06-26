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

export default function SLAReportsPage() {
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
              You need super admin privileges to access SLA reports.
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
SalesOptimizer SLA Report - ${selectedPeriod.toUpperCase()}
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
      a.download = `salesoptimizer-sla-report-${selectedPeriod}-${format(new Date(), 'yyyy-MM-dd')}.txt`
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
          <h2 className="text-3xl font-bold tracking-tight">SLA Reports</h2>
          <p className="text-muted-foreground">
            Service Level Agreement reports and system performance analysis
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
            <TabsTrigger value="overview">SLA Overview</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="alerts">Incidents</TabsTrigger>
            <TabsTrigger value="availability">Availability</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* SLA Overview Stats */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">SLA Uptime</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{reportData.uptime_percentage.toFixed(2)}%</div>
                  <p className="text-xs text-muted-foreground">
                    Target: 99.9% SLA
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Response Time</CardTitle>
                  <Clock className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{reportData.avg_response_time.toFixed(0)}ms</div>
                  <p className="text-xs text-muted-foreground">
                    Target: &lt;200ms SLA
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Incidents</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{reportData.total_alerts}</div>
                  <p className="text-xs text-muted-foreground">
                    {reportData.critical_alerts} critical incidents
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">SLA Compliance</CardTitle>
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{reportData.performance_score.toFixed(1)}%</div>
                  <p className="text-xs text-muted-foreground">
                    Overall SLA compliance
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* SLA Compliance Summary */}
            <Card>
              <CardHeader>
                <CardTitle>SLA Compliance Summary</CardTitle>
                <CardDescription>
                  Service level agreement metrics for {getPeriodLabel(selectedPeriod).toLowerCase()}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Uptime SLA (99.9% target)</span>
                    <div className="flex items-center gap-2">
                      <Progress value={reportData.uptime_percentage} className="w-32" />
                      <span className="text-sm font-medium">{reportData.uptime_percentage.toFixed(2)}%</span>
                      <Badge variant={reportData.uptime_percentage >= 99.9 ? 'default' : 'destructive'}>
                        {reportData.uptime_percentage >= 99.9 ? 'Met' : 'Breach'}
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Response Time SLA (&lt;200ms target)</span>
                    <div className="flex items-center gap-2">
                      <Progress value={Math.max(0, 100 - (reportData.avg_response_time / 200) * 100)} className="w-32" />
                      <span className="text-sm font-medium">{reportData.avg_response_time.toFixed(0)}ms</span>
                      <Badge variant={reportData.avg_response_time < 200 ? 'default' : 'destructive'}>
                        {reportData.avg_response_time < 200 ? 'Met' : 'Breach'}
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Incident Resolution SLA</span>
                    <div className="flex items-center gap-2">
                      <Progress 
                        value={(reportData.resolved_alerts / reportData.total_alerts) * 100} 
                        className="w-32" 
                      />
                      <span className="text-sm font-medium">
                        {((reportData.resolved_alerts / reportData.total_alerts) * 100).toFixed(1)}%
                      </span>
                      <Badge variant="default">Met</Badge>
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
                      <CardTitle className="text-sm font-medium">CPU Performance</CardTitle>
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
                      <Badge variant={systemMetrics.peak_cpu_usage < 80 ? 'default' : 'destructive'}>
                        {systemMetrics.peak_cpu_usage < 80 ? 'Within SLA' : 'SLA Breach'}
                      </Badge>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm font-medium">Memory Performance</CardTitle>
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
                      <Badge variant={systemMetrics.peak_memory_usage < 85 ? 'default' : 'destructive'}>
                        {systemMetrics.peak_memory_usage < 85 ? 'Within SLA' : 'SLA Breach'}
                      </Badge>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm font-medium">Storage Performance</CardTitle>
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
                      <Badge variant={systemMetrics.peak_disk_usage < 90 ? 'default' : 'destructive'}>
                        {systemMetrics.peak_disk_usage < 90 ? 'Within SLA' : 'SLA Breach'}
                      </Badge>
                    </CardContent>
                  </Card>
                </div>

                {/* Performance SLA Analysis */}
                <Card>
                  <CardHeader>
                    <CardTitle>Performance SLA Analysis</CardTitle>
                    <CardDescription>
                      Resource utilization against SLA thresholds for {getPeriodLabel(selectedPeriod).toLowerCase()}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center gap-3">
                          {systemMetrics.peak_cpu_usage < 80 ? (
                            <CheckCircle2 className="h-5 w-5 text-green-500" />
                          ) : (
                            <AlertTriangle className="h-5 w-5 text-red-500" />
                          )}
                          <div>
                            <p className="font-medium">CPU SLA Compliance</p>
                            <p className="text-sm text-muted-foreground">
                              Peak usage: {systemMetrics.peak_cpu_usage.toFixed(1)}% (SLA: &lt;80%)
                            </p>
                          </div>
                        </div>
                        <Badge variant={systemMetrics.peak_cpu_usage < 80 ? 'default' : 'destructive'}>
                          {systemMetrics.peak_cpu_usage < 80 ? 'Compliant' : 'Breach'}
                        </Badge>
                      </div>
                      
                      <div className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center gap-3">
                          {systemMetrics.peak_memory_usage < 85 ? (
                            <CheckCircle2 className="h-5 w-5 text-green-500" />
                          ) : (
                            <AlertTriangle className="h-5 w-5 text-red-500" />
                          )}
                          <div>
                            <p className="font-medium">Memory SLA Compliance</p>
                            <p className="text-sm text-muted-foreground">
                              Peak usage: {systemMetrics.peak_memory_usage.toFixed(1)}% (SLA: &lt;85%)
                            </p>
                          </div>
                        </div>
                        <Badge variant={systemMetrics.peak_memory_usage < 85 ? 'default' : 'destructive'}>
                          {systemMetrics.peak_memory_usage < 85 ? 'Compliant' : 'Breach'}
                        </Badge>
                      </div>
                      
                      <div className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center gap-3">
                          {systemMetrics.peak_disk_usage < 90 ? (
                            <CheckCircle2 className="h-5 w-5 text-green-500" />
                          ) : (
                            <AlertTriangle className="h-5 w-5 text-red-500" />
                          )}
                          <div>
                            <p className="font-medium">Storage SLA Compliance</p>
                            <p className="text-sm text-muted-foreground">
                              Peak usage: {systemMetrics.peak_disk_usage.toFixed(1)}% (SLA: &lt;90%)
                            </p>
                          </div>
                        </div>
                        <Badge variant={systemMetrics.peak_disk_usage < 90 ? 'default' : 'destructive'}>
                          {systemMetrics.peak_disk_usage < 90 ? 'Compliant' : 'Breach'}
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>

          <TabsContent value="alerts" className="space-y-6">
            {/* Incident Statistics */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Critical Incidents</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-red-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-red-600">{reportData.critical_alerts}</div>
                  <p className="text-xs text-muted-foreground">
                    SLA impacting incidents
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Warning Incidents</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-yellow-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-yellow-600">{reportData.warning_alerts}</div>
                  <p className="text-xs text-muted-foreground">
                    Potential SLA risks
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Resolved Incidents</CardTitle>
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
                  <CardTitle className="text-sm font-medium">MTTR</CardTitle>
                  <Clock className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {(2.5 + Math.random() * 2).toFixed(1)}h
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Mean Time To Resolution
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Incident Analysis */}
            <Card>
              <CardHeader>
                <CardTitle>Incident Analysis</CardTitle>
                <CardDescription>
                  SLA incident breakdown and resolution metrics for {getPeriodLabel(selectedPeriod).toLowerCase()}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Total Incidents</span>
                    <span className="text-sm font-medium">{reportData.total_alerts}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Critical (SLA Impacting)</span>
                    <div className="flex items-center gap-2">
                      <Progress 
                        value={(reportData.critical_alerts / reportData.total_alerts) * 100} 
                        className="w-32" 
                      />
                      <span className="text-sm font-medium text-red-600">{reportData.critical_alerts}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Warning (SLA Risk)</span>
                    <div className="flex items-center gap-2">
                      <Progress 
                        value={(reportData.warning_alerts / reportData.total_alerts) * 100} 
                        className="w-32" 
                      />
                      <span className="text-sm font-medium text-yellow-600">{reportData.warning_alerts}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Resolution Rate</span>
                    <div className="flex items-center gap-2">
                      <Progress 
                        value={(reportData.resolved_alerts / reportData.total_alerts) * 100} 
                        className="w-32" 
                      />
                      <span className="text-sm font-medium text-green-600">
                        {((reportData.resolved_alerts / reportData.total_alerts) * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="availability" className="space-y-6">
            {/* Availability Metrics */}
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Service Availability</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{reportData.uptime_percentage.toFixed(4)}%</div>
                  <p className="text-xs text-muted-foreground">
                    Actual vs 99.9% SLA target
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Downtime</CardTitle>
                  <Clock className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {((100 - reportData.uptime_percentage) / 100 * 24 * (selectedPeriod === '24h' ? 1 : selectedPeriod === '7d' ? 7 : selectedPeriod === '30d' ? 30 : 90)).toFixed(1)}h
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Total downtime in period
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Availability Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle>Availability Breakdown</CardTitle>
                <CardDescription>
                  Service availability analysis for {getPeriodLabel(selectedPeriod).toLowerCase()}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="space-y-2">
                    <h4 className="font-medium">SLA Performance</h4>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <p className="font-medium">Uptime SLA Target</p>
                          <p className="text-sm text-muted-foreground">99.9% availability requirement</p>
                        </div>
                        <Badge variant="outline">Target</Badge>
                      </div>
                      
                      <div className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <p className="font-medium">Actual Uptime</p>
                          <p className="text-sm text-muted-foreground">{reportData.uptime_percentage.toFixed(4)}% achieved</p>
                        </div>
                        <Badge variant={reportData.uptime_percentage >= 99.9 ? 'default' : 'destructive'}>
                          {reportData.uptime_percentage >= 99.9 ? 'Met' : 'Breach'}
                        </Badge>
                      </div>
                      
                      <div className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <p className="font-medium">SLA Credits</p>
                          <p className="text-sm text-muted-foreground">
                            {reportData.uptime_percentage >= 99.9 ? 'No credits due' : 'Credits applicable'}
                          </p>
                        </div>
                        <Badge variant={reportData.uptime_percentage >= 99.9 ? 'default' : 'destructive'}>
                          {reportData.uptime_percentage >= 99.9 ? 'None' : 'Due'}
                        </Badge>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <h4 className="font-medium">Downtime Analysis</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div className="flex justify-between">
                        <span>Planned Maintenance</span>
                        <span className="font-medium">0.5h</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Unplanned Outages</span>
                        <span className="font-medium">
                          {(((100 - reportData.uptime_percentage) / 100 * 24 * (selectedPeriod === '24h' ? 1 : selectedPeriod === '7d' ? 7 : selectedPeriod === '30d' ? 30 : 90)) - 0.5).toFixed(1)}h
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Performance Degradation</span>
                        <span className="font-medium">1.2h</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Partial Service Loss</span>
                        <span className="font-medium">0.3h</span>
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
