"use client"

import { useState, useEffect } from "react"
import { useAuth } from "@/features/auth/hooks/useAuth"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { 
  Building2,
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
  Download,
  Settings,
  Trash2,
  CreditCard,
  Globe
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

// Client Organization interface for super admin management
interface ClientOrganization {
  id: string
  name: string
  slug: string
  status: 'active' | 'trial' | 'suspended' | 'inactive'
  subscriptionTier: 'basic' | 'pro' | 'enterprise' | 'custom'
  userCount: number
  teamCount: number
  adminName: string
  adminEmail: string
  createdAt: string
  lastActivity: string
  monthlyRevenue: number
  growth: number
  region: string
  industry: string
  billingStatus: 'current' | 'overdue' | 'cancelled'
  website?: string
}

// Mock data for client organizations registered on the platform
const mockClientOrganizations: ClientOrganization[] = [
  {
    id: 'org_1',
    name: 'Acme Corporation',
    slug: 'acme-corp',
    status: 'active',
    subscriptionTier: 'enterprise',
    userCount: 247,
    teamCount: 12,
    adminName: 'John Smith',
    adminEmail: 'john.smith@acme.com',
    createdAt: '2024-01-15T10:30:00Z',
    lastActivity: '2025-06-27T14:22:00Z',
    monthlyRevenue: 12450,
    growth: 15.2,
    region: 'North America',
    industry: 'Technology',
    billingStatus: 'current',
    website: 'https://acme.com'
  },
  {
    id: 'org_2',
    name: 'Global Solutions Ltd',
    slug: 'global-solutions',
    status: 'active',
    subscriptionTier: 'pro',
    userCount: 89,
    teamCount: 6,
    adminName: 'Sarah Johnson',
    adminEmail: 'sarah@globalsolutions.com',
    createdAt: '2024-03-20T09:15:00Z',
    lastActivity: '2025-06-27T11:45:00Z',
    monthlyRevenue: 4250,
    growth: 8.7,
    region: 'Europe',
    industry: 'Consulting',
    billingStatus: 'current',
    website: 'https://globalsolutions.com'
  },
  {
    id: 'org_3',
    name: 'TechStart Inc',
    slug: 'techstart',
    status: 'trial',
    subscriptionTier: 'basic',
    userCount: 15,
    teamCount: 2,
    adminName: 'Mike Chen',
    adminEmail: 'mike@techstart.co',
    createdAt: '2024-06-10T16:20:00Z',
    lastActivity: '2025-06-26T09:30:00Z',
    monthlyRevenue: 0,
    growth: 0,
    region: 'Asia Pacific',
    industry: 'Technology',
    billingStatus: 'current',
    website: 'https://techstart.co'
  },
  {
    id: 'org_4',
    name: 'Enterprise Corp',
    slug: 'enterprise-corp',
    status: 'suspended',
    subscriptionTier: 'enterprise',
    userCount: 156,
    teamCount: 8,
    adminName: 'Lisa Brown',
    adminEmail: 'lisa@enterprise.com',
    createdAt: '2023-11-05T12:45:00Z',
    lastActivity: '2025-06-20T16:10:00Z',
    monthlyRevenue: 8900,
    growth: -5.2,
    region: 'North America',
    industry: 'Finance',
    billingStatus: 'overdue',
    website: 'https://enterprise.com'
  },
  {
    id: 'org_5',
    name: 'StartupHub',
    slug: 'startuphub',
    status: 'active',
    subscriptionTier: 'basic',
    userCount: 32,
    teamCount: 3,
    adminName: 'Alex Rodriguez',
    adminEmail: 'alex@startuphub.io',
    createdAt: '2024-05-12T14:30:00Z',
    lastActivity: '2025-06-27T10:15:00Z',
    monthlyRevenue: 890,
    growth: 22.1,
    region: 'North America',
    industry: 'Software',
    billingStatus: 'current',
    website: 'https://startuphub.io'
  }
]

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'active':
      return <Badge variant="default" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Active</Badge>
    case 'trial':
      return <Badge variant="secondary" className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">Trial</Badge>
    case 'suspended':
      return <Badge variant="destructive" className="bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">Suspended</Badge>
    case 'inactive':
      return <Badge variant="outline" className="text-gray-600">Inactive</Badge>
    default:
      return <Badge variant="outline">{status}</Badge>
  }
}

