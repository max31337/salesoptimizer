import { useState, useEffect, useRef, useCallback } from 'react'
import { slaWebSocketClient, type SLAUpdateData } from '@/lib/websocket'
import { slaService, type SLASystemHealth, type SLAAlert } from '../services/sla-service'

interface WebSocketSLAData {
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

export function useWebSocketSLA(autoConnect: boolean = true) {
  const [data, setData] = useState<WebSocketSLAData>({
    systemHealth: null,
    alerts: [],
    connectionInfo: null,
    isConnected: false,
    isLoading: true,
    error: null,
    lastUpdated: null
  })

  const isInitialized = useRef(false)
  const retryTimeout = useRef<NodeJS.Timeout | null>(null)
  // Handle SLA updates from WebSocket
  const handleSLAUpdate = useCallback((updateData: SLAUpdateData) => {    // Convert WebSocket data to SLA service types
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

    const alerts: SLAAlert[] = updateData.alerts

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
      
      // Request immediate update when connected
      slaWebSocketClient.requestUpdate()
    } else {
      // Set loading state when disconnected
      setData(prev => ({
        ...prev,
        isLoading: true
      }))
    }
  }, [])
  // Initialize WebSocket connection
  useEffect(() => {
    if (!autoConnect || isInitialized.current || typeof window === 'undefined') return

    // Subscribe to WebSocket events
    const unsubscribeSLAUpdate = slaWebSocketClient.onSLAUpdate(handleSLAUpdate)
    const unsubscribeConnectionStatus = slaWebSocketClient.onConnectionStatus(handleConnectionStatus)

    // Connect to WebSocket (only on client side)
    slaWebSocketClient.connect()
    isInitialized.current = true

    // Fallback: Load initial data via REST API if WebSocket doesn't connect quickly
    const fallbackTimeout = setTimeout(async () => {
      if (!slaWebSocketClient.getConnectionStatus()) {
        try {
          console.log('WebSocket not connected, falling back to REST API')
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
        } catch (error) {
          console.error('Failed to load SLA data via REST API:', error)
          setData(prev => ({
            ...prev,
            error: 'Failed to load SLA data',
            isLoading: false
          }))
        }
      }
    }, 3000) // Wait 3 seconds for WebSocket connection

    return () => {
      clearTimeout(fallbackTimeout)
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
