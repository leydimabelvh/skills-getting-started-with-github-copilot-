import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture to provide a TestClient for the FastAPI app."""
    return TestClient(app)


def test_root_redirect(client):
    """Test that GET / redirects to /activities."""
    # Arrange - no special setup needed

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200  # TestClient follows redirects by default


def test_get_activities(client):
    """Test GET /activities returns all activities."""
    # Arrange - no special setup needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # Based on the initial data
    # Check structure of one activity
    activity = data["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_signup_success(client):
    """Test successful signup for an activity."""
    # Arrange
    activity_name = "Chess Club"
    email = "student@example.com"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Signed up {email} for {activity_name}"
    # Verify the student is now in the participants
    response_check = client.get("/activities")
    activities = response_check.json()
    activity = activities[activity_name]
    assert email in activity["participants"]


def test_signup_duplicate(client):
    """Test signup fails when student is already signed up."""
    # Arrange
    activity_name = "Chess Club"
    email = "student@example.com"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})  # First signup

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_invalid_activity(client):
    """Test signup fails for non-existent activity."""
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@example.com"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_success(client):
    """Test successful unregister from an activity."""
    # Arrange
    activity_name = "Programming Class"
    email = "student@example.com"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})  # Signup first

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Unregistered {email} from {activity_name}"
    # Verify the student is removed from participants
    response_check = client.get("/activities")
    activities = response_check.json()
    activity = activities[activity_name]
    assert email not in activity["participants"]


def test_unregister_not_enrolled(client):
    """Test unregister fails when student is not signed up."""
    # Arrange
    activity_name = "Programming Class"
    email = "student@example.com"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]


def test_unregister_invalid_activity(client):
    """Test unregister fails for non-existent activity."""
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@example.com"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]