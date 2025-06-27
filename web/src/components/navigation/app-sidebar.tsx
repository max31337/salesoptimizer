"use client"

import * as React from "react"
import { usePathname } from "next/navigation"
import Link from "next/link"
import { 
  Building, 
  Users, 
  Activity, 
  UserPlus, 
  Settings, 
  FileText, 
  LogOut, 
  User as UserIcon, 
  Monitor, 
  AlertTriangle,
  BarChart3,
  Shield,
  Home,
  ChevronRight,
  ChevronDown,
  Bell,
  Brain,
  Zap,
  Sun,
  Moon,
  DollarSign,
  Flag,
  Database,
  type LucideIcon
} from "lucide-react"

import { cn } from "@/lib/utils"
import { useAuth } from "@/features/auth/hooks/useAuth"
import { useTheme } from "@/contexts/theme-context"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
  SidebarRail,
} from "@/components/ui/sidebar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { UserAvatar } from "@/components/ui/user-avatar"
import { createFullName } from "@/utils/nameParser"

interface NavItem {
  title: string
  url: string
  icon: LucideIcon
  badge?: string
  isActive?: boolean
  items?: {
    title: string
    url: string
    icon?: LucideIcon
  }[]
}

interface CollapsibleNavGroup {
  title: string
  icon: LucideIcon
  items: NavItem[]
  isCollapsible?: boolean
  defaultOpen?: boolean
}

// Settings items helper function
const getSettingsItems = (userRole?: string) => {
  const baseSettingsItems = [
    {
      title: "Profile",
      url: "/profile",
      icon: UserIcon,
    },
    {
      title: "Security",
      url: "/settings/security",
      icon: Shield,
    },
    {
      title: "Notifications",
      url: "/settings/notifications",
      icon: Bell,
    },
    {
      title: "General",
      url: "/settings/general",
      icon: Settings,
    },
  ]

  const adminSettingsItems = [
    {
      title: "Organization",
      url: "/settings/organization",
      icon: Building,
    },
    {
      title: "Team Management",
      url: "/settings/team",
      icon: Users,
    },
  ]

  const isAdmin = userRole === 'super_admin' || userRole === 'org_admin'
  return isAdmin ? [...baseSettingsItems, ...adminSettingsItems] : baseSettingsItems
}

