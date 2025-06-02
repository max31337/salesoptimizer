import os
from typing import Tuple, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EmailTemplateService:
    """Service for rendering email templates."""
    
    def __init__(self, templates_dir: Optional[str] = None):
        if templates_dir is None:
            # Default to templates directory relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            templates_dir = os.path.join(current_dir, "templates")
        
        self.templates_dir = templates_dir
        
        # Check if templates directory exists
        if not os.path.exists(templates_dir):
            logger.error(f"Templates directory does not exist: {templates_dir}")
            raise FileNotFoundError(f"Templates directory not found: {templates_dir}")
        
        # List available templates
        template_files = os.listdir(templates_dir) if os.path.exists(templates_dir) else []
        logger.info(f"Templates directory: {templates_dir}")
        logger.info(f"Available template files: {template_files}")
        
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def render_invitation_email(
        self,
        organization_name: str,
        invitation_token: str,
        invited_by_name: str,
        expires_at: datetime,
        base_url: str = "http://localhost:3000"
    ) -> Tuple[str, str]:
        """Render invitation email templates."""
        try:
            # Create accept URL
            accept_url = f"{base_url}/invitations/accept?token={invitation_token}"
            
            # Format expiration date
            formatted_expires = expires_at.strftime("%B %d, %Y at %I:%M %p UTC")
            
            context = {
                "organization_name": organization_name,
                "invitation_token": invitation_token,
                "invited_by_name": invited_by_name,
                "expires_at": formatted_expires,
                "accept_url": accept_url
            }
            
            logger.info(f"Rendering templates with context: {context}")
            
            # Check if templates exist
            html_template_path = os.path.join(self.templates_dir, "invitation_admin.html")
            text_template_path = os.path.join(self.templates_dir, "invitation_admin.txt")
            
            if not os.path.exists(html_template_path):
                logger.error(f"HTML template not found: {html_template_path}")
                raise FileNotFoundError(f"HTML template not found: {html_template_path}")
            
            if not os.path.exists(text_template_path):
                logger.error(f"Text template not found: {text_template_path}")
                raise FileNotFoundError(f"Text template not found: {text_template_path}")
            
            # Render both HTML and text templates
            html_template = self.env.get_template("invitation_admin.html")
            text_template = self.env.get_template("invitation_admin.txt")
            
            html_content = html_template.render(**context)
            text_content = text_template.render(**context)
            
            logger.info("Templates rendered successfully")
            return html_content, text_content
            
        except TemplateNotFound as e:
            logger.error(f"Template not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error rendering templates: {e}")
            raise