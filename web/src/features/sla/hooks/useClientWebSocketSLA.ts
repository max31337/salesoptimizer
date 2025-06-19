'use client'

import { useEffect, useState } from 'react'
import { useWebSocketSLA } from '@/features/sla/hooks/useWebSocketSLA'

export function useClientWebSocketSLA(autoConnect: boolean = true) {
  const [isClient, setIsClient] = useState(false)
  const hookResult = useWebSocketSLA(isClient && autoConnect)

  useEffect(() => {
    setIsClient(true)
  }, [])

  // Return default values during SSR
  if (!isClient) {
    return {
      systemHealth: null,
      alerts: [],
      connectionInfo: null,
      isConnected: false,
      isLoading: true,
      error: null,
      lastUpdated: null,
      refreshData: async () => {},
      acknowledgeAlert: async () => ({ success: false, message: '', acknowledged_by: '', acknowledged_at: '' }),
      connect: () => {},
      disconnect: () => {}
    }
  }

  return hookResult
}
