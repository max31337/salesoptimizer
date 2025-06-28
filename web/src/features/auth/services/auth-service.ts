import { apiClient } from '@/lib/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface LoginCredentials {
  email: string
  password: string
}

interface LoginResponse {
  user: {
    id: string
    email: string
    role: string
    first_name?: string
    last_name?: string
  }
  access_token: string
  refresh_token: string
}

interface ChangePasswordRequest {
  current_password: string
  new_password: string
}

interface ChangePasswordResponse {
  message: string
}

interface SignupData {
  firstName: string
  lastName: string
  email: string
  password: string
  organizationName: string
  subscriptionTier: 'trial' | 'basic' | 'pro'
}

interface SignupResponse {
  success: boolean
  message: string
  user?: {
    id: string
    email: string
    role: string
    first_name?: string
    last_name?: string
  }
  organization?: {
    id: string
    name: string
    slug: string
  }
}

class AuthService {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const formData = new URLSearchParams()
    formData.append('username', credentials.email)
    formData.append('password', credentials.password)

    return await apiClient.postForm<LoginResponse>('/auth/login', formData)
  }

  async getCurrentUser() {
    return await apiClient.get('/auth/me')
  }

  async logout() {
    return await apiClient.post('/auth/logout', {})
  }

  async refreshToken() {
    return await apiClient.post('/auth/refresh', {})
  }

  async changePassword(data: ChangePasswordRequest): Promise<ChangePasswordResponse> {
    return await apiClient.post<ChangePasswordResponse>('/auth/change-password', data)
  }

  async signup(data: SignupData): Promise<SignupResponse> {
    return await apiClient.post<SignupResponse>('/auth/signup', {
      first_name: data.firstName,
      last_name: data.lastName,
      email: data.email,
      password: data.password,
      organization_name: data.organizationName,
      subscription_tier: data.subscriptionTier
    })
  }
}

export const authService = new AuthService()

// Export types for use in components
export type { LoginCredentials, LoginResponse, ChangePasswordRequest, ChangePasswordResponse, SignupData, SignupResponse }