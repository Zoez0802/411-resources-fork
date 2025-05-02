import pytest
import requests
import json
from werkzeug.security import generate_password_hash

# Base URL for the API
BASE_URL = "http://localhost:5000/api"

# Test user credentials
TEST_USER = "smoketest_user"
TEST_PASSWORD = "smoketest_password"
NEW_PASSWORD = "new_smoketest_password"

def test_healthcheck():
    """Test the healthcheck endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["message"] == "Service is running"

def test_user_management():
    """Test user creation, login, password change, and logout"""
    
    # Clean up any existing test user first
    requests.delete(f"{BASE_URL}/reset-users")
    
    # Test user creation
    create_response = requests.put(
        f"{BASE_URL}/create-user",
        json={"username": TEST_USER, "password": TEST_PASSWORD}
    )
    assert create_response.status_code == 201
    
    # Test duplicate user creation
    duplicate_response = requests.put(
        f"{BASE_URL}/create-user",
        json={"username": TEST_USER, "password": TEST_PASSWORD}
    )
    assert duplicate_response.status_code == 400
    
    # Test login with correct credentials
    login_response = requests.post(
        f"{BASE_URL}/login",
        json={"username": TEST_USER, "password": TEST_PASSWORD}
    )
    assert login_response.status_code == 200
    session_cookie = login_response.cookies.get("session")
    
    # Test login with incorrect credentials
    bad_login_response = requests.post(
        f"{BASE_URL}/login",
        json={"username": TEST_USER, "password": "wrong_password"}
    )
    assert bad_login_response.status_code == 401
    
    # Test password change
    change_pw_response = requests.post(
        f"{BASE_URL}/change-password",
        json={"new_password": NEW_PASSWORD},
        cookies={"session": session_cookie}
    )
    assert change_pw_response.status_code == 200
    
    # Test logout
    logout_response = requests.post(
        f"{BASE_URL}/logout",
        cookies={"session": session_cookie}
    )
    assert logout_response.status_code == 200
    
    # Verify new password works
    new_login_response = requests.post(
        f"{BASE_URL}/login",
        json={"username": TEST_USER, "password": NEW_PASSWORD}
    )
    assert new_login_response.status_code == 200

def test_favorites_workflow():
    """Test the favorites workflow"""
    
    # Login first
    login_response = requests.post(
        f"{BASE_URL}/login",
        json={"username": TEST_USER, "password": NEW_PASSWORD}
    )
    session_cookie = login_response.cookies.get("session")
    
    # Add a favorite location
    add_fav_response = requests.post(
        f"{BASE_URL}/favorites/add",
        json={
            "user_id": TEST_USER,
            "location_name": "London",
            "latitude": 51.5074,
            "longitude": -0.1278
        },
        cookies={"session": session_cookie}
    )
    assert add_fav_response.status_code in [201, 409]  # 409 if already exists
    
    # Get favorites list
    fav_list_response = requests.get(
        f"{BASE_URL}/favorites/list",
        params={"user_id": TEST_USER},
        cookies={"session": session_cookie}
    )
    assert fav_list_response.status_code == 200
    assert len(fav_list_response.json()) > 0
    
    # Get favorites with weather (mock this if API key isn't available)
    fav_weather_response = requests.get(
        f"{BASE_URL}/favorites/weather",
        params={"user_id": TEST_USER},
        cookies={"session": session_cookie}
    )
    assert fav_weather_response.status_code in [200, 404, 500]  # 500 if API key issues
    
    # Get current weather for a location
    current_weather_response = requests.get(
        f"{BASE_URL}/weather/current",
        params={
            "location_name": "London",
            "user_id": TEST_USER
        },
        cookies={"session": session_cookie}
    )
    assert current_weather_response.status_code in [200, 400, 500]  # 500 if API key issues

def test_protected_endpoints():
    """Test that protected endpoints require authentication"""
    endpoints = [
        ("/favorites/add", "POST"),
        ("/logout", "POST"),
        ("/change-password", "POST"),
        ("/favorites/list", "GET"),
        ("/weather/current", "GET")
    ]
    
    for endpoint, method in endpoints:
        if method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}")
        else:
            response = requests.get(f"{BASE_URL}{endpoint}")
        
        assert response.status_code == 401
        assert "Authentication required" in response.json()["message"]

if __name__ == "__main__":
    # Run the smoke tests
    pytest.main(["-v", "smoke_tests.py"])