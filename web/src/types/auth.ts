export interface User {
  id: string
  email: string
  username: string
  full_name: string
  role: 'super_admin' | 'org_admin' | 'sales_manager' | 'sales_rep'
  status: 'active' | 'inactive' | 'pending'
  is_email_verified: boolean
  tenant_id?: string
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
}