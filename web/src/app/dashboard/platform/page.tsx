"use client"

import { useState, useEffect } from "react"
import { useAuth } from "@/features/auth/hooks/useAuth"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  Brain,
  Server,
  Database,
  Shield,
  Users,
  Building,
  Activity,
  TrendingUp,
  BarChart3,
  Globe,
  Zap,
  Monitor,
  AlertTriangle,
  CheckCircle,
  Clock,
  DollarSign,
  RefreshCw,
  Settings,
  Info,
  ExternalLink
} from "lucide-react"

// Mock data for platform overview - in real app this would come from APIs
const platformMetrics = {
  version: "2.1.4",
  uptime: "99.97%",
  lastDeployment: "2025-01-15T10:30:00Z",
  environment: "Production",
  region: "US-West-2",
  instances: 12,
  activeConnections: 8547,
  requestsPerMinute: 15420,
  averageResponseTime: 145,
  systemLoad: 68,
  memoryUsage: 72,
  diskUsage: 45,
  networkIn: 2.4,
  networkOut: 3.1
}

const organizationStats = {
  total: 247,
  active: 231,
  trial: 45,
  premium: 156,
  enterprise: 30,
  growth: {
    thisMonth: 12,
    lastMonth: 8,
    percentage: 50
  }
}

const userStats = {
  total: 15847,
  active: 12956,
  newToday: 67,
  newThisWeek: 423,
  activeThisWeek: 9847,
  averageSessions: 4.2,
  averageSessionDuration: "24m 35s"
}

const subscriptionStats = {
  totalRevenue: 89420,
  monthlyRecurring: 67890,
  annualRecurring: 21530,
  churnRate: 2.1,
  expansionRevenue: 8940,
  netRevenueRetention: 114
}

const systemComponents = [
  {
    name: "API Gateway",
    status: "healthy",
    uptime: "99.99%",
    lastCheck: "2 minutes ago",
    version: "3.2.1",
    instances: 3
  },
  {
    name: "Authentication Service",
    status: "healthy",
    uptime: "99.95%",
    lastCheck: "1 minute ago",
    version: "2.8.4",
    instances: 2
  },
  {
    name: "Database Cluster",
    status: "healthy",
    uptime: "99.97%",
    lastCheck: "30 seconds ago",
    version: "15.4",
    instances: 5
  },
  {
    name: "Redis Cache",
    status: "healthy",
    uptime: "99.98%",
    lastCheck: "1 minute ago",
    version: "7.2.1",
    instances: 3
  },
  {
    name: "Message Queue",
    status: "warning",
    uptime: "99.89%",
    lastCheck: "45 seconds ago",
    version: "3.11.2",
    instances: 2,
    issues: ["High memory usage on queue-02"]
  },
  {
    name: "File Storage",
    status: "healthy",
    uptime: "99.99%",
    lastCheck: "2 minutes ago",
    version: "S3",
    instances: 1
  }
]

const recentDeployments = [
  {
    version: "2.1.4",
    timestamp: "2025-01-15T10:30:00Z",
    status: "success",
    deployer: "CI/CD Pipeline",
    changes: [
      "Fixed notification bell positioning",
      "Improved sidebar navigation",
      "Added platform overview page",
      "Performance optimizations"
    ]
  },
  {
    version: "2.1.3",
    timestamp: "2025-01-12T14:15:00Z",
    status: "success",
    deployer: "DevOps Team",
    changes: [
      "Enhanced security headers",
      "Database connection pooling improvements",
      "Updated dependencies"
    ]
  },
  {
    version: "2.1.2",
    timestamp: "2025-01-10T09:45:00Z",
    status: "success",
    deployer: "CI/CD Pipeline",
    changes: [
      "New user invitation flow",
      "SLA monitoring enhancements",
      "Bug fixes and improvements"
    ]
  }
]

const securityMetrics = {
  activeThreats: 0,
  blockedAttacks: 247,
  sslCertificateExpiry: "2025-11-15",
  lastSecurityScan: "2025-01-20T03:00:00Z",
  vulnerabilities: {
    critical: 0,
    high: 1,
    medium: 3,
    low: 12
  },
  compliance: {
    soc2: "Compliant",
    gdpr: "Compliant",
    hipaa: "N/A",
    iso27001: "In Progress"
  }
}

