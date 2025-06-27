"use client"

import { useState, useEffect } from "react"
import { useAuth } from "@/features/auth/hooks/useAuth"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  UserPlus,
  Search,
  Plus,
  MoreHorizontal,
  Activity,
  UserCheck,
  AlertTriangle,
  Eye,
  Edit,
  Trash2,
  Settings,
  Shield,
  Crown,
  Building2,
  Mail,
  Phone,
  Calendar,
  Clock,
  Filter,
  Download,
  UserMinus,
  Code,
  GitBranch,
  Database,
  Server,
  Zap,
  Terminal,
  Layers,
  Cpu,
  Cloud,
  Wrench,
  Users,
  Award,
  CheckCircle,
  XCircle,
  Star,
  TrendingUp
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
import { UserAvatar } from "@/components/ui/user-avatar"

// Platform Team Member interface
interface PlatformTeamMember {
  id: string
  firstName: string
  lastName: string
  email: string
  role: 'platform_engineer' | 'senior_engineer' | 'tech_lead' | 'architect' | 'devops_engineer' | 'qa_engineer' | 'product_manager'
  status: 'active' | 'inactive' | 'on_leave' | 'busy'
  level: 'junior' | 'mid' | 'senior' | 'staff' | 'principal'
  department: 'engineering' | 'devops' | 'qa' | 'product' | 'design'
  specializations: string[]
  technologies: string[]
  currentProjects: string[]
  lastCommit: string
  totalCommits: number
  codeReviews: number
  bugsFixed: number
  featuresDelivered: number
  performanceRating: number // 1-5
  timezone: string
  lastLogin: string
  createdAt: string
  phone?: string
  location?: string
  avatar?: string
  isOnline: boolean
  lastActivity: string
  githubUsername?: string
  slackUsername?: string
}

