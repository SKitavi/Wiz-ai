import requests
import json
from loguru import logger

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health endpoint"""
    logger.info("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    logger.info(f"Health Status: {response.json()}")
    assert response.status_code == 200

def test_register():
    """Test user registration"""
    logger.info("Testing user registration...")
    
    user_data = {
        "email": "test@wizai.com",
        "password": "TestPass123",
        "full_name": "Test User",
        "preferences": {
            "study_hours": {"start": "09:00", "end": "21:00"}
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=user_data
    )
    
    if response.status_code == 201:
        data = response.json()
        logger.info(f"✅ Registration successful!")
        logger.info(f"Access Token: {data['access_token'][:20]}...")
        logger.info(f"User: {data['user']['email']}")
        return data['access_token']
    elif response.status_code == 400:
        logger.warning("User already exists, trying login...")
        return test_login()
    else:
        logger.error(f"Registration failed: {response.text}")
        return None

def test_login():
    """Test user login"""
    logger.info("Testing user login...")
    
    # OAuth2 password flow format
    login_data = {
        "username": "test@wizai.com",  # OAuth2 uses 'username' field
        "password": "TestPass123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data=login_data  # Use form data for OAuth2
    )
    
    if response.status_code == 200:
        data = response.json()
        logger.info("✅ Login successful!")
        logger.info(f"Access Token: {data['access_token'][:20]}...")
        return data['access_token']
    else:
        logger.error(f"Login failed: {response.text}")
        return None

def test_login_json():
    """Test JSON login endpoint"""
    logger.info("Testing JSON login...")
    
    login_data = {
        "email": "test@wizai.com",
        "password": "TestPass123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login/json",
        json=login_data
    )
    
    if response.status_code == 200:
        data = response.json()
        logger.info("✅ JSON login successful!")
        return data['access_token']
    else:
        logger.error(f"JSON login failed: {response.text}")
        return None

def test_get_me(token):
    """Test getting current user info"""
    logger.info("Testing /me endpoint...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers=headers
    )
    
    if response.status_code == 200:
        user = response.json()
        logger.info("✅ Got user info!")
        logger.info(f"User: {json.dumps(user, indent=2)}")
        return user
    else:
        logger.error(f"Failed to get user: {response.text}")
        return None

def test_update_profile(token):
    """Test updating user profile"""
    logger.info("Testing profile update...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    update_data = {
        "full_name": "Updated Test User",
        "preferences": {
            "study_hours": {"start": "08:00", "end": "22:00"},
            "break_duration": 20
        }
    }
    
    response = requests.put(
        f"{BASE_URL}/api/auth/me",
        headers=headers,
        params=update_data  # FastAPI will parse query params
    )
    
    if response.status_code == 200:
        user = response.json()
        logger.info("✅ Profile updated!")
        logger.info(f"Updated name: {user['full_name']}")
        return user
    else:
        logger.error(f"Profile update failed: {response.text}")
        return None

def test_protected_route_without_token():
    """Test accessing protected route without token"""
    logger.info("Testing protected route without token (should fail)...")
    
    response = requests.get(f"{BASE_URL}/api/auth/me")
    
    if response.status_code == 401:
        logger.info("✅ Correctly rejected unauthorized request!")
    else:
        logger.error("❌ Should have rejected unauthorized request!")

def test_invalid_token():
    """Test with invalid token"""
    logger.info("Testing with invalid token (should fail)...")
    
    headers = {
        "Authorization": "Bearer invalid_token_here"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers=headers
    )
    
    if response.status_code == 401:
        logger.info("✅ Correctly rejected invalid token!")
    else:
        logger.error("❌ Should have rejected invalid token!")

def run_all_tests():
    """Run all authentication tests"""
    logger.info("=" * 60)
    logger.info("Starting WizAI Authentication Tests")
    logger.info("=" * 60)
    
    try:
        # Test 1: Health check
        test_health_check()
        
        # Test 2: Register user (or login if exists)
        token = test_register()
        
        if not token:
            logger.error("❌ Failed to get authentication token")
            return
        
        # Test 3: Get current user
        test_get_me(token)
        
        # Test 4: Update profile
        test_update_profile(token)
        
        # Test 5: Test JSON login
        token2 = test_login_json()
        if token2:
            test_get_me(token2)
        
        # Test 6: Security tests
        test_protected_route_without_token()
        test_invalid_token()
        
        logger.info("=" * 60)
        logger.info("🎉 All tests completed!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()