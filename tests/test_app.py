from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app, activities


# keep original data for resetting between tests
INITIAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Arrange fixture: restore module-level activities before each test"""
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))
    yield


client = TestClient(app)


def test_root_redirect():
    # Arrange: none
    # Act (disable auto-redirects so we can inspect the response status)
    response = client.get("/", follow_redirects=False)
    # Assert
    assert response.status_code == 307 or response.status_code == 200
    # if redirect is followed (status 200), header may not contain location
    if response.status_code == 307:
        assert response.headers["location"].endswith("/static/index.html")


def test_get_activities():
    # Arrange: none
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()


def test_successful_signup():
    # Arrange
    email = "newstudent@mergington.edu"
    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_already_signed():
    # Arrange
    email = INITIAL_ACTIVITIES["Chess Club"]["participants"][0]
    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})
    # Assert
    assert response.status_code == 400


def test_signup_nonexistent_activity():
    # Arrange
    email = "student@mergington.edu"
    # Act
    response = client.post("/activities/Nonexistent/signup", params={"email": email})
    # Assert
    assert response.status_code == 404


def test_successful_unregister():
    # Arrange
    email = INITIAL_ACTIVITIES["Chess Club"]["participants"][0]
    # Act
    response = client.delete("/activities/Chess Club/participants", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_not_signed():
    # Arrange
    email = "nobody@mergington.edu"
    # Act
    response = client.delete("/activities/Chess Club/participants", params={"email": email})
    # Assert
    assert response.status_code == 400


def test_unregister_nonexistent_activity():
    # Arrange
    email = "student@mergington.edu"
    # Act
    response = client.delete("/activities/Unknown/participants", params={"email": email})
    # Assert
    assert response.status_code == 404
