interface SessionInfo {
  id: string;
  device_info: string;
  ip_address: string;
  user_agent: string;
  created_at: string;
  expires_at: string;
  is_current: boolean;
}

interface RefreshTokenInfo {
  id: string;
  device_info: string;
  ip_address: string;
  user_agent: string;
  created_at: string;
  expires_at: string;
  is_current: boolean;
}

interface ApiResponse<T> {
  success?: boolean;
  message?: string;
  data?: T;
}

interface SessionsResponse {
  sessions: SessionInfo[];
  total_count: number;
}

interface RefreshTokensResponse {
  refresh_tokens: RefreshTokenInfo[];
  total_count: number;
}

class TokenRevocationService {
  private readonly baseUrl = '/api/auth';
  async logoutCurrentDevice(): Promise<{ success: boolean; message: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/logout-current`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to logout from current device');
      }      // Close WebSocket connection on successful logout
      try {
        // Dispatch logout event for WebSocket cleanup
        if (typeof window !== 'undefined') {
          const event = new CustomEvent('auth-logout')
          window.dispatchEvent(event)
        }
        
        const { slaWebSocketClient } = await import('@/lib/websocket')
        slaWebSocketClient.disconnect()
        console.log('🔌 WebSocket disconnected on device logout')
      } catch (error) {
        console.warn('Failed to disconnect WebSocket on logout:', error)
      }

      const data = await response.json();
      return {
        success: true,
        message: data.message || 'Successfully logged out from current device'
      };
    } catch (error) {
      console.error('Error logging out from current device:', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to logout from current device'
      };
    }
  }
  async logoutAllDevices(): Promise<{ success: boolean; message: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/logout-all-devices`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ confirm: true }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to logout from all devices');
      }      // Close WebSocket connection on successful logout
      try {
        // Dispatch logout event for WebSocket cleanup
        if (typeof window !== 'undefined') {
          const event = new CustomEvent('auth-logout')
          window.dispatchEvent(event)
        }
        
        const { slaWebSocketClient } = await import('@/lib/websocket')
        slaWebSocketClient.disconnect()
        console.log('🔌 WebSocket disconnected on all devices logout')
      } catch (error) {
        console.warn('Failed to disconnect WebSocket on logout:', error)
      }

      const data = await response.json();
      return {
        success: true,
        message: data.message || 'Successfully logged out from all devices'
      };
    } catch (error) {
      console.error('Error logging out from all devices:', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to logout from all devices'
      };
    }
  }

  async getActiveSessions(): Promise<SessionInfo[]> {
    try {
      const response = await fetch(`${this.baseUrl}/sessions`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to get active sessions');
      }

      const data: SessionsResponse = await response.json();
      return data.sessions || [];
    } catch (error) {
      console.error('Error getting active sessions:', error);
      return [];
    }
  }

  async getRefreshTokens(): Promise<RefreshTokenInfo[]> {
    try {
      const response = await fetch(`${this.baseUrl}/refresh-tokens`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to get refresh tokens');
      }

      const data: RefreshTokensResponse = await response.json();
      return data.refresh_tokens || [];
    } catch (error) {
      console.error('Error getting refresh tokens:', error);
      return [];
    }
  }

  async revokeSpecificToken(token: string): Promise<{ success: boolean; message: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/revoke-token`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to revoke token');
      }

      const data = await response.json();
      return {
        success: true,
        message: data.message || 'Token revoked successfully'
      };
    } catch (error) {
      console.error('Error revoking token:', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to revoke token'
      };
    }
  }

  async revokeSessionById(sessionId: string): Promise<{ success: boolean; message: string }> {
    // This would revoke a specific session by its ID
    // For now, we don't have a specific endpoint for this, so we'll use the general revoke
    return this.revokeSpecificToken(sessionId);
  }
}

export const tokenRevocationService = new TokenRevocationService();
export type { SessionInfo, RefreshTokenInfo };
