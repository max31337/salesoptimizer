"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { InviteOrgAdminModal } from "@/components/admin/invite-org-admin-modal"
import { useAuth } from "@/features/auth/hooks/useAuth"
import { Icons } from "@/components/ui/icons"
import { Building, Users, Activity, UserPlus, Settings, FileText } from "lucide-react"

export default function SuperAdminDashboard() {
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false)
  const { user } = useAuth()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Super Admin Dashboard</h1>
              <p className="mt-1 text-sm text-gray-600">
                Welcome back, {user?.first_name || user?.email}
              </p>
            </div>
            <Badge variant="secondary" className="bg-purple-100 text-purple-800">
              Super Admin
            </Badge>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Organizations</CardTitle>
                <Building className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">24</div>
                <p className="text-xs text-muted-foreground">
                  +3 from last month
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Users</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">1,247</div>
                <p className="text-xs text-muted-foreground">
                  +12% from last month
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">System Health</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">98.9%</div>
                <p className="text-xs text-muted-foreground">
                  Uptime this month
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>
                Common administrative tasks
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-4">
                <Button 
                  onClick={() => setIsInviteModalOpen(true)}
                  className="flex items-center gap-2"
                >
                  <UserPlus className="h-4 w-4" />
                  Invite Organization Admin
                </Button>
                
                <Button variant="outline" className="flex items-center gap-2">
                  <Settings className="h-4 w-4" />
                  System Settings
                </Button>
                
                <Button variant="outline" className="flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  View Audit Logs
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>
                Latest system events and user activities
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center space-x-4">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">New organization created</p>
                    <p className="text-xs text-muted-foreground">Acme Corp - 2 hours ago</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Organization admin invited</p>
                    <p className="text-xs text-muted-foreground">admin@techstart.com - 4 hours ago</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">System maintenance completed</p>
                    <p className="text-xs text-muted-foreground">Database optimization - 6 hours ago</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Invite Modal */}
      <InviteOrgAdminModal 
        open={isInviteModalOpen}
        onOpenChange={setIsInviteModalOpen}
      />
    </div>
  )
}