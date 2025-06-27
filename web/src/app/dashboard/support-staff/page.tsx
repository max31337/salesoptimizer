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
  Headphones,
  MessageSquare,
  BarChart3,
  Award,
  Timer,
  CheckCircle,
  XCircle
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

// Support Staff interface
interface SupportStaff {
  id: string
  firstName: string
  lastName: string
  email: string
  role: 'support' | 'support_lead' | 'support_manager'
  status: 'active' | 'inactive' | 'on_break' | 'offline'
  level: 'L1' | 'L2' | 'L3' | 'escalation'
  specializations: string[]
  languages: string[]
  shift: 'morning' | 'afternoon' | 'evening' | 'night' | 'weekend'
  timezone: string
  lastLogin: string
  createdAt: string
  totalTickets: number
  resolvedTickets: number
  avgResponseTime: number // in minutes
  avgResolutionTime: number // in hours
  customerRating: number // 1-5
  currentTickets: number
  phone?: string
  department?: string
  location?: string
  avatar?: string
  isOnline: boolean
  lastActivity: string
}

// Mock data for support staff
const mockSupportStaff: SupportStaff[] = [
  {
    id: 'support_1',
    firstName: 'Emma',
    lastName: 'Thompson',
    email: 'emma.thompson@salesoptimizer.com',
    role: 'support_manager',
    status: 'active',
    level: 'escalation',
    specializations: ['Technical Issues', 'Billing', 'Account Management', 'API Support'],
    languages: ['English', 'Spanish'],
    shift: 'morning',
    timezone: 'PST',
    lastLogin: '2025-06-27T14:30:00Z',
    createdAt: '2023-08-15T10:30:00Z',
    totalTickets: 1247,
    resolvedTickets: 1189,
    avgResponseTime: 12,
    avgResolutionTime: 4.2,
    customerRating: 4.8,
    currentTickets: 3,
    phone: '+1-555-0101',
    department: 'Customer Success',
    location: 'Seattle, WA',
    isOnline: true,
    lastActivity: '2025-06-27T15:25:00Z'
  },
  {
    id: 'support_2',
    firstName: 'Marcus',
    lastName: 'Johnson',
    email: 'marcus.johnson@salesoptimizer.com',
    role: 'support_lead',
    status: 'active',
    level: 'L3',
    specializations: ['Technical Issues', 'API Support', 'Integrations'],
    languages: ['English'],
    shift: 'afternoon',
    timezone: 'EST',
    lastLogin: '2025-06-27T13:15:00Z',
    createdAt: '2024-01-20T09:15:00Z',
    totalTickets: 892,
    resolvedTickets: 834,
    avgResponseTime: 8,
    avgResolutionTime: 2.8,
    customerRating: 4.6,
    currentTickets: 7,
    phone: '+1-555-0102',
    department: 'Technical Support',
    location: 'New York, NY',
    isOnline: true,
    lastActivity: '2025-06-27T15:10:00Z'
  },
  {
    id: 'support_3',
    firstName: 'Sofia',
    lastName: 'Garcia',
    email: 'sofia.garcia@salesoptimizer.com',
    role: 'support',
    status: 'active',
    level: 'L2',
    specializations: ['Billing', 'Account Management', 'General Support'],
    languages: ['English', 'Spanish', 'Portuguese'],
    shift: 'morning',
    timezone: 'MST',
    lastLogin: '2025-06-27T12:45:00Z',
    createdAt: '2024-03-12T14:20:00Z',
    totalTickets: 567,
    resolvedTickets: 523,
    avgResponseTime: 15,
    avgResolutionTime: 3.5,
    customerRating: 4.7,
    currentTickets: 5,
    phone: '+1-555-0103',
    department: 'Customer Success',
    location: 'Denver, CO',
    isOnline: true,
    lastActivity: '2025-06-27T15:00:00Z'
  },
  {
    id: 'support_4',
    firstName: 'James',
    lastName: 'Wilson',
    email: 'james.wilson@salesoptimizer.com',
    role: 'support',
    status: 'on_break',
    level: 'L1',
    specializations: ['General Support', 'Basic Technical'],
    languages: ['English'],
    shift: 'afternoon',
    timezone: 'PST',
    lastLogin: '2025-06-27T11:30:00Z',
    createdAt: '2024-05-08T16:45:00Z',
    totalTickets: 234,
    resolvedTickets: 201,
    avgResponseTime: 22,
    avgResolutionTime: 6.1,
    customerRating: 4.2,
    currentTickets: 2,
    phone: '+1-555-0104',
    department: 'Customer Success',
    location: 'Los Angeles, CA',
    isOnline: false,
    lastActivity: '2025-06-27T14:15:00Z'
  },
  {
    id: 'support_5',
    firstName: 'Priya',
    lastName: 'Patel',
    email: 'priya.patel@salesoptimizer.com',
    role: 'support',
    status: 'active',
    level: 'L2',
    specializations: ['Technical Issues', 'Data Migration', 'Training'],
    languages: ['English', 'Hindi'],
    shift: 'evening',
    timezone: 'IST',
    lastLogin: '2025-06-27T09:20:00Z',
    createdAt: '2024-02-28T11:00:00Z',
    totalTickets: 445,
    resolvedTickets: 412,
    avgResponseTime: 18,
    avgResolutionTime: 4.7,
    customerRating: 4.5,
    currentTickets: 6,
    phone: '+91-98765-43210',
    department: 'Technical Support',
    location: 'Bangalore, India',
    isOnline: true,
    lastActivity: '2025-06-27T14:45:00Z'
  },
  {
    id: 'support_6',
    firstName: 'Alex',
    lastName: 'Kim',
    email: 'alex.kim@salesoptimizer.com',
    role: 'support',
    status: 'offline',
    level: 'L1',
    specializations: ['General Support', 'Account Setup'],
    languages: ['English', 'Korean'],
    shift: 'night',
    timezone: 'KST',
    lastLogin: '2025-06-26T22:15:00Z',
    createdAt: '2024-04-15T13:30:00Z',
    totalTickets: 156,
    resolvedTickets: 142,
    avgResponseTime: 25,
    avgResolutionTime: 5.8,
    customerRating: 4.3,
    currentTickets: 0,
    phone: '+82-10-1234-5678',
    department: 'Customer Success',
    location: 'Seoul, South Korea',
    isOnline: false,
    lastActivity: '2025-06-26T22:30:00Z'
  }
]

