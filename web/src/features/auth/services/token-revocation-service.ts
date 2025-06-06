import { apiClient } from '@/lib/api'

interface Session {
  id: string
  device_info: string
  ip_address: string
  user_agent: string
  created_at: string
  last_used_at: string
  is_current: boolean
}

interface RefreshTokenInfo {
  id: string
  device_info: string
  ip_address: string
  user_agent: string
  created_at: string
  expires_at: string
  is_current: boolean
}

interface SessionsResponse {
  sessions: Session[]
  total_count: number
  page: number
  page_size: number
  total_pages: number
}

interface RefreshTokensResponse {
  refresh_tokens: RefreshTokenInfo[]
  total_count: number
  page: number
  page_size: number
  total_pages: number
}

interface RevokedSession {
  id: string
  device_info: string
  ip_address: string
  user_agent: string
  created_at: string
  expires_at: string
  revoked_at: string
  is_current: boolean
}

interface RevokedSessionsResponse {
  sessions: RevokedSession[]
  total_count: number
  page: number
  page_size: number
  total_pages: number
}

interface RevocationResponse {
  message: string
  success: boolean
  devices_affected?: string
}

export class TokenRevocationService {
  /**
   * Logout from current device only
   */
  async logoutCurrentDevice(): Promise<RevocationResponse> {
    return await apiClient.post<RevocationResponse>('/auth/logout-current', {})
  }

  /**
   * Logout from all devices
   */
  async logoutAllDevices(confirm: boolean = true): Promise<RevocationResponse> {
    return await apiClient.post<RevocationResponse>('/auth/logout-all-devices', {
      confirm
    })
  }  /**
   * Get list of active sessions for the user with pagination
   */
  async getActiveSessions(page: number = 1, pageSize: number = 10): Promise<SessionsResponse> {
    const params = new URLSearchParams({ 
      page: page.toString(), 
      page_size: pageSize.toString() 
    })
    return await apiClient.get<SessionsResponse>(`/auth/sessions?${params}`)
  }

  /**
   * Get list of revoked sessions for the user with pagination
   */
  async getRevokedSessions(page: number = 1, pageSize: number = 10): Promise<RevokedSessionsResponse> {
    const params = new URLSearchParams({ 
      page: page.toString(), 
      page_size: pageSize.toString() 
    })
    return await apiClient.get<RevokedSessionsResponse>(`/auth/sessions/revoked?${params}`)
  }

  /**
   * Revoke a specific token
   */
  async revokeSpecificToken(token: string): Promise<RevocationResponse> {
    return await apiClient.post<RevocationResponse>('/auth/revoke-token', {
      token
    })
  }

  /**
   * Revoke a specific session by ID
   */
  async revokeSessionById(sessionId: string): Promise<RevocationResponse> {
    return await apiClient.post<RevocationResponse>('/auth/revoke-session', {
      session_id: sessionId
    })
  }

  /**
   * Get user's refresh tokens from database for session management display with pagination
   */
  async getRefreshTokens(page: number = 1, pageSize: number = 10): Promise<RefreshTokensResponse> {
    const params = new URLSearchParams({ 
      page: page.toString(), 
      page_size: pageSize.toString() 
    })
    return await apiClient.get<RefreshTokensResponse>(`/auth/refresh-tokens?${params}`)
  }
}

export const tokenRevocationService = new TokenRevocationService()
export type { Session, RefreshTokenInfo, SessionsResponse, RefreshTokensResponse, RevokedSession, RevokedSessionsResponse, RevocationResponse }
