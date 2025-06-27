"use client"

import { useState, useEffect } from "react"
import { useAuth } from "@/features/auth/hooks/useAuth"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Progress } from "@/components/ui/progress"
import { 
  Users,
  Search,
  Plus,
  MoreHorizontal,
  TrendingUp,
  TrendingDown,
  Activity,
  DollarSign,
  AlertTriangle,
  Eye,
  Edit,
  Trash2,
  Building2,
  Target,
  Award,
  UserCheck,
  Settings,
  Filter,
  Download,
  Calendar
} from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs"

// Team interface for organization teams management
interface Team {
  id: string
  name: string
  description: string
  organizationId: string
  organizationName: string
  organizationSlug: string
  leaderId: string
  leaderName: string
  leaderEmail: string
  memberCount: number
  status: 'active' | 'inactive' | 'archived'
  performance: number
  monthlyTarget: number
  currentRevenue: number
  tasksCompleted: number
  tasksTotal: number
  createdAt: string
  lastActivity: string
  region: string
  department: 'sales' | 'marketing' | 'support' | 'product' | 'operations'
}

// Mock data for teams across organizations
const mockTeams: Team[] = [
  {
    id: 'team_1',
    name: 'Enterprise Sales Team',
    description: 'Primary sales team for enterprise clients',
    organizationId: 'org_1',
    organizationName: 'Acme Corporation',
    organizationSlug: 'acme-corp',
    leaderId: 'user_1',
    leaderName: 'Alice Johnson',
    leaderEmail: 'alice.johnson@acme.com',
    memberCount: 12,
    status: 'active',
    performance: 94,
    monthlyTarget: 120000,
    currentRevenue: 112800,
    tasksCompleted: 45,
    tasksTotal: 52,
    createdAt: '2024-01-20T10:00:00Z',
    lastActivity: '2025-06-27T15:30:00Z',
    region: 'North America',
    department: 'sales'
  },
  {
    id: 'team_2',
    name: 'SMB Sales Division',
    description: 'Small and medium business sales team',
    organizationId: 'org_1',
    organizationName: 'Acme Corporation',
    organizationSlug: 'acme-corp',
    leaderId: 'user_2',
    leaderName: 'Bob Smith',
    leaderEmail: 'bob.smith@acme.com',
    memberCount: 8,
    status: 'active',
    performance: 87,
    monthlyTarget: 60000,
    currentRevenue: 52200,
    tasksCompleted: 32,
    tasksTotal: 38,
    createdAt: '2024-02-15T09:30:00Z',
    lastActivity: '2025-06-27T14:15:00Z',
    region: 'North America',
    department: 'sales'
  },
  {
    id: 'team_3',
    name: 'European Sales Team',
    description: 'Sales team covering European markets',
    organizationId: 'org_2',
    organizationName: 'Global Solutions Ltd',
    organizationSlug: 'global-solutions',
    leaderId: 'user_3',
    leaderName: 'Claire Dubois',
    leaderEmail: 'claire@globalsolutions.com',
    memberCount: 6,
    status: 'active',
    performance: 78,
    monthlyTarget: 45000,
    currentRevenue: 35100,
    tasksCompleted: 28,
    tasksTotal: 35,
    createdAt: '2024-03-25T11:00:00Z',
    lastActivity: '2025-06-27T12:45:00Z',
    region: 'Europe',
    department: 'sales'
  },
  {
    id: 'team_4',
    name: 'Marketing Outreach',
    description: 'Digital marketing and lead generation',
    organizationId: 'org_2',
    organizationName: 'Global Solutions Ltd',
    organizationSlug: 'global-solutions',
    leaderId: 'user_4',
    leaderName: 'David Chen',
    leaderEmail: 'david@globalsolutions.com',
    memberCount: 4,
    status: 'active',
    performance: 85,
    monthlyTarget: 25000,
    currentRevenue: 21250,
    tasksCompleted: 18,
    tasksTotal: 22,
    createdAt: '2024-04-10T14:20:00Z',
    lastActivity: '2025-06-27T11:20:00Z',
    region: 'Europe',
    department: 'marketing'
  },
  {
    id: 'team_5',
    name: 'Growth Team',
    description: 'Product growth and user acquisition',
    organizationId: 'org_3',
    organizationName: 'TechStart Inc',
    organizationSlug: 'techstart',
    leaderId: 'user_5',
    leaderName: 'Emma Wilson',
    leaderEmail: 'emma@techstart.co',
    memberCount: 3,
    status: 'active',
    performance: 72,
    monthlyTarget: 15000,
    currentRevenue: 10800,
    tasksCompleted: 12,
    tasksTotal: 18,
    createdAt: '2024-06-12T08:00:00Z',
    lastActivity: '2025-06-26T16:20:00Z',
    region: 'Asia Pacific',
    department: 'marketing'
  },
  {
    id: 'team_6',
    name: 'Customer Success',
    description: 'Customer retention and support',
    organizationId: 'org_4',
    organizationName: 'Enterprise Corp',
    organizationSlug: 'enterprise-corp',
    leaderId: 'user_6',
    leaderName: 'Frank Miller',
    leaderEmail: 'frank@enterprise.com',
    memberCount: 7,
    status: 'inactive',
    performance: 45,
    monthlyTarget: 30000,
    currentRevenue: 13500,
    tasksCompleted: 8,
    tasksTotal: 20,
    createdAt: '2023-11-10T13:00:00Z',
    lastActivity: '2025-06-18T10:30:00Z',
    region: 'North America',
    department: 'support'
  },
  {
    id: 'team_7',
    name: 'Product Development',
    description: 'Product feature development and innovation',
    organizationId: 'org_5',
    organizationName: 'StartupHub',
    organizationSlug: 'startuphub',
    leaderId: 'user_7',
    leaderName: 'Grace Lee',
    leaderEmail: 'grace@startuphub.io',
    memberCount: 5,
    status: 'active',
    performance: 89,
    monthlyTarget: 20000,
    currentRevenue: 17800,
    tasksCompleted: 24,
    tasksTotal: 28,
    createdAt: '2024-05-20T09:15:00Z',
    lastActivity: '2025-06-27T13:45:00Z',
    region: 'North America',
    department: 'product'
  }
]

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'active':
      return <Badge variant="default" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Active</Badge>
    case 'inactive':
      return <Badge variant="secondary" className="bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200">Inactive</Badge>
    case 'archived':
      return <Badge variant="outline" className="text-gray-600">Archived</Badge>
    default:
      return <Badge variant="outline">{status}</Badge>
  }
}

