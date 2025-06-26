import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from infrastructure.services.password_service import PasswordService

def test_password_service():
    password_service = PasswordService()
    test_password = "SuperAdmin123!"
    
    print(f"🔍 Testing PasswordService:")
    print(f"   Test password: {test_password}")
    
    # Hash the password
    hashed = password_service.hash_password(test_password)
    print(f"   Generated hash: {hashed}")
    print(f"   Hash length: {len(hashed)}")
    print(f"   Hash starts with: {hashed[:10]}...")
    
    # Verify the password
    is_valid = password_service.verify_password(test_password, hashed)
    print(f"   ✅ Verification result: {is_valid}")
    
    # Test with wrong password
    is_valid_wrong = password_service.verify_password("wrong_password", hashed)
    print(f"   ❌ Wrong password result: {is_valid_wrong}")

if __name__ == "__main__":
    test_password_service()