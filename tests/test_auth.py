def test_register_user_success(client):
    response = client.post(
        "/register",
        json={"email": "test@example.com", "password": "securepassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_register_duplicate_email(client):
    # 1. First registration
    client.post(
        "/register",
        json={"email": "duplicate@example.com", "password": "password123"}
    )
    
    # 2. Second registration (should fail)
    response = client.post(
        "/register",
        json={"email": "duplicate@example.com", "password": "password456"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_success(client):
    # Register first
    client.post(
        "/register",
        json={"email": "login@example.com", "password": "mypassword"}
    )
    
    # Attempt login
    response = client.post(
        "/token",
        data={"username": "login@example.com", "password": "mypassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure(client):
    # Register first
    client.post(
        "/register",
        json={"email": "fail@example.com", "password": "correctpassword"}
    )
    
    # Attempt login with wrong password
    response = client.post(
        "/token",
        data={"username": "fail@example.com", "password": "WRONGpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
