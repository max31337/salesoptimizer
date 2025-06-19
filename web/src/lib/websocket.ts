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
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000 // Start with 1 second
  private maxReconnectDelay = 30000 // Max 30 seconds
  private reconnectTimer: NodeJS.Timeout | null = null
  private pingTimer: NodeJS.Timeout | null = null
  private isConnected = false
  private shouldReconnect = true
  private isConnecting = false // Prevent multiple connection attempts
  private connectionPromise: Promise<void> | null = null // Cache connection promise

  // Event handlers
  private messageHandlers: MessageHandler[] = []
  private slaUpdateHandlers: SLAUpdateHandler[] = []
  private connectionStatusHandlers: ConnectionStatusHandler[] = []

  constructor() {
    // Don't initialize URL during SSR - will be set when connect() is called
    this.url = null
    
    // Add page visibility change listener to handle reconnection
    if (typeof window !== 'undefined') {
      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible' && !this.isConnected && !this.isConnecting) {
          console.log('Page became visible, checking WebSocket connection...')
          this.connect().catch(console.error)
        }
      })
        // Add beforeunload listener to gracefully close connection
      window.addEventListener('beforeunload', () => {
        console.log('🔌 Page unloading, disconnecting WebSocket...')
        this.shouldReconnect = false
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
          this.ws.close(1000, 'Page unload')
        }
      })
      
      // Add error event listener to handle connection errors
      window.addEventListener('error', (event) => {
        if (event.message?.includes('WebSocket')) {
          console.error('🚨 WebSocket error detected:', event.message)
          this.shouldReconnect = false
          this.disconnect()
        }
      })
    }
  }

  private initializeUrl(): void {
    if (this.url || typeof window === 'undefined') return
    
    // Construct WebSocket URL only on client side
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = process.env.NODE_ENV === 'development' 
      ? 'localhost:8000' 
      : window.location.host
    this.url = `${protocol}//${host}/api/v1/ws/sla-monitoring`
  }  private async checkAuthentication(): Promise<boolean> {
    // Check if we're on the client side
    if (typeof window === 'undefined') return false
    
    try {
      // Use relative URL - Next.js will proxy to backend via rewrites
      const apiUrl = process.env.NODE_ENV === 'development' 
        ? 'http://localhost:8000/api/v1/auth/websocket-token'
        : '/api/v1/auth/websocket-token'
      
      // Check if user is authenticated and has proper permissions
      const response = await fetch(apiUrl, {
        method: 'GET',
        credentials: 'include', // Include httpOnly cookies
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        console.log('🔑 WebSocket authentication check passed')
        return true
      } else {
        console.error('❌ WebSocket authentication check failed:', response.status, response.statusText)
        return false
      }
    } catch (error) {
      console.error('❌ Error checking WebSocket authentication:', error)
      return false
    }
  }  public async connect(): Promise<void> {
    // Check if we're on the client side
    if (typeof window === 'undefined') {
      console.warn('⚠️ Cannot connect WebSocket on server side')
      return
    }

    // Return existing connection promise if one is in progress
    if (this.connectionPromise) {
      console.log('⏳ WebSocket connection already in progress, waiting...')
      return this.connectionPromise
    }

    // If already connected, don't reconnect
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('✅ WebSocket already connected')
      return Promise.resolve()
    }

    // If currently connecting, wait for it to complete
    if (this.isConnecting) {
      console.log('⏳ WebSocket connection in progress, waiting...')
      return new Promise((resolve) => {
        const checkConnection = () => {
          if (!this.isConnecting) {
            resolve()
          } else {
            setTimeout(checkConnection, 100)
          }
        }
        checkConnection()
      })
    }

    console.log('🔌 Starting new WebSocket connection...')
    this.connectionPromise = this._connect()
    try {
      await this.connectionPromise
    } finally {
      this.connectionPromise = null
    }
  }
  private async _connect(): Promise<void> {
    this.initializeUrl()
    
    if (!this.url) {
      console.error('WebSocket URL not initialized')
      return
    }

    this.isConnecting = true

    try {
      // Check authentication before connecting
      const isAuthenticated = await this.checkAuthentication()
      if (!isAuthenticated) {
        console.error('WebSocket authentication failed')
        this.isConnecting = false
        return
      }

      // Connect without token parameter - cookies will be sent automatically
      console.log('Connecting to SLA WebSocket:', this.url)

      this.ws = new WebSocket(this.url)

      return new Promise<void>((resolve, reject) => {
        if (!this.ws) {
          reject(new Error('WebSocket instance is null'))
          return
        }

        this.ws.onopen = () => {
          console.log('SLA WebSocket connected')
          this.isConnected = true
          this.isConnecting = false
          this.reconnectAttempts = 0
          this.reconnectDelay = 1000
          this.notifyConnectionStatus(true)
          this.startPingInterval()
          
          // Request initial data after connection is established
          setTimeout(() => {
            this.requestUpdate()
          }, 500)
          
          resolve()
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
          this.isConnecting = false
          this.notifyConnectionStatus(false)
          this.stopPingInterval()

          if (this.shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect()
          }
        }

        this.ws.onerror = (error) => {
          console.error('SLA WebSocket error:', error)
          this.isConnected = false
          this.isConnecting = false
          this.notifyConnectionStatus(false)
          reject(error)
        }
      })
    } catch (error) {
      console.error('Error creating WebSocket connection:', error)
      this.isConnecting = false
      throw error
    }  }
  private handleMessage(message: WebSocketMessage): void {
    console.log('📨 WebSocket message received:', message.type, message)
    
    // Notify all message handlers
    this.messageHandlers.forEach(handler => handler(message))

    // Handle specific message types
    switch (message.type) {
      case 'connection_established':
        console.log('🔗 SLA WebSocket connection established:', message.data)
        break

      case 'sla_update':
        console.log('📊 Received SLA update via WebSocket:', message.data)
        if (message.data) {
          console.log('🔄 Forwarding to SLA handlers, count:', this.slaUpdateHandlers.length)
          this.slaUpdateHandlers.forEach(handler => handler(message.data))
        } else {
          console.error('❌ SLA update message has no data')
        }
        break

      case 'uptime_update':
        console.log('📈 Uptime update received:', message.data)
        break

      case 'new_alert':
        console.log('🚨 New alert received:', message.data)
        // You could show a notification here
        break

      case 'pong':
        // Handle ping response
        break

      default:
        console.log('❓ Unknown message type:', message.type, message)
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
    }

    this.reconnectAttempts++
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), this.maxReconnectDelay)

    console.log(`Scheduling WebSocket reconnect attempt ${this.reconnectAttempts} in ${delay}ms`)

    this.reconnectTimer = setTimeout(async () => {
      if (this.shouldReconnect) {
        await this.connect()
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

// Global instance - singleton that persists across page refreshes and component re-renders
let slaWebSocketClientInstance: SLAWebSocketClient | null = null

export const slaWebSocketClient = (() => {
  // Only create instance on client side
  if (typeof window !== 'undefined') {
    if (!slaWebSocketClientInstance) {
      slaWebSocketClientInstance = new SLAWebSocketClient()
      
      // Store instance globally to persist across page refreshes
      ;(window as any).__slaWebSocketClient = slaWebSocketClientInstance
    }
    return slaWebSocketClientInstance
  }
  
  // Return a mock instance for SSR that does nothing
  return {
    connect: () => Promise.resolve(),
    disconnect: () => {},
    requestUpdate: () => {},
    send: () => {},
    onMessage: () => () => {},
    onSLAUpdate: () => () => {},
    onConnectionStatus: () => () => {},
    getConnectionStatus: () => false
  } as any
})()
