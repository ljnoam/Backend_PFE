from unittest.mock import patch

def test_generate_prompt_with_auth(client):
    # 1. Register and get token
    email = "prompt_user@example.com"
    password = "secret_password"
    client.post("/register", json={"email": email, "password": password})
    
    login_res = client.post("/token", data={"username": email, "password": password})
    token = login_res.json()["access_token"]
    
    # 2. Mock 'rewrite_prompt' to avoid real API call
    # We mock the function where it is IMPORTED in the router, not defined!
    with patch("app.api.routes.prompts.rewrite_prompt") as mock_rewrite:
        mock_rewrite.return_value = "MOCKED PROMPT"
        
        # 3. Call protected endpoint
        response = client.post(
            "/api/generate",
            headers={"Authorization": f"Bearer {token}"},
            json={"input_text": "Make me a logo", "target_model": "mistral"}
        )
        
        # 4. Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["original_text"] == "Make me a logo"
        assert data["optimized_prompt"] == "MOCKED PROMPT"
        # Check that sovereignty is correct for mistral
        assert data["sovereignty_location"] == "EU" 
