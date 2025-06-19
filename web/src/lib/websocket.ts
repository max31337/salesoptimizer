// Simple cookie utility function
function getCookie(name: string): string | null {
  // Check if we're on the client side
  if (typeof document === 'undefined') return null
  
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
  return null;
}

export interface WebSocketMessage {
  type: string
  timestamp: string
  data?: any
}

export interface SLAUpdateData {
  system_health: {
    overall_status: 'healthy' | 'warning' | 'critical'
    health_percentage: number
    uptime_status: string
    uptime_percentage: number
    uptime_duration: string
    system_start_time: string | null
    last_updated: string
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
  }
  alerts: Array<{
    id: string
    alert_type: 'warning' | 'critical'
    title: string
    message: string
    metric_type: string
    current_value: number
    threshold_value: number
    triggered_at: string
    acknowledged: boolean
    acknowledged_at: string | null
    acknowledged_by: string | null
  }>
  connection_info: {
    active_connections: number
    update_interval: number
  }
}

type MessageHandler = (message: WebSocketMessage) => void
type SLAUpdateHandler = (data: SLAUpdateData) => void
type ConnectionStatusHandler = (connected: boolean) => void

export class SLAWebSocketClient {
  private ws: WebSocket | null = null
  private url: string | null = null
  private token: string | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000 // Start with 1 second
  private maxReconnectDelay = 30000 // Max 30 seconds
  private reconnectTimer: NodeJS.Timeout | null = null
  private pingTimer: NodeJS.Timeout | null = null
  private isConnected = false
  private shouldReconnect = true

  // Event handlers
  private messageHandlers: MessageHandler[] = []
  private slaUpdateHandlers: SLAUpdateHandler[] = []
  private connectionStatusHandlers: ConnectionStatusHandler[] = []

  constructor() {
    // Don't initialize URL during SSR - will be set when connect() is called
    this.url = null
  }

  private initializeUrl(): void {
    if (this.url || typeof window === 'undefined') return
    
    // Construct WebSocket URL only on client side
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = process.env.NODE_ENV === 'development' 
      ? 'localhost:8000' 
      : window.location.host
    this.url = `${protocol}//${host}/api/v1/ws/sla-monitoring`
  }
  private getAuthToken(): string | null {
    // Check if we're on the client side
    if (typeof window === 'undefined') return null
    
    // Try to get token from cookie or localStorage
    return getCookie('access_token') || localStorage.getItem('access_token')
  }

  public connect(): void {
    // Check if we're on the client side
    if (typeof window === 'undefined') {
      console.warn('Cannot connect WebSocket on server side')
      return
    }

    this.initializeUrl()
    
    if (!this.url) {
      console.error('WebSocket URL not initialized')
      return
    }

    this.token = this.getAuthToken()
    if (!this.token) {
      console.error('No authentication token found for WebSocket connection')
      return
    }

    if (this.ws && (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN)) {
      return // Already connecting or connected
    }

    const wsUrl = `${this.url}?token=${this.token}`
    console.log('Connecting to SLA WebSocket:', wsUrl)

    try {
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log('SLA WebSocket connected')
        this.isConnected = true
        this.reconnectAttempts = 0
        this.reconnectDelay = 1000
        this.notifyConnectionStatus(true)
        this.startPingInterval()
      }

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          this.handleMessage(message)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      this.ws.onclose = (event) => {
        console.log('SLA WebSocket closed:', event.code, event.reason)
        this.isConnected = false
        this.notifyConnectionStatus(false)
        this.stopPingInterval()

        if (this.shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect()
        }
      }

      this.ws.onerror = (error) => {
        console.error('SLA WebSocket error:', error)
        this.isConnected = false
        this.notifyConnectionStatus(false)
      }
    } catch (error) {
      console.error('Error creating WebSocket connection:', error)
    }
  }

  private handleMessage(message: WebSocketMessage): void {
    // Notify all message handlers
    this.messageHandlers.forEach(handler => handler(message))

    // Handle specific message types
    switch (message.type) {
      case 'connection_established':
        console.log('SLA WebSocket connection established:', message.data)
        break

      case 'sla_update':
        if (message.data) {
          this.slaUpdateHandlers.forEach(handler => handler(message.data))
        }
        break

      case 'uptime_update':
        console.log('Uptime update received:', message.data)
        break

      case 'new_alert':
        console.log('New alert received:', message.data)
        // You could show a notification here
        break

      case 'pong':
        // Handle ping response
        break

      default:
        console.log('Unknown message type:', message.type, message)
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
    }

    this.reconnectAttempts++
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), this.maxReconnectDelay)

    console.log(`Scheduling WebSocket reconnect attempt ${this.reconnectAttempts} in ${delay}ms`)

    this.reconnectTimer = setTimeout(() => {
      if (this.shouldReconnect) {
        this.connect()
      }
    }, delay)
  }

  private startPingInterval(): void {
    this.pingTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send({
          type: 'ping',
          timestamp: new Date().toISOString()
        })
      }
    }, 30000) // Ping every 30 seconds
  }

  private stopPingInterval(): void {
    if (this.pingTimer) {
      clearInterval(this.pingTimer)
      this.pingTimer = null
    }
  }

  private notifyConnectionStatus(connected: boolean): void {
    this.connectionStatusHandlers.forEach(handler => handler(connected))
  }

  public send(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected, cannot send message:', message)
    }
  }

  public requestUpdate(): void {
    this.send({
      type: 'request_update',
      timestamp: new Date().toISOString()
    })
  }

  public disconnect(): void {
    this.shouldReconnect = false
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    this.stopPingInterval()

    if (this.ws) {
      this.ws.close()
      this.ws = null
    }

    this.isConnected = false
    this.notifyConnectionStatus(false)
  }

  // Event handler registration methods
  public onMessage(handler: MessageHandler): () => void {
    this.messageHandlers.push(handler)
    return () => {
      const index = this.messageHandlers.indexOf(handler)
      if (index > -1) {
        this.messageHandlers.splice(index, 1)
      }
    }
  }

  public onSLAUpdate(handler: SLAUpdateHandler): () => void {
    this.slaUpdateHandlers.push(handler)
    return () => {
      const index = this.slaUpdateHandlers.indexOf(handler)
      if (index > -1) {
        this.slaUpdateHandlers.splice(index, 1)
      }
    }
  }

  public onConnectionStatus(handler: ConnectionStatusHandler): () => void {
    this.connectionStatusHandlers.push(handler)
    return () => {
      const index = this.connectionStatusHandlers.indexOf(handler)
      if (index > -1) {
        this.connectionStatusHandlers.splice(index, 1)
      }
    }
  }
  public getConnectionStatus(): boolean {
    return this.isConnected
  }
}

// Global instance - will be created but not initialized until client-side
let slaWebSocketClientInstance: SLAWebSocketClient | null = null

export const slaWebSocketClient = (() => {
  if (typeof window !== 'undefined' && !slaWebSocketClientInstance) {
    slaWebSocketClientInstance = new SLAWebSocketClient()
  }
  return slaWebSocketClientInstance || new SLAWebSocketClient()
})()
