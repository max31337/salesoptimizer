# Organization Onboarding Flows

This document outlines the two main organization onboarding flows implemented in the SalesOptimizer platform.

## 1. Self-Serve Organization Registration

### Flow Overview
- **Who**: Anyone can register a new organization
- **Access**: Public registration page at `/register`
- **Plans**: Trial (14 days free), Basic ($29/month), Pro ($79/month)
- **Outcome**: Creates organization + admin user + immediate login

### Implementation

#### Frontend
- **Page**: `web/src/app/register/page.tsx`
- **Features**: 
  - Multi-step form (4 steps)
  - Organization details, admin user details, plan selection, legal agreements
  - Real-time validation
  - Responsive design

#### Backend
- **API Endpoint**: `POST /api/v1/organizations/register`
- **Use Case**: `OrganizationRegistrationUseCases.register_organization()`
- **Flow**:
  1. Validate registration request
  2. Create organization/tenant
  3. Create admin user with org_admin role
  4. Set user as tenant owner
  5. Generate authentication tokens
  6. Set httpOnly cookies for immediate login

#### Data Model
```typescript
{
  organization_name: string
  organization_slug?: string
  industry: string
  organization_size: string
  website?: string
  first_name: string
  last_name: string
  email: string
  password: string
  job_title: string
  plan: 'trial' | 'basic' | 'pro'
  accept_terms: boolean
  accept_privacy: boolean
  marketing_opt_in: boolean
}
```

## 2. Invitation-Based Organization Setup

### Flow Overview
- **Who**: Super admin invites organization admin
- **Access**: Email invitation link to `/invitation?token=<invitation_token>`
- **Plans**: Set by super admin during invitation creation
- **Outcome**: Creates admin user + links to pre-created organization + immediate login

### Implementation

#### Super Admin Flow
- **Page**: `web/src/app/dashboard/organizations/page.tsx`
- **Action**: "Invite Organization Admin" button
- **API**: `POST /api/v1/invitations/` (existing)
- **Flow**:
  1. Super admin creates invitation with organization details
  2. System creates organization/tenant
  3. Email sent to invited org admin with token

#### Invited User Flow
- **Page**: `web/src/app/invitation/page.tsx`
- **API**: 
  - `GET /api/v1/organizations/invitation/{token}` - Get invitation details
  - `POST /api/v1/organizations/complete-invitation` - Complete signup
- **Flow**:
  1. User clicks invitation link
  2. System validates token and shows invitation details
  3. User completes account setup (name, password, job title)
  4. System creates user account and links to organization
  5. Immediate login with authentication cookies

#### Data Flow
```typescript
// Invitation Details (GET)
{
  email: string
  organization_name: string
  invited_by: string
  expires_at: string | null
  is_valid: boolean
}

// Signup Completion (POST)
{
  invitation_token: string
  first_name: string
  last_name: string
  password: string
  job_title?: string
}
```

## Architecture Components

### Use Cases
- `OrganizationRegistrationUseCases` - Handles both flows
  - `register_organization()` - Self-serve registration
  - `complete_invitation_signup()` - Invitation completion

### API Routes
- `api/routes/organization_registration.py` - New registration endpoints
- `api/routes/invitations.py` - Existing invitation management

### Domain Services
- `AuthService` - User authentication and token management
- `TenantService` - Organization/tenant management
- `InvitationService` - Invitation creation and validation

### DTOs
- `OrganizationRegistrationRequest/Response`
- `InvitationSignupRequest/Response`

## Security Considerations

### Authentication
- Both flows result in immediate login via httpOnly cookies
- No tokens returned in response body for security
- Secure cookie settings (domain, samesite, secure flags)

### Validation
- Email uniqueness check
- Password strength requirements
- Organization name/slug uniqueness
- Invitation token validation and expiration
- Legal agreement acceptance required

### Authorization
- Self-serve: No authorization required (public endpoint)
- Invitation: Only super admins can create org admin invitations
- Completed users get `org_admin` role with appropriate permissions

## Future Enhancements

### Email Integration
- Welcome emails for self-serve registrations
- Invitation emails with branded templates
- Email verification for self-serve users

### Analytics & Monitoring
- Registration conversion tracking
- Invitation acceptance rates
- User onboarding completion metrics

### Enhanced Validation
- Organization domain verification
- Credit card validation for paid plans
- CAPTCHA for spam prevention

### Multi-Step Onboarding
- Post-registration setup wizard
- Team member invitations
- Integration setup guides
- Success metrics configuration

## Error Handling

### Common Errors
- Email already exists
- Organization name/slug taken
- Invalid/expired invitation tokens
- Password validation failures
- Missing required fields

### Error Responses
All API endpoints return standardized error responses:
```json
{
  "detail": "Human-readable error message"
}
```

### Frontend Error Handling
- Form validation with real-time feedback
- API error display with user-friendly messages
- Loading states during API calls
- Graceful degradation for network issues

## Testing Strategy

### Backend Tests
- Unit tests for use cases and domain logic
- Integration tests for API endpoints
- Database transaction rollback on failures

### Frontend Tests
- Component testing for form validation
- E2E testing for complete registration flows
- API mocking for isolated frontend testing

### Manual Testing Scenarios
1. Complete self-serve registration (all plans)
2. Complete invitation-based signup
3. Error scenarios (duplicate emails, invalid data)
4. Expired invitation handling
5. Cross-browser compatibility
6. Mobile responsiveness
