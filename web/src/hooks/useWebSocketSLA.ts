import { useState, useEffect, useCallback, useRef } from 'react'
import { slaWebSocketClient, type SLAUpdateData } from '@/lib/websocket'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { slaService, type SLASystemHealth, type SLAAlert } from '@/features/sla/services/sla-service'

interface WebSocketMessage {
  type: string
  data?: any
}

export interface WebSocketSLAData {
  systemHealth: SLASystemHealth | null
  alerts: SLAAlert[]
  isConnected: boolean
  connectionState: string
  lastUpdated: Date | null
  acknowledgeAlert: (alertId: string) => Promise<{ success: boolean; message: string; acknowledged_by: string; acknowledged_at: string }>
  connect: () => Promise<void>
  disconnect: () => void
  requestUpdate: () => void
}

export function useWebSocketSLA(): WebSocketSLAData {
  const { isAuthenticated, user } = useAuth()
  const [systemHealth, setSystemHealth] = useState<SLASystemHealth | null>(null)
  const [alerts, setAlerts] = useState<SLAAlert[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [connectionState, setConnectionState] = useState('disconnected')
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  
  // Use refs to avoid stale closures in event handlers
  const isInitialized = useRef(false)
  const hasPermission = user?.role === 'super_admin'

  // Convert WebSocket data to frontend types
  const convertToFrontendTypes = useCallback((data: SLAUpdateData): { systemHealth: SLASystemHealth, alerts: SLAAlert[] } => {
    const systemHealth: SLASystemHealth = {
      overall_status: data.system_health.overall_status as 'healthy' | 'warning' | 'critical',
      health_percentage: data.system_health.health_percentage,
      uptime_status: data.system_health.uptime_status,
      last_updated: new Date().toISOString(),
      total_metrics: data.system_health.total_metrics,
      healthy_metrics: data.system_health.healthy_metrics,
      warning_metrics: data.system_health.warning_metrics,
      critical_metrics: data.system_health.critical_metrics,
      uptime_percentage: data.system_health.uptime_percentage,
      uptime_duration: data.system_health.uptime_duration,
      system_start_time: data.system_health.system_start_time ?? undefined,
      metrics_summary: data.system_health.metrics_summary
    }

    const alerts: SLAAlert[] = data.alerts.map(alert => ({
      id: alert.id,
      alert_type: alert.alert_type as 'warning' | 'critical',
      title: alert.title,
      message: alert.message,
      metric_type: alert.metric_type,
      current_value: alert.current_value,
      threshold_value: alert.threshold_value,
      triggered_at: alert.triggered_at,
      acknowledged: alert.acknowledged,
      acknowledged_at: null,
      acknowledged_by: null
    }))

    return { systemHealth, alerts }
  }, [])

  const updateConnectionState = useCallback(() => {
    const connected = slaWebSocketClient.getConnectionStatus()
    setIsConnected(connected)
    setConnectionState(connected ? 'connected' : 'disconnected')
  }, [])

  const handleSLAUpdate = useCallback((data: SLAUpdateData) => {
    try {
      const converted = convertToFrontendTypes(data)
      setSystemHealth(converted.systemHealth)
      setAlerts(converted.alerts)
      setLastUpdated(new Date())
      console.log('📊 Updated SLA data from WebSocket:', converted.systemHealth.overall_status)
    } catch (error) {
      console.error('Error converting WebSocket data:', error)
    }
  }, [convertToFrontendTypes])

  const handleConnectionChange = useCallback((connected: boolean) => {
    setIsConnected(connected)
    setConnectionState(connected ? 'connected' : 'disconnected')
    
    if (!connected) {
      console.log('WebSocket disconnected, falling back to REST API')
      // Fallback to REST API when WebSocket disconnects
      fetchDataFromAPI()
    }
  }, [])

  // Fallback to REST API
  const fetchDataFromAPI = useCallback(async () => {
    if (!hasPermission) return
    
    try {
      const [healthData, alertsData] = await Promise.all([
        slaService.getSystemHealth(),
        slaService.getCurrentAlerts()
      ])
      
      setSystemHealth(healthData)
      setAlerts(alertsData)
      setLastUpdated(new Date())
      console.log('📡 Updated SLA data from REST API')
    } catch (error) {
      console.error('Failed to fetch SLA data from API:', error)
    }
  }, [hasPermission])

  const connect = useCallback(async () => {
    if (!hasPermission || !isAuthenticated) {
      console.log('No permission or not authenticated for WebSocket connection')
      return
    }

    try {
      await slaWebSocketClient.connect()
      console.log('🔌 WebSocket connected successfully')
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      // Fallback to REST API
      await fetchDataFromAPI()
    }
  }, [hasPermission, isAuthenticated, fetchDataFromAPI])

  const disconnect = useCallback(() => {
    slaWebSocketClient.disconnect()
  }, [])

  const requestUpdate = useCallback(() => {
    if (isConnected) {
      slaWebSocketClient.requestUpdate()
    } else {
      fetchDataFromAPI()
    }
  }, [isConnected, fetchDataFromAPI])

  const acknowledgeAlert = useCallback(async (alertId: string) => {
    try {
      const result = await slaService.acknowledgeAlert(alertId)
      
      // Update local state
      setAlerts(prev => 
        prev.map(alert => 
          alert.id === alertId 
            ? { 
                ...alert, 
                acknowledged: true, 
                acknowledged_at: result.acknowledged_at,
                acknowledged_by: result.acknowledged_by
              }
            : alert
        )
      )
      
      return result
    } catch (error) {
      console.error('Failed to acknowledge alert:', error)
      throw error
    }
  }, [])

  // Initialize WebSocket connection
  useEffect(() => {
    if (!hasPermission || !isAuthenticated || isInitialized.current) {
      return
    }

    isInitialized.current = true

    // Set up event handlers
    slaWebSocketClient.onSLAUpdate(handleSLAUpdate)

    // Initial connection attempt
    connect()

    // Initial data fetch as fallback
    fetchDataFromAPI()

    return () => {
      disconnect()
      isInitialized.current = false
    }
  }, [hasPermission, isAuthenticated, connect, disconnect, handleSLAUpdate, handleConnectionChange, fetchDataFromAPI])

  return {
    systemHealth,
    alerts,
    isConnected,
    connectionState,
    lastUpdated,
    acknowledgeAlert,
    connect,
    disconnect,
    requestUpdate
  }
}
