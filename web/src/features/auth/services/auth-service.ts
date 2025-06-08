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
}

export const authService = new AuthService()
export type { ChangePasswordRequest, ChangePasswordResponse }