import pytest
from fastapi.testclient import TestClient
from src.app import app

@pytest.fixture
def client():
    return TestClient(app)

def test_root_redirect(client):
    """Test that root path redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (301, 302, 307)  # Any valid redirect code
    assert response.headers["location"] == "/static/index.html"

def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    
    # Test structure of an activity
    activity = next(iter(activities.values()))
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)

def test_signup_for_activity(client):
    """Test signing up for an activity"""
    # Test successful signup
    response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    assert "Signed up test@mergington.edu for Chess Club" in response.json()["message"]
    
    # Verify participant was added
    activities = client.get("/activities").json()
    assert "test@mergington.edu" in activities["Chess Club"]["participants"]
    
    # Test duplicate signup
    response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()
    
    # Test signup for non-existent activity
    response = client.post("/activities/NonExistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unregister_from_activity(client):
    """Test unregistering from an activity"""
    # First sign up a test participant
    email = "unregister_test@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")
    
    # Test successful unregistration
    response = client.post(f"/activities/Chess Club/unregister?email={email}")
    assert response.status_code == 200
    assert f"Unregistered {email} from Chess Club" in response.json()["message"]
    
    # Verify participant was removed
    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]
    
    # Test unregistering non-registered participant
    response = client.post(f"/activities/Chess Club/unregister?email={email}")
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"].lower()
    
    # Test unregistering from non-existent activity
    response = client.post(f"/activities/NonExistentClub/unregister?email={email}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()