import { useState, useEffect, useCallback } from 'react'
import { slaService, type SLASystemHealth, type SLAAlert, type SLAMetric } from '../services/sla-service'

export function useSLAData(autoRefresh: boolean = true, refreshInterval: number = 30000) {
  const [systemHealth, setSystemHealth] = useState<SLASystemHealth | null>(null)
  const [alerts, setAlerts] = useState<SLAAlert[]>([])
  const [metrics, setMetrics] = useState<SLAMetric[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const fetchSystemHealth = useCallback(async () => {
    try {
      const data = await slaService.getSystemHealth()
      setSystemHealth(data)
      setError(null)
    } catch (err) {
      console.error('Failed to fetch system health:', err)
      setError('Failed to fetch system health data')
    }
  }, [])

  const fetchAlerts = useCallback(async () => {
    try {
      const data = await slaService.getCurrentAlerts()
      setAlerts(data)
      setError(null)
    } catch (err) {
      console.error('Failed to fetch alerts:', err)
      setError('Failed to fetch alerts data')
    }
  }, [])

  const fetchMetrics = useCallback(async (metricTypes?: string[]) => {
    try {
      const data = await slaService.getMetrics(metricTypes)
      setMetrics(data)
      setError(null)
    } catch (err) {
      console.error('Failed to fetch metrics:', err)
      setError('Failed to fetch metrics data')
    }
  }, [])

  const fetchAllData = useCallback(async () => {
    setIsLoading(true)
    try {
      await Promise.all([
        fetchSystemHealth(),
        fetchAlerts(),
        fetchMetrics()
      ])
      setLastUpdated(new Date())
    } catch (err) {
      console.error('Failed to fetch SLA data:', err)
    } finally {
      setIsLoading(false)
    }
  }, [fetchSystemHealth, fetchAlerts, fetchMetrics])

  const acknowledgeAlert = useCallback(async (alertId: string) => {
    try {
      const response = await slaService.acknowledgeAlert(alertId)
      
      // Update the alert in the local state
      setAlerts(prevAlerts => 
        prevAlerts.map(alert => 
          alert.id === alertId 
            ? { 
                ...alert, 
                acknowledged: true, 
                acknowledged_at: response.acknowledged_at,
                acknowledged_by: response.acknowledged_by
              }
            : alert
        )
      )
      
      // Refresh system health to update counts
      await fetchSystemHealth()
      
      return response
    } catch (err) {
      console.error('Failed to acknowledge alert:', err)
      throw err
    }
  }, [fetchSystemHealth])

  const refreshData = useCallback(() => {
    fetchAllData()
  }, [fetchAllData])

  // Initial data fetch
  useEffect(() => {
    fetchAllData()
  }, [fetchAllData])

  // Auto-refresh setup
  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      fetchAllData()
    }, refreshInterval)

    return () => clearInterval(interval)
  }, [autoRefresh, refreshInterval, fetchAllData])

  return {
    systemHealth,
    alerts,
    metrics,
    isLoading,
    error,
    lastUpdated,
    acknowledgeAlert,
    refreshData,
    fetchMetrics
  }
}
