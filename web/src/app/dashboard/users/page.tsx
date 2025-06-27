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
  Users,
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
  UserPlus,
  UserMinus
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

// User interface for platform user management
interface PlatformUser {
  id: string
  firstName: string
  lastName: string
  email: string
  role: 'super_admin' | 'org_admin' | 'team_lead' | 'sales_rep' | 'support' | 'user'
  status: 'active' | 'inactive' | 'suspended' | 'pending'
  organizationId?: string
  organizationName?: string
  teamId?: string
  teamName?: string
  lastLogin: string
  createdAt: string
  loginCount: number
  permissions: string[]
  phone?: string
  department?: string
  location?: string
  avatar?: string
}

// Mock data for platform users
const mockUsers: PlatformUser[] = [
  {
    id: 'user_1',
    firstName: 'John',
    lastName: 'Smith',
    email: 'john.smith@acme.com',
    role: 'org_admin',
    status: 'active',
    organizationId: 'org_1',
    organizationName: 'Acme Corporation',
    teamId: 'team_1',
    teamName: 'Sales Team Alpha',
    lastLogin: '2025-06-27T14:30:00Z',
    createdAt: '2024-01-15T10:30:00Z',
    loginCount: 245,
    permissions: ['manage_organization', 'manage_teams', 'view_reports'],
    phone: '+1-555-0123',
    department: 'Sales',
    location: 'New York, NY'
  },
  {
    id: 'user_2',
    firstName: 'Sarah',
    lastName: 'Johnson',
    email: 'sarah@globalsolutions.com',
    role: 'org_admin',
    status: 'active',
    organizationId: 'org_2',
    organizationName: 'Global Solutions Ltd',
    teamId: 'team_3',
    teamName: 'European Division',
    lastLogin: '2025-06-27T12:15:00Z',
    createdAt: '2024-03-20T09:15:00Z',
    loginCount: 189,
    permissions: ['manage_organization', 'manage_teams', 'view_reports'],
    phone: '+44-20-7946-0958',
    department: 'Operations',
    location: 'London, UK'
  },
  {
    id: 'user_3',
    firstName: 'Mike',
    lastName: 'Chen',
    email: 'mike@techstart.co',
    role: 'team_lead',
    status: 'active',
    organizationId: 'org_3',
    organizationName: 'TechStart Inc',
    teamId: 'team_4',
    teamName: 'Startup Division',
    lastLogin: '2025-06-26T16:45:00Z',
    createdAt: '2024-06-10T16:20:00Z',
    loginCount: 67,
    permissions: ['manage_team', 'view_reports'],
    phone: '+1-415-555-0987',
    department: 'Product',
    location: 'San Francisco, CA'
  },
  {
    id: 'user_4',
    firstName: 'Emily',
    lastName: 'Rodriguez',
    email: 'emily@salesoptimizer.com',
    role: 'super_admin',
    status: 'active',
    lastLogin: '2025-06-27T15:00:00Z',
    createdAt: '2023-10-01T08:00:00Z',
    loginCount: 892,
    permissions: ['platform_admin', 'manage_organizations', 'system_settings'],
    phone: '+1-555-0001',
    department: 'Platform',
    location: 'Seattle, WA'
  },
  {
    id: 'user_5',
    firstName: 'David',
    lastName: 'Kim',
    email: 'david@acme.com',
    role: 'sales_rep',
    status: 'active',
    organizationId: 'org_1',
    organizationName: 'Acme Corporation',
    teamId: 'team_1',
    teamName: 'Sales Team Alpha',
    lastLogin: '2025-06-27T10:20:00Z',
    createdAt: '2024-02-12T11:00:00Z',
    loginCount: 156,
    permissions: ['manage_leads', 'view_reports'],
    phone: '+1-555-0456',
    department: 'Sales',
    location: 'Los Angeles, CA'
  },
  {
    id: 'user_6',
    firstName: 'Lisa',
    lastName: 'Brown',
    email: 'lisa@enterprise.com',
    role: 'org_admin',
    status: 'suspended',
    organizationId: 'org_4',
    organizationName: 'Enterprise Corp',
    teamId: 'team_5',
    teamName: 'Legacy Accounts',
    lastLogin: '2025-06-18T14:30:00Z',
    createdAt: '2023-11-05T12:45:00Z',
    loginCount: 234,
    permissions: ['manage_organization', 'manage_teams'],
    phone: '+1-555-0789',
    department: 'Finance',
    location: 'Chicago, IL'
  },
  {
    id: 'user_7',
    firstName: 'Alex',
    lastName: 'Rodriguez',
    email: 'alex@startuphub.io',
    role: 'team_lead',
    status: 'active',
    organizationId: 'org_5',
    organizationName: 'StartupHub',
    lastLogin: '2025-06-27T09:45:00Z',
    createdAt: '2024-05-12T14:30:00Z',
    loginCount: 78,
    permissions: ['manage_team', 'view_reports'],
    phone: '+1-555-0321',
    department: 'Business Development',
    location: 'Austin, TX'
  }
]

