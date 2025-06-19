export interface User {
  id: string
  email: string
  username?: string
  first_name?: string
  last_name?: string
  phone?: string
  bio?: string
  role: 'super_admin' | 'org_admin' | 'sales_manager' | 'sales_rep'
  status: 'active' | 'inactive' | 'pending'
  is_email_verified: boolean
  password_strength?: 'weak' | 'medium' | 'strong' | 'very_strong'
  tenant_id?: string
  profile_picture_url?: string
  last_login?: string
  created_at: string
  updated_at: string
  team_info?: {
    id: string
    name: string
    description?: string
    member_count: number
    manager_name?: string
    is_active: boolean
  }
}

export interface LoginRequest {
  emailOrUsername: string
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