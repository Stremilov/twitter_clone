import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from starlette.testclient import TestClient
from fastapi.testclient import TestClient
# Добавление корневого каталога проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, get_db
from app.main import app_api,app , create_test_user
from app import crud, models

SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# Dependency override
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


client_base = TestClient(app)
client_api = TestClient(app_api)

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    db = TestingSessionLocal()

    test_user = create_test_user(db, name="Test User", api_key="test2")
    test_user_2 = create_test_user(db, name="Test User 2", api_key="test")
    db.commit()
    yield test_user, test_user_2


def test_create_tweet(setup_and_teardown):
    test_user, _ = setup_and_teardown
    response = client_api.post(
        "/tweets",
        json={"tweet_data": "This is a test tweet"},
        headers={"api_key": test_user.api_key},
    )
    assert response.status_code == 200
    assert response.json()["result"] == True

def test_upload_media(setup_and_teardown):
    test_user, _ = setup_and_teardown
    with open("tests/test_image.png", "wb") as f:
        f.write(os.urandom(1024))  # create a dummy file

    with open("tests/test_image.png", "rb") as f:
        response = client.post(
            "/medias",
            files={"file": f},
            headers={"api_key": test_user.api_key},
        )
    os.remove("tests/test_image.png")  # clean up the dummy file

    assert response.status_code == 200
    assert response.json()["result"] == True

def test_delete_tweet(setup_and_teardown):
    test_user, _ = setup_and_teardown
    response = client.post(
        "/tweets",
        json={"tweet_data": "This is a tweet to be deleted"},
        headers={"api_key": test_user.api_key},
    )
    tweet_id = response.json()["tweet_id"]

    response = client.delete(
        f"/tweets/{tweet_id}",
        headers={"api_key": test_user.api_key},
    )
    assert response.status_code == 200
    assert response.json()["result"] == True

def test_like_tweet(setup_and_teardown):
    test_user, _ = setup_and_teardown
    response = client.post(
        "/tweets",
        json={"tweet_data": "This is a tweet to be liked"},
        headers={"api_key": test_user.api_key},
    )
    tweet_id = response.json()["tweet_id"]

    response = client.post(
        f"/tweets/{tweet_id}/likes",
        headers={"api_key": test_user.api_key},
    )
    assert response.status_code == 200
    assert response.json()["result"] == True

def test_unlike_tweet(setup_and_teardown):
    test_user, _ = setup_and_teardown
    response = client.post(
        "/tweets",
        json={"tweet_data": "This is a tweet to be unliked"},
        headers={"api_key": test_user.api_key},
    )
    tweet_id = response.json()["tweet_id"]

    response = client.post(
        f"/tweets/{tweet_id}/likes",
        headers={"api_key": test_user.api_key},
    )
    response = client.delete(
        f"/tweets/{tweet_id}/likes",
        headers={"api_key": test_user.api_key},
    )
    assert response.status_code == 200
    assert response.json()["result"] == True

def test_follow_user(setup_and_teardown):
    test_user, test_user_2 = setup_and_teardown
    user_id = test_user_2.id

    response = client.post(
        f"/users/{user_id}/follow",
        headers={"api_key": test_user.api_key},
    )
    assert response.status_code == 200
    assert response.json()["result"] == True

def test_unfollow_user(setup_and_teardown):
    test_user, test_user_2 = setup_and_teardown
    user_id = test_user_2.id

    response = client.delete(
        f"/users/{user_id}/follow",
        headers={"api_key": test_user.api_key},
    )
    assert response.status_code == 200
    assert response.json()["result"] == True

def test_get_feed():
    response = client.get("/tweets")
    assert response.status_code == 200
    assert response.json()["result"] == True

def test_get_profile(setup_and_teardown):
    test_user, _ = setup_and_teardown
    response = client.get(
        "/users/me",
        headers={"api_key": test_user.api_key},
    )
    assert response.status_code == 200
    assert response.json()["result"] == "true"

def test_get_user_profile(setup_and_teardown):
    test_user, test_user_2 = setup_and_teardown
    user_id = test_user_2.id

    response = client.get(
        f"/users/{user_id}",
        headers={"api_key": test_user.api_key},
    )
    assert response.status_code == 200
    assert response.json()["result"] == True
