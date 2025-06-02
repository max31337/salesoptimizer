import asyncio
import aiosmtplib
from email.mime.text import MIMEText
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

async def test_simple_email():
    """Test basic email sending without TLS."""
    
    # Your Mailtrap credentials
    smtp_host = "sandbox.smtp.mailtrap.io"
    smtp_port = 25  # Try plain port first
    smtp_username = "YOUR_USERNAME_HERE"  # Replace with actual
    smtp_password = "YOUR_PASSWORD_HERE"  # Replace with actual
    
    print(f"Testing simple email to: {smtp_host}:{smtp_port}")
    
    # Create simple message
    message = MIMEText("This is a test email from SalesOptimizer!", "plain")
    message["Subject"] = "Test Email"
    message["From"] = f"SalesOptimizer <{smtp_username}>"
    message["To"] = "test@example.com"
    
    try:
        # Try without any TLS/SSL
        await aiosmtplib.send(
            message,
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_username,
            password=smtp_password,
            use_tls=False,
            start_tls=False,
            timeout=30
        )
        print("✅ Email sent successfully!")
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        
        # Try with STARTTLS
        try:
            print("Trying with STARTTLS...")
            await aiosmtplib.send(
                message,
                hostname=smtp_host,
                port=2525,
                username=smtp_username,
                password=smtp_password,
                use_tls=False,
                start_tls=True,
                timeout=30
            )
            print("✅ Email sent with STARTTLS!")
            
        except Exception as e2:
            print(f"❌ STARTTLS also failed: {e2}")

if __name__ == "__main__":
    asyncio.run(test_simple_email())