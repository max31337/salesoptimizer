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
  CreditCard,
  DollarSign,
  TrendingUp,
  TrendingDown,
  Calendar,
  AlertTriangle,
  CheckCircle,
  Clock,
  Building2,
  Users,
  Download,
  Eye,
  RefreshCw,
  FileText,
  Search,
  Filter,
  MoreHorizontal,
  Ban,
  Play
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

// Billing interfaces
interface BillingOrganization {
  id: string
  name: string
  subscriptionTier: 'basic' | 'pro' | 'enterprise' | 'custom'
  billingStatus: 'current' | 'overdue' | 'cancelled' | 'trial'
  monthlyAmount: number
  yearlyAmount: number
  billingCycle: 'monthly' | 'yearly'
  nextBillingDate: string
  lastPaymentDate: string
  lastPaymentAmount: number
  paymentMethod: 'credit_card' | 'bank_transfer' | 'paypal'
  cardLast4?: string
  userCount: number
  teamCount: number
  overdueDays?: number
  totalRevenue: number
  mrr: number // Monthly Recurring Revenue
  adminEmail: string
}

interface PlatformRevenue {
  totalMrr: number
  totalArr: number // Annual Recurring Revenue
  totalRevenue: number
  growthRate: number
  churnRate: number
  newCustomers: number
  cancelledCustomers: number
}

// Mock billing data
const mockBillingOrganizations: BillingOrganization[] = [
  {
    id: 'org_1',
    name: 'Acme Corporation',
    subscriptionTier: 'enterprise',
    billingStatus: 'current',
    monthlyAmount: 2490,
    yearlyAmount: 24900,
    billingCycle: 'yearly',
    nextBillingDate: '2025-07-15T00:00:00Z',
    lastPaymentDate: '2024-07-15T00:00:00Z',
    lastPaymentAmount: 24900,
    paymentMethod: 'credit_card',
    cardLast4: '4532',
    userCount: 247,
    teamCount: 12,
    totalRevenue: 49800,
    mrr: 2075,
    adminEmail: 'john.smith@acme.com'
  },
  {
    id: 'org_2',
    name: 'Global Solutions Ltd',
    subscriptionTier: 'pro',
    billingStatus: 'current',
    monthlyAmount: 850,
    yearlyAmount: 8500,
    billingCycle: 'monthly',
    nextBillingDate: '2025-07-20T00:00:00Z',
    lastPaymentDate: '2025-06-20T00:00:00Z',
    lastPaymentAmount: 850,
    paymentMethod: 'bank_transfer',
    userCount: 89,
    teamCount: 6,
    totalRevenue: 12750,
    mrr: 850,
    adminEmail: 'sarah@globalsolutions.com'
  },
  {
    id: 'org_3',
    name: 'TechStart Inc',
    subscriptionTier: 'basic',
    billingStatus: 'trial',
    monthlyAmount: 199,
    yearlyAmount: 1990,
    billingCycle: 'monthly',
    nextBillingDate: '2025-07-10T00:00:00Z',
    lastPaymentDate: '',
    lastPaymentAmount: 0,
    paymentMethod: 'credit_card',
    cardLast4: '8901',
    userCount: 15,
    teamCount: 2,
    totalRevenue: 0,
    mrr: 0,
    adminEmail: 'mike@techstart.co'
  },
  {
    id: 'org_4',
    name: 'Enterprise Corp',
    subscriptionTier: 'enterprise',
    billingStatus: 'overdue',
    monthlyAmount: 1790,
    yearlyAmount: 17900,
    billingCycle: 'monthly',
    nextBillingDate: '2025-06-25T00:00:00Z',
    lastPaymentDate: '2025-05-25T00:00:00Z',
    lastPaymentAmount: 1790,
    paymentMethod: 'credit_card',
    cardLast4: '2345',
    userCount: 156,
    teamCount: 8,
    overdueDays: 2,
    totalRevenue: 14320,
    mrr: 1790,
    adminEmail: 'lisa@enterprise.com'
  },
  {
    id: 'org_5',
    name: 'StartupHub',
    subscriptionTier: 'basic',
    billingStatus: 'current',
    monthlyAmount: 199,
    yearlyAmount: 1990,
    billingCycle: 'yearly',
    nextBillingDate: '2026-05-12T00:00:00Z',
    lastPaymentDate: '2025-05-12T00:00:00Z',
    lastPaymentAmount: 1990,
    paymentMethod: 'paypal',
    userCount: 32,
    teamCount: 3,
    totalRevenue: 1990,
    mrr: 166,
    adminEmail: 'alex@startuphub.io'
  }
]

