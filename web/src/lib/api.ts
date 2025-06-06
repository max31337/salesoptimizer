import axios from 'axios'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
const API_VERSION = '/api/v1'

class ApiClient {
  private baseUrl: string
  private isRefreshing = false
  private refreshSubscribers: Array<(token: string) => void> = []

  constructor() {
    this.baseUrl = `${BASE_URL}${API_VERSION}`
    console.log('API Client initialized with base URL:', this.baseUrl)
  }

  private getAuthHeaders(): Record<string, string> {
    return {
      'Content-Type': 'application/json',
    }
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      // Handle 401 errors for token refresh
      if (response.status === 401) {
        console.log('🔄 Got 401, attempting token refresh...')
        // Only attempt refresh if we think user should be authenticated
        if (this.hasAuthIndicators()) {
          const refreshed = await this.attemptTokenRefresh()
          if (refreshed) {
            console.log('✅ Token refreshed, retrying request')
            throw new Error('RETRY_REQUEST')
          } else {
            console.log('❌ Token refresh failed')
          }
        }
      }
      
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`)
    }
    return response.json()
  }

  private hasAuthIndicators(): boolean {
    if (typeof window === 'undefined') return false
    
    // Check for cookies more reliably
    const hasAccessToken = document.cookie.split(';').some(cookie => 
      cookie.trim().startsWith('access_token=')
    )
    const hasRefreshToken = document.cookie.split(';').some(cookie => 
      cookie.trim().startsWith('refresh_token=')
    )
    
    return hasAccessToken || hasRefreshToken || 
           localStorage.getItem('salesoptimizer_was_logged_in') === 'true'
  }

  private async attemptTokenRefresh(): Promise<boolean> {
    if (this.isRefreshing) {
      return new Promise((resolve) => {
        this.refreshSubscribers.push(() => resolve(true))
      })
    }

    this.isRefreshing = true
    console.log('🔄 Attempting token refresh...')

    try {
      const response = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        credentials: 'include',  // ✅ Include cookies
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        console.log('✅ Token refresh successful')
        this.refreshSubscribers.forEach(callback => callback('refreshed'))
        this.refreshSubscribers = []
        this.isRefreshing = false
        return true
      } else {
        console.log('❌ Token refresh failed:', response.status, response.statusText)
      }
    } catch (error) {
      console.error('❌ Token refresh failed:', error)
    }

    this.isRefreshing = false
    this.refreshSubscribers = []
    
    // Clear auth indicators on refresh failure
    if (typeof window !== 'undefined') {
      localStorage.removeItem('salesoptimizer_was_logged_in')
    }
    
    return false
  }

  async get<T>(endpoint: string): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    console.log('🌐 GET request to:', url)
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: this.getAuthHeaders(),
        credentials: 'include',  // ✅ Include cookies
      })
      
      console.log('📡 Response status:', response.status)
      return this.handleResponse<T>(response)
    } catch (error) {
      if (error instanceof Error && error.message === 'RETRY_REQUEST') {
        console.log('🔄 Retrying GET request after token refresh')
        const response = await fetch(url, {
          method: 'GET',
          headers: this.getAuthHeaders(),
          credentials: 'include',  // ✅ Include cookies
        })
        return this.handleResponse<T>(response)
      }
      throw error
    }
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    console.log('🌐 POST request to:', url, 'with data:', data)
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(data),
        credentials: 'include',  // ✅ Include cookies
      })
      
      console.log('📡 Response status:', response.status)
      return this.handleResponse<T>(response)
    } catch (error) {
      if (error instanceof Error && error.message === 'RETRY_REQUEST') {
        console.log('🔄 Retrying POST request after token refresh')
        const response = await fetch(url, {
          method: 'POST',
          headers: this.getAuthHeaders(),
          body: JSON.stringify(data),
          credentials: 'include',  // ✅ Include cookies
        })
        return this.handleResponse<T>(response)
      }
      throw error
    }
  }

  async put<T>(endpoint: string, data: any): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    
    try {
      const response = await fetch(url, {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(data),
        credentials: 'include',  // ✅ Include cookies
      })
      return this.handleResponse<T>(response)
    } catch (error) {
      if (error instanceof Error && error.message === 'RETRY_REQUEST') {
        const response = await fetch(url, {
          method: 'PUT',
          headers: this.getAuthHeaders(),
          body: JSON.stringify(data),
          credentials: 'include',  // ✅ Include cookies
        })
        return this.handleResponse<T>(response)
      }
      throw error
    }
  }

  async delete<T>(endpoint: string): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    
    try {
      const response = await fetch(url, {
        method: 'DELETE',
        headers: this.getAuthHeaders(),
        credentials: 'include',  // ✅ Include cookies
      })
      return this.handleResponse<T>(response)
    } catch (error) {
      if (error instanceof Error && error.message === 'RETRY_REQUEST') {
        const response = await fetch(url, {
          method: 'DELETE',
          headers: this.getAuthHeaders(),
          credentials: 'include',  // ✅ Include cookies
        })
        return this.handleResponse<T>(response)
      }
      throw error
    }
  }

  async postForm<T>(endpoint: string, formData: URLSearchParams): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    console.log('🌐 POST FORM request to:', url)
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
      credentials: 'include',  // ✅ Include cookies
    })
    
    console.log('📡 Response status:', response.status)
    return this.handleResponse<T>(response)
  }
}

export const apiClient = new ApiClient()

// Remove the axios instance since we're using fetch with credentials