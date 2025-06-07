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

interface GroupedSessionsResponse {
  grouped_sessions: Record<string, Session[]>
  grouping: 'device' | 'ip'
  total_sessions: number
  total_groups: number
  page: number
  page_size: number
  total_pages: number
}

interface GroupedRevokedSessionsResponse {
  grouped_sessions: Record<string, RevokedSession[]>
  grouping: 'device' | 'ip'
  total_sessions: number
  total_groups: number
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
   * Helper function to check if response is grouped
   */
  private isGroupedSessionsResponse(response: SessionsResponse | GroupedSessionsResponse): response is GroupedSessionsResponse {
    return 'grouped_sessions' in response
  }

  /**
   * Helper function to check if revoked response is grouped  
   */
  private isGroupedRevokedSessionsResponse(response: RevokedSessionsResponse | GroupedRevokedSessionsResponse): response is GroupedRevokedSessionsResponse {
    return 'grouped_sessions' in response
  }

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
  async getActiveSessions(page: number = 1, pageSize: number = 10, groupBy?: 'device' | 'ip'): Promise<SessionsResponse | GroupedSessionsResponse> {
    const params = new URLSearchParams({ 
      page: page.toString(), 
      page_size: pageSize.toString() 
    })
    if (groupBy) {
      params.set('group_by', groupBy)
    }
    return await apiClient.get<SessionsResponse | GroupedSessionsResponse>(`/auth/sessions?${params}`)
  }  /**
   * Get list of revoked sessions for the user with pagination
   */
  async getRevokedSessions(page: number = 1, pageSize: number = 10, groupBy?: 'device' | 'ip'): Promise<RevokedSessionsResponse | GroupedRevokedSessionsResponse> {
    const params = new URLSearchParams({ 
      page: page.toString(), 
      page_size: pageSize.toString() 
    })
    if (groupBy) {
      params.set('group_by', groupBy)
    }
    return await apiClient.get<RevokedSessionsResponse | GroupedRevokedSessionsResponse>(`/auth/sessions/revoked?${params}`)
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
  /**
   * Get sessions grouped by device
   */
  async getActiveSessionsGroupedByDevice(page: number = 1, pageSize: number = 10): Promise<GroupedSessionsResponse> {
    const response = await this.getActiveSessions(page, pageSize, 'device')
    return response as GroupedSessionsResponse
  }

  /**
   * Get sessions grouped by IP address
   */
  async getActiveSessionsGroupedByIP(page: number = 1, pageSize: number = 10): Promise<GroupedSessionsResponse> {
    const response = await this.getActiveSessions(page, pageSize, 'ip')
    return response as GroupedSessionsResponse
  }

  /**
   * Get revoked sessions grouped by device
   */
  async getRevokedSessionsGroupedByDevice(page: number = 1, pageSize: number = 10): Promise<GroupedRevokedSessionsResponse> {
    const response = await this.getRevokedSessions(page, pageSize, 'device')
    return response as GroupedRevokedSessionsResponse
  }

  /**
   * Get revoked sessions grouped by IP address
   */
  async getRevokedSessionsGroupedByIP(page: number = 1, pageSize: number = 10): Promise<GroupedRevokedSessionsResponse> {
    const response = await this.getRevokedSessions(page, pageSize, 'ip')
    return response as GroupedRevokedSessionsResponse
  }
}

export const tokenRevocationService = new TokenRevocationService()
export type { 
  Session, 
  RefreshTokenInfo, 
  SessionsResponse, 
  GroupedSessionsResponse,
  RefreshTokensResponse, 
  RevokedSession, 
  RevokedSessionsResponse,
  GroupedRevokedSessionsResponse,
  RevocationResponse 
}
