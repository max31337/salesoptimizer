import axios from 'axios'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'  // Use IPv4 explicitly
const API_VERSION = '/api/v1'

class ApiClient {
  private baseUrl: string
  private isRefreshing = false
  private refreshSubscribers: Array<(token: string) => void> = []

  constructor() {
    this.baseUrl = `${BASE_URL}${API_VERSION}`
    console.log('API Client initialized with base URL:', this.baseUrl)  // Debug log
  }

  private getAuthHeaders(): Record<string, string> {
    // No need to manually add Authorization header - cookies are sent automatically
    return {
      'Content-Type': 'application/json',
    }
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      // Handle 401 errors for token refresh
      if (response.status === 401) {
        const refreshed = await this.attemptTokenRefresh()
        if (refreshed) {
          // Retry the original request
          throw new Error('RETRY_REQUEST')
        }
      }
      
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`)
    }
    return response.json()
  }

  private async attemptTokenRefresh(): Promise<boolean> {
    if (this.isRefreshing) {
      // If already refreshing, wait for it to complete
      return new Promise((resolve) => {
        this.refreshSubscribers.push(() => resolve(true))
      })
    }

    this.isRefreshing = true

    try {
      const response = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        // Notify all waiting requests that refresh succeeded
        this.refreshSubscribers.forEach(callback => callback('refreshed'))
        this.refreshSubscribers = []
        this.isRefreshing = false
        return true
      }
    } catch (error) {
      console.error('Token refresh failed:', error)
    }

    this.isRefreshing = false
    this.refreshSubscribers = []
    
    // Redirect to login on refresh failure
    if (typeof window !== 'undefined') {
      window.location.href = '/login'
    }
    
    return false
  }

  async get<T>(endpoint: string): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    console.log('GET request to:', url)  // Debug log
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: this.getAuthHeaders(),
        credentials: 'include', // Include httpOnly cookies
      })
      return this.handleResponse<T>(response)
    } catch (error) {
      if (error instanceof Error && error.message === 'RETRY_REQUEST') {
        // Retry the request after successful token refresh
        const response = await fetch(url, {
          method: 'GET',
          headers: this.getAuthHeaders(),
          credentials: 'include',
        })
        return this.handleResponse<T>(response)
      }
      throw error
    }
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    console.log('POST request to:', url, 'with data:', data)  // Debug log
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(data),
        credentials: 'include', // Include httpOnly cookies
      })
      return this.handleResponse<T>(response)
    } catch (error) {
      if (error instanceof Error && error.message === 'RETRY_REQUEST') {
        const response = await fetch(url, {
          method: 'POST',
          headers: this.getAuthHeaders(),
          body: JSON.stringify(data),
          credentials: 'include',
        })
        return this.handleResponse<T>(response)
      }
      throw error
    }
  }

  async put<T>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
      credentials: 'include', // Include httpOnly cookies
    })
    return this.handleResponse<T>(response)
  }

  async delete<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders(),
      credentials: 'include', // Include httpOnly cookies
    })
    return this.handleResponse<T>(response)
  }

  // Special method for form data (like login)
  async postForm<T>(endpoint: string, formData: URLSearchParams): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
      credentials: 'include', // Include httpOnly cookies
    })
    return this.handleResponse<T>(response)
  }
}

export const apiClient = new ApiClient()

// Remove the axios instance since we're using fetch with credentials