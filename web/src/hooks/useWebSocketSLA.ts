import { useState, useEffect, useCallback, useRef } from 'react'
import { webSocketService, type WebSocketMessage, type SLAUpdateData } from '@/services/websocket-service'
import { useAuth } from '@/features/auth/hooks/useAuth'

export interface WebSocketSLAData {
  systemHealth: SLAUpdateData['system_health'] | null
  alerts: SLAUpdateData['alerts']
  connectionCount: number
  isConnected: boolean
  connectionState: string
  lastUpdated: Date | null
  connect: () => Promise<void>
  disconnect: () => void
  requestUpdate: () => void
}

export function useWebSocketSLA(): WebSocketSLAData {
  const { isAuthenticated, user } = useAuth()
  const [systemHealth, setSystemHealth] = useState<SLAUpdateData['system_health'] | null>(null)
  const [alerts, setAlerts] = useState<SLAUpdateData['alerts']>([])
  const [connectionCount, setConnectionCount] = useState(0)
  const [isConnected, setIsConnected] = useState(false)
  const [connectionState, setConnectionState] = useState('disconnected')
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  
  // Use refs to avoid stale closures in event handlers
  const systemHealthRef = useRef(systemHealth)
  const alertsRef = useRef(alerts)
  
  systemHealthRef.current = systemHealth
  alertsRef.current = alerts

  // Check if user has super admin permissions
  const hasPermission = user?.role === 'super_admin'

  const updateConnectionState = useCallback(() => {
    setIsConnected(webSocketService.isConnected)
    setConnectionState(webSocketService.connectionState)
  }, [])

  const handleSLAUpdate = useCallback((message: WebSocketMessage) => {
    if (message.type === 'sla_update' && message.data) {
      const data: SLAUpdateData = message.data
      setSystemHealth(data.system_health)
      setAlerts(data.alerts)
      setConnectionCount(data.connection_count || 0)
      setLastUpdated(new Date())
      console.log('📊 Updated SLA data from WebSocket')
    }
  }, [])

  const handleUptimeUpdate = useCallback((message: WebSocketMessage) => {
    if (message.type === 'uptime_update' && message.data) {
      // Update only uptime-related fields in system health
      setSystemHealth(current => {
        if (!current) return current
        return {
          ...current,
          uptime_percentage: message.data.uptime_percentage ?? current.uptime_percentage,
          uptime_duration: message.data.uptime_duration ?? current.uptime_duration,
          uptime_status: message.data.uptime_status ?? current.uptime_status,
          system_start_time: message.data.system_start_time ?? current.system_start_time
        }
      })
      setLastUpdated(new Date())
      console.log('⏱️ Updated uptime data from WebSocket')
    }
  }, [])

  const handleNewAlert = useCallback((message: WebSocketMessage) => {
    if (message.type === 'new_alert' && message.data) {
      // Add new alert to the beginning of the alerts array
      setAlerts(current => [message.data, ...current])
      setLastUpdated(new Date())
      console.log('🚨 Received new alert from WebSocket')
    }
  }, [])

  const handleConnectionEstablished = useCallback((message: WebSocketMessage) => {
    if (message.type === 'connection_established') {
      console.log('✅ WebSocket connection established')
      // Request initial data
      webSocketService.requestUpdate()
    }
  }, [])

  const connect = useCallback(async () => {
    if (!isAuthenticated || !hasPermission) {
      console.log('❌ Cannot connect WebSocket: not authenticated or insufficient permissions')
      return
    }

    try {
      await webSocketService.connect()
      updateConnectionState()
    } catch (error) {
      console.error('❌ Failed to connect WebSocket:', error)
      updateConnectionState()
    }
  }, [isAuthenticated, hasPermission, updateConnectionState])

  const disconnect = useCallback(() => {
    webSocketService.disconnect()
    updateConnectionState()
  }, [updateConnectionState])

  const requestUpdate = useCallback(() => {
    const success = webSocketService.requestUpdate()
    if (!success) {
      console.warn('⚠️ Failed to request update: WebSocket not connected')
    }
  }, [])

  // Set up event listeners
  useEffect(() => {
    // Add event listeners
    webSocketService.on('sla_update', handleSLAUpdate)
    webSocketService.on('uptime_update', handleUptimeUpdate)
    webSocketService.on('new_alert', handleNewAlert)
    webSocketService.on('connection_established', handleConnectionEstablished)

    // Update connection state periodically
    const stateInterval = setInterval(updateConnectionState, 1000)

    return () => {
      // Remove event listeners
      webSocketService.off('sla_update', handleSLAUpdate)
      webSocketService.off('uptime_update', handleUptimeUpdate)
      webSocketService.off('new_alert', handleNewAlert)
      webSocketService.off('connection_established', handleConnectionEstablished)
      
      clearInterval(stateInterval)
    }
  }, [handleSLAUpdate, handleUptimeUpdate, handleNewAlert, handleConnectionEstablished, updateConnectionState])

  // Auto-connect when authenticated and has permission
  useEffect(() => {
    if (isAuthenticated && hasPermission && !webSocketService.isConnected) {
      connect()
    } else if ((!isAuthenticated || !hasPermission) && webSocketService.isConnected) {
      disconnect()
    }
  }, [isAuthenticated, hasPermission, connect, disconnect])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [disconnect])

  return {
    systemHealth,
    alerts,
    connectionCount,
    isConnected,
    connectionState,
    lastUpdated,
    connect,
    disconnect,
    requestUpdate
  }
}
