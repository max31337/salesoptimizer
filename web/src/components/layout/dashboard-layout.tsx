"use client"

import * as React from "react"
import { SidebarProvider, SidebarInset, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/navigation/app-sidebar"
import { Separator } from "@/components/ui/separator"
import { SimpleThemeToggle } from "@/components/ui/theme-toggle"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Bell, Check, X, AlertCircle, Info, CheckCircle } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"

interface DashboardLayoutProps {
  children: React.ReactNode
  breadcrumbs?: {
    label: string
    href?: string
  }[]
}

interface Notification {
  id: string
  title: string
  message: string
  type: 'info' | 'success' | 'warning' | 'error'
  isRead: boolean
  timestamp: Date
}

// Mock notifications data - in real app this would come from an API
const mockNotifications: Notification[] = [
  {
    id: '1',
    title: 'New Organization Created',
    message: 'Acme Corp has been successfully created and is ready for setup.',
    type: 'success',
    isRead: false,
    timestamp: new Date(Date.now() - 1000 * 60 * 5) // 5 minutes ago
  },
  {
    id: '2',
    title: 'SLA Alert',
    message: 'Platform response time exceeded threshold for the last 10 minutes.',
    type: 'warning',
    isRead: false,
    timestamp: new Date(Date.now() - 1000 * 60 * 15) // 15 minutes ago
  },
  {
    id: '3',
    title: 'System Maintenance',
    message: 'Scheduled maintenance window will begin at 2:00 AM UTC tonight.',
    type: 'info',
    isRead: true,
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2) // 2 hours ago
  },
  {
    id: '4',
    title: 'User Registration Spike',
    message: '50+ new users registered in the last hour. Consider scaling resources.',
    type: 'info',
    isRead: true,
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4) // 4 hours ago
  },
  {
    id: '5',
    title: 'Database Connection Error',
    message: 'Temporary connection issues resolved. All services are operational.',
    type: 'error',
    isRead: true,
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 6) // 6 hours ago
  }
]