const getRoleBadge = (role: string) => {
  switch (role) {
    case 'super_admin':
      return <Badge className="bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
        <Crown className="h-3 w-3 mr-1" />
        Super Admin
      </Badge>
    case 'org_admin':
      return <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
        <Shield className="h-3 w-3 mr-1" />
        Org Admin
      </Badge>
    case 'team_lead':
      return <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
        <Users className="h-3 w-3 mr-1" />
        Team Lead
      </Badge>
    case 'sales_rep':
      return <Badge className="bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200">
        Sales Rep
      </Badge>
    case 'support':
      return <Badge className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
        Support
      </Badge>
    case 'user':
      return <Badge variant="secondary">User</Badge>
    default:
      return <Badge variant="outline">{role}</Badge>
  }
}

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'active':
      return <Badge variant="default" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Active</Badge>
    case 'inactive':
      return <Badge variant="secondary" className="bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200">Inactive</Badge>
    case 'suspended':
      return <Badge variant="destructive" className="bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">Suspended</Badge>
    case 'pending':
      return <Badge variant="outline" className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">Pending</Badge>
    default:
      return <Badge variant="outline">{status}</Badge>
  }
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
  
  if (diffInDays > 7) return formatDate(dateString)
  if (diffInDays > 0) return `${diffInDays}d ago`
  if (diffInHours > 0) return `${diffInHours}h ago`
  return 'Just now'
}

