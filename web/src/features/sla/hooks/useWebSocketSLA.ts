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
  // Use the persistent global store
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
    hasData: hasStoreData,
    hasFreshData,
    restoreFromCache
  } = useSLADataStore()

  const [isConnected, setIsConnected] = useState(false)
  const isInitialized = useRef(false)
  const retryTimeout = useRef<NodeJS.Timeout | null>(null)
  // Initialize with cached data on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      // Try to restore from cache first
      restoreFromCache()
      
      // If we have fresh cached data, show it immediately and don't show loading
      if (hasFreshData()) {
        console.log('📦 Using fresh cached SLA data - stopping loading state')
        setStoreLoading(false)
      } else if (hasStoreData()) {
        // If we have stale data, show it but keep loading state to indicate refresh
        console.log('📦 Using stale cached SLA data - keeping loading state for refresh')
        setStoreLoading(true)
      } else {
        // No data at all, definitely loading
        console.log('📦 No cached SLA data - showing loading state')
        setStoreLoading(true)
      }
    }
  }, [hasFreshData, hasStoreData, restoreFromCache, setStoreLoading])

  // Handle SLA updates from WebSocket
  const handleSLAUpdate = useCallback((updateData: SLAUpdateData) => {
    console.log('🔄 Processing SLA update in hook:', updateData)
    
    if (!updateData?.system_health) {
      console.error('❌ Invalid SLA update data - missing system_health:', updateData)
      return
    }
    
    updateStoreData(updateData)
    console.log('✅ Updated SLA data in store and cache')
  }, [updateStoreData])

  // Handle connection status changes  
  const handleConnectionStatus = useCallback((connected: boolean) => {
    setIsConnected(connected)
    
    if (connected) {
      console.log('✅ WebSocket connected')
      setStoreError(null)
      
      // Clear any retry timeout
      if (retryTimeout.current) {
        clearTimeout(retryTimeout.current)
        retryTimeout.current = null
      }
      
      // Request immediate update when connected
      setTimeout(() => {
        slaWebSocketClient.requestUpdate()
      }, 100)
    } else {
      console.log('❌ WebSocket disconnected')
      setStoreError('WebSocket disconnected')
    }
  }, [setStoreError])
  // Load initial data from REST API as fallback
  const loadInitialData = useCallback(async () => {
    // If we have fresh data, don't make unnecessary API calls
    if (hasFreshData()) {
      console.log('📦 Fresh data available, skipping REST API load')
      setStoreLoading(false)
      return
    }

    // If we have stale data, keep it visible while refreshing
    if (hasStoreData()) {
      console.log('📦 Stale data available, refreshing in background...')
      // Don't set loading to true here to avoid hiding the stale data
    } else {
      console.log('🌐 No data available, loading initial SLA data via REST API...')
      setStoreLoading(true)
    }

    try {
      const [systemHealth, alerts] = await Promise.all([
        slaService.getSystemHealth(),
        slaService.getCurrentAlerts()
      ])

      // Create update data structure for the store
      const updateData: SLAUpdateData = {
        system_health: {
          overall_status: systemHealth.overall_status,
          health_percentage: systemHealth.health_percentage,
          uptime_status: systemHealth.uptime_status,
          uptime_percentage: systemHealth.uptime_percentage || 0,
          uptime_duration: systemHealth.uptime_duration || '',
          system_start_time: systemHealth.system_start_time || null,
          last_updated: systemHealth.last_updated,
          total_metrics: systemHealth.total_metrics,
          healthy_metrics: systemHealth.healthy_metrics,
          warning_metrics: systemHealth.warning_metrics,
          critical_metrics: systemHealth.critical_metrics,
          metrics_summary: systemHealth.metrics_summary
        },
        alerts: alerts.map(alert => ({
          id: alert.id,
          alert_type: alert.alert_type,
          title: alert.title,
          message: alert.message,
          metric_type: alert.metric_type,
          current_value: alert.current_value,
          threshold_value: alert.threshold_value,
          triggered_at: alert.triggered_at,
          acknowledged: alert.acknowledged,
          acknowledged_at: alert.acknowledged_at,
          acknowledged_by: alert.acknowledged_by
        })),
        connection_info: {
          active_connections: 1,
          update_interval: 30000
        }
      }

      updateStoreData(updateData)
      console.log('✅ Initial SLA data loaded via REST API')
    } catch (error) {
      console.error('❌ Failed to load initial SLA data:', error)
      setStoreError('Failed to load SLA data')
    } finally {
      setStoreLoading(false)
    }
  }, [hasFreshData, hasStoreData, updateStoreData, setStoreLoading, setStoreError])

  // Initialize WebSocket connection
  useEffect(() => {
    if (!autoConnect || isInitialized.current || typeof window === 'undefined') return

    console.log('🔌 Initializing WebSocket SLA connection...')
    isInitialized.current = true

    // Load initial data immediately (from cache or REST API)
    loadInitialData()

    // Subscribe to WebSocket events
    const unsubscribeSLAUpdate = slaWebSocketClient.onSLAUpdate(handleSLAUpdate)
    const unsubscribeConnectionStatus = slaWebSocketClient.onConnectionStatus(handleConnectionStatus)

    // Start WebSocket connection
    slaWebSocketClient.connect().catch((error: Error) => {
      console.error('❌ Failed to connect WebSocket:', error)
    })

    return () => {
      unsubscribeSLAUpdate()
      unsubscribeConnectionStatus()
      if (retryTimeout.current) {
        clearTimeout(retryTimeout.current)
      }
    }
  }, [autoConnect, handleSLAUpdate, handleConnectionStatus, loadInitialData])
  // Manual refresh function
  const refreshData = useCallback(async () => {
    try {
      // Only show loading if we don't have any data to avoid hiding current data
      if (!hasStoreData()) {
        setStoreLoading(true)
      }
      setStoreError(null)

      if (isConnected) {
        // If WebSocket is connected, request update
        console.log('🔄 Requesting WebSocket update...')
        slaWebSocketClient.requestUpdate()
      } else {
        // Otherwise, use REST API
        console.log('🔄 Refreshing via REST API...')
        const [systemHealth, alerts] = await Promise.all([
          slaService.getSystemHealth(),
          slaService.getCurrentAlerts()
        ])

        const updateData: SLAUpdateData = {
          system_health: {
            overall_status: systemHealth.overall_status,
            health_percentage: systemHealth.health_percentage,
            uptime_status: systemHealth.uptime_status,
            uptime_percentage: systemHealth.uptime_percentage || 0,
            uptime_duration: systemHealth.uptime_duration || '',
            system_start_time: systemHealth.system_start_time || null,
            last_updated: systemHealth.last_updated,
            total_metrics: systemHealth.total_metrics,
            healthy_metrics: systemHealth.healthy_metrics,
            warning_metrics: systemHealth.warning_metrics,
            critical_metrics: systemHealth.critical_metrics,
            metrics_summary: systemHealth.metrics_summary
          },
          alerts: alerts.map(alert => ({
            id: alert.id,
            alert_type: alert.alert_type,
            title: alert.title,
            message: alert.message,
            metric_type: alert.metric_type,
            current_value: alert.current_value,
            threshold_value: alert.threshold_value,
            triggered_at: alert.triggered_at,
            acknowledged: alert.acknowledged,
            acknowledged_at: alert.acknowledged_at,
            acknowledged_by: alert.acknowledged_by
          })),
          connection_info: {
            active_connections: 1,
            update_interval: 30000
          }
        }

        updateStoreData(updateData)
        console.log('✅ Data refreshed via REST API')
      }
    } catch (error) {
      console.error('❌ Failed to refresh SLA data:', error)
      setStoreError('Failed to refresh data')
    } finally {
      setStoreLoading(false)
    }
  }, [isConnected, hasStoreData, updateStoreData, setStoreLoading, setStoreError])

  // Acknowledge alert function with better error handling
  const acknowledgeAlert = useCallback(async (alertId: string) => {
    try {
      // First check if the alert exists and is not already acknowledged
      const alertToAcknowledge = storeAlerts.find(alert => alert.id === alertId)
      
      if (!alertToAcknowledge) {
        console.warn(`⚠️ Alert ${alertId} not found in current alerts`)
        throw new Error('Alert not found')
      }
      
      if (alertToAcknowledge.acknowledged) {
        console.warn(`⚠️ Alert ${alertId} is already acknowledged`)
        return {
          success: false,
          message: 'Alert is already acknowledged',
          acknowledged_by: alertToAcknowledge.acknowledged_by || '',
          acknowledged_at: alertToAcknowledge.acknowledged_at || ''
        }
      }
      
      console.log(`🔄 Acknowledging alert ${alertId}...`)
      const response = await slaService.acknowledgeAlert(alertId)
      
      // Update alerts in store immediately for better UX
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
      console.log(`✅ Alert ${alertId} acknowledged and cached`)

      return response
    } catch (error) {
      console.error(`❌ Failed to acknowledge alert ${alertId}:`, error)
      
      // If the error is that the alert doesn't exist or is already acknowledged,
      // refresh the data to get the latest state
      if (error instanceof Error && 
          (error.message.includes('not found') || error.message.includes('already acknowledged'))) {
        console.log('🔄 Refreshing data due to stale alert state...')
        try {
          await refreshData()
        } catch (refreshError) {
          console.error('Failed to refresh data:', refreshError)
        }
      }
      
      throw error
    }
  }, [storeAlerts, setStoreAlerts, refreshData])

  // Connect/disconnect functions
  const connect = useCallback(() => {
    slaWebSocketClient.connect()
  }, [])

  const disconnect = useCallback(() => {
    slaWebSocketClient.disconnect()
    setIsConnected(false)
  }, [])

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
