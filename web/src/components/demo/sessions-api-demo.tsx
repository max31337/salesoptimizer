"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  tokenRevocationService, 
  type Session, 
  type RevokedSession,
  type SessionsResponse,
  type RevokedSessionsResponse,
  type GroupedSessionsResponse,
  type GroupedRevokedSessionsResponse
} from "@/features/auth/services/token-revocation-service"
import { Loader2, Users, Globe, List } from "lucide-react"

export function SessionsApiDemo() {
  const [isLoading, setIsLoading] = useState(false)
  const [activeTab, setActiveTab] = useState("active")
  const [groupMode, setGroupMode] = useState<'list' | 'device' | 'ip'>('list')
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState("")

  const fetchSessions = async () => {
    try {
      setIsLoading(true)
      setError("")
      
      let result
      
      if (activeTab === "active") {
        if (groupMode === 'list') {
          result = await tokenRevocationService.getActiveSessions(1, 10)
        } else {
          result = await tokenRevocationService.getActiveSessions(1, 10, groupMode)
        }
      } else {
        if (groupMode === 'list') {
          result = await tokenRevocationService.getRevokedSessions(1, 10)
        } else {
          result = await tokenRevocationService.getRevokedSessions(1, 10, groupMode)
        }
      }
      
      setData(result)
      console.log(`${activeTab} sessions (${groupMode}):`, result)
    } catch (err: any) {
      console.error('Error fetching sessions:', err)
      setError(err?.message || 'Failed to fetch sessions')
    } finally {
      setIsLoading(false)
    }
  }

  const renderApiResponse = () => {
    if (!data) return null

    return (
      <Card className="mt-4">
        <CardHeader>
          <CardTitle>API Response</CardTitle>
          <CardDescription>
            {activeTab === "active" ? "GET /api/v1/auth/sessions" : "GET /api/v1/auth/sessions/revoked"}
            {groupMode !== 'list' && ` with group_by=${groupMode}`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <pre className="bg-muted p-4 rounded-lg text-sm overflow-auto max-h-96">
            {JSON.stringify(data, null, 2)}
          </pre>
        </CardContent>
      </Card>
    )
  }

  const renderSessionsSummary = () => {
    if (!data) return null

    const isGrouped = 'grouped_sessions' in data
    
    if (isGrouped) {
      const groupedData = data as GroupedSessionsResponse | GroupedRevokedSessionsResponse
      return (
        <div className="flex items-center space-x-4">
          <Badge variant="outline">
            {groupedData.total_sessions} total sessions
          </Badge>
          <Badge variant="outline">
            {groupedData.total_groups} groups
          </Badge>
          <Badge variant="outline">
            Grouped by {groupedData.grouping}
          </Badge>
        </div>
      )
    } else {
      const listData = data as SessionsResponse | RevokedSessionsResponse
      return (
        <div className="flex items-center space-x-4">
          <Badge variant="outline">
            {listData.total_count} total sessions
          </Badge>
          <Badge variant="outline">
            Page {listData.page} of {listData.total_pages}
          </Badge>
        </div>
      )
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Sessions API Demo</h2>
        <p className="text-muted-foreground">
          Test the GET /api/v1/auth/sessions and /api/v1/auth/sessions/revoked endpoints with grouping
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>API Configuration</CardTitle>
          <CardDescription>
            Configure which endpoint and grouping mode to test
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Endpoint Selector */}
          <div>
            <label className="text-sm font-medium mb-2 block">Endpoint</label>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="active">Active Sessions</TabsTrigger>
                <TabsTrigger value="revoked">Revoked Sessions</TabsTrigger>
              </TabsList>
            </Tabs>
          </div>

          {/* Grouping Mode Selector */}
          <div>
            <label className="text-sm font-medium mb-2 block">Grouping Mode</label>
            <div className="flex items-center space-x-2">
              <Button
                variant={groupMode === 'list' ? "default" : "outline"}
                size="sm"
                onClick={() => setGroupMode('list')}
              >
                <List className="h-4 w-4 mr-2" />
                List View
              </Button>
              <Button
                variant={groupMode === 'device' ? "default" : "outline"}
                size="sm"
                onClick={() => setGroupMode('device')}
              >
                <Users className="h-4 w-4 mr-2" />
                Group by Device
              </Button>
              <Button
                variant={groupMode === 'ip' ? "default" : "outline"}
                size="sm"
                onClick={() => setGroupMode('ip')}
              >
                <Globe className="h-4 w-4 mr-2" />
                Group by IP
              </Button>
            </div>
          </div>

          {/* Fetch Button */}
          <Button onClick={fetchSessions} disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Fetching...
              </>
            ) : (
              'Fetch Sessions'
            )}
          </Button>

          {/* Error Display */}
          {error && (
            <div className="text-sm text-red-600 bg-red-50 p-3 rounded-md">
              {error}
            </div>
          )}

          {/* Summary */}
          {data && (
            <div>
              <label className="text-sm font-medium mb-2 block">Summary</label>
              {renderSessionsSummary()}
            </div>
          )}
        </CardContent>
      </Card>

      {/* API Response */}
      {renderApiResponse()}
    </div>
  )
}
