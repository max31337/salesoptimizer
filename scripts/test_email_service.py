import asyncio
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from infrastructure.email.smtp_email_service import SMTPEmailService
from infrastructure.config.settings import settings
from datetime import datetime, timezone, timedelta

async def test_invitation_email():
    """Test sending an invitation email."""
    
    email_service = SMTPEmailService(
        smtp_host=settings.SMTP_HOST,
        smtp_port=settings.SMTP_PORT,
        smtp_username=settings.SMTP_USERNAME,
        smtp_password=settings.SMTP_PASSWORD,
        use_tls=settings.SMTP_USE_TLS,
        default_from_email=settings.DEFAULT_FROM_EMAIL,
        default_from_name=settings.DEFAULT_FROM_NAME,
        base_url=settings.FRONTEND_URL
    )
    
    # Test invitation email
    success = await email_service.send_invitation_email(
        to_email="test@example.com",
        organization_name="Test Organization",
        invitation_token="test-token-123",
        invited_by_name="John Doe",
        expires_at=(datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    )
    
    if success:
        print("✅ Invitation email sent successfully!")
        print("📧 Check your Mailtrap inbox to see the email")
    else:
        print("❌ Failed to send invitation email")

if __name__ == "__main__":
    asyncio.run(test_invitation_email())