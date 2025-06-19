import { useState, useEffect, useRef, useCallback } from 'react'
import { slaWebSocketClient, type SLAUpdateData } from '@/lib/websocket'
import { slaService, type SLASystemHealth, type SLAAlert } from '../services/sla-service'
import { useSLADataStore } from '@/lib/sla-data-store'

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

export function useWebSocketSLA(autoConnect: boolean = true): WebSocketSLAData {
  // Use the global store for persistent data across navigation
  const {
    systemHealth: storeSystemHealth,
    alerts: storeAlerts,
    connectionInfo: storeConnectionInfo,
    lastUpdated: storeLastUpdated,
    isLoading: storeIsLoading,
    error: storeError,
    updateData: updateStoreData,
    setLoading: setStoreLoading,
    setError: setStoreError,
    setAlerts: setStoreAlerts,
    hasData: hasStoreData
  } = useSLADataStore()

  const [isConnected, setIsConnected] = useState(false)
  const isInitialized = useRef(false)
  const retryTimeout = useRef<NodeJS.Timeout | null>(null)

  // Initialize store with cached data if available on first load
  useEffect(() => {
    if (!hasStoreData() && typeof window !== 'undefined') {
      const cachedData = slaWebSocketClient.getCachedData()
      if (cachedData) {
        console.log('🔄 Initializing store with cached WebSocket data')
        updateStoreData(cachedData)
        setStoreLoading(false)
      }
    }
  }, [hasStoreData, updateStoreData, setStoreLoading])

  // Handle SLA updates from WebSocket
  const handleSLAUpdate = useCallback((updateData: SLAUpdateData) => {
    console.log('🔄 Processing SLA update in hook:', updateData)
    
    // Check if we have valid data
    if (!updateData?.system_health) {
      console.error('❌ Invalid SLA update data - missing system_health:', updateData)
      return
    }
    
    // Update the global store
    updateStoreData(updateData)
    console.log('✅ Updated SLA data in global store')
  }, [updateStoreData])

  // Handle connection status changes
  const handleConnectionStatus = useCallback((connected: boolean) => {
    setIsConnected(connected)

    if (connected) {
      // Clear any retry timeout
      if (retryTimeout.current) {
        clearTimeout(retryTimeout.current)
        retryTimeout.current = null
      }
      
      // Clear any errors when connected
      setStoreError(null)
      
      // Request immediate update when connected
      console.log('🔄 WebSocket connected, requesting immediate data update...')
      slaWebSocketClient.requestUpdate()
    } else {
      // Don't set loading state when disconnected since we have cached/REST API data
      console.log('🔌 WebSocket disconnected, will rely on cached/REST API data')
    }
  }, [setStoreError])

  // Initialize WebSocket connection
  useEffect(() => {
    if (!autoConnect || isInitialized.current || typeof window === 'undefined') return

    console.log('🔌 Initializing WebSocket connection...')

    // Set connection status from existing connection
    setIsConnected(slaWebSocketClient.getConnectionStatus())

    // Subscribe to WebSocket events
    const unsubscribeSLAUpdate = slaWebSocketClient.onSLAUpdate(handleSLAUpdate)
    const unsubscribeConnectionStatus = slaWebSocketClient.onConnectionStatus(handleConnectionStatus)

    // Check if WebSocket is already connected (from previous component mount)
    if (slaWebSocketClient.getConnectionStatus()) {
      console.log('✅ WebSocket already connected, requesting fresh data')
      slaWebSocketClient.requestUpdate()
      isInitialized.current = true
      return
    }

    // Immediately start loading data if we don't have any
    const loadInitialData = async () => {
      // Skip loading if we already have fresh cached data or store data
      if (slaWebSocketClient.hasFreshCachedData() || hasStoreData()) {
        console.log('🔄 Using cached/store data, skipping REST API call')
        setStoreLoading(false)
        return
      }

      try {
        console.log('🚀 Loading initial data via REST API for fast display...')
        setStoreLoading(true)
        const [systemHealth, alerts] = await Promise.all([
          slaService.getSystemHealth(),
          slaService.getCurrentAlerts()
        ])

        // Create updateData format for store
        const updateData: SLAUpdateData = {
          system_health: {
            ...systemHealth,
            system_start_time: systemHealth.system_start_time || null,
            uptime_percentage: systemHealth.uptime_percentage ?? 0,
            uptime_duration: systemHealth.uptime_duration ?? '',
            metrics_summary: systemHealth.metrics_summary
          },
          alerts,
          connection_info: {
            active_connections: 1,
            update_interval: 30000
          }
        }

        updateStoreData(updateData)
        console.log('✅ Initial data loaded via REST API')
      } catch (error) {
        console.error('Failed to load initial SLA data via REST API:', error)
        setStoreError('Failed to load initial data')
        setStoreLoading(false)
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
  }, [autoConnect, handleSLAUpdate, handleConnectionStatus, hasStoreData, setStoreLoading, setStoreError, updateStoreData])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (retryTimeout.current) {
        clearTimeout(retryTimeout.current)
      }
    }
  }, [])

  // Manual refresh function
  const refreshData = useCallback(async () => {
    try {
      setStoreLoading(true)
      setStoreError(null)

      if (slaWebSocketClient.getConnectionStatus()) {
        // If WebSocket is connected, request update
        slaWebSocketClient.requestUpdate()
      } else {
        // Otherwise, use REST API
        const [systemHealth, alerts] = await Promise.all([
          slaService.getSystemHealth(),
          slaService.getCurrentAlerts()
        ])

        const updateData: SLAUpdateData = {
          system_health: {
            ...systemHealth,
            system_start_time: systemHealth.system_start_time || null,
            uptime_percentage: systemHealth.uptime_percentage ?? 0,
            uptime_duration: systemHealth.uptime_duration ?? '',
            metrics_summary: systemHealth.metrics_summary
          },
          alerts,
          connection_info: {
            active_connections: 1,
            update_interval: 30000
          }
        }

        updateStoreData(updateData)
      }
    } catch (error) {
      console.error('Failed to refresh SLA data:', error)
      setStoreError('Failed to refresh data')
      setStoreLoading(false)
    }
  }, [setStoreLoading, setStoreError, updateStoreData])

  // Acknowledge alert function
  const acknowledgeAlert = useCallback(async (alertId: string) => {
    try {
      const response = await slaService.acknowledgeAlert(alertId)
      
      // Update local state immediately for better UX
      const updatedAlerts = storeAlerts.map(alert => 
        alert.id === alertId 
          ? { 
              ...alert, 
              acknowledged: true, 
              acknowledged_at: response.acknowledged_at,
              acknowledged_by: response.acknowledged_by
            }
          : alert
      )
      
      setStoreAlerts(updatedAlerts)

      // WebSocket will send real-time update to all clients
      return response
    } catch (error) {
      console.error('Failed to acknowledge alert:', error)
      throw error
    }
  }, [storeAlerts, setStoreAlerts])

  // Connect/disconnect functions
  const connect = useCallback(() => {
    slaWebSocketClient.connect()
  }, [])

  const disconnect = useCallback(() => {
    slaWebSocketClient.disconnect()
    setIsConnected(false)
  }, [])

  // Return combined state from store and local state
  return {
    systemHealth: storeSystemHealth,
    alerts: storeAlerts,
    connectionInfo: storeConnectionInfo,
    isConnected,
    isLoading: storeIsLoading,
    error: storeError,
    lastUpdated: storeLastUpdated,
    refreshData,
    acknowledgeAlert,
    connect,
    disconnect
  }
}
