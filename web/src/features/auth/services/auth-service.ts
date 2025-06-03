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

class AuthService {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Login failed')
    }

    return response.json()
  }

  async getCurrentUser() {
    const token = localStorage.getItem('access_token')
    if (!token) throw new Error('No token found')

    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      throw new Error('Failed to get user info')
    }

    return response.json()
  }
}

export const authService = new AuthService()