const getRoleBadge = (role: string) => {
  switch (role) {
    case 'support_manager':
      return <Badge className="bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
        <Crown className="h-3 w-3 mr-1" />
        Support Manager
      </Badge>
    case 'support_lead':
      return <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
        <Shield className="h-3 w-3 mr-1" />
        Support Lead
      </Badge>
    case 'support':
      return <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
        <Headphones className="h-3 w-3 mr-1" />
        Support Agent
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
    case 'on_break':
      return <Badge variant="outline" className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">On Break</Badge>
    case 'offline':
      return <Badge variant="secondary" className="bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200">Offline</Badge>
    case 'inactive':
      return <Badge variant="destructive" className="bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">Inactive</Badge>
    default:
      return <Badge variant="outline">{status}</Badge>
  }
}

const getLevelBadge = (level: string) => {
  const colors = {
    'L1': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'L2': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
    'L3': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    'escalation': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
  }
  
  return (
    <Badge className={colors[level as keyof typeof colors] || 'bg-gray-100 text-gray-800'}>
      {level === 'escalation' ? 'Escalation' : level}
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

const formatResponseTime = (minutes: number) => {
  if (minutes < 60) return `${minutes}m`
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`
}

export default function SupportStaffPage() {
  const { user } = useAuth()
  const [searchTerm, setSearchTerm] = useState("")
  const [roleFilter, setRoleFilter] = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")
  const [levelFilter, setLevelFilter] = useState("all")
  const [shiftFilter, setShiftFilter] = useState("all")
  const [supportStaff, setSupportStaff] = useState<SupportStaff[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState("all")

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setSupportStaff(mockSupportStaff)
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

  // Filter support staff based on search, filters, and active tab
  const filteredStaff = supportStaff.filter(s => {
    const matchesSearch = s.firstName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         s.lastName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         s.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         s.specializations.some(spec => spec.toLowerCase().includes(searchTerm.toLowerCase())) ||
                         s.languages.some(lang => lang.toLowerCase().includes(searchTerm.toLowerCase()))
    
    const matchesRole = roleFilter === "all" || s.role === roleFilter
    const matchesStatus = statusFilter === "all" || s.status === statusFilter
    const matchesLevel = levelFilter === "all" || s.level === levelFilter
    const matchesShift = shiftFilter === "all" || s.shift === shiftFilter
    
    // Tab filtering
    let matchesTab = true
    if (activeTab === "online") {
      matchesTab = s.isOnline && s.status === 'active'
    } else if (activeTab === "leads") {
      matchesTab = s.role === 'support_lead' || s.role === 'support_manager'
    } else if (activeTab === "l3") {
      matchesTab = s.level === 'L3' || s.level === 'escalation'
    }
    
    return matchesSearch && matchesRole && matchesStatus && matchesLevel && matchesShift && matchesTab
  })

  // Calculate statistics
  const stats = {
    totalStaff: supportStaff.length,
    onlineStaff: supportStaff.filter(s => s.isOnline && s.status === 'active').length,
    totalTickets: supportStaff.reduce((sum, s) => sum + s.currentTickets, 0),
    avgRating: Number((supportStaff.reduce((sum, s) => sum + s.customerRating, 0) / supportStaff.length).toFixed(1)),
    avgResponseTime: Math.round(supportStaff.reduce((sum, s) => sum + s.avgResponseTime, 0) / supportStaff.length),
    resolutionRate: Math.round((supportStaff.reduce((sum, s) => sum + (s.resolvedTickets / s.totalTickets * 100), 0) / supportStaff.length))
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
              <Headphones className="h-6 w-6 text-white" />
            </div>
            Support Staff Management
          </h1>
          <p className="text-muted-foreground mt-2">
            Manage support team members and monitor performance metrics
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
          <Button className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700">
            <UserPlus className="h-4 w-4 mr-2" />
            Add Support Agent
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Support Staff</CardTitle>
            <Headphones className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalStaff}</div>
            <p className="text-xs text-muted-foreground">
              {stats.onlineStaff} currently online
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Tickets</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalTickets}</div>
            <p className="text-xs text-muted-foreground">
              Currently being handled
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
            <Timer className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatResponseTime(stats.avgResponseTime)}</div>
            <p className="text-xs text-muted-foreground">
              First response to tickets
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Customer Rating</CardTitle>
            <Award className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.avgRating}/5</div>
            <p className="text-xs text-muted-foreground">
              Average satisfaction score
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Support Staff Management */}
      <Card>
        <CardHeader>
          <CardTitle>Support Team Directory</CardTitle>
          <CardDescription>
            Monitor performance, workload, and manage support staff assignments
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-6">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="all">All Staff</TabsTrigger>
              <TabsTrigger value="online">Online Now</TabsTrigger>
              <TabsTrigger value="leads">Team Leads</TabsTrigger>
              <TabsTrigger value="l3">Senior (L3+)</TabsTrigger>
            </TabsList>
          </Tabs>

          {/* Filters */}
          <div className="flex flex-col lg:flex-row gap-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search agents, specializations, languages..."
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
                <SelectItem value="support_manager">Support Manager</SelectItem>
                <SelectItem value="support_lead">Support Lead</SelectItem>
                <SelectItem value="support">Support Agent</SelectItem>
              </SelectContent>
            </Select>
            <Select value={levelFilter} onValueChange={setLevelFilter}>
              <SelectTrigger className="w-full lg:w-[120px]">
                <SelectValue placeholder="Level" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Levels</SelectItem>
                <SelectItem value="L1">Level 1</SelectItem>
                <SelectItem value="L2">Level 2</SelectItem>
                <SelectItem value="L3">Level 3</SelectItem>
                <SelectItem value="escalation">Escalation</SelectItem>
              </SelectContent>
            </Select>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full lg:w-[130px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="on_break">On Break</SelectItem>
                <SelectItem value="offline">Offline</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
              </SelectContent>
            </Select>
            <Select value={shiftFilter} onValueChange={setShiftFilter}>
              <SelectTrigger className="w-full lg:w-[130px]">
                <SelectValue placeholder="Shift" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Shifts</SelectItem>
                <SelectItem value="morning">Morning</SelectItem>
                <SelectItem value="afternoon">Afternoon</SelectItem>
                <SelectItem value="evening">Evening</SelectItem>
                <SelectItem value="night">Night</SelectItem>
                <SelectItem value="weekend">Weekend</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Support Staff Table */}
          <div className="rounded-md border overflow-hidden">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="min-w-[250px]">Agent</TableHead>
                    <TableHead className="min-w-[120px]">Role & Level</TableHead>
                    <TableHead className="min-w-[120px]">Status</TableHead>
                    <TableHead className="min-w-[150px] hidden lg:table-cell">Specializations</TableHead>
                    <TableHead className="min-w-[120px] hidden xl:table-cell">Current Load</TableHead>
                    <TableHead className="min-w-[120px] hidden lg:table-cell">Performance</TableHead>
                    <TableHead className="min-w-[100px] hidden xl:table-cell">Shift</TableHead>
                    <TableHead className="text-right min-w-[80px]">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredStaff.map((agent) => (
                    <TableRow key={agent.id} className="hover:bg-muted/50">
                      <TableCell className="min-w-[250px]">
                        <div className="flex items-center gap-3">
                          <div className="relative">
                            <UserAvatar 
                              user={{
                                first_name: agent.firstName,
                                last_name: agent.lastName,
                                email: agent.email,
                                avatar_url: agent.avatar
                              }}
                              className="h-10 w-10"
                            />
                            <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white ${
                              agent.isOnline ? 'bg-green-500' : 'bg-gray-400'
                            }`} />
                          </div>
                          <div>
                            <div className="font-semibold">{agent.firstName} {agent.lastName}</div>
                            <div className="text-sm text-muted-foreground">{agent.email}</div>
                            <div className="text-xs text-muted-foreground">{agent.location}</div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[120px]">
                        <div className="space-y-1">
                          {getRoleBadge(agent.role)}
                          {getLevelBadge(agent.level)}
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[120px]">
                        {getStatusBadge(agent.status, agent.isOnline)}
                        <div className="text-xs text-muted-foreground mt-1">
                          Last: {formatRelativeTime(agent.lastActivity)}
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[150px] hidden lg:table-cell">
                        <div className="space-y-1">
                          <div className="flex flex-wrap gap-1">
                            {agent.specializations.slice(0, 2).map(spec => (
                              <Badge key={spec} variant="secondary" className="text-xs">{spec}</Badge>
                            ))}
                            {agent.specializations.length > 2 && (
                              <Badge variant="outline" className="text-xs">+{agent.specializations.length - 2}</Badge>
                            )}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {agent.languages.join(', ')}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[120px] hidden xl:table-cell">
                        <div className="space-y-1">
                          <div className="text-sm font-medium">{agent.currentTickets} tickets</div>
                          <div className="text-xs text-muted-foreground">
                            {agent.totalTickets} total
                          </div>
                          <div className="text-xs">
                            {Math.round((agent.resolvedTickets / agent.totalTickets) * 100)}% resolved
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[120px] hidden lg:table-cell">
                        <div className="space-y-1">
                          <div className="flex items-center gap-1 text-sm">
                            <Award className="h-3 w-3 text-yellow-500" />
                            <span>{agent.customerRating}/5</span>
                          </div>
                          <div className="text-xs text-muted-foreground">
                            Avg: {formatResponseTime(agent.avgResponseTime)}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {agent.avgResolutionTime}h resolution
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[100px] hidden xl:table-cell">
                        <div className="text-sm">
                          <div className="font-medium capitalize">{agent.shift}</div>
                          <div className="text-xs text-muted-foreground">{agent.timezone}</div>
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
                            <DropdownMenuLabel>Agent Actions</DropdownMenuLabel>
                            <DropdownMenuItem>
                              <Eye className="mr-2 h-4 w-4" />
                              View Profile
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <BarChart3 className="mr-2 h-4 w-4" />
                              Performance
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <MessageSquare className="mr-2 h-4 w-4" />
                              View Tickets
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Edit className="mr-2 h-4 w-4" />
                              Edit Details
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem>
                              <Settings className="mr-2 h-4 w-4" />
                              Assignments
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Calendar className="mr-2 h-4 w-4" />
                              Schedule
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            {agent.status === 'inactive' ? (
                              <DropdownMenuItem className="text-green-600">
                                <UserCheck className="mr-2 h-4 w-4" />
                                Activate Agent
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
          {filteredStaff.length === 0 && (
            <div className="text-center py-12">
              <Headphones className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No support staff found</h3>
              <p className="text-muted-foreground mb-4">
                {searchTerm || roleFilter !== "all" || statusFilter !== "all" || levelFilter !== "all" || shiftFilter !== "all"
                  ? "Try adjusting your search or filters"
                  : "No support staff have been added yet"}
              </p>
              {(!searchTerm && roleFilter === "all" && statusFilter === "all" && levelFilter === "all" && shiftFilter === "all") && (
                <Button>
                  <UserPlus className="h-4 w-4 mr-2" />
                  Add Support Agent
                </Button>
              )}
            </div>
          )}

          {/* Results Summary */}
          {filteredStaff.length > 0 && (
            <div className="flex items-center justify-between pt-4 border-t">
              <div className="text-sm text-muted-foreground">
                Showing {filteredStaff.length} of {supportStaff.length} support staff
              </div>
              <div className="flex gap-4 text-sm text-muted-foreground">
                <span>Active Tickets: {filteredStaff.reduce((sum, s) => sum + s.currentTickets, 0)}</span>
                <span>Avg Rating: {(filteredStaff.reduce((sum, s) => sum + s.customerRating, 0) / filteredStaff.length).toFixed(1)}/5</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
