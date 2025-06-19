import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { SLAUpdateData } from './websocket'
import { SLASystemHealth, SLAAlert } from '@/features/sla/services/sla-service'

interface SLADataState {
  systemHealth: SLASystemHealth | null
  alerts: SLAAlert[]
  connectionInfo: {
    active_connections: number
    update_interval: number
  } | null
  lastUpdated: Date | null
  isLoading: boolean
  error: string | null
  cacheTimestamp: number | null
}

interface SLADataStore extends SLADataState {
  updateData: (data: SLAUpdateData) => void
  setSystemHealth: (health: SLASystemHealth) => void
  setAlerts: (alerts: SLAAlert[]) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearData: () => void
  hasData: () => boolean
  hasFreshData: () => boolean
  restoreFromCache: () => void
}

export const useSLADataStore = create<SLADataStore>()(
  persist(
    (set, get) => ({
      systemHealth: null,
      alerts: [],
      connectionInfo: null,
      lastUpdated: null,
      isLoading: true,
      error: null,
      cacheTimestamp: null,

      updateData: (data: SLAUpdateData) => {
        const systemHealth: SLASystemHealth = {
          ...data.system_health,
          uptime_percentage: data.system_health.uptime_percentage,
          uptime_duration: data.system_health.uptime_duration,
          system_start_time: data.system_health.system_start_time || undefined,
          cpu_usage: data.system_health.metrics_summary.cpu_usage,
          memory_usage: data.system_health.metrics_summary.memory_usage,
          disk_usage: data.system_health.metrics_summary.disk_usage,
          database_response_time: data.system_health.metrics_summary.database_response_time,
          active_users_24h: data.system_health.metrics_summary.active_users,
          metrics_summary: data.system_health.metrics_summary
        }

        const now = new Date()
        set({
          systemHealth,
          alerts: data.alerts || [],
          connectionInfo: data.connection_info,
          lastUpdated: now,
          isLoading: false,
          error: null,
          cacheTimestamp: now.getTime()
        })
      },

      setSystemHealth: (health: SLASystemHealth) => {
        const now = new Date()
        set({ 
          systemHealth: health, 
          lastUpdated: now,
          cacheTimestamp: now.getTime()
        })
      },

      setAlerts: (alerts: SLAAlert[]) => {
        const now = new Date()
        set({ 
          alerts, 
          lastUpdated: now,
          cacheTimestamp: now.getTime()
        })
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading })
      },

      setError: (error: string | null) => {
        set({ error })
      },

      clearData: () => {
        set({
          systemHealth: null,
          alerts: [],
          connectionInfo: null,
          lastUpdated: null,
          isLoading: true,
          error: null,
          cacheTimestamp: null
        })
      },

      hasData: () => {
        const state = get()
        return state.systemHealth !== null || state.alerts.length > 0
      },

      hasFreshData: () => {
        const state = get()
        if (!state.cacheTimestamp) return false
        const now = Date.now()
        const fiveMinutesAgo = now - (5 * 60 * 1000) // 5 minutes cache
        return state.cacheTimestamp > fiveMinutesAgo
      },

      restoreFromCache: () => {
        // Data is automatically restored from localStorage via zustand persist
        const state = get()
        if (state.hasFreshData()) {
          set({ isLoading: false })
        }
      }
    }),
    {
      name: 'sla-data-cache',
      storage: typeof window !== 'undefined' ? {
        getItem: (key: string) => {
          try {
            const item = localStorage.getItem(key)
            return item ? JSON.parse(item) : null
          } catch {
            return null
          }
        },
        setItem: (key: string, value: any) => {
          try {
            localStorage.setItem(key, JSON.stringify(value))
          } catch {
            // Ignore localStorage errors
          }
        },
        removeItem: (key: string) => {
          try {
            localStorage.removeItem(key)
          } catch {
            // Ignore localStorage errors
          }
        }
      } : {
        getItem: () => null,
        setItem: () => {},
        removeItem: () => {}
      },
      partialize: (state) => ({
        systemHealth: state.systemHealth,
        alerts: state.alerts,
        connectionInfo: state.connectionInfo,
        lastUpdated: state.lastUpdated,
        cacheTimestamp: state.cacheTimestamp
      })
    }
  )
)
