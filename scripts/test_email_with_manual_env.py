import asyncio
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables manually
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from infrastructure.email.smtp_email_service import SMTPEmailService
from datetime import datetime, timezone, timedelta

async def test_email_with_manual_env():
    """Test email with manually loaded environment variables."""
    
    # Get credentials directly from environment
    smtp_host = os.getenv("SMTP_HOST", "sandbox.smtp.mailtrap.io")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_use_tls = os.getenv("SMTP_USE_TLS", "false").lower() == "true"
    smtp_use_starttls = os.getenv("SMTP_USE_STARTTLS", "true").lower() == "true"
    
    print("📧 Manual Environment Loading Test:")
    print(f"   SMTP Host: {smtp_host}")
    print(f"   SMTP Port: {smtp_port}")
    print(f"   SMTP Username: '{smtp_username}' (length: {len(smtp_username)})")
    print(f"   SMTP Password: {'SET' if smtp_password else 'NOT SET'} (length: {len(smtp_password)})")
    print(f"   Use TLS: {smtp_use_tls}")
    print(f"   Use STARTTLS: {smtp_use_starttls}")
    
    if not smtp_username or not smtp_password:
        print("❌ Credentials still missing after manual load!")
        return
    
    email_service = SMTPEmailService(
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_username=smtp_username,
        smtp_password=smtp_password,
        use_tls=smtp_use_tls,
        use_starttls=smtp_use_starttls,
        default_from_email="admin@salesoptimizer.com",
        default_from_name="SalesOptimizer",
        base_url="http://localhost:3000"
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
        print("✅ Email sent successfully!")
        print("📧 Check your Mailtrap inbox")
    else:
        print("❌ Failed to send email")

if __name__ == "__main__":
    asyncio.run(test_email_with_manual_env())