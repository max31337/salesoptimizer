from typing import Any, Dict
from fastapi import status
from fastapi.testclient import TestClient
from uuid import UUID

class TestUserRoutes:
    
    def test_create_user_success(self, client: TestClient, sample_user_data: Dict[str, Any]) -> None:
        """Test successfully creating a user."""
        response = client.post("/api/v1/users/", json=sample_user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data: Dict[str, Any] = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["username"] == sample_user_data["username"]
        assert data["first_name"] == sample_user_data["first_name"]
        assert data["last_name"] == sample_user_data["last_name"]
        assert data["role"] == sample_user_data["role"]
        assert data["status"] == "active"  # Changed from "pending" to "active"
        assert data["is_email_verified"] is False
        assert "id" in data
        # Verify it's a valid UUID string
        try:
            UUID(data["id"])
        except ValueError:
            assert False, "ID should be a valid UUID string"
        assert "created_at" in data
        assert data["full_name"] == f"{sample_user_data['first_name']} {sample_user_data['last_name']}"
    
    def test_create_user_duplicate_email(self, client: TestClient, sample_user_data: Dict[str, Any]) -> None:
        """Test creating a user with duplicate email."""
        # Create first user
        client.post("/api/v1/users/", json=sample_user_data)
        
        # Try to create second user with same email
        duplicate_data: Dict[str, Any] = sample_user_data.copy()
        duplicate_data["username"] = "differentuser"
        
        response = client.post("/api/v1/users/", json=duplicate_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.json()["detail"]
    
    def test_create_user_duplicate_username(self, client: TestClient, sample_user_data: Dict[str, Any]) -> None:
        """Test creating a user with duplicate username."""
        # Create first user
        client.post("/api/v1/users/", json=sample_user_data)
        
        # Try to create second user with same username
        duplicate_data: Dict[str, Any] = sample_user_data.copy()
        duplicate_data["email"] = "different@example.com"
        
        response = client.post("/api/v1/users/", json=duplicate_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username already taken" in response.json()["detail"]
    
    def test_create_user_invalid_data(self, client: TestClient) -> None:
        """Test creating a user with invalid data."""
        invalid_data: Dict[str, str] = {
            "email": "invalid-email",  # Invalid email
            "username": "ab",  # Too short
            "first_name": "",  # Empty
            "last_name": "User"
        }
        
        response = client.post("/api/v1/users/", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_user_by_id_success(self, client: TestClient, sample_user_data: Dict[str, Any]) -> None:
        """Test successfully getting a user by ID."""
        # Create user first
        create_response = client.post("/api/v1/users/", json=sample_user_data)
        user_id: str = create_response.json()["id"]
        
        # Get user by ID
        response = client.get(f"/api/v1/users/{user_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data: Dict[str, Any] = response.json()
        assert data["id"] == user_id
        assert data["email"] == sample_user_data["email"]
        assert data["username"] == sample_user_data["username"]
    
    def test_get_user_by_id_not_found(self, client: TestClient) -> None:
        """Test getting a user by ID when user doesn't exist."""
        fake_uuid: str = "123e4567-e89b-12d3-a456-426614174000"
        response = client.get(f"/api/v1/users/{fake_uuid}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in response.json()["detail"]
    
    def test_get_all_users(self, client: TestClient) -> None:
        """Test getting all users."""
        # Create multiple users
        for i in range(3):
            user_data: Dict[str, str] = {
                "email": f"user{i}@example.com",
                "username": f"user{i}",
                "first_name": f"User{i}",
                "last_name": "Test",
                "role": "sales_rep"
            }
            client.post("/api/v1/users/", json=user_data)
        
        # Get all users
        response = client.get("/api/v1/users/")
        
        assert response.status_code == status.HTTP_200_OK
        data: list[Any] = response.json()
        assert len(data) == 3
        assert all("full_name" in user for user in data)
    
    def test_get_all_users_with_pagination(self, client: TestClient) -> None:
        """Test getting all users with pagination."""
        # Create multiple users
        for i in range(5):
            user_data: Dict[str, str] = {
                "email": f"user{i}@example.com",
                "username": f"user{i}",
                "first_name": f"User{i}",
                "last_name": "Test",
                "role": "sales_rep"
            }
            client.post("/api/v1/users/", json=user_data)
        
        # Get users with pagination
        response = client.get("/api/v1/users/?skip=2&limit=2")
        
        assert response.status_code == status.HTTP_200_OK
        data: list[Any] = response.json()
        assert len(data) == 2
    
    def test_update_user_success(self, client: TestClient, sample_user_data: Dict[str, Any]) -> None:
        """Test successfully updating a user."""
        # Create user first
        create_response = client.post("/api/v1/users/", json=sample_user_data)
        user_id: str = create_response.json()["id"]
        
        # Update user
        update_data: Dict[str, str] = {
            "first_name": "Updated",
            "last_name": "Name",
            "role": "manager"  # Changed from "admin" to valid role
        }
        
        response = client.put(f"/api/v1/users/{user_id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data: Dict[str, Any] = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["role"] == "manager"
        assert data["full_name"] == "Updated Name"
    
    def test_update_user_not_found(self, client: TestClient) -> None:
        """Test updating a user that doesn't exist."""
        update_data: Dict[str, str] = {
            "first_name": "Updated"
        }
        
        fake_uuid: str = "123e4567-e89b-12d3-a456-426614174000"
        response = client.put(f"/api/v1/users/{fake_uuid}", json=update_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in response.json()["detail"]
    
    def test_delete_user_success(self, client: TestClient, sample_user_data: Dict[str, Any]) -> None:
        """Test successfully deleting a user."""
        # Create user first
        create_response = client.post("/api/v1/users/", json=sample_user_data)
        user_id: str = create_response.json()["id"]
        
        # Delete user
        response = client.delete(f"/api/v1/users/{user_id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify user is deleted
        get_response = client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_user_not_found(self, client: TestClient) -> None:
        """Test deleting a user that doesn't exist."""
        fake_uuid: str = "123e4567-e89b-12d3-a456-426614174000"
        response = client.delete(f"/api/v1/users/{fake_uuid}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in response.json()["detail"]