const getPerformanceBadge = (performance: number) => {
  if (performance >= 90) {
    return <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Excellent</Badge>
  } else if (performance >= 75) {
    return <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">Good</Badge>
  } else if (performance >= 60) {
    return <Badge className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">Fair</Badge>
  } else {
    return <Badge className="bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">Needs Improvement</Badge>
  }
}

const getDepartmentBadge = (department: string) => {
  const config = {
    sales: { label: 'Sales', className: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' },
    marketing: { label: 'Marketing', className: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200' },
    support: { label: 'Support', className: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' },
    product: { label: 'Product', className: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200' },
    operations: { label: 'Operations', className: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200' }
  }
  
  const dept = config[department as keyof typeof config] || config.operations
  return <Badge className={dept.className}>{dept.label}</Badge>
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const formatRelativeTime = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))
  const diffInDays = Math.floor(diffInHours / 24)
  
  if (diffInDays > 0) return `${diffInDays}d ago`
  if (diffInHours > 0) return `${diffInHours}h ago`
  return 'Just now'
}

const getTaskCompletionPercentage = (completed: number, total: number) => {
  return total > 0 ? Math.round((completed / total) * 100) : 0
}

const getRevenueProgress = (current: number, target: number) => {
  return target > 0 ? Math.min(Math.round((current / target) * 100), 100) : 0
}

export default function OrganizationTeamsPage() {
  const { user } = useAuth()
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [organizationFilter, setOrganizationFilter] = useState("all")
  const [departmentFilter, setDepartmentFilter] = useState("all")
  const [performanceFilter, setPerformanceFilter] = useState("all")
  const [teams, setTeams] = useState<Team[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setTeams(mockTeams)
      setLoading(false)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  // Check if user is super admin
  if (user?.role !== 'super_admin') {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Card className="w-full max-w-md text-center">
          <CardHeader>
            <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
            <CardTitle>Access Restricted</CardTitle>
            <CardDescription>
              This page is only accessible to super administrators.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  // Filter teams based on search and filters
  const filteredTeams = teams.filter(team => {
    const matchesSearch = team.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         team.organizationName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         team.leaderName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         team.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "all" || team.status === statusFilter
    const matchesOrganization = organizationFilter === "all" || team.organizationId === organizationFilter
    const matchesDepartment = departmentFilter === "all" || team.department === departmentFilter
    const matchesPerformance = performanceFilter === "all" || 
      (performanceFilter === "high" && team.performance >= 80) ||
      (performanceFilter === "medium" && team.performance >= 60 && team.performance < 80) ||
      (performanceFilter === "low" && team.performance < 60)
    
    return matchesSearch && matchesStatus && matchesOrganization && matchesDepartment && matchesPerformance
  })

  // Get unique organizations and departments for filters
  const organizations = Array.from(new Set(teams.map(team => ({ id: team.organizationId, name: team.organizationName }))
    .map(org => JSON.stringify(org))))
    .map(org => JSON.parse(org))

  const departments = Array.from(new Set(teams.map(team => team.department)))

  // Calculate statistics
  const stats = {
    totalTeams: teams.length,
    activeTeams: teams.filter(team => team.status === 'active').length,
    totalMembers: teams.reduce((sum, team) => sum + team.memberCount, 0),
    totalRevenue: teams.reduce((sum, team) => sum + team.currentRevenue, 0),
    totalTarget: teams.reduce((sum, team) => sum + team.monthlyTarget, 0),
    avgPerformance: teams.length > 0 ? teams.reduce((sum, team) => sum + team.performance, 0) / teams.length : 0,
    totalTasksCompleted: teams.reduce((sum, team) => sum + team.tasksCompleted, 0),
    totalTasks: teams.reduce((sum, team) => sum + team.tasksTotal, 0)
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-r from-green-600 to-blue-600 rounded-lg flex items-center justify-center">
              <Users className="h-6 w-6 text-white" />
            </div>
            Organization Teams
          </h1>
          <p className="text-muted-foreground mt-2">
            Manage teams across all client organizations on the platform
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Teams
          </Button>
          <Button className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700">
            <Plus className="h-4 w-4 mr-2" />
            Create Team
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Teams</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalTeams}</div>
            <p className="text-xs text-muted-foreground">
              {stats.activeTeams} active teams
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Members</CardTitle>
            <UserCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalMembers}</div>
            <p className="text-xs text-muted-foreground">
              Across all teams
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Revenue vs Target</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(stats.totalRevenue)}</div>
            <p className="text-xs text-muted-foreground">
              of {formatCurrency(stats.totalTarget)} target
            </p>
            <Progress value={getRevenueProgress(stats.totalRevenue, stats.totalTarget)} className="mt-2" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Performance</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.avgPerformance.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">
              {getTaskCompletionPercentage(stats.totalTasksCompleted, stats.totalTasks)}% task completion
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Teams Management */}
      <Card>
        <CardHeader>
          <CardTitle>Teams Directory</CardTitle>
          <CardDescription>
            Search, filter, and manage teams across all client organizations
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4 mb-6">
            <div className="lg:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search teams, organizations, leaders..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={organizationFilter} onValueChange={setOrganizationFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Organization" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Organizations</SelectItem>
                {organizations.map(org => (
                  <SelectItem key={org.id} value={org.id}>{org.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={departmentFilter} onValueChange={setDepartmentFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Department" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Departments</SelectItem>
                {departments.map(dept => (
                  <SelectItem key={dept} value={dept}>{dept.charAt(0).toUpperCase() + dept.slice(1)}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
                <SelectItem value="archived">Archived</SelectItem>
              </SelectContent>
            </Select>
            <Select value={performanceFilter} onValueChange={setPerformanceFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Performance" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Performance</SelectItem>
                <SelectItem value="high">High (80%+)</SelectItem>
                <SelectItem value="medium">Medium (60-79%)</SelectItem>
                <SelectItem value="low">Low (&lt;60%)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Teams Table */}
          <div className="rounded-md border overflow-hidden">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="min-w-[200px]">Team</TableHead>
                    <TableHead className="min-w-[180px]">Organization</TableHead>
                    <TableHead className="min-w-[150px]">Team Leader</TableHead>
                    <TableHead className="min-w-[100px]">Department</TableHead>
                    <TableHead className="min-w-[100px]">Status</TableHead>
                    <TableHead className="min-w-[120px]">Performance</TableHead>
                    <TableHead className="min-w-[80px]">Members</TableHead>
                    <TableHead className="min-w-[120px]">Revenue</TableHead>
                    <TableHead className="min-w-[100px] hidden lg:table-cell">Tasks</TableHead>
                    <TableHead className="min-w-[100px] hidden xl:table-cell">Last Active</TableHead>
                    <TableHead className="text-right min-w-[80px]">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredTeams.map((team) => (
                    <TableRow key={team.id} className="hover:bg-muted/50">
                      <TableCell className="min-w-[200px]">
                        <div>
                          <div className="font-semibold">{team.name}</div>
                          <div className="text-sm text-muted-foreground">{team.description}</div>
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[180px]">
                        <div className="flex items-center gap-2">
                          <Building2 className="h-4 w-4 text-muted-foreground" />
                          <div>
                            <div className="font-medium">{team.organizationName}</div>
                            <div className="text-sm text-muted-foreground">{team.organizationSlug}</div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[150px]">
                        <div>
                          <div className="font-medium">{team.leaderName}</div>
                          <div className="text-sm text-muted-foreground">{team.leaderEmail}</div>
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[100px]">
                        {getDepartmentBadge(team.department)}
                      </TableCell>
                      <TableCell className="min-w-[100px]">
                        {getStatusBadge(team.status)}
                      </TableCell>
                      <TableCell className="min-w-[120px]">
                        <div className="space-y-2">
                          {getPerformanceBadge(team.performance)}
                          <div className="text-sm font-medium">{team.performance}%</div>
                          <Progress value={team.performance} className="w-full h-1" />
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[80px]">
                        <div className="flex items-center gap-1">
                          <Users className="h-3 w-3 text-muted-foreground" />
                          <span className="font-medium">{team.memberCount}</span>
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[120px]">
                        <div className="space-y-1">
                          <div className="font-semibold">{formatCurrency(team.currentRevenue)}</div>
                          <div className="text-sm text-muted-foreground">
                            of {formatCurrency(team.monthlyTarget)}
                          </div>
                          <Progress value={getRevenueProgress(team.currentRevenue, team.monthlyTarget)} className="w-full h-1" />
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[100px] hidden lg:table-cell">
                        <div className="space-y-1">
                          <div className="text-sm">{team.tasksCompleted} / {team.tasksTotal}</div>
                          <Progress value={getTaskCompletionPercentage(team.tasksCompleted, team.tasksTotal)} className="w-16 h-1" />
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[100px] hidden xl:table-cell">
                        <div className="text-sm">{formatRelativeTime(team.lastActivity)}</div>
                      </TableCell>
                      <TableCell className="text-right min-w-[80px]">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                              <span className="sr-only">Open menu</span>
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Team Actions</DropdownMenuLabel>
                            <DropdownMenuItem>
                              <Eye className="mr-2 h-4 w-4" />
                              View Team Details
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Users className="mr-2 h-4 w-4" />
                              Manage Members
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Target className="mr-2 h-4 w-4" />
                              Set Targets
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Award className="mr-2 h-4 w-4" />
                              Performance Report
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem>
                              <Edit className="mr-2 h-4 w-4" />
                              Edit Team
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Settings className="mr-2 h-4 w-4" />
                              Team Settings
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem className="text-red-600">
                              <Trash2 className="mr-2 h-4 w-4" />
                              Archive Team
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </div>

          {/* Empty State */}
          {filteredTeams.length === 0 && (
            <div className="text-center py-12">
              <Users className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No teams found</h3>
              <p className="text-muted-foreground mb-4">
                {searchTerm || statusFilter !== "all" || organizationFilter !== "all" || departmentFilter !== "all" || performanceFilter !== "all"
                  ? "Try adjusting your search or filters"
                  : "No teams have been created yet"}
              </p>
              {(!searchTerm && statusFilter === "all" && organizationFilter === "all" && departmentFilter === "all" && performanceFilter === "all") && (
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Create First Team
                </Button>
              )}
            </div>
          )}

          {/* Results Summary */}
          {filteredTeams.length > 0 && (
            <div className="flex items-center justify-between pt-4 border-t">
              <div className="text-sm text-muted-foreground">
                Showing {filteredTeams.length} of {teams.length} teams
              </div>
              <div className="text-sm text-muted-foreground">
                Total Members: {filteredTeams.reduce((sum, team) => sum + team.memberCount, 0)} | 
                Total Revenue: {formatCurrency(filteredTeams.reduce((sum, team) => sum + team.currentRevenue, 0))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
