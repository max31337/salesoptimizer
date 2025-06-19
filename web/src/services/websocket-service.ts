import { getCookie } from '@/lib/utils'

export interface WebSocketMessage {
  type: string
  timestamp: string
  data?: any
  message?: string
}

export interface SLAUpdateData {
  system_health: {
    overall_status: string
    health_percentage: number
    uptime_status: string
    uptime_percentage?: number
    uptime_duration?: string
    system_start_time?: string
    total_metrics: number
    healthy_metrics: number
    warning_metrics: number
    critical_metrics: number
    metrics_summary: {
      cpu_usage: number
      memory_usage: number
      disk_usage: number
      database_response_time: number
      active_users: number
      database_connections: number
    }
    last_updated: string
  }
  alerts: Array<{
    id: string
    alert_type: string
    title: string
    message: string
    metric_type: string
    current_value: number
    threshold_value: number
    triggered_at: string
    acknowledged: boolean
    acknowledged_at?: string
    acknowledged_by?: string
  }>
  connection_count: number
}

export type WebSocketEventHandler = (message: WebSocketMessage) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000 // Start with 1 second
  private maxReconnectDelay = 30000 // Max 30 seconds
  private heartbeatInterval: NodeJS.Timeout | null = null
  private isIntentionallyClosed = false
  private baseUrl: string
  private eventHandlers: Map<string, Set<WebSocketEventHandler>> = new Map()

  constructor() {
    // Use WebSocket protocol based on current protocol
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = process.env.NEXT_PUBLIC_API_URL || 'localhost:8000'
    // Remove http/https prefix if present
    const cleanHost = host.replace(/^https?:\/\//, '')
    this.baseUrl = `${protocol}//${cleanHost}/api/v1`
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve()
        return
      }

      this.isIntentionallyClosed = false

      // Get authentication token from cookie
      const accessToken = getCookie('access_token')
      if (!accessToken) {
        reject(new Error('No authentication token found'))
        return
      }

      const wsUrl = `${this.baseUrl}/ws/sla-monitoring?token=${encodeURIComponent(accessToken)}`
      
      console.log('🔌 Connecting to WebSocket:', wsUrl)
      
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log('✅ WebSocket connected')
        this.reconnectAttempts = 0
        this.reconnectDelay = 1000
        this.startHeartbeat()
        resolve()
      }

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          this.handleMessage(message)
        } catch (error) {
          console.error('❌ Error parsing WebSocket message:', error)
        }
      }

      this.ws.onclose = (event) => {
        console.log('🔌 WebSocket closed:', event.code, event.reason)
        this.stopHeartbeat()
        
        if (!this.isIntentionallyClosed && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect()
        }
      }

      this.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error)
        reject(error)
      }
    })
  }

  disconnect(): void {
    this.isIntentionallyClosed = true
    this.stopHeartbeat()
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnecting')
      this.ws = null
    }
  }

  private scheduleReconnect(): void {
    this.reconnectAttempts++
    const delay = Math.min(this.reconnectDelay * this.reconnectAttempts, this.maxReconnectDelay)
    
    console.log(`🔄 Scheduling reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`)
    
    setTimeout(() => {
      if (!this.isIntentionallyClosed) {
        this.connect().catch(error => {
          console.error('❌ Reconnect failed:', error)
        })
      }
    }, delay)
  }

  private startHeartbeat(): void {
    this.stopHeartbeat()
    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({
          type: 'ping',
          timestamp: new Date().toISOString()
        })
      }
    }, 30000) // Ping every 30 seconds
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  private handleMessage(message: WebSocketMessage): void {
    console.log('📨 Received WebSocket message:', message.type)
    
    // Emit to specific event handlers
    const handlers = this.eventHandlers.get(message.type)
    if (handlers) {
      handlers.forEach(handler => handler(message))
    }

    // Emit to global handlers
    const globalHandlers = this.eventHandlers.get('*')
    if (globalHandlers) {
      globalHandlers.forEach(handler => handler(message))
    }
  }

  send(data: any): boolean {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
      return true
    }
    return false
  }

  requestUpdate(): boolean {
    return this.send({
      type: 'request_update',
      timestamp: new Date().toISOString()
    })
  }

  // Event handling
  on(eventType: string, handler: WebSocketEventHandler): void {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, new Set())
    }
    this.eventHandlers.get(eventType)!.add(handler)
  }

  off(eventType: string, handler: WebSocketEventHandler): void {
    const handlers = this.eventHandlers.get(eventType)
    if (handlers) {
      handlers.delete(handler)
      if (handlers.size === 0) {
        this.eventHandlers.delete(eventType)
      }
    }
  }

  // Connection status
  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  get connectionState(): string {
    if (!this.ws) return 'disconnected'
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'connecting'
      case WebSocket.OPEN: return 'connected'
      case WebSocket.CLOSING: return 'closing'
      case WebSocket.CLOSED: return 'closed'
      default: return 'unknown'
    }
  }
}

// Global WebSocket service instance
export const webSocketService = new WebSocketService()

// Utility function to get cookie value
function getCookieValue(name: string): string | null {
  if (typeof document === 'undefined') return null
  
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) {
    const cookieValue = parts.pop()?.split(';').shift()
    return cookieValue || null
  }
  return null
}