const getTierBadge = (tier: string) => {
  switch (tier) {
    case 'enterprise':
      return <Badge className="bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">Enterprise</Badge>
    case 'pro':
      return <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">Pro</Badge>
    case 'basic':
      return <Badge className="bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200">Basic</Badge>
    case 'custom':
      return <Badge className="bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200">Custom</Badge>
    default:
      return <Badge variant="outline">{tier}</Badge>
  }
}

const getBillingStatusBadge = (status: string) => {
  switch (status) {
    case 'current':
      return <Badge variant="default" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Current</Badge>
    case 'overdue':
      return <Badge variant="destructive" className="bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">Overdue</Badge>
    case 'cancelled':
      return <Badge variant="outline" className="text-gray-600">Cancelled</Badge>
    default:
      return <Badge variant="outline">{status}</Badge>
  }
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
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

export default function AllOrganizationsPage() {
  const { user } = useAuth()
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [tierFilter, setTierFilter] = useState("all")
  const [regionFilter, setRegionFilter] = useState("all")
  const [organizations, setOrganizations] = useState<ClientOrganization[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setOrganizations(mockClientOrganizations)
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

  // Filter organizations based on search and filters
  const filteredOrganizations = organizations.filter(org => {
    const matchesSearch = org.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         org.adminName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         org.adminEmail.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         org.industry.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "all" || org.status === statusFilter
    const matchesTier = tierFilter === "all" || org.subscriptionTier === tierFilter
    const matchesRegion = regionFilter === "all" || org.region === regionFilter
    
    return matchesSearch && matchesStatus && matchesTier && matchesRegion
  })

  // Get unique regions for filter
  const regions = Array.from(new Set(organizations.map(org => org.region)))

  // Calculate statistics
  const stats = {
    totalOrganizations: organizations.length,
    activeOrganizations: organizations.filter(org => org.status === 'active').length,
    trialOrganizations: organizations.filter(org => org.status === 'trial').length,
    totalUsers: organizations.reduce((sum, org) => sum + org.userCount, 0),
    totalRevenue: organizations.reduce((sum, org) => sum + org.monthlyRevenue, 0),
    avgGrowth: organizations.length > 0 ? organizations.reduce((sum, org) => sum + org.growth, 0) / organizations.length : 0
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
              <Building2 className="h-6 w-6 text-white" />
            </div>
            All Organizations
          </h1>
          <p className="text-muted-foreground mt-2">
            Manage all client organizations registered on the SalesOptimizer platform
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Data
          </Button>
          <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
            <Plus className="h-4 w-4 mr-2" />
            Add Organization
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Organizations</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalOrganizations}</div>
            <p className="text-xs text-muted-foreground">
              {stats.activeOrganizations} active, {stats.trialOrganizations} on trial
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalUsers.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              Across all organizations
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Monthly Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(stats.totalRevenue)}</div>
            <p className="text-xs text-muted-foreground">
              +{stats.avgGrowth.toFixed(1)}% average growth
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Platform Health</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">99.2%</div>
            <p className="text-xs text-muted-foreground">
              Uptime this month
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle>Organizations Directory</CardTitle>
          <CardDescription>
            Search, filter, and manage all client organizations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col lg:flex-row gap-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search organizations, admins, industries..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full lg:w-[150px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="trial">Trial</SelectItem>
                <SelectItem value="suspended">Suspended</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
              </SelectContent>
            </Select>
            <Select value={tierFilter} onValueChange={setTierFilter}>
              <SelectTrigger className="w-full lg:w-[150px]">
                <SelectValue placeholder="Tier" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Tiers</SelectItem>
                <SelectItem value="basic">Basic</SelectItem>
                <SelectItem value="pro">Pro</SelectItem>
                <SelectItem value="enterprise">Enterprise</SelectItem>
                <SelectItem value="custom">Custom</SelectItem>
              </SelectContent>
            </Select>
            <Select value={regionFilter} onValueChange={setRegionFilter}>
              <SelectTrigger className="w-full lg:w-[150px]">
                <SelectValue placeholder="Region" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Regions</SelectItem>
                {regions.map(region => (
                  <SelectItem key={region} value={region}>{region}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Organizations Table */}
          <div className="rounded-md border overflow-hidden">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="min-w-[250px]">Organization</TableHead>
                    <TableHead className="min-w-[180px]">Administrator</TableHead>
                    <TableHead className="min-w-[120px]">Status</TableHead>
                    <TableHead className="min-w-[100px]">Subscription</TableHead>
                    <TableHead className="min-w-[100px]">Users/Teams</TableHead>
                    <TableHead className="min-w-[120px]">Revenue</TableHead>
                    <TableHead className="min-w-[100px] hidden lg:table-cell">Industry</TableHead>
                    <TableHead className="min-w-[100px] hidden xl:table-cell">Last Active</TableHead>
                    <TableHead className="text-right min-w-[80px]">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredOrganizations.map((org) => (
                    <TableRow key={org.id} className="hover:bg-muted/50">
                      <TableCell className="min-w-[250px]">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <div className="w-8 h-8 bg-gradient-to-r from-blue-100 to-purple-100 rounded-lg flex items-center justify-center">
                              <Building2 className="h-4 w-4 text-blue-600" />
                            </div>
                            <div>
                              <div className="font-semibold">{org.name}</div>
                              <div className="text-sm text-muted-foreground flex items-center gap-1">
                                <Globe className="h-3 w-3" />
                                {org.slug}
                              </div>
                            </div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[180px]">
                        <div>
                          <div className="font-medium">{org.adminName}</div>
                          <div className="text-sm text-muted-foreground">{org.adminEmail}</div>
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[120px]">
                        <div className="space-y-1">
                          {getStatusBadge(org.status)}
                          {getBillingStatusBadge(org.billingStatus)}
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[100px]">
                        {getTierBadge(org.subscriptionTier)}
                      </TableCell>
                      <TableCell className="min-w-[100px]">
                        <div className="space-y-1">
                          <div className="flex items-center gap-1 text-sm">
                            <Users className="h-3 w-3 text-muted-foreground" />
                            <span>{org.userCount} users</span>
                          </div>
                          <div className="flex items-center gap-1 text-sm">
                            <Building2 className="h-3 w-3 text-muted-foreground" />
                            <span>{org.teamCount} teams</span>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[120px]">
                        <div>
                          <div className="font-semibold">{formatCurrency(org.monthlyRevenue)}</div>
                          <div className={`text-sm flex items-center gap-1 ${
                            org.growth >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {org.growth >= 0 ? (
                              <TrendingUp className="h-3 w-3" />
                            ) : (
                              <TrendingDown className="h-3 w-3" />
                            )}
                            {Math.abs(org.growth).toFixed(1)}%
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[100px] hidden lg:table-cell">
                        <div className="text-sm">
                          <div>{org.industry}</div>
                          <div className="text-muted-foreground">{org.region}</div>
                        </div>
                      </TableCell>
                      <TableCell className="min-w-[100px] hidden xl:table-cell">
                        <div className="text-sm">
                          {formatRelativeTime(org.lastActivity)}
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
                            <DropdownMenuLabel>Organization Actions</DropdownMenuLabel>
                            <DropdownMenuItem>
                              <Eye className="mr-2 h-4 w-4" />
                              View Details
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Users className="mr-2 h-4 w-4" />
                              View Teams
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Settings className="mr-2 h-4 w-4" />
                              Organization Settings
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <CreditCard className="mr-2 h-4 w-4" />
                              Billing & Usage
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem>
                              <Download className="mr-2 h-4 w-4" />
                              Export Data
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            {org.status === 'suspended' ? (
                              <DropdownMenuItem className="text-green-600">
                                <Activity className="mr-2 h-4 w-4" />
                                Reactivate
                              </DropdownMenuItem>
                            ) : (
                              <DropdownMenuItem className="text-red-600">
                                <Trash2 className="mr-2 h-4 w-4" />
                                Suspend Organization
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
          {filteredOrganizations.length === 0 && (
            <div className="text-center py-12">
              <Building2 className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No organizations found</h3>
              <p className="text-muted-foreground mb-4">
                {searchTerm || statusFilter !== "all" || tierFilter !== "all" || regionFilter !== "all"
                  ? "Try adjusting your search or filters"
                  : "No client organizations are registered yet"}
              </p>
              {(!searchTerm && statusFilter === "all" && tierFilter === "all" && regionFilter === "all") && (
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Add First Organization
                </Button>
              )}
            </div>
          )}

          {/* Results Summary */}
          {filteredOrganizations.length > 0 && (
            <div className="flex items-center justify-between pt-4 border-t">
              <div className="text-sm text-muted-foreground">
                Showing {filteredOrganizations.length} of {organizations.length} organizations
              </div>
              <div className="text-sm text-muted-foreground">
                Total Revenue: {formatCurrency(filteredOrganizations.reduce((sum, org) => sum + org.monthlyRevenue, 0))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
