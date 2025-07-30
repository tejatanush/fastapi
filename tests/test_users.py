import pytest
from jose import jwt
from app import schemas
from app.config import settings

# Note: We don't need to import 'client' or 'session'. Pytest finds them in conftest.py
# and injects them automatically based on the function arguments in our tests.

@pytest.fixture
def test_user(client):
    """
    This fixture creates a user before any test that needs it.
    Because our fixtures have "function" scope, this user is created in a clean
    database and will be wiped out after the test is complete.
    """
    user_data = {"email": "testuser123@example.com", "password": "password123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user

def test_create_user(client):
    """
    Tests the user creation endpoint. This test is fully independent.
    """
    res = client.post("/users/", json={"email": "newuser456@example.com", "password": "password456"})
    
    # Validate the response against our Pydantic schema for correctness.
    new_user = schemas.UserOut(**res.json())
    
    assert res.status_code == 201
    assert new_user.email == "newuser456@example.com"

def test_login_user(client, test_user):
    """
    Tests a successful user login. It depends on the `test_user` fixture
    to first create a user to log in with.
    """
    res = client.post(
        "/login", 
        data={"username": test_user['email'], "password": test_user['password']}
    )
    
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token, settings.SECRETE_KEY, algorithms=[settings.ALGORITHM])
    user_id_from_token = payload.get("user_id")
    
    assert res.status_code == 200
    assert user_id_from_token == test_user['id']
    assert login_res.token_type == "bearer"

@pytest.mark.parametrize("email, password, status_code, detail_message", [
    ("testuser123@example.com", "wrongpassword", 403, "Invalid Credentials"),
    ("nonexistent@example.com", "password123", 403, "Invalid Credentials"),
    (None, "password123", 403, "Invalid Credentials"),
    #("testuser123@example.com", None, 403, None) # FastAPI gives 422 for missing form data
])
def test_incorrect_login(test_user, client, email, password, status_code, detail_message):
    """
    Tests various scenarios for failed login attempts using pytest's parametrize feature.
    This makes the test clean and DRY (Don't Repeat Yourself).
    """
    # The `test_user` fixture runs here to ensure a user exists in the database
    # against which we can test incorrect credentials.
    
    # Use the email from the parameters, which might be the correct one or a non-existent one.
    res = client.post(
        "/login", 
        data={"username": email, "password": password}
    )
    
    assert res.status_code == status_code
    
    # For failed authentication, we also check if the error message is correct.
    if detail_message:
        assert res.json().get('detail') == detail_message

