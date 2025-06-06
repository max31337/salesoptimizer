import { apiClient } from '@/lib/api'

interface CreateInvitationRequest {
  email: string
  organization_name: string
  subscription_tier: string
  slug?: string
}

interface InvitationResponse {
  id: string
  email: string
  organization_name: string
  subscription_tier: string
  slug: string
  token: string
  expires_at: string
  created_at: string
}

interface TenantResponse {
  id: string
  name: string
  slug: string
  subscription_tier: string
  is_active: boolean
  owner_id?: string
  created_at: string
}

interface InvitationWithTenantResponse {
  invitation: InvitationResponse
  tenant: TenantResponse
}

class InvitationService {
  async createOrgAdminInvitation(data: CreateInvitationRequest): Promise<InvitationWithTenantResponse> {
    return apiClient.post('/invitations/', data)
  }

  async getInvitations(): Promise<InvitationResponse[]> {
    return apiClient.get('/invitations/')
  }

  async deleteInvitation(invitationId: string): Promise<void> {
    return apiClient.delete(`/invitations/${invitationId}`)
  }
}

export const invitationService = new InvitationService()