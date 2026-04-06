import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import Base, get_db

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop them after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data
    assert "created_at" in data


def test_register_duplicate_email(client):
    """Test registering with duplicate email fails"""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    # First registration
    response1 = client.post("/auth/register", json=user_data)
    assert response1.status_code == 201
    
    # Try to register with same email but different username
    response2 = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "anotheruser",
            "password": "testpass123"
        }
    )
    assert response2.status_code == 400
    assert "Email already registered" in response2.json()["detail"]


def test_register_duplicate_username(client):
    """Test registering with duplicate username fails"""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    # First registration
    response1 = client.post("/auth/register", json=user_data)
    assert response1.status_code == 201
    
    # Try to register with same username but different email
    response2 = client.post(
        "/auth/register",
        json={
            "email": "another@example.com",
            "username": "testuser",
            "password": "testpass123"
        }
    )
    assert response2.status_code == 400
    assert "Username already taken" in response2.json()["detail"]


def test_login_success(client):
    """Test successful login"""
    # Register user
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123"
        }
    )
    
    # Login
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    """Test login with wrong password fails"""
    # Register user
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123"
        }
    )
    
    # Try to login with wrong password
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Test login with non-existent user fails"""
    response = client.post(
        "/auth/login",
        data={"username": "nonexistent", "password": "testpass123"}
    )
    assert response.status_code == 401


def test_get_current_user(client):
    """Test getting current user info"""
    # Register and login
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123"
        }
    )
    login_response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


def test_get_current_user_no_token(client):
    """Test accessing protected endpoint without token fails"""
    response = client.get("/users/me")
    assert response.status_code == 401


def test_get_current_user_invalid_token(client):
    """Test accessing protected endpoint with invalid token fails"""
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