// Calculate platform revenue metrics
const calculatePlatformRevenue = (orgs: BillingOrganization[]): PlatformRevenue => {
  const currentOrgs = orgs.filter(org => org.billingStatus === 'current')
  const totalMrr = currentOrgs.reduce((sum, org) => sum + org.mrr, 0)
  const totalRevenue = orgs.reduce((sum, org) => sum + org.totalRevenue, 0)
  
  return {
    totalMrr,
    totalArr: totalMrr * 12,
    totalRevenue,
    growthRate: 15.2, // Mock growth rate
    churnRate: 2.1, // Mock churn rate
    newCustomers: 3, // Mock new customers this month
    cancelledCustomers: 1 // Mock cancelled customers this month
  }
}

const getBillingStatusBadge = (status: string, overdueDays?: number) => {
  switch (status) {
    case 'current':
      return <Badge variant="default" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Current</Badge>
    case 'trial':
      return <Badge variant="secondary" className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">Trial</Badge>
    case 'overdue':
      return (
        <Badge variant="destructive" className="bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
          Overdue {overdueDays ? `(${overdueDays}d)` : ''}
        </Badge>
      )
    case 'cancelled':
      return <Badge variant="outline" className="text-gray-600">Cancelled</Badge>
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

const getPaymentMethodIcon = (method: string) => {
  switch (method) {
    case 'credit_card':
      return <CreditCard className="h-4 w-4" />
    case 'bank_transfer':
      return <Building2 className="h-4 w-4" />
    case 'paypal':
      return <DollarSign className="h-4 w-4" />
    default:
      return <CreditCard className="h-4 w-4" />
  }
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0
  }).format(amount)
}

