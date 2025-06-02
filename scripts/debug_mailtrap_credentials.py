import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from infrastructure.config.settings import settings

def debug_credentials():
    """Debug Mailtrap credentials."""
    print("🔍 Checking Mailtrap Configuration:")
    print(f"SMTP_HOST: {settings.SMTP_HOST}")
    print(f"SMTP_PORT: {settings.SMTP_PORT}")
    print(f"SMTP_USERNAME: '{settings.SMTP_USERNAME}' (Length: {len(settings.SMTP_USERNAME)})")
    print(f"SMTP_PASSWORD: {'SET' if settings.SMTP_PASSWORD else 'NOT SET'} (Length: {len(settings.SMTP_PASSWORD)})")
    print(f"SMTP_USE_TLS: {settings.SMTP_USE_TLS}")
    print(f"SMTP_USE_STARTTLS: {settings.SMTP_USE_STARTTLS}")
    
    # Check if credentials are missing
    missing: list[str] = []
    if not settings.SMTP_USERNAME:
        missing.append("SMTP_USERNAME")
    if not settings.SMTP_PASSWORD:
        missing.append("SMTP_PASSWORD")
    
    if missing:
        print(f"\n❌ Missing credentials: {', '.join(missing)}")
        print("\n📝 To fix this:")
        print("1. Go to https://mailtrap.io")
        print("2. Login to your account")
        print("3. Go to Email Testing → Inboxes")
        print("4. Click on your inbox")
        print("5. Go to SMTP Settings tab")
        print("6. Copy the Username and Password")
        print("7. Update your .env file")
    else:
        print("\n✅ All credentials are set!")

if __name__ == "__main__":
    debug_credentials()