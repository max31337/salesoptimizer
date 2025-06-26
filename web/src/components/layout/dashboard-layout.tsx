"use client"

import * as React from "react"
import { SidebarProvider, SidebarInset, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/navigation/app-sidebar"
import { Separator } from "@/components/ui/separator"
import { SimpleThemeToggle } from "@/components/ui/theme-toggle"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { usePathname } from "next/navigation"

interface DashboardLayoutProps {
  children: React.ReactNode
  breadcrumbs?: {
    label: string
    href?: string
  }[]
}

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