export default function AllUsersPage() {
  const { user } = useAuth()
  const [searchTerm, setSearchTerm] = useState("")
  const [roleFilter, setRoleFilter] = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")
  const [organizationFilter, setOrganizationFilter] = useState("all")
  const [users, setUsers] = useState<PlatformUser[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState("all")

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setUsers(mockUsers)
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

  // Filter users based on search, filters, and active tab
  const filteredUsers = users.filter(u => {
    const matchesSearch = u.firstName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         u.lastName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         u.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         u.organizationName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         u.teamName?.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesRole = roleFilter === "all" || u.role === roleFilter
    const matchesStatus = statusFilter === "all" || u.status === statusFilter
    const matchesOrganization = organizationFilter === "all" || u.organizationId === organizationFilter
    
    // Tab filtering
    let matchesTab = true
    if (activeTab === "admins") {
      matchesTab = u.role === 'super_admin' || u.role === 'org_admin'
    } else if (activeTab === "team_leads") {
      matchesTab = u.role === 'team_lead'
    } else if (activeTab === "sales") {
      matchesTab = u.role === 'sales_rep'
    } else if (activeTab === "support") {
      matchesTab = u.role === 'support'
    }
    
    return matchesSearch && matchesRole && matchesStatus && matchesOrganization && matchesTab
  })

  // Get unique organizations and roles for filters
  const organizations = Array.from(new Set(users.filter(u => u.organizationId).map(u => ({ id: u.organizationId!, name: u.organizationName! }))
    .map(org => JSON.stringify(org))))
    .map(org => JSON.parse(org))
  
  const roles = Array.from(new Set(users.map(u => u.role)))

  // Calculate statistics
  const stats = {
    totalUsers: users.length,
    activeUsers: users.filter(u => u.status === 'active').length,
    adminUsers: users.filter(u => u.role === 'super_admin' || u.role === 'org_admin').length,
    suspendedUsers: users.filter(u => u.status === 'suspended').length,
    totalLogins: users.reduce((sum, u) => sum + u.loginCount, 0),
    recentLogins: users.filter(u => {
      const daysSinceLogin = Math.floor((Date.now() - new Date(u.lastLogin).getTime()) / (1000 * 60 * 60 * 24))
      return daysSinceLogin <= 7
    }).length
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
              <Users className="h-6 w-6 text-white" />
            </div>
            All Platform Users
          </h1>
          <p className="text-muted-foreground mt-2">
            Manage all users across the SalesOptimizer platform
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Users
          </Button>
          <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
            <UserPlus className="h-4 w-4 mr-2" />
            Invite User
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalUsers}</div>
            <p className="text-xs text-muted-foreground">
              {stats.activeUsers} active users
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Administrators</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.adminUsers}</div>
            <p className="text-xs text-muted-foreground">
              Platform & org admins
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Recent Activity</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.recentLogins}</div>
            <p className="text-xs text-muted-foreground">
              Logged in this week
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Issues</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.suspendedUsers}</div>
            <p className="text-xs text-muted-foreground">
              Suspended accounts
            </p>
          </CardContent>
        </Card>
      </div>

      {/* User Management */}
      <Card>
        <CardHeader>
          <CardTitle>User Directory</CardTitle>
          <CardDescription>
            Search, filter, and manage all platform users
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-6">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="all">All Users</TabsTrigger>
              <TabsTrigger value="admins">Admins</TabsTrigger>
              <TabsTrigger value="team_leads">Team Leads</TabsTrigger>
              <TabsTrigger value="sales">Sales Reps</TabsTrigger>
              <TabsTrigger value="support">Support</TabsTrigger>
            </TabsList>
          </Tabs>

          {/* Filters */}
          <div className="flex flex-col lg:flex-row gap-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search users, emails, organizations..."
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
                {roles.map(role => (
                  <SelectItem key={role} value={role}>
                    {role.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full lg:w-[150px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
                <SelectItem value="suspended">Suspended</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
              </SelectContent>
            </Select>
            <Select value={organizationFilter} onValueChange={setOrganizationFilter}>
              <SelectTrigger className="w-full lg:w-[200px]">
                <SelectValue placeholder="Organization" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Organizations</SelectItem>
                {organizations.map(org => (
                  <SelectItem key={org.id} value={org.id}>{org.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Users Table */}
          <div className="rounded-md border overflow-hidden">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="min-w-[250px]">User</TableHead>
                    <TableHead className="min-w-[120px]">Role</TableHead>
                    <TableHead className="min-w-[100px]">Status</TableHead>
                    <TableHead className="min-w-[200px] hidden lg:table-cell">Organization</TableHead>
                    <TableHead className="min-w-[150px] hidden xl:table-cell">Contact</TableHead>
                    <TableHead className="min-w-[120px] hidden lg:table-cell">Last Login</TableHead>
                    <TableHead className="min-w-[100px] hidden xl:table-cell">Login Count</TableHead>
                    <TableHead className="text-right min-w-[80px]">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredUsers.map((u) => (
                    <TableRow key={u.id} className="hover:bg-muted/50">
                      <TableCell className="min-w-[250px]">
                        <div className="flex items-center gap-3">
                          <UserAvatar 
                            user={{
                              first_name: u.firstName,
                              last_name: u.lastName,
                              email: u.email,
                              avatar_url: u.avatar
                            }}
                            className="h-10 w-10"
                          />
                          <div>
                            <div className="font-semibold">{u.firstName} {u.lastName}</div>
                            <div className="text-sm text-muted-foreground">{u.email}</div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[120px]">
                        {getRoleBadge(u.role)}
                      </TableCell>
                      <TableCell className="min-w-[100px]">
                        {getStatusBadge(u.status)}
                      </TableCell>
                      <TableCell className="min-w-[200px] hidden lg:table-cell">
                        {u.organizationName ? (
                          <div>
                            <div className="flex items-center gap-1">
                              <Building2 className="h-3 w-3 text-muted-foreground" />
                              <span className="font-medium">{u.organizationName}</span>
                            </div>
                            {u.teamName && (
                              <div className="text-sm text-muted-foreground">{u.teamName}</div>
                            )}
                          </div>
                        ) : (
                          <span className="text-muted-foreground">Platform User</span>
                        )}
                      </TableCell>
                      <TableCell className="min-w-[150px] hidden xl:table-cell">
                        <div className="space-y-1">
                          {u.phone && (
                            <div className="flex items-center gap-1 text-sm">
                              <Phone className="h-3 w-3 text-muted-foreground" />
                              <span>{u.phone}</span>
                            </div>
                          )}
                          {u.location && (
                            <div className="text-sm text-muted-foreground">{u.location}</div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[120px] hidden lg:table-cell">
                        <div className="flex items-center gap-1 text-sm">
                          <Clock className="h-3 w-3 text-muted-foreground" />
                          <span>{formatRelativeTime(u.lastLogin)}</span>
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[100px] hidden xl:table-cell">
                        <div className="text-sm font-medium">{u.loginCount}</div>
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
                            <DropdownMenuLabel>User Actions</DropdownMenuLabel>
                            <DropdownMenuItem>
                              <Eye className="mr-2 h-4 w-4" />
                              View Profile
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Edit className="mr-2 h-4 w-4" />
                              Edit User
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Settings className="mr-2 h-4 w-4" />
                              Permissions
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Mail className="mr-2 h-4 w-4" />
                              Send Message
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            {u.status === 'suspended' ? (
                              <DropdownMenuItem className="text-green-600">
                                <UserCheck className="mr-2 h-4 w-4" />
                                Reactivate User
                              </DropdownMenuItem>
                            ) : (
                              <DropdownMenuItem className="text-yellow-600">
                                <UserMinus className="mr-2 h-4 w-4" />
                                Suspend User
                              </DropdownMenuItem>
                            )}
                            <DropdownMenuSeparator />
                            <DropdownMenuItem className="text-red-600">
                              <Trash2 className="mr-2 h-4 w-4" />
                              Delete User
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
          {filteredUsers.length === 0 && (
            <div className="text-center py-12">
              <Users className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No users found</h3>
              <p className="text-muted-foreground mb-4">
                {searchTerm || roleFilter !== "all" || statusFilter !== "all" || organizationFilter !== "all"
                  ? "Try adjusting your search or filters"
                  : "No users have been added to the platform yet"}
              </p>
              {(!searchTerm && roleFilter === "all" && statusFilter === "all" && organizationFilter === "all") && (
                <Button>
                  <UserPlus className="h-4 w-4 mr-2" />
                  Invite First User
                </Button>
              )}
            </div>
          )}

          {/* Results Summary */}
          {filteredUsers.length > 0 && (
            <div className="flex items-center justify-between pt-4 border-t">
              <div className="text-sm text-muted-foreground">
                Showing {filteredUsers.length} of {users.length} users
              </div>
              <div className="text-sm text-muted-foreground">
                Total Logins: {filteredUsers.reduce((sum, u) => sum + u.loginCount, 0).toLocaleString()}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
