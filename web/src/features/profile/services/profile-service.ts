import { apiClient } from '@/lib/api'

export interface UserProfile {
  id: string
  email: string
  first_name?: string
  last_name?: string
  phone?: string
  profile_picture_url?: string
  role: string
  organization_id?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ProfileUpdateRequest {
  email?: string
  first_name?: string
  last_name?: string
  phone?: string
}

export interface ProfileUpdateResponse {
  user: UserProfile
  message: string
}

export interface ProfileUpdatePendingResponse {
  message: string
  status: 'pending_approval'
}

export interface UploadProfilePictureResponse {
  profile_picture_url: string
  message: string
}

class ProfileService {
  /**
   * Get current user's profile
   */
  async getCurrentProfile(): Promise<UserProfile> {
    return apiClient.get<UserProfile>('/profile/me')
  }

  /**
   * Get specific user's profile (for admins)
   */
  async getUserProfile(userId: string): Promise<UserProfile> {
    return apiClient.get<UserProfile>(`/profile/${userId}`)
  }

  /**
   * Update current user's profile
   * Returns either ProfileUpdateResponse for direct updates (super_admin/org_admin)
   * or ProfileUpdatePendingResponse for approval-required updates (other roles)
   */
  async updateProfile(data: ProfileUpdateRequest): Promise<ProfileUpdateResponse | ProfileUpdatePendingResponse> {
    return apiClient.put<ProfileUpdateResponse | ProfileUpdatePendingResponse>('/profile/me', data)
  }

  /**
   * Update specific user's profile (for admins)
   */
  async updateUserProfile(userId: string, data: ProfileUpdateRequest): Promise<ProfileUpdateResponse> {
    return apiClient.put<ProfileUpdateResponse>(`/profile/${userId}`, data)
  }

  /**
   * Upload profile picture
   */
  async uploadProfilePicture(file: File): Promise<UploadProfilePictureResponse> {
    const formData = new FormData()
    formData.append('file', file)

    // Use fetch directly for FormData uploads
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/v1/profile/me/profile-picture`, {
      method: 'POST',
      body: formData,
      credentials: 'include',
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }))
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * Delete profile picture
   */
  async deleteProfilePicture(): Promise<{ message: string }> {
    return apiClient.delete<{ message: string }>('/profile/me/profile-picture')
  }

  /**
   * Check if response indicates pending approval
   */
  isPendingResponse(response: ProfileUpdateResponse | ProfileUpdatePendingResponse): response is ProfileUpdatePendingResponse {
    return 'status' in response && response.status === 'pending_approval'
  }
}

export const profileService = new ProfileService()