// Navigation items for different user roles
const getNavigationItems = (userRole?: string): { groups: CollapsibleNavGroup[] } => {
  // Platform Management items for super admins
  const platformManagementItems: NavItem[] = [
    {
      title: "Dashboard",
      url: "/dashboard",
      icon: Home,
    },
    {
      title: "SLA Monitoring",
      url: "/dashboard/sla-monitoring",
      icon: Activity,
      items: [
        {
          title: "Overview",
          url: "/dashboard/sla-monitoring",
          icon: Activity,
        },
        {
          title: "Alerts",
          url: "/dashboard/sla-monitoring/alerts",
          icon: AlertTriangle,
        },
        {
          title: "Metrics",
          url: "/dashboard/sla-monitoring/metrics",
          icon: BarChart3,
        },
        {
          title: "Reports",
          url: "/dashboard/sla-monitoring/reports",
          icon: FileText,
        },
      ]
    },
    {
      title: "SalesOptimizer Platform",
      url: "/dashboard/platform",
      icon: Brain,
      items: [
        {
          title: "Platform Overview",
          url: "/dashboard/platform",
          icon: Brain,
        },
        {
          title: "Organizations",
          url: "/dashboard/organizations",
          icon: Building,
        },
        {
          title: "Multi-tenant",
          url: "/dashboard/tenants",
          icon: Database,
        },
        {
          title: "Billing & Subscriptions",
          url: "/dashboard/billing",
          icon: DollarSign,
        },
      ]
    },
    {
      title: "User Management",
      url: "/dashboard/users",
      icon: Users,
      items: [
        {
          title: "All Users",
          url: "/dashboard/users",
          icon: Users,
        },
        {
          title: "Support Staff",
          url: "/dashboard/support-staff",
          icon: UserPlus,
        },
        {
          title: "Platform Team",
          url: "/dashboard/platform-team",
          icon: Shield,
        },
        {
          title: "Invitations",
          url: "/dashboard/invitations",
          icon: UserPlus,
        },
      ]
    },
    {
      title: "System Configuration",
      url: "/dashboard/system",
      icon: Settings,
      items: [
        {
          title: "System Health",
          url: "/dashboard/health",
          icon: Monitor,
        },
        {
          title: "Global Settings",
          url: "/dashboard/global-settings",
          icon: Settings,
        },
        {
          title: "Feature Flags",
          url: "/dashboard/feature-flags",
          icon: Flag,
        },
        {
          title: "Analytics",
          url: "/dashboard/analytics",
          icon: BarChart3,
        },
      ]
    },
  ]

  // Advanced Admin Tools (consolidated from Super Admin Panel)
  const advancedAdminItems: NavItem[] = [
    {
      title: "Advanced Monitoring",
      url: "/admin",
      icon: Zap,
    },
    {
      title: "Advanced Alerts",
      url: "/admin/alerts",
      icon: AlertTriangle,
    },
    {
      title: "Advanced Metrics",
      url: "/admin/metrics",
      icon: Zap,
    },
    {
      title: "Advanced Reports",
      url: "/admin/reports",
      icon: FileText,
    },
  ]

  if (userRole === 'super_admin') {
    return {
      groups: [
        {
          title: "Platform Management",
          icon: Brain,
          items: platformManagementItems,
          isCollapsible: true,
          defaultOpen: true,
        },
        {
          title: "Advanced Tools",
          icon: Zap,
          items: advancedAdminItems,
          isCollapsible: true,
          defaultOpen: false,
        },
      ],
    }
  }

  // Regular user navigation - simplified settings only
  const userNavItems: NavItem[] = [
    {
      title: "Dashboard",
      url: "/dashboard",
      icon: Home,
    },
    {
      title: "Profile",
      url: "/profile",
      icon: UserIcon,
    },
  ]

  return {
    groups: [
      {
        title: "Main",
        icon: Home,
        items: userNavItems,
        isCollapsible: false,
      },
    ],
  }
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const { user, logout } = useAuth()
  const { setTheme, theme } = useTheme()
  const pathname = usePathname()
  const [isLoggingOut, setIsLoggingOut] = React.useState(false)
  const [collapsedGroups, setCollapsedGroups] = React.useState<Record<string, boolean>>({})
  const [expandedItems, setExpandedItems] = React.useState<Record<string, boolean>>({})

  const handleLogout = React.useCallback(async () => {
    setIsLoggingOut(true)
    try {
      await logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setIsLoggingOut(false)
    }
  }, [logout])

  const navigation = React.useMemo(() => getNavigationItems(user?.role), [user?.role])

  // Initialize collapsed states based on defaultOpen - only run once per user role change
  React.useEffect(() => {
    const initialStates: Record<string, boolean> = {}
    const nav = getNavigationItems(user?.role)
    nav.groups.forEach(group => {
      if (group.isCollapsible) {
        initialStates[group.title] = !(group.defaultOpen ?? false)
      }
    })
    setCollapsedGroups(initialStates)
  }, [user?.role]) // Only depend on user role to prevent infinite loops

  const toggleGroup = React.useCallback((groupTitle: string) => {
    setCollapsedGroups(prev => ({
      ...prev,
      [groupTitle]: !prev[groupTitle]
    }))
  }, [])

  const toggleItem = React.useCallback((itemTitle: string) => {
    setExpandedItems(prev => ({
      ...prev,
      [itemTitle]: !prev[itemTitle]
    }))
  }, [])

  const renderNavItem = React.useCallback((item: NavItem) => {
    const isActive = pathname === item.url || 
      (item.items && item.items.some(subItem => pathname === subItem.url))
    const isExpanded = expandedItems[item.title] || false
    
    return (
      <SidebarMenuItem key={item.title}>
        {item.items && item.items.length > 0 ? (
          <div className="space-y-1">
            <SidebarMenuButton
              onClick={() => toggleItem(item.title)}
              isActive={isActive}
              tooltip={item.title}
              className="w-full text-sm py-1.5 px-2"
            >
              <item.icon className="h-4 w-4" />
              <span className="text-sm">{item.title}</span>
              <ChevronRight className={cn(
                "ml-auto h-3 w-3 transition-transform duration-200",
                isExpanded && "rotate-90"
              )} />
            </SidebarMenuButton>
            <div className={cn(
              "ml-4 overflow-hidden transition-all duration-200 ease-in-out",
              isExpanded ? "max-h-96 opacity-100" : "max-h-0 opacity-0"
            )}>
              <SidebarMenuSub>
                {item.items.map((subItem) => (
                  <SidebarMenuSubItem key={subItem.title}>
                    <SidebarMenuSubButton asChild isActive={pathname === subItem.url} className="text-xs py-1 px-2">
                      <Link href={subItem.url} className="flex items-center gap-2">
                        {subItem.icon && <subItem.icon className="h-3 w-3" />}
                        <span className="text-xs">{subItem.title}</span>
                      </Link>
                    </SidebarMenuSubButton>
                  </SidebarMenuSubItem>
                ))}
              </SidebarMenuSub>
            </div>
          </div>
        ) : (
          <SidebarMenuButton asChild isActive={isActive} tooltip={item.title} className="text-sm py-1.5 px-2">
            <Link href={item.url} className="flex items-center gap-2">
              <item.icon className="h-4 w-4" />
              <span className="text-sm">{item.title}</span>
              {item.badge && (
                <span className="ml-auto flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-primary text-xs text-primary-foreground">
                  {item.badge}
                </span>
              )}
            </Link>
          </SidebarMenuButton>
        )}
      </SidebarMenuItem>
    )
  }, [pathname, expandedItems, toggleItem])

  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <Link href="/" className="flex items-center space-x-2 p-2 group">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center group-hover:shadow-lg transition-shadow duration-200">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <span className="group-data-[collapsible=icon]:hidden text-lg font-bold text-foreground group-hover:text-primary transition-colors duration-200">
            SalesOptimizer
          </span>
        </Link>
      </SidebarHeader>
      <SidebarContent>
        {/* Navigation Groups */}
        {navigation.groups.map((group) => (
          <SidebarGroup key={group.title}>
            <div className="space-y-2">
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <button
                      onClick={() => toggleGroup(group.title)}
                      className={cn(
                        "w-full text-left group/label text-xs text-muted-foreground hover:text-foreground cursor-pointer flex items-center gap-2 py-1.5 transition-all duration-200",
                        collapsedGroups[group.title] ? "mb-0" : "mb-1"
                      )}
                    >
                      <group.icon className="h-3.5 w-3.5 shrink-0" />
                      <span className="group-data-[collapsible=icon]:hidden text-xs font-medium">{group.title}</span>
                      <ChevronDown className={cn(
                        "ml-auto h-3 w-3 transition-transform duration-200 group-data-[collapsible=icon]:hidden",
                        collapsedGroups[group.title] ? "rotate-0" : "rotate-180"
                      )} />
                    </button>
                  </TooltipTrigger>
                  <TooltipContent 
                    side="right" 
                    className="group-data-[collapsible=open]:hidden"
                  >
                    {group.title}
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
              <div className={cn(
                "overflow-hidden transition-all duration-200 ease-in-out",
                collapsedGroups[group.title] ? "max-h-0 opacity-0" : "max-h-96 opacity-100"
              )}>
                <SidebarGroupContent>
                  <SidebarMenu>
                    {group.items.map(renderNavItem)}
                  </SidebarMenu>
                </SidebarGroupContent>
              </div>
            </div>
          </SidebarGroup>
        ))}
      </SidebarContent>
      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <SidebarMenuButton
                  size="lg"
                  className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
                >
                  <UserAvatar 
                    user={user} 
                    className="h-8 w-8"
                  />
                  <div className="grid flex-1 text-left text-sm leading-tight">
                    <span className="truncate font-semibold">
                      {user ? createFullName(user.first_name || '', user.last_name || '') : 'User'}
                    </span>
                    <span className="truncate text-xs text-muted-foreground">
                      {user?.email}
                    </span>
                  </div>
                </SidebarMenuButton>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                className="w-[--radix-dropdown-menu-trigger-width] min-w-56 rounded-lg"
                side="bottom"
                align="end"
                sideOffset={4}
              >
                <DropdownMenuLabel className="p-0 font-normal">
                  <div className="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
                    <UserAvatar 
                      user={user} 
                      className="h-8 w-8"
                    />
                    <div className="grid flex-1 text-left text-sm leading-tight">
                      <span className="truncate font-semibold">
                        {user ? createFullName(user.first_name || '', user.last_name || '') : 'User'}
                      </span>
                      <span className="truncate text-xs text-muted-foreground">
                        {user?.email}
                      </span>
                    </div>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link href="/profile">
                    <UserIcon className="mr-2 h-4 w-4" />
                    Profile
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/settings/security">
                    <Shield className="mr-2 h-4 w-4" />
                    Security
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/settings/notifications">
                    <Bell className="mr-2 h-4 w-4" />
                    Notifications
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/settings/general">
                    <Settings className="mr-2 h-4 w-4" />
                    General Settings
                  </Link>
                </DropdownMenuItem>
                {(user?.role === 'super_admin' || user?.role === 'org_admin') && (
                  <>
                    <DropdownMenuItem asChild>
                      <Link href="/settings/organization">
                        <Building className="mr-2 h-4 w-4" />
                        Organization
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link href="/settings/team">
                        <Users className="mr-2 h-4 w-4" />
                        Team Management
                      </Link>
                    </DropdownMenuItem>
                  </>
                )}
                <DropdownMenuSeparator />
                <DropdownMenuItem 
                  onClick={() => setTheme("light")}
                  className="cursor-pointer"
                >
                  <Sun className="mr-2 h-4 w-4" />
                  Light theme
                  {theme === "light" && <span className="ml-auto">✓</span>}
                </DropdownMenuItem>
                <DropdownMenuItem 
                  onClick={() => setTheme("dark")}
                  className="cursor-pointer"
                >
                  <Moon className="mr-2 h-4 w-4" />
                  Dark theme
                  {theme === "dark" && <span className="ml-auto">✓</span>}
                </DropdownMenuItem>
                <DropdownMenuItem 
                  onClick={() => setTheme("system")}
                  className="cursor-pointer"
                >
                  <Monitor className="mr-2 h-4 w-4" />
                  System theme
                  {theme === "system" && <span className="ml-auto">✓</span>}
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem 
                  onClick={handleLogout}
                  disabled={isLoggingOut}
                  className="cursor-pointer"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  {isLoggingOut ? 'Logging out...' : 'Log out'}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