export default function PlatformOverviewPage() {
  const { user } = useAuth()
  const [isLoading, setIsLoading] = useState(true)
  const [lastRefresh, setLastRefresh] = useState(new Date())

  useEffect(() => {
    // Simulate data loading
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  const handleRefresh = () => {
    setIsLoading(true)
    setLastRefresh(new Date())
    
    // Simulate refresh
    setTimeout(() => {
      setIsLoading(false)
    }, 2000)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-100 dark:bg-green-900/30'
      case 'warning':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30'
      case 'error':
        return 'text-red-600 bg-red-100 dark:bg-red-900/30'
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-900/30'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4" />
      case 'warning':
        return <AlertTriangle className="h-4 w-4" />
      case 'error':
        return <AlertTriangle className="h-4 w-4" />
      default:
        return <Info className="h-4 w-4" />
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString()
  }

  const formatDuration = (timestamp: string) => {
    const now = new Date()
    const then = new Date(timestamp)
    const diff = now.getTime() - then.getTime()
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const days = Math.floor(hours / 24)
    
    if (days > 0) return `${days}d ago`
    if (hours > 0) return `${hours}h ago`
    return 'Just now'
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Brain className="h-6 w-6 text-white" />
            </div>
            Platform Overview
          </h1>
          <p className="text-muted-foreground mt-2">
            Comprehensive view of the SalesOptimizer platform health, metrics, and operations
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">
            Last updated: {lastRefresh.toLocaleTimeString()}
          </span>
          <Button 
            onClick={handleRefresh} 
            variant="outline" 
            size="sm"
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Platform Health Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Platform Version</CardTitle>
            <Monitor className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{platformMetrics.version}</div>
            <p className="text-xs text-muted-foreground">
              Deployed {formatDuration(platformMetrics.lastDeployment)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Uptime</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{platformMetrics.uptime}</div>
            <p className="text-xs text-muted-foreground">
              Last 30 days
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{userStats.active.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              +{userStats.newToday} today
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Monthly Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${subscriptionStats.monthlyRecurring.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              {subscriptionStats.netRevenueRetention}% retention
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Metrics Tabs */}
      <Tabs defaultValue="system" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="system">System Health</TabsTrigger>
          <TabsTrigger value="organizations">Organizations</TabsTrigger>
          <TabsTrigger value="users">Users</TabsTrigger>
          <TabsTrigger value="revenue">Revenue</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
        </TabsList>

        {/* System Health Tab */}
        <TabsContent value="system" className="space-y-6">
          {/* System Performance */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Server className="h-5 w-5" />
                  System Performance
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>CPU Usage</span>
                    <span>{platformMetrics.systemLoad}%</span>
                  </div>
                  <Progress value={platformMetrics.systemLoad} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Memory Usage</span>
                    <span>{platformMetrics.memoryUsage}%</span>
                  </div>
                  <Progress value={platformMetrics.memoryUsage} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Disk Usage</span>
                    <span>{platformMetrics.diskUsage}%</span>
                  </div>
                  <Progress value={platformMetrics.diskUsage} className="h-2" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Traffic Metrics
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-2xl font-bold">{platformMetrics.requestsPerMinute.toLocaleString()}</div>
                    <p className="text-xs text-muted-foreground">Requests/min</p>
                  </div>
                  <div>
                    <div className="text-2xl font-bold">{platformMetrics.averageResponseTime}ms</div>
                    <p className="text-xs text-muted-foreground">Avg response</p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-lg font-semibold">{platformMetrics.networkIn} GB/h</div>
                    <p className="text-xs text-muted-foreground">Network In</p>
                  </div>
                  <div>
                    <div className="text-lg font-semibold">{platformMetrics.networkOut} GB/h</div>
                    <p className="text-xs text-muted-foreground">Network Out</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* System Components */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                System Components
              </CardTitle>
              <CardDescription>
                Status and health of all platform components
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {systemComponents.map((component, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <Badge className={getStatusColor(component.status)}>
                        {getStatusIcon(component.status)}
                        <span className="ml-1 capitalize">{component.status}</span>
                      </Badge>
                      <div>
                        <div className="font-medium">{component.name}</div>
                        <div className="text-sm text-muted-foreground">
                          v{component.version} • {component.instances} instance{component.instances > 1 ? 's' : ''}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium">{component.uptime} uptime</div>
                      <div className="text-xs text-muted-foreground">
                        Checked {component.lastCheck}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recent Deployments */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5" />
                Recent Deployments
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentDeployments.map((deployment, index) => (
                  <div key={index} className="flex items-start justify-between p-4 border rounded-lg">
                    <div className="flex items-start gap-3">
                      <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Success
                      </Badge>
                      <div>
                        <div className="font-medium">Version {deployment.version}</div>
                        <div className="text-sm text-muted-foreground mb-2">
                          {formatTimestamp(deployment.timestamp)} • by {deployment.deployer}
                        </div>
                        <div className="text-sm">
                          <ul className="list-disc list-inside space-y-1">
                            {deployment.changes.map((change, changeIndex) => (
                              <li key={changeIndex} className="text-muted-foreground">{change}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Organizations Tab */}
        <TabsContent value="organizations" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Organizations</CardTitle>
                <Building className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{organizationStats.total}</div>
                <p className="text-xs text-muted-foreground">
                  {organizationStats.active} active
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Trial Organizations</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{organizationStats.trial}</div>
                <p className="text-xs text-muted-foreground">
                  Active trials
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Premium Organizations</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{organizationStats.premium}</div>
                <p className="text-xs text-muted-foreground">
                  Paid subscriptions
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Enterprise</CardTitle>
                <Shield className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{organizationStats.enterprise}</div>
                <p className="text-xs text-muted-foreground">
                  Enterprise clients
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Organization Growth</CardTitle>
              <CardDescription>
                New organizations joining the platform
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-2xl font-bold">{organizationStats.growth.thisMonth}</div>
                  <p className="text-sm text-muted-foreground">New this month</p>
                </div>
                <div className="text-right">
                  <div className="text-lg font-semibold text-green-600">
                    +{organizationStats.growth.percentage}%
                  </div>
                  <p className="text-sm text-muted-foreground">vs last month</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Users Tab */}
        <TabsContent value="users" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{userStats.total.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">
                  All registered users
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Users</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{userStats.active.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">
                  Active this month
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">New Today</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{userStats.newToday}</div>
                <p className="text-xs text-muted-foreground">
                  {userStats.newThisWeek} this week
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Avg Sessions</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{userStats.averageSessions}</div>
                <p className="text-xs text-muted-foreground">
                  {userStats.averageSessionDuration} avg duration
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Revenue Tab */}
        <TabsContent value="revenue" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">${subscriptionStats.totalRevenue.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">
                  This month
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Monthly Recurring</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">${subscriptionStats.monthlyRecurring.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">
                  MRR
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Churn Rate</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{subscriptionStats.churnRate}%</div>
                <p className="text-xs text-muted-foreground">
                  This month
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Revenue Breakdown</CardTitle>
              <CardDescription>
                Monthly and annual subscription revenue
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span>Monthly Subscriptions</span>
                  <span className="font-medium">${subscriptionStats.monthlyRecurring.toLocaleString()}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Annual Subscriptions</span>
                  <span className="font-medium">${subscriptionStats.annualRecurring.toLocaleString()}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Expansion Revenue</span>
                  <span className="font-medium">${subscriptionStats.expansionRevenue.toLocaleString()}</span>
                </div>
                <div className="flex items-center justify-between border-t pt-4">
                  <span className="font-medium">Net Revenue Retention</span>
                  <span className="font-bold text-green-600">{subscriptionStats.netRevenueRetention}%</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Threats</CardTitle>
                <Shield className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{securityMetrics.activeThreats}</div>
                <p className="text-xs text-muted-foreground">
                  No active threats
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Blocked Attacks</CardTitle>
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{securityMetrics.blockedAttacks}</div>
                <p className="text-xs text-muted-foreground">
                  Last 30 days
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">SSL Certificate</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">Valid</div>
                <p className="text-xs text-muted-foreground">
                  Expires {new Date(securityMetrics.sslCertificateExpiry).toLocaleDateString()}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Last Scan</CardTitle>
                <Monitor className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatDuration(securityMetrics.lastSecurityScan)}</div>
                <p className="text-xs text-muted-foreground">
                  Security scan
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Vulnerability Report</CardTitle>
                <CardDescription>
                  Current security vulnerabilities by severity
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                      <span>Critical</span>
                    </div>
                    <span className="font-medium">{securityMetrics.vulnerabilities.critical}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                      <span>High</span>
                    </div>
                    <span className="font-medium">{securityMetrics.vulnerabilities.high}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                      <span>Medium</span>
                    </div>
                    <span className="font-medium">{securityMetrics.vulnerabilities.medium}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                      <span>Low</span>
                    </div>
                    <span className="font-medium">{securityMetrics.vulnerabilities.low}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Compliance Status</CardTitle>
                <CardDescription>
                  Current compliance certifications and standards
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(securityMetrics.compliance).map(([standard, status]) => (
                    <div key={standard} className="flex items-center justify-between">
                      <span className="uppercase font-medium">{standard}</span>
                      <Badge 
                        className={
                          status === 'Compliant' 
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/30' 
                            : status === 'In Progress'
                            ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30'
                            : 'bg-gray-100 text-gray-800 dark:bg-gray-900/30'
                        }
                      >
                        {status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
