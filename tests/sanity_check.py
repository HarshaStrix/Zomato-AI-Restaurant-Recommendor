
import requests
import json
import time

API_URL = "http://localhost:8000/api/v1/recommend"

def test_health():
    print("Checking API health...")
    res = requests.get("http://localhost:8000/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
    print("✅ API is healthy")

def test_recommendations_basic():
    print("Testing basic recommendations...")
    payload = {
        "location": {"place": "Bangalore"},
        "cuisine": "Italian",
        "limit": 3
    }
    res = requests.post(API_URL, json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["data"]["recommendations"]) > 0
    assert data["data"]["summary"]["ai_explanation"] is not None
    print(f"✅ Found {len(data['data']['recommendations'])} recommendations with AI summary")

def test_no_results():
    print("Testing no results with AI summary...")
    payload = {
        "location": {"place": "NonExistentPlaceForTestingPurpose"},
        "limit": 5
    }
    res = requests.post(API_URL, json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["data"]["recommendations"]) == 0
    # Now that we fixed it, ai_explanation should be present even if 0 results
    assert data["data"]["summary"]["ai_explanation"] is not None
    print("✅ Handled zero results with AI summary")

def test_natural_language():
    print("Testing natural language query extraction...")
    payload = {
        "natural_language_query": "cheap pizza in Bangalore",
        "limit": 5
    }
    res = requests.post(API_URL, json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    # The extraction should have found something
    print(f"✅ Natural language query returned {len(data['data']['recommendations'])} results")

if __name__ == "__main__":
    try:
        test_health()
        test_recommendations_basic()
        test_no_results()
        test_natural_language()
        print("\n🎉 ALL SANITY TESTS PASSED!")
    except Exception as e:
        print(f"\n❌ SANITY TEST FAILED: {e}")
        if 'res' in locals():
            print(f"Response: {res.text}")
