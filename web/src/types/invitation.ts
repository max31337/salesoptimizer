export interface CreateInvitationRequest {
  email: string
  organization_name: string
  subscription_tier?: 'basic' | 'pro' | 'enterprise'
  slug?: string
}

export interface Invitation {
  id: string
  email: string
  organization_name: string
  role: string
  status: 'pending' | 'accepted' | 'expired'
  token: string
  invited_by_id: string
  tenant_id: string
  expires_at: string
  created_at: string
  updated_at: string
}

export interface Tenant {
  id: string
  name: string
  slug: string
  subscription_tier: string
  status: 'active' | 'inactive' | 'suspended'
  owner_id?: string
  created_at: string
  updated_at: string
}

export interface InvitationWithTenantResponse {
  invitation: Invitation
  tenant: Tenant
}