
import pytest
from unittest.mock import MagicMock
from phase4.llm_service import LLMService
from phase4.clients.groq_client import GroqClient
from phase4.parsers.response_parser import ResponseParser

def test_llm_service_error_handling():
    # Mock client to raise an exception
    mock_client = MagicMock(spec=GroqClient)
    mock_client.is_available.return_value = True
    mock_client.complete.side_effect = Exception("Groq API Error")
    
    service = LLMService(client=mock_client)
    
    restaurants = [{"name": "Test Resto", "rating": 4.5}]
    result = service.generate_explanations(restaurants, "Bangalore", "Italian")
    
    assert result["from_fallback"] is True
    assert "Test Resto" in str(result["explanations"])
    assert "summary" in result
    assert "Bangalore" in result["summary"]

def test_response_parser_non_json():
    parser = ResponseParser()
    raw = "This is not JSON but a conversational response."
    parsed = parser.parse(raw)
    
    assert parsed["summary"] == raw
    assert parsed["explanations"] == []

if __name__ == "__main__":
    import sys
    pytest.main([__file__])
