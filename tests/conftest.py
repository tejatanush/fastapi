import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app  # Make sure this import points to your main FastAPI app instance
from app.database import Base, get_db
from app.config import settings
from app.oauth2 import create_access_token
from app import models
# 1. DEFINE THE TEST DATABASE URL
# It's a critical practice to separate your testing database from your development
# or production database to prevent accidental data loss.
SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}_test'

# 2. CREATE THE TEST DATABASE ENGINE AND SESSION MAKER
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. DEFINE THE CORE FIXTURES
# Pytest will automatically find these fixtures and use them in your test files.
@pytest.fixture
def test_user(client):
    """
    This fixture creates a user before any test that needs it.
    Because our fixtures have "function" scope, this user is created in a clean
    database and will be wiped out after the test is complete.
    """
    user_data = {"email": "sanjeev@example.com", "password": "password123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture
def test_user2(client):
    """
    This fixture creates a user before any test that needs it.
    Because our fixtures have "function" scope, this user is created in a clean
    database and will be wiped out after the test is complete.
    """
    user_data = {"email": "sanjeev1@example.com", "password": "password123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture(scope="function")
def session():
    """
    This fixture provides an isolated database session for each test function.
    
    KEY CONCEPTS:
    - scope="function": This is the crucial part. It ensures that a brand new,
      clean database is set up for EVERY single test. This prevents the state
      from one test (e.g., a created user) from leaking into another.
    - Clean Slate: We drop and recreate all tables before each test. This
      guarantees that every test starts from a known, empty state.
    """
    # Before the test runs, drop all existing tables and create new ones.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db  # The test runs at this point.
    finally:
        # After the test is finished, the session is closed.
        db.close()


@pytest.fixture(scope="function")
def client(session):
    """
    This fixture creates a TestClient that uses our clean `session` fixture.
    
    KEY CONCEPTS:
    - Dependency Override: This is a powerful FastAPI feature. We are telling
      the app: "For the duration of this test, whenever you ask for a database
      session (via `Depends(get_db)`), don't connect to the real database.
      Instead, use the clean, isolated `session` we just created."
    """
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    # Apply the override to our app
    app.dependency_overrides[get_db] = override_get_db
    
    # Provide the configured TestClient to our test functions
    yield TestClient(app)

@pytest.fixture
def token(test_user):
    return create_access_token({"user_id":test_user['id']})
@pytest.fixture
def authorized_client(client,token):
    client.headers={
        **client.headers,
        "Authorization":f"Bearer {token}"
    }
    return client


@pytest.fixture
def test_posts(test_user, session,test_user2):
    posts_data = [{
        "title": "first title",
        "content": "first content",
        "owner_id": test_user['id']
    }, {
        "title": "2nd title",
        "content": "2nd content",
        "owner_id": test_user['id']
    },
        {
        "title": "3rd title",
        "content": "3rd content",
        "owner_id": test_user['id']
    },{
        "title": "3rd title",
        "content": "3rd content",
        "owner_id": test_user2['id']
    }]
    def create_post_model(post):
        return models.Post(**post)
    posts = list(map(create_post_model, posts_data))
    session.add_all(posts)
    session.commit()
    all_posts=session.query(models.Post).all()
    return all_posts
