import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def debug_env_loading():
    """Debug environment variable loading."""
    print("🔍 Environment Variables Debug:")
    print(f"📁 Project root: {project_root}")
    
    # Check if .env file exists
    env_file = project_root / ".env"
    print(f"📄 .env file path: {env_file}")
    print(f"📄 .env file exists: {env_file.exists()}")
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            print(f"📄 .env file size: {len(content)} characters")
            
            # Check for SMTP settings in file
            lines = content.split('\n')
            smtp_lines = [line for line in lines if 'SMTP' in line and not line.startswith('#')]
            print(f"📄 SMTP lines in .env file:")
            for line in smtp_lines:
                print(f"   {line}")
    
    # Check raw environment variables
    print(f"\n🌍 Raw Environment Variables:")
    smtp_vars = ['SMTP_HOST', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'SMTP_USE_TLS', 'SMTP_USE_STARTTLS']
    for var in smtp_vars:
        value = os.getenv(var)
        print(f"   {var}: '{value}' (Type: {type(value)})")
    
    # Try loading dotenv manually
    try:
        from dotenv import load_dotenv
        print(f"\n📦 Loading .env manually...")
        load_dotenv(env_file)
        
        print(f"🌍 After manual dotenv load:")
        for var in smtp_vars:
            value = os.getenv(var)
            print(f"   {var}: '{value}'")
            
    except ImportError:
        print("❌ python-dotenv not installed")
    
    # Check settings module
    try:
        print(f"\n⚙️ Checking settings module...")
        from infrastructure.config.settings import settings
        print(f"   SMTP_HOST: '{settings.SMTP_HOST}'")
        print(f"   SMTP_PORT: {settings.SMTP_PORT}")
        print(f"   SMTP_USERNAME: '{settings.SMTP_USERNAME}'")
        print(f"   SMTP_PASSWORD: '{settings.SMTP_PASSWORD}'")
        print(f"   SMTP_USE_TLS: {settings.SMTP_USE_TLS}")
        print(f"   SMTP_USE_STARTTLS: {settings.SMTP_USE_STARTTLS}")
    except Exception as e:
        print(f"❌ Error loading settings: {e}")

if __name__ == "__main__":
    debug_env_loading()