const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export default function BillingPage() {
  const { user } = useAuth()
  const [organizations, setOrganizations] = useState<BillingOrganization[]>([])
  const [filteredOrganizations, setFilteredOrganizations] = useState<BillingOrganization[]>([])
  const [platformRevenue, setPlatformRevenue] = useState<PlatformRevenue | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [tierFilter, setTierFilter] = useState("all")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setOrganizations(mockBillingOrganizations)
      setFilteredOrganizations(mockBillingOrganizations)
      setPlatformRevenue(calculatePlatformRevenue(mockBillingOrganizations))
      setLoading(false)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  // Filter organizations
  useEffect(() => {
    let filtered = organizations

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(org => 
        org.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        org.adminEmail.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Apply status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(org => org.billingStatus === statusFilter)
    }

    // Apply tier filter
    if (tierFilter !== 'all') {
      filtered = filtered.filter(org => org.subscriptionTier === tierFilter)
    }

    setFilteredOrganizations(filtered)
  }, [organizations, searchTerm, statusFilter, tierFilter])

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
              <CreditCard className="h-6 w-6 text-white" />
            </div>
            Billing & Subscriptions
          </h1>
          <p className="text-muted-foreground mt-2">
            Manage billing and subscriptions across all client organizations
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
          <Button variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Sync Billing
          </Button>
        </div>
      </div>

      {/* Revenue Metrics */}
      {platformRevenue && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Monthly Recurring Revenue</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(platformRevenue.totalMrr)}</div>
              <p className="text-xs text-muted-foreground flex items-center gap-1">
                <TrendingUp className="h-3 w-3 text-green-600" />
                +{platformRevenue.growthRate}% from last month
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Annual Recurring Revenue</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(platformRevenue.totalArr)}</div>
              <p className="text-xs text-muted-foreground">
                Projected annual revenue
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(platformRevenue.totalRevenue)}</div>
              <p className="text-xs text-muted-foreground">
                All-time revenue
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Churn Rate</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{platformRevenue.churnRate}%</div>
              <p className="text-xs text-muted-foreground">
                {platformRevenue.cancelledCustomers} cancelled this month
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Billing Management */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="subscriptions">Subscriptions</TabsTrigger>
          <TabsTrigger value="overdue">Overdue ({organizations.filter(org => org.billingStatus === 'overdue').length})</TabsTrigger>
          <TabsTrigger value="trials">Trials ({organizations.filter(org => org.billingStatus === 'trial').length})</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Payment Status</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm">Current</span>
                  <Badge variant="default" className="bg-green-100 text-green-800">
                    {organizations.filter(org => org.billingStatus === 'current').length}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Overdue</span>
                  <Badge variant="destructive">
                    {organizations.filter(org => org.billingStatus === 'overdue').length}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Trial</span>
                  <Badge variant="secondary">
                    {organizations.filter(org => org.billingStatus === 'trial').length}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Cancelled</span>
                  <Badge variant="outline">
                    {organizations.filter(org => org.billingStatus === 'cancelled').length}
                  </Badge>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Subscription Tiers</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm">Enterprise</span>
                  <Badge className="bg-purple-100 text-purple-800">
                    {organizations.filter(org => org.subscriptionTier === 'enterprise').length}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Pro</span>
                  <Badge className="bg-blue-100 text-blue-800">
                    {organizations.filter(org => org.subscriptionTier === 'pro').length}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Basic</span>
                  <Badge className="bg-gray-100 text-gray-800">
                    {organizations.filter(org => org.subscriptionTier === 'basic').length}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Custom</span>
                  <Badge className="bg-orange-100 text-orange-800">
                    {organizations.filter(org => org.subscriptionTier === 'custom').length}
                  </Badge>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Recent Activity</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span>Acme Corp paid {formatCurrency(2490)}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <AlertTriangle className="h-4 w-4 text-red-600" />
                    <span>Enterprise Corp payment overdue</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Clock className="h-4 w-4 text-blue-600" />
                    <span>TechStart trial ending soon</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="subscriptions" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>All Subscriptions</CardTitle>
              <CardDescription>
                Manage billing and subscription details for all organizations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col lg:flex-row gap-4 mb-6">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      placeholder="Search organizations..."
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
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="current">Current</SelectItem>
                    <SelectItem value="overdue">Overdue</SelectItem>
                    <SelectItem value="trial">Trial</SelectItem>
                    <SelectItem value="cancelled">Cancelled</SelectItem>
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
              </div>

              <div className="rounded-md border overflow-hidden">
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="min-w-[200px]">Organization</TableHead>
                        <TableHead className="min-w-[100px]">Subscription</TableHead>
                        <TableHead className="min-w-[100px]">Status</TableHead>
                        <TableHead className="min-w-[120px]">Amount</TableHead>
                        <TableHead className="min-w-[100px]">Cycle</TableHead>
                        <TableHead className="min-w-[120px]">Next Billing</TableHead>
                        <TableHead className="min-w-[100px] hidden lg:table-cell">Payment Method</TableHead>
                        <TableHead className="min-w-[100px] hidden xl:table-cell">MRR</TableHead>
                        <TableHead className="text-right min-w-[80px]">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredOrganizations.map((org) => (
                        <TableRow key={org.id} className="hover:bg-muted/50">
                          <TableCell className="min-w-[200px]">
                            <div>
                              <div className="font-medium">{org.name}</div>
                              <div className="text-sm text-muted-foreground">{org.adminEmail}</div>
                            </div>
                          </TableCell>
                          <TableCell className="min-w-[100px]">
                            {getTierBadge(org.subscriptionTier)}
                          </TableCell>
                          <TableCell className="min-w-[100px]">
                            {getBillingStatusBadge(org.billingStatus, org.overdueDays)}
                          </TableCell>
                          <TableCell className="min-w-[120px]">
                            <div>
                              <div className="font-medium">
                                {formatCurrency(org.billingCycle === 'monthly' ? org.monthlyAmount : org.yearlyAmount)}
                              </div>
                              {org.billingCycle === 'yearly' && (
                                <div className="text-sm text-muted-foreground">
                                  {formatCurrency(org.monthlyAmount)}/mo
                                </div>
                              )}
                            </div>
                          </TableCell>
                          <TableCell className="min-w-[100px]">
                            <Badge variant="outline" className="capitalize">
                              {org.billingCycle}
                            </Badge>
                          </TableCell>
                          <TableCell className="min-w-[120px]">
                            <div className="text-sm">
                              {formatDate(org.nextBillingDate)}
                            </div>
                          </TableCell>
                          <TableCell className="min-w-[100px] hidden lg:table-cell">
                            <div className="flex items-center gap-2">
                              {getPaymentMethodIcon(org.paymentMethod)}
                              <span className="text-sm">
                                {org.cardLast4 ? `****${org.cardLast4}` : org.paymentMethod.replace('_', ' ')}
                              </span>
                            </div>
                          </TableCell>
                          <TableCell className="min-w-[100px] hidden xl:table-cell">
                            <div className="font-medium">
                              {formatCurrency(org.mrr)}
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
                                <DropdownMenuLabel>Billing Actions</DropdownMenuLabel>
                                <DropdownMenuItem>
                                  <Eye className="mr-2 h-4 w-4" />
                                  View Details
                                </DropdownMenuItem>
                                <DropdownMenuItem>
                                  <FileText className="mr-2 h-4 w-4" />
                                  View Invoices
                                </DropdownMenuItem>
                                <DropdownMenuItem>
                                  <CreditCard className="mr-2 h-4 w-4" />
                                  Update Payment Method
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem>
                                  <Download className="mr-2 h-4 w-4" />
                                  Export Data
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                {org.billingStatus === 'cancelled' ? (
                                  <DropdownMenuItem className="text-green-600">
                                    <Play className="mr-2 h-4 w-4" />
                                    Reactivate
                                  </DropdownMenuItem>
                                ) : (
                                  <DropdownMenuItem className="text-red-600">
                                    <Ban className="mr-2 h-4 w-4" />
                                    Cancel Subscription
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

              {filteredOrganizations.length === 0 && (
                <div className="text-center py-8">
                  <CreditCard className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No subscriptions found</h3>
                  <p className="text-muted-foreground">
                    {searchTerm || statusFilter !== "all" || tierFilter !== "all"
                      ? "Try adjusting your search or filters"
                      : "No subscriptions available"}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="overdue" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-red-600">Overdue Payments</CardTitle>
              <CardDescription>
                Organizations with overdue payments requiring immediate attention
              </CardDescription>
            </CardHeader>
            <CardContent>
              {organizations.filter(org => org.billingStatus === 'overdue').length === 0 ? (
                <div className="text-center py-8">
                  <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No overdue payments</h3>
                  <p className="text-muted-foreground">
                    All organizations are current with their payments
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {organizations.filter(org => org.billingStatus === 'overdue').map((org) => (
                    <div key={org.id} className="border border-red-200 rounded-lg p-4 bg-red-50 dark:bg-red-900/10">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-semibold">{org.name}</h4>
                          <p className="text-sm text-muted-foreground">{org.adminEmail}</p>
                          <p className="text-sm text-red-600">
                            Overdue: {formatCurrency(org.monthlyAmount)} ({org.overdueDays} days)
                          </p>
                        </div>
                        <div className="flex gap-2">
                          <Button size="sm" variant="outline">
                            Send Reminder
                          </Button>
                          <Button size="sm">
                            Contact Customer
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trials" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-blue-600">Trial Organizations</CardTitle>
              <CardDescription>
                Organizations currently on trial subscriptions
              </CardDescription>
            </CardHeader>
            <CardContent>
              {organizations.filter(org => org.billingStatus === 'trial').length === 0 ? (
                <div className="text-center py-8">
                  <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No trial organizations</h3>
                  <p className="text-muted-foreground">
                    No organizations are currently on trial
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {organizations.filter(org => org.billingStatus === 'trial').map((org) => (
                    <div key={org.id} className="border border-blue-200 rounded-lg p-4 bg-blue-50 dark:bg-blue-900/10">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-semibold">{org.name}</h4>
                          <p className="text-sm text-muted-foreground">{org.adminEmail}</p>
                          <p className="text-sm text-blue-600">
                            Trial ends: {formatDate(org.nextBillingDate)}
                          </p>
                        </div>
                        <div className="flex gap-2">
                          <Button size="sm" variant="outline">
                            Extend Trial
                          </Button>
                          <Button size="sm">
                            Convert to Paid
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
