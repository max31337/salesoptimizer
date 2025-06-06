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
}

interface RefreshTokensResponse {
  refresh_tokens: RefreshTokenInfo[]
  total_count: number
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
  }

  /**
   * Get list of active sessions for the user
   */
  async getActiveSessions(): Promise<SessionsResponse> {
    return await apiClient.get<SessionsResponse>('/auth/sessions')
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
   * Get user's refresh tokens from database for session management display
   */
  async getRefreshTokens(): Promise<RefreshTokensResponse> {
    return await apiClient.get<RefreshTokensResponse>('/auth/refresh-tokens')
  }
  /**
   * Revoke a specific session by ID
   */
  async revokeSessionById(sessionId: string): Promise<RevocationResponse> {
    return await apiClient.post<RevocationResponse>('/auth/revoke-session', {
      session_id: sessionId
    })
  }
}

export const tokenRevocationService = new TokenRevocationService()