// Mock data for platform team
const mockPlatformTeam: PlatformTeamMember[] = [
  {
    id: 'platform_1',
    firstName: 'Sarah',
    lastName: 'Chen',
    email: 'sarah.chen@salesoptimizer.com',
    role: 'architect',
    status: 'active',
    level: 'principal',
    department: 'engineering',
    specializations: ['System Architecture', 'Microservices', 'Cloud Infrastructure', 'Performance Optimization'],
    technologies: ['Node.js', 'TypeScript', 'AWS', 'Kubernetes', 'Redis', 'PostgreSQL'],
    currentProjects: ['Multi-tenant Architecture Redesign', 'Performance Optimization'],
    lastCommit: '2025-06-27T14:45:00Z',
    totalCommits: 2847,
    codeReviews: 156,
    bugsFixed: 89,
    featuresDelivered: 23,
    performanceRating: 5.0,
    timezone: 'PST',
    lastLogin: '2025-06-27T15:30:00Z',
    createdAt: '2022-03-15T09:00:00Z',
    phone: '+1-555-0201',
    location: 'San Francisco, CA',
    isOnline: true,
    lastActivity: '2025-06-27T15:30:00Z',
    githubUsername: 'sarahchen',
    slackUsername: 'sarah.chen'
  },
  {
    id: 'platform_2',
    firstName: 'Michael',
    lastName: 'Rodriguez',
    email: 'michael.rodriguez@salesoptimizer.com',
    role: 'tech_lead',
    status: 'active',
    level: 'staff',
    department: 'engineering',
    specializations: ['Frontend Architecture', 'React/Next.js', 'UI/UX Engineering', 'Mobile Development'],
    technologies: ['React', 'Next.js', 'TypeScript', 'React Native', 'GraphQL', 'Tailwind CSS'],
    currentProjects: ['Dashboard Redesign', 'Mobile App', 'Component Library'],
    lastCommit: '2025-06-27T13:20:00Z',
    totalCommits: 1923,
    codeReviews: 203,
    bugsFixed: 134,
    featuresDelivered: 45,
    performanceRating: 4.8,
    timezone: 'EST',
    lastLogin: '2025-06-27T15:15:00Z',
    createdAt: '2022-08-20T10:30:00Z',
    phone: '+1-555-0202',
    location: 'New York, NY',
    isOnline: true,
    lastActivity: '2025-06-27T15:15:00Z',
    githubUsername: 'mrodriguez',
    slackUsername: 'michael.r'
  },
  {
    id: 'platform_3',
    firstName: 'Emily',
    lastName: 'Watson',
    email: 'emily.watson@salesoptimizer.com',
    role: 'devops_engineer',
    status: 'active',
    level: 'senior',
    department: 'devops',
    specializations: ['CI/CD', 'Container Orchestration', 'Infrastructure as Code', 'Monitoring'],
    technologies: ['Docker', 'Kubernetes', 'Terraform', 'Jenkins', 'Prometheus', 'Grafana'],
    currentProjects: ['Auto-scaling Implementation', 'Monitoring Dashboard', 'Security Hardening'],
    lastCommit: '2025-06-27T12:55:00Z',
    totalCommits: 1456,
    codeReviews: 89,
    bugsFixed: 67,
    featuresDelivered: 31,
    performanceRating: 4.7,
    timezone: 'GMT',
    lastLogin: '2025-06-27T14:30:00Z',
    createdAt: '2023-01-10T11:15:00Z',
    phone: '+44-20-1234-5678',
    location: 'London, UK',
    isOnline: true,
    lastActivity: '2025-06-27T14:30:00Z',
    githubUsername: 'emilywatson',
    slackUsername: 'emily.watson'
  },
  {
    id: 'platform_4',
    firstName: 'David',
    lastName: 'Kim',
    email: 'david.kim@salesoptimizer.com',
    role: 'senior_engineer',
    status: 'active',
    level: 'senior',
    department: 'engineering',
    specializations: ['Backend Development', 'API Design', 'Database Optimization', 'Security'],
    technologies: ['Python', 'FastAPI', 'PostgreSQL', 'Redis', 'OAuth', 'JWT'],
    currentProjects: ['API Gateway', 'Authentication System', 'Database Migration'],
    lastCommit: '2025-06-27T11:30:00Z',
    totalCommits: 1678,
    codeReviews: 124,
    bugsFixed: 98,
    featuresDelivered: 38,
    performanceRating: 4.6,
    timezone: 'KST',
    lastLogin: '2025-06-27T14:00:00Z',
    createdAt: '2023-04-22T13:45:00Z',
    phone: '+82-10-9876-5432',
    location: 'Seoul, South Korea',
    isOnline: false,
    lastActivity: '2025-06-27T14:00:00Z',
    githubUsername: 'davidkim',
    slackUsername: 'david.kim'
  },
  {
    id: 'platform_5',
    firstName: 'Jessica',
    lastName: 'Thompson',
    email: 'jessica.thompson@salesoptimizer.com',
    role: 'product_manager',
    status: 'active',
    level: 'senior',
    department: 'product',
    specializations: ['Product Strategy', 'User Research', 'Roadmap Planning', 'Stakeholder Management'],
    technologies: ['Figma', 'Mixpanel', 'Amplitude', 'Notion', 'Slack', 'Jira'],
    currentProjects: ['Q3 Roadmap', 'User Analytics', 'Feature Prioritization'],
    lastCommit: '2025-06-26T16:20:00Z',
    totalCommits: 234,
    codeReviews: 45,
    bugsFixed: 12,
    featuresDelivered: 67,
    performanceRating: 4.9,
    timezone: 'PST',
    lastLogin: '2025-06-27T15:00:00Z',
    createdAt: '2023-02-14T12:00:00Z',
    phone: '+1-555-0203',
    location: 'Los Angeles, CA',
    isOnline: true,
    lastActivity: '2025-06-27T15:00:00Z',
    githubUsername: 'jessicathompson',
    slackUsername: 'jessica.t'
  },
  {
    id: 'platform_6',
    firstName: 'Alex',
    lastName: 'Petrov',
    email: 'alex.petrov@salesoptimizer.com',
    role: 'qa_engineer',
    status: 'on_leave',
    level: 'mid',
    department: 'qa',
    specializations: ['Test Automation', 'Performance Testing', 'Security Testing', 'Mobile Testing'],
    technologies: ['Selenium', 'Cypress', 'Jest', 'Postman', 'JMeter', 'TestRail'],
    currentProjects: ['Test Suite Automation', 'Performance Benchmarks'],
    lastCommit: '2025-06-25T10:15:00Z',
    totalCommits: 892,
    codeReviews: 67,
    bugsFixed: 156,
    featuresDelivered: 22,
    performanceRating: 4.4,
    timezone: 'EET',
    lastLogin: '2025-06-25T18:00:00Z',
    createdAt: '2023-09-05T14:30:00Z',
    phone: '+359-88-123-4567',
    location: 'Sofia, Bulgaria',
    isOnline: false,
    lastActivity: '2025-06-25T18:00:00Z',
    githubUsername: 'alexpetrov',
    slackUsername: 'alex.petrov'
  }
]