// Generate breadcrumbs from pathname
function generateBreadcrumbs(pathname: string) {
  const segments = pathname.split('/').filter(Boolean)
  const breadcrumbs = []

  // Handle different page types
  if (segments[0] === 'dashboard') {
    if (segments.length === 1) {
      // For /dashboard route, just show "Dashboard" once
      breadcrumbs.push({ label: 'Dashboard' })
    } else {
      // For dashboard sub-pages, show Dashboard > SubPage
      breadcrumbs.push({ label: 'Dashboard', href: '/dashboard' })
      
      // Handle special cases for SLA monitoring
      if (segments[1] === 'sla-monitoring') {
        breadcrumbs.push({ label: 'SLA Monitoring', href: '/dashboard/sla-monitoring' })
        
        if (segments.length > 2) {
          const subPage = segments[2]
          if (subPage === 'alerts') {
            breadcrumbs.push({ label: 'Alerts' })
          } else if (subPage === 'metrics') {
            breadcrumbs.push({ label: 'Metrics' })
          } else if (subPage === 'reports') {
            breadcrumbs.push({ label: 'Reports' })
          } else {
            const label = subPage.split('-').map(word => 
              word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ')
            breadcrumbs.push({ label })
          }
        }
      } else {
        // Handle other dashboard sub-pages
        segments.slice(1).forEach((segment, index) => {
          if (index === segments.length - 2) {
            // Last segment - no link
            const label = segment.split('-').map(word => 
              word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ')
            breadcrumbs.push({ label })
          } else {
            // Intermediate segments - with link
            const href = '/' + segments.slice(0, index + 2).join('/')
            const label = segment.split('-').map(word => 
              word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ')
            breadcrumbs.push({ label, href })
          }
        })
      }
    }
  } else if (segments[0] === 'admin') {
    // Handle super admin routes
    breadcrumbs.push({ label: 'Dashboard', href: '/dashboard' })
    
    if (segments.length === 1) {
      // For /admin route
      breadcrumbs.push({ label: 'Super Admin' })
    } else {
      breadcrumbs.push({ label: 'Super Admin', href: '/admin' })
      
      // Handle admin sub-pages
      segments.slice(1).forEach((segment, index) => {
        if (index === segments.length - 2) {
          // Last segment - no link
          const label = segment.charAt(0).toUpperCase() + segment.slice(1)
          breadcrumbs.push({ label })
        } else {
          // Intermediate segments - with link
          const href = '/' + segments.slice(0, index + 2).join('/')
          const label = segment.charAt(0).toUpperCase() + segment.slice(1)
          breadcrumbs.push({ label, href })
        }
      })
    }
  } else if (segments[0] === 'settings') {
    breadcrumbs.push({ label: 'Dashboard', href: '/dashboard' })
    breadcrumbs.push({ label: 'Settings', href: '/settings' })
    
    // Handle settings sub-pages
    if (segments.length > 1) {
      const pageLabel = segments[1].charAt(0).toUpperCase() + segments[1].slice(1)
      breadcrumbs.push({ label: pageLabel })
    }
  } else {
    // For other pages, start with Dashboard and add the current page
    breadcrumbs.push({ label: 'Dashboard', href: '/dashboard' })
    
    // Handle other pages
    segments.forEach((segment, index) => {
      if (index === segments.length - 1) {
        // Last segment - no link
        const label = segment.charAt(0).toUpperCase() + segment.slice(1)
        breadcrumbs.push({ label })
      } else {
        // Intermediate segments - with link
        const href = '/' + segments.slice(0, index + 1).join('/')
        const label = segment.charAt(0).toUpperCase() + segment.slice(1)
        breadcrumbs.push({ label, href })
      }
    })
  }

  return breadcrumbs
}

export function DashboardLayout({ children, breadcrumbs: customBreadcrumbs }: DashboardLayoutProps) {
  const pathname = usePathname()
  const breadcrumbs = customBreadcrumbs || generateBreadcrumbs(pathname)
  const [notifications, setNotifications] = React.useState<Notification[]>(mockNotifications)

  const unreadCount = notifications.filter(n => !n.isRead).length

  const markAsRead = (id: string) => {
    setNotifications(prev => 
      prev.map(notification => 
        notification.id === id 
          ? { ...notification, isRead: true }
          : notification
      )
    )
  }

  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(notification => ({ ...notification, isRead: true }))
    )
  }

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id))
  }

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'warning':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      default:
        return <Info className="h-4 w-4 text-blue-500" />
    }
  }

  const formatTimestamp = (timestamp: Date) => {
    const now = new Date()
    const diff = now.getTime() - timestamp.getTime()
    const minutes = Math.floor(diff / (1000 * 60))
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    return `${days}d ago`
  }

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="sticky top-0 z-50 flex h-16 shrink-0 items-center gap-2 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12">
          <div className="flex items-center gap-2 px-4 flex-1">
            <SidebarTrigger className="-ml-1" />
            <Separator orientation="vertical" className="mr-2 h-4" />
            <Breadcrumb>
              <BreadcrumbList>
                {breadcrumbs.map((breadcrumb, index) => (
                  <React.Fragment key={index}>
                    <BreadcrumbItem className="hidden md:block">
                      {breadcrumb.href && index < breadcrumbs.length - 1 ? (
                        <BreadcrumbLink href={breadcrumb.href}>
                          {breadcrumb.label}
                        </BreadcrumbLink>
                      ) : (
                        <BreadcrumbPage>{breadcrumb.label}</BreadcrumbPage>
                      )}
                    </BreadcrumbItem>
                    {index < breadcrumbs.length - 1 && (
                      <BreadcrumbSeparator className="hidden md:block" />
                    )}
                  </React.Fragment>
                ))}
              </BreadcrumbList>
            </Breadcrumb>
          </div>
          <div className="flex items-center gap-2 px-4">
            {/* Notifications Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="relative h-8 w-8 p-0"
                >
                  <Bell className="h-4 w-4" />
                  {unreadCount > 0 && (
                    <Badge 
                      variant={
                        notifications.some(n => !n.isRead && (n.type === 'error' || n.type === 'warning')) 
                          ? "destructive" 
                          : "default"
                      }
                      className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 text-xs flex items-center justify-center"
                    >
                      {unreadCount > 9 ? '9+' : unreadCount}
                    </Badge>
                  )}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                className="w-80 max-h-96 overflow-y-auto"
                side="bottom"
                align="end"
                sideOffset={4}
              >
                <DropdownMenuLabel className="flex items-center justify-between">
                  <span>Notifications</span>
                  {unreadCount > 0 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={markAllAsRead}
                      className="h-6 px-2 text-xs"
                    >
                      Mark all read
                    </Button>
                  )}
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                {notifications.length === 0 ? (
                  <div className="p-4 text-center text-muted-foreground">
                    No notifications
                  </div>
                ) : (
                  notifications.map((notification) => (
                    <DropdownMenuItem
                      key={notification.id}
                      className={cn(
                        "flex flex-col items-start p-3 cursor-pointer",
                        !notification.isRead && "bg-accent/50"
                      )}
                      onClick={() => markAsRead(notification.id)}
                    >
                      <div className="flex items-start justify-between w-full">
                        <div className="flex items-start gap-2 flex-1">
                          {getNotificationIcon(notification.type)}
                          <div className="flex-1 min-w-0">
                            <div className="font-medium text-sm truncate">
                              {notification.title}
                            </div>
                            <div className="text-xs text-muted-foreground mt-1 line-clamp-2">
                              {notification.message}
                            </div>
                            <div className="text-xs text-muted-foreground mt-2">
                              {formatTimestamp(notification.timestamp)}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-1 ml-2">
                          {!notification.isRead && (
                            <div className="w-2 h-2 bg-primary rounded-full" />
                          )}
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation()
                              removeNotification(notification.id)
                            }}
                            className="h-6 w-6 p-0 hover:bg-destructive/20"
                          >
                            <X className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    </DropdownMenuItem>
                  ))
                )}
                {notifications.length > 0 && (
                  <>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="text-center justify-center">
                      <Button variant="ghost" size="sm" className="text-xs">
                        View all notifications
                      </Button>
                    </DropdownMenuItem>
                  </>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
            <SimpleThemeToggle />
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          {children}
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
