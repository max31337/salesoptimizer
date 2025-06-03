import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import Optional, Tuple
from datetime import datetime

from domain.shared.services.email_service import EmailService, EmailMessage
from infrastructure.email.template_service import EmailTemplateService
from infrastructure.config.settings import settings

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SMTPEmailService(EmailService):
    """SMTP implementation of email service."""
    def __init__(
        self,
        smtp_host: str = settings.SMTP_HOST,
        smtp_port: int = settings.SMTP_PORT,
        smtp_username: str = settings.SMTP_USERNAME,
        smtp_password: str = settings.SMTP_PASSWORD,
        use_tls: bool = settings.SMTP_USE_TLS,
        use_starttls: bool = settings.SMTP_USE_STARTTLS,
        default_from_email: Optional[str] = settings.DEFAULT_FROM_EMAIL,
        default_from_name: str = settings.DEFAULT_FROM_NAME,
        base_url: str = settings.FRONTEND_URL
    ):
        # Store configuration as instance attributes
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.use_tls = use_tls
        self.use_starttls = use_starttls
        self.default_from_email = default_from_email
        self.default_from_name = default_from_name
        self.base_url = base_url
        
        # Try to use file templates first, fallback to inline
        try:
            self.template_service = EmailTemplateService()
            logger.info("Using file-based email templates")
        except Exception as e:
            logger.warning(f"File templates failed ({e}), using inline templates")
            self.template_service = self._create_inline_template_service()
        
        # Log configuration
        logger.info(f"Email service initialized with:")
        logger.info(f"  SMTP Host: {self.smtp_host}")
        logger.info(f"  SMTP Port: {self.smtp_port}")
        logger.info(f"  SMTP Username: {self.smtp_username}")
        logger.info(f"  Use TLS: {self.use_tls}")
        logger.info(f"  Use STARTTLS: {self.use_starttls}")
        logger.info(f"  Default From: {self.default_from_email}")
    def _create_inline_template_service(self):
        """Create an inline template service as fallback."""
        class InlineTemplateService:
            def render_invitation_email(
                self, 
                organization_name: str, 
                invitation_token: str, 
                invited_by_name: str, 
                expires_at: datetime, 
                base_url: str = "http://localhost:3000"
            ) -> Tuple[str, str]:
                accept_url = f"{base_url}/invitations/accept?token={invitation_token}"
                formatted_expires = expires_at.strftime("%B %d, %Y at %I:%M %p UTC")
                
                html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #667eea; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ padding: 30px; border: 1px solid #e0e0e0; border-top: none; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 8px 8px; }}
        .btn {{ background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
        .warning {{ background: #fff3cd; padding: 15px; margin: 20px 0; border-left: 4px solid #ffc107; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎉 You're Invited!</h1>
        <p>Join {organization_name} as an Organization Administrator</p>
    </div>
    <div class="content">
        <h2>Hello!</h2>
        <p>{invited_by_name} has invited you to become an Organization Administrator for <strong>{organization_name}</strong> on SalesOptimizer.</p>
        
        <p style="text-align: center;">
            <a href="{accept_url}" class="btn">Accept Invitation & Setup Account</a>
        </p>
        
        <div class="warning">
            <p><strong>⏰ Important:</strong> This invitation expires on <strong>{formatted_expires}</strong>.</p>
        </div>
        
        <p>If the button doesn't work, copy this link: {accept_url}</p>
        <p>Welcome to the team! 🚀</p>
    </div>
    <div class="footer">
        <p>© 2025 SalesOptimizer. All rights reserved.</p>
    </div>
</body>
</html>
                """
                
                text_content = f"""
You're Invited to Join {organization_name}!

Hello!

{invited_by_name} has invited you to become an Organization Administrator for {organization_name} on SalesOptimizer.

To accept this invitation and set up your account, please visit:
{accept_url}

IMPORTANT: This invitation expires on {formatted_expires}.

Welcome to the team!

---
© 2025 SalesOptimizer. All rights reserved.
                """
                
                return html_content.strip(), text_content.strip()
        
        return InlineTemplateService()
    
    async def send_email(self, message: EmailMessage) -> bool:
        """Send an email message via SMTP."""
        try:
            logger.info(f"Preparing to send email to: {message.to_email}")
            logger.info(f"Subject: {message.subject}")
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.subject
            msg['From'] = f"{message.from_name or self.default_from_name} <{message.from_email or self.default_from_email}>"
            msg['To'] = message.to_email
            
            # Add text content
            if message.text_content:
                text_part = MIMEText(message.text_content, 'plain', 'utf-8')
                msg.attach(text_part)
                logger.debug("Added text content to email")
            
            # Add HTML content
            if message.html_content:
                html_part = MIMEText(message.html_content, 'html', 'utf-8')
                msg.attach(html_part)
                logger.debug("Added HTML content to email")
            
            logger.info(f"Connecting to SMTP server: {self.smtp_host}:{self.smtp_port}")
            logger.info(f"TLS: {self.use_tls}, STARTTLS: {self.use_starttls}")
            
            # Send email with correct TLS configuration for Mailtrap
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                use_tls=self.use_tls,        # False for Mailtrap
                start_tls=self.use_starttls,  # True for Mailtrap
                timeout=30
            )
            
            logger.info(f"✅ Email sent successfully to {message.to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {message.to_email}: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    async def send_invitation_email(
        self,
        to_email: str,
        organization_name: str,
        invitation_token: str,
        invited_by_name: str,
        expires_at: str
    ) -> bool:
        """Send an organization admin invitation email."""
        try:
            logger.info(f"🚀 Starting invitation email process for: {to_email}")
            logger.info(f"Organization: {organization_name}")
            logger.info(f"Token: {invitation_token[:20]}...")
            
            # Parse expires_at string to datetime
            from datetime import datetime
            # Handle different datetime formats
            try:
                expires_dt = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            except ValueError:
                # Try parsing as datetime string
                expires_dt = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S.%f%z')
            
            logger.info(f"Parsed expiration date: {expires_dt}")
            
            # Render email templates
            html_content, text_content = self.template_service.render_invitation_email(
                organization_name=organization_name,
                invitation_token=invitation_token,
                invited_by_name=invited_by_name,
                expires_at=expires_dt,
                base_url=self.base_url
            )
            
            logger.info("Email templates rendered successfully")
            logger.debug(f"HTML content length: {len(html_content)} chars")
            logger.debug(f"Text content length: {len(text_content)} chars")
            
            # Create email message
            message = EmailMessage(
                to_email=to_email,
                subject=f"You're invited to join {organization_name} as Organization Admin",
                html_content=html_content,
                text_content=text_content,
                from_email=self.default_from_email,
                from_name=self.default_from_name
            )
            
            logger.info("Email message created, sending...")
            result = await self.send_email(message)
            
            if result:
                logger.info(f"✅ Invitation email sent successfully to {to_email}")
            else:
                logger.error(f"❌ Failed to send invitation email to {to_email}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Exception in send_invitation_email: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False