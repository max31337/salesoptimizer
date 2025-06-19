import { useState, useEffect, useRef, useCallback } from 'react'
import { slaWebSocketClient, type SLAUpdateData } from '@/lib/websocket'
import { slaService, type SLASystemHealth, type SLAAlert } from '../services/sla-service'

interface WebSocketSLAState {
  systemHealth: SLASystemHealth | null
  alerts: SLAAlert[]
  connectionInfo: {
    active_connections: number
    update_interval: number
  } | null
  isConnected: boolean
  isLoading: boolean
  error: string | null
  lastUpdated: Date | null
}

interface WebSocketSLAData extends WebSocketSLAState {
  refreshData: () => Promise<void>
  acknowledgeAlert: (alertId: string) => Promise<{ success: boolean; message: string; acknowledged_by: string; acknowledged_at: string }>
  connect: () => void
  disconnect: () => void
}

export function useWebSocketSLA(autoConnect: boolean = true): WebSocketSLAData {  const [data, setData] = useState<WebSocketSLAState>({
    systemHealth: null,
    alerts: [],
    connectionInfo: null,
    isConnected: false,
    isLoading: true,
    error: null,
    lastUpdated: null
  })

  const isInitialized = useRef(false)
  const retryTimeout = useRef<NodeJS.Timeout | null>(null)  // Handle SLA updates from WebSocket
  const handleSLAUpdate = useCallback((updateData: SLAUpdateData) => {
    console.log('🔄 Processing SLA update in hook:', updateData)
    
    // Check if we have valid data
    if (!updateData?.system_health) {
      console.error('❌ Invalid SLA update data - missing system_health:', updateData)
      return
    }
    
    // Convert WebSocket data to SLA service types
    const systemHealth: SLASystemHealth = {
      ...updateData.system_health,
      uptime_percentage: updateData.system_health.uptime_percentage,
      uptime_duration: updateData.system_health.uptime_duration,
      system_start_time: updateData.system_health.system_start_time || undefined,
      cpu_usage: updateData.system_health.metrics_summary.cpu_usage,
      memory_usage: updateData.system_health.metrics_summary.memory_usage,
      disk_usage: updateData.system_health.metrics_summary.disk_usage,
      database_response_time: updateData.system_health.metrics_summary.database_response_time,
      active_users_24h: updateData.system_health.metrics_summary.active_users,
      metrics_summary: updateData.system_health.metrics_summary
    }

    const alerts: SLAAlert[] = updateData.alerts || []

    console.log('✅ Setting SLA data in state:', { 
      systemHealthStatus: systemHealth.overall_status,
      healthPercentage: systemHealth.health_percentage,
      uptimePercentage: systemHealth.uptime_percentage,
      uptimeStatus: systemHealth.uptime_status,
      alertsCount: alerts.length,
      connectionInfo: updateData.connection_info
    })
    
    setData(prev => ({
      ...prev,
      systemHealth,
      alerts,
      connectionInfo: updateData.connection_info,
      isLoading: false,
      error: null,
      lastUpdated: new Date()
    }))
  }, [])
  // Handle connection status changes
  const handleConnectionStatus = useCallback((connected: boolean) => {
    setData(prev => ({
      ...prev,
      isConnected: connected,
      error: connected ? null : 'WebSocket disconnected'
    }))

    if (connected) {
      // Clear any retry timeout
      if (retryTimeout.current) {
        clearTimeout(retryTimeout.current)
        retryTimeout.current = null
      }
      
      // Request immediate update when connected (faster than waiting for backend push)
      console.log('🔄 WebSocket connected, requesting immediate data update...')
      slaWebSocketClient.requestUpdate()
    } else {
      // Don't set loading state when disconnected since we have REST API data
      console.log('🔌 WebSocket disconnected, will rely on REST API data')
    }
  }, [])
  // Initialize WebSocket connection
  useEffect(() => {
    if (!autoConnect || isInitialized.current || typeof window === 'undefined') return

    console.log('🔌 Initializing WebSocket connection...')

    // Check if WebSocket is already connected (from previous component mount)
    if (slaWebSocketClient.getConnectionStatus()) {
      console.log('✅ WebSocket already connected, skipping reconnection')
      setData(prev => ({
        ...prev,
        isConnected: true,
        isLoading: false
      }))
      
      // Request data update since we're using existing connection
      slaWebSocketClient.requestUpdate()
      isInitialized.current = true
      return
    }    console.log('🔌 Setting up new WebSocket connection...')

    // Subscribe to WebSocket events
    const unsubscribeSLAUpdate = slaWebSocketClient.onSLAUpdate(handleSLAUpdate)
    const unsubscribeConnectionStatus = slaWebSocketClient.onConnectionStatus(handleConnectionStatus)

    // Immediately start loading data via REST API for faster initial load
    const loadInitialData = async () => {
      try {
        console.log('🚀 Loading initial data via REST API for fast display...')
        const [systemHealth, alerts] = await Promise.all([
          slaService.getSystemHealth(),
          slaService.getCurrentAlerts()
        ])

        setData(prev => ({
          ...prev,
          systemHealth,
          alerts,
          isLoading: false,
          lastUpdated: new Date()
        }))
        console.log('✅ Initial data loaded via REST API')
      } catch (error) {
        console.error('Failed to load initial SLA data via REST API:', error)
        setData(prev => ({
          ...prev,
          error: 'Failed to load initial data',
          isLoading: false
        }))
      }
    }

    // Load initial data immediately
    loadInitialData()

    // Connect to WebSocket in parallel (will overlay data when connected)
    const connectWebSocket = async () => {
      try {
        await slaWebSocketClient.connect()
      } catch (error) {
        console.error('Failed to connect WebSocket:', error)
      }
    }    
    connectWebSocket()
    isInitialized.current = true

    return () => {
      unsubscribeSLAUpdate()
      unsubscribeConnectionStatus()
    }
  }, [autoConnect, handleSLAUpdate, handleConnectionStatus])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (retryTimeout.current) {
        clearTimeout(retryTimeout.current)
      }
    }
  }, [])

  // Manual refresh function (fallback to REST API)
  const refreshData = useCallback(async () => {
    try {
      setData(prev => ({ ...prev, isLoading: true, error: null }))

      if (slaWebSocketClient.getConnectionStatus()) {
        // If WebSocket is connected, request update
        slaWebSocketClient.requestUpdate()
      } else {
        // Otherwise, use REST API
        const [systemHealth, alerts] = await Promise.all([
          slaService.getSystemHealth(),
          slaService.getCurrentAlerts()
        ])

        setData(prev => ({
          ...prev,
          systemHealth,
          alerts,
          isLoading: false,
          lastUpdated: new Date()
        }))
      }
    } catch (error) {
      console.error('Failed to refresh SLA data:', error)
      setData(prev => ({
        ...prev,
        error: 'Failed to refresh data',
        isLoading: false
      }))
    }
  }, [])

  // Acknowledge alert function with WebSocket integration
  const acknowledgeAlert = useCallback(async (alertId: string) => {
    try {
      const response = await slaService.acknowledgeAlert(alertId)
      
      // Update local state immediately for better UX
      setData(prev => ({
        ...prev,
        alerts: prev.alerts.map(alert => 
          alert.id === alertId 
            ? { 
                ...alert, 
                acknowledged: true, 
                acknowledged_at: response.acknowledged_at,
                acknowledged_by: response.acknowledged_by
              }
            : alert
        )
      }))

      // WebSocket will send real-time update to all clients
      return response
    } catch (error) {
      console.error('Failed to acknowledge alert:', error)
      throw error
    }
  }, [])

  // Connect/disconnect functions
  const connect = useCallback(() => {
    slaWebSocketClient.connect()
  }, [])

  const disconnect = useCallback(() => {
    slaWebSocketClient.disconnect()
    setData(prev => ({
      ...prev,
      isConnected: false
    }))
  }, [])
  return {
    ...data,
    refreshData,
    acknowledgeAlert,
    connect,
    disconnect
  }
}

