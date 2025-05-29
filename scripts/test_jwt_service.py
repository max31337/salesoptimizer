import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from infrastructure.services.jwt_service import JWTService
from uuid import uuid4

def test_jwt_service():
    print(f"🔍 Testing JWTService:")
    
    # Check environment variables
    jwt_secret_key = os.getenv('JWT_SECRET_KEY')
    print(f"   JWT_SECRET_KEY exists: {'Yes' if jwt_secret_key else 'No'}")
    if jwt_secret_key:
        print(f"   JWT_SECRET_KEY length: {len(jwt_secret_key)}")
    
    try:
        jwt_service = JWTService()
        print(f"   ✅ JWTService initialized successfully")
        
        # Test token creation
        user_id = uuid4()
        token = jwt_service.create_access_token(user_id, None, "super_admin", "admin@salesoptimizer.com")
        print(f"   ✅ Token created: {token[:50]}...")
        
        # Test token verification
        payload = jwt_service.verify_token(token)
        print(f"   ✅ Token verified: {payload is not None}")
        
    except Exception as e:
        print(f"   ❌ JWTService error: {e}")

if __name__ == "__main__":
    test_jwt_service()