const getRoleBadge = (role: string) => {
  switch (role) {
    case 'architect':
      return <Badge className="bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
        <Crown className="h-3 w-3 mr-1" />
        Architect
      </Badge>
    case 'tech_lead':
      return <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
        <Shield className="h-3 w-3 mr-1" />
        Tech Lead
      </Badge>
    case 'senior_engineer':
      return <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
        <Code className="h-3 w-3 mr-1" />
        Senior Engineer
      </Badge>
    case 'platform_engineer':
      return <Badge className="bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-200">
        <Server className="h-3 w-3 mr-1" />
        Platform Engineer
      </Badge>
    case 'devops_engineer':
      return <Badge className="bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200">
        <Cloud className="h-3 w-3 mr-1" />
        DevOps Engineer
      </Badge>
    case 'qa_engineer':
      return <Badge className="bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200">
        <CheckCircle className="h-3 w-3 mr-1" />
        QA Engineer
      </Badge>
    case 'product_manager':
      return <Badge className="bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200">
        <Users className="h-3 w-3 mr-1" />
        Product Manager
      </Badge>
    default:
      return <Badge variant="outline">{role}</Badge>
  }
}

const getStatusBadge = (status: string, isOnline: boolean) => {
  switch (status) {
    case 'active':
      return (
        <div className="flex items-center gap-1">
          <Badge variant="default" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
            Active
          </Badge>
          <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-500' : 'bg-gray-400'}`} title={isOnline ? 'Online' : 'Offline'} />
        </div>
      )
    case 'on_leave':
      return <Badge variant="outline" className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">On Leave</Badge>
    case 'busy':
      return <Badge variant="outline" className="bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200">Busy</Badge>
    case 'inactive':
      return <Badge variant="destructive" className="bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">Inactive</Badge>
    default:
      return <Badge variant="outline">{status}</Badge>
  }
}

const getLevelBadge = (level: string) => {
  const colors = {
    'junior': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'mid': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
    'senior': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    'staff': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    'principal': 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200'
  }
  
  return (
    <Badge className={colors[level as keyof typeof colors] || 'bg-gray-100 text-gray-800'}>
      {level.charAt(0).toUpperCase() + level.slice(1)}
    </Badge>
  )
}

const getDepartmentBadge = (department: string) => {
  const colors = {
    'engineering': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'devops': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    'qa': 'bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200',
    'product': 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200',
    'design': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
  }
  
  return (
    <Badge variant="outline" className={colors[department as keyof typeof colors] || 'bg-gray-100 text-gray-800'}>
      {department.charAt(0).toUpperCase() + department.slice(1)}
    </Badge>
  )
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
  const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
  const diffInHours = Math.floor(diffInMinutes / 60)
  const diffInDays = Math.floor(diffInHours / 24)
  
  if (diffInDays > 7) return formatDate(dateString)
  if (diffInDays > 0) return `${diffInDays}d ago`
  if (diffInHours > 0) return `${diffInHours}h ago`
  if (diffInMinutes > 0) return `${diffInMinutes}m ago`
  return 'Just now'
}

