import axios from 'axios'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_VERSION = '/api/v1'

class ApiClient {
  private baseUrl: string

  constructor() {
    this.baseUrl = `${BASE_URL}${API_VERSION}`
  }

  private getAuthHeaders(): Record<string, string> {
    // No need to manually add Authorization header - cookies are sent automatically
    return {
      'Content-Type': 'application/json',
    }
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`)
    }
    return response.json()
  }

  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
      credentials: 'include', // Include httpOnly cookies
    })
    return this.handleResponse<T>(response)
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
      credentials: 'include', // Include httpOnly cookies
    })
    return this.handleResponse<T>(response)
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