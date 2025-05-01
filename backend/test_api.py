import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import os
import sys

# Add the src directory to the path so we can import the API
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Import the API
from api import app, get_or_create_agent

# Create a test client
client = TestClient(app)

# Create a simulated AI agent
@pytest.fixture
def simulated_agent():
    agent = MagicMock()
    # Create a response object with test data
    result = MagicMock()
    result.data = "I found information about your receipts. You have 3 receipts from last month with a total value of $123.45."
    result.all_messages.return_value = [
        {"role": "user", "content": "Show me my receipts"},
        {"role": "assistant", "content": "I found information about your receipts. You have 3 receipts from last month with a total value of $123.45."}
    ]
    agent.run.return_value = result
    return agent

# Test the health endpoint
def test_health_endpoint(simulated_agent):
    with patch("api.get_or_create_agent", return_value=simulated_agent):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["connected"] == True

# Test the connect endpoint
def test_connect_endpoint(simulated_agent):
    with patch("api.get_or_create_agent", return_value=simulated_agent):
        response = client.post("/api/connect")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "connected"

# Test the chat endpoint
def test_chat_endpoint(simulated_agent):
    with patch("api.get_or_create_agent", return_value=simulated_agent):
        response = client.post(
            "/api/chat",
            json={"message": "Show me my receipts"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "Show me my receipts" in simulated_agent.run.call_args[0][0]
        assert data["response"] == "I found information about your receipts. You have 3 receipts from last month with a total value of $123.45."

# Test error handling
def test_chat_endpoint_error_handling():
    with patch("api.get_or_create_agent", side_effect=Exception("Test error")):
        response = client.post(
            "/api/chat",
            json={"message": "Show me my receipts"}
        )
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data 