export default function PlatformTeamPage() {
  const { user } = useAuth()
  const [searchTerm, setSearchTerm] = useState("")
  const [roleFilter, setRoleFilter] = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")
  const [levelFilter, setLevelFilter] = useState("all")
  const [departmentFilter, setDepartmentFilter] = useState("all")
  const [platformTeam, setPlatformTeam] = useState<PlatformTeamMember[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState("all")

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setPlatformTeam(mockPlatformTeam)
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

  // Filter platform team based on search, filters, and active tab
  const filteredTeam = platformTeam.filter(member => {
    const matchesSearch = member.firstName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         member.lastName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         member.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         member.specializations.some(spec => spec.toLowerCase().includes(searchTerm.toLowerCase())) ||
                         member.technologies.some(tech => tech.toLowerCase().includes(searchTerm.toLowerCase())) ||
                         member.currentProjects.some(project => project.toLowerCase().includes(searchTerm.toLowerCase()))
    
    const matchesRole = roleFilter === "all" || member.role === roleFilter
    const matchesStatus = statusFilter === "all" || member.status === statusFilter
    const matchesLevel = levelFilter === "all" || member.level === levelFilter
    const matchesDepartment = departmentFilter === "all" || member.department === departmentFilter
    
    // Tab filtering
    let matchesTab = true
    if (activeTab === "online") {
      matchesTab = member.isOnline && member.status === 'active'
    } else if (activeTab === "leads") {
      matchesTab = member.role === 'tech_lead' || member.role === 'architect' || member.level === 'staff' || member.level === 'principal'
    } else if (activeTab === "engineering") {
      matchesTab = member.department === 'engineering' || member.department === 'devops'
    }
    
    return matchesSearch && matchesRole && matchesStatus && matchesLevel && matchesDepartment && matchesTab
  })

  // Calculate statistics
  const stats = {
    totalMembers: platformTeam.length,
    onlineMembers: platformTeam.filter(m => m.isOnline && m.status === 'active').length,
    totalCommits: platformTeam.reduce((sum, m) => sum + m.totalCommits, 0),
    avgRating: Number((platformTeam.reduce((sum, m) => sum + m.performanceRating, 0) / platformTeam.length).toFixed(1)),
    activeProjects: Array.from(new Set(platformTeam.flatMap(m => m.currentProjects))).length,
    bugsFixed: platformTeam.reduce((sum, m) => sum + m.bugsFixed, 0)
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
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Code className="h-6 w-6 text-white" />
            </div>
            Platform Team Management
          </h1>
          <p className="text-muted-foreground mt-2">
            Manage internal development team members and track engineering metrics
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
          <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
            <UserPlus className="h-4 w-4 mr-2" />
            Add Team Member
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Team Members</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalMembers}</div>
            <p className="text-xs text-muted-foreground">
              {stats.onlineMembers} currently online
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Commits</CardTitle>
            <GitBranch className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalCommits.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              Across all repositories
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Projects</CardTitle>
            <Layers className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeProjects}</div>
            <p className="text-xs text-muted-foreground">
              Currently in development
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Performance</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.avgRating}/5</div>
            <p className="text-xs text-muted-foreground">
              Average team rating
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Platform Team Management */}
      <Card>
        <CardHeader>
          <CardTitle>Platform Team Directory</CardTitle>
          <CardDescription>
            Monitor development team performance, workload, and manage assignments
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-6">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="all">All Members</TabsTrigger>
              <TabsTrigger value="online">Online Now</TabsTrigger>
              <TabsTrigger value="leads">Team Leads</TabsTrigger>
              <TabsTrigger value="engineering">Engineering</TabsTrigger>
            </TabsList>
          </Tabs>

          {/* Filters */}
          <div className="flex flex-col lg:flex-row gap-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search members, technologies, projects..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={roleFilter} onValueChange={setRoleFilter}>
              <SelectTrigger className="w-full lg:w-[150px]">
                <SelectValue placeholder="Role" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Roles</SelectItem>
                <SelectItem value="architect">Architect</SelectItem>
                <SelectItem value="tech_lead">Tech Lead</SelectItem>
                <SelectItem value="senior_engineer">Senior Engineer</SelectItem>
                <SelectItem value="platform_engineer">Platform Engineer</SelectItem>
                <SelectItem value="devops_engineer">DevOps Engineer</SelectItem>
                <SelectItem value="qa_engineer">QA Engineer</SelectItem>
                <SelectItem value="product_manager">Product Manager</SelectItem>
              </SelectContent>
            </Select>
            <Select value={levelFilter} onValueChange={setLevelFilter}>
              <SelectTrigger className="w-full lg:w-[120px]">
                <SelectValue placeholder="Level" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Levels</SelectItem>
                <SelectItem value="junior">Junior</SelectItem>
                <SelectItem value="mid">Mid</SelectItem>
                <SelectItem value="senior">Senior</SelectItem>
                <SelectItem value="staff">Staff</SelectItem>
                <SelectItem value="principal">Principal</SelectItem>
              </SelectContent>
            </Select>
            <Select value={departmentFilter} onValueChange={setDepartmentFilter}>
              <SelectTrigger className="w-full lg:w-[130px]">
                <SelectValue placeholder="Department" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Departments</SelectItem>
                <SelectItem value="engineering">Engineering</SelectItem>
                <SelectItem value="devops">DevOps</SelectItem>
                <SelectItem value="qa">QA</SelectItem>
                <SelectItem value="product">Product</SelectItem>
                <SelectItem value="design">Design</SelectItem>
              </SelectContent>
            </Select>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full lg:w-[130px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="on_leave">On Leave</SelectItem>
                <SelectItem value="busy">Busy</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Platform Team Table */}
          <div className="rounded-md border overflow-hidden">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="min-w-[250px]">Team Member</TableHead>
                    <TableHead className="min-w-[140px]">Role & Level</TableHead>
                    <TableHead className="min-w-[120px]">Status</TableHead>
                    <TableHead className="min-w-[150px] hidden lg:table-cell">Technologies</TableHead>
                    <TableHead className="min-w-[150px] hidden xl:table-cell">Current Projects</TableHead>
                    <TableHead className="min-w-[120px] hidden lg:table-cell">Performance</TableHead>
                    <TableHead className="min-w-[100px] hidden xl:table-cell">Activity</TableHead>
                    <TableHead className="text-right min-w-[80px]">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredTeam.map((member) => (
                    <TableRow key={member.id} className="hover:bg-muted/50">
                      <TableCell className="min-w-[250px]">
                        <div className="flex items-center gap-3">
                          <div className="relative">
                            <UserAvatar 
                              user={{
                                first_name: member.firstName,
                                last_name: member.lastName,
                                email: member.email,
                                avatar_url: member.avatar
                              }}
                              className="h-10 w-10"
                            />
                            <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white ${
                              member.isOnline ? 'bg-green-500' : 'bg-gray-400'
                            }`} />
                          </div>
                          <div>
                            <div className="font-semibold">{member.firstName} {member.lastName}</div>
                            <div className="text-sm text-muted-foreground">{member.email}</div>
                            <div className="text-xs text-muted-foreground flex items-center gap-2">
                              <span>{member.location}</span>
                              {member.githubUsername && (
                                <Badge variant="outline" className="text-xs px-1 py-0">
                                  <GitBranch className="h-2 w-2 mr-1" />
                                  {member.githubUsername}
                                </Badge>
                              )}
                            </div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[140px]">
                        <div className="space-y-1">
                          {getRoleBadge(member.role)}
                          <div className="flex gap-1">
                            {getLevelBadge(member.level)}
                            {getDepartmentBadge(member.department)}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[120px]">
                        {getStatusBadge(member.status, member.isOnline)}
                        <div className="text-xs text-muted-foreground mt-1">
                          Last: {formatRelativeTime(member.lastActivity)}
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[150px] hidden lg:table-cell">
                        <div className="space-y-1">
                          <div className="flex flex-wrap gap-1">
                            {member.technologies.slice(0, 3).map(tech => (
                              <Badge key={tech} variant="secondary" className="text-xs">{tech}</Badge>
                            ))}
                            {member.technologies.length > 3 && (
                              <Badge variant="outline" className="text-xs">+{member.technologies.length - 3}</Badge>
                            )}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {member.specializations.slice(0, 2).join(', ')}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[150px] hidden xl:table-cell">
                        <div className="space-y-1">
                          {member.currentProjects.slice(0, 2).map(project => (
                            <div key={project} className="text-xs bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-300 px-2 py-1 rounded">
                              {project}
                            </div>
                          ))}
                          {member.currentProjects.length > 2 && (
                            <div className="text-xs text-muted-foreground">
                              +{member.currentProjects.length - 2} more
                            </div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[120px] hidden lg:table-cell">
                        <div className="space-y-1">
                          <div className="flex items-center gap-1 text-sm">
                            <Star className="h-3 w-3 text-yellow-500" />
                            <span>{member.performanceRating}/5</span>
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {member.totalCommits} commits
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {member.bugsFixed} bugs fixed
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[100px] hidden xl:table-cell">
                        <div className="text-sm space-y-1">
                          <div className="text-xs text-muted-foreground">
                            Last commit: {formatRelativeTime(member.lastCommit)}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {member.codeReviews} reviews
                          </div>
                          <div className="text-xs">
                            {member.timezone}
                          </div>
                        </div>
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
                            <DropdownMenuLabel>Member Actions</DropdownMenuLabel>
                            <DropdownMenuItem>
                              <Eye className="mr-2 h-4 w-4" />
                              View Profile
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <GitBranch className="mr-2 h-4 w-4" />
                              GitHub Activity
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Layers className="mr-2 h-4 w-4" />
                              View Projects
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Edit className="mr-2 h-4 w-4" />
                              Edit Details
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem>
                              <Settings className="mr-2 h-4 w-4" />
                              Permissions
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Calendar className="mr-2 h-4 w-4" />
                              Schedule
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            {member.status === 'inactive' ? (
                              <DropdownMenuItem className="text-green-600">
                                <UserCheck className="mr-2 h-4 w-4" />
                                Activate Member
                              </DropdownMenuItem>
                            ) : (
                              <DropdownMenuItem className="text-yellow-600">
                                <UserMinus className="mr-2 h-4 w-4" />
                                Deactivate
                              </DropdownMenuItem>
                            )}
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
          {filteredTeam.length === 0 && (
            <div className="text-center py-12">
              <Code className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No team members found</h3>
              <p className="text-muted-foreground mb-4">
                {searchTerm || roleFilter !== "all" || statusFilter !== "all" || levelFilter !== "all" || departmentFilter !== "all"
                  ? "Try adjusting your search or filters"
                  : "No platform team members have been added yet"}
              </p>
              {(!searchTerm && roleFilter === "all" && statusFilter === "all" && levelFilter === "all" && departmentFilter === "all") && (
                <Button>
                  <UserPlus className="h-4 w-4 mr-2" />
                  Add Team Member
                </Button>
              )}
            </div>
          )}

          {/* Results Summary */}
          {filteredTeam.length > 0 && (
            <div className="flex items-center justify-between pt-4 border-t">
              <div className="text-sm text-muted-foreground">
                Showing {filteredTeam.length} of {platformTeam.length} team members
              </div>
              <div className="flex gap-4 text-sm text-muted-foreground">
                <span>Total Commits: {filteredTeam.reduce((sum, m) => sum + m.totalCommits, 0).toLocaleString()}</span>
                <span>Avg Rating: {(filteredTeam.reduce((sum, m) => sum + m.performanceRating, 0) / filteredTeam.length).toFixed(1)}/5</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
