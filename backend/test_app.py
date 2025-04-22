import pytest
from app import app

# ------------------------------
# Unit Tests
# ------------------------------
@pytest.fixture
def client():
    """Fixture to create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_chat_endpoint_valid_request(client):
    """Unit Test: Test the /api/chat endpoint with a valid request."""
    payload = {
        "messages": [
            {"role": "user", "content": "What is the current stock price of AAPL?"},
            {"role": "assistant", "content": "The current stock price of AAPL is $150."}
        ]
    }
    response = client.post('/api/chat', json=payload)
    assert response.status_code == 200
    assert "message" in response.json
    assert isinstance(response.json["message"], str)

def test_chat_endpoint_missing_messages(client):
    """Unit Test: Test the /api/chat endpoint with a missing 'messages' field."""
    payload = {}
    response = client.post('/api/chat', json=payload)
    assert response.status_code == 400
    assert response.json == {"error": "Invalid request. 'messages' is required"}

def test_chat_endpoint_no_user_message(client):
    """Unit Test: Test the /api/chat endpoint with no user message in the 'messages' array."""
    payload = {
        "messages": [
            {"role": "assistant", "content": "Hello, how can I help you?"}
        ]
    }
    response = client.post('/api/chat', json=payload)
    assert response.status_code == 400
    assert response.json == {"error": "No user message found"}

def test_chat_endpoint_agent_error(client, mocker):
    """Unit Test: Test the /api/chat endpoint when the financial agent raises an error."""
    payload = {
        "messages": [
            {"role": "user", "content": "What is the current stock price of AAPL?"}
        ]
    }
    # Mock the financial_agent.chat method to raise an exception
    mocker.patch('agentic_rag.agent.chat', side_effect=Exception("Agent error"))
    response = client.post('/api/chat', json=payload)
    assert response.status_code == 500
    assert "I encountered an error processing your request" in response.json["message"]

def test_chat_endpoint_invalid_json(client):
    """Unit Test: Test the /api/chat endpoint with invalid JSON payload."""
    response = client.post('/api/chat', data="Invalid JSON", content_type='application/json')
    assert response.status_code == 400  # Flask automatically returns 400 for malformed JSON

# ------------------------------
# Integration Tests
# ------------------------------
def test_integration_server_health():
    """Integration Test: Test the /api/test endpoint to verify the server is up."""
    import requests
    url = "http://127.0.0.1:5000/api/test"
    response = requests.get(url)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
    assert response.status_code == 200
    assert response.json() == {"message": "Backend is working"}

def test_integration_chat_endpoint():
    """Integration Test: Test the /api/chat endpoint to verify the third-party service is operational."""
    import requests
    url = "http://127.0.0.1:5000/api/chat"
    
    # Test a valid request
    payload = {
        "messages": [
            {"role": "user", "content": "What is the current stock price of AAPL?"}
        ]
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    assert "message" in response.json()
    assert isinstance(response.json()["message"], str)

    # Test an invalid request (missing 'messages' field)
    invalid_payload = {}
    response = requests.post(url, json=invalid_payload)
    assert response.status_code == 400
    assert response.json() == {"error": "Invalid request. 'messages' is required"}