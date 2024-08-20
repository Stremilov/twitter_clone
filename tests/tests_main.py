import sys
import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import get_db
from app.models import create_test_user, Base


SQLALCHEMY_TEST_DATABASE_URL = "postgresql://postgres:postgres@db:5432/test_db"

engine_test_db = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test_db)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture(scope="module")
def db():
    app.dependency_overrides[get_db] = override_get_db

    Base.metadata.create_all(bind=engine_test_db)

    yield TestingSessionLocal()

    # Base.metadata.drop_all(bind=engine_test_db)


@pytest.fixture(scope="module")
def setup_and_teardown(db):
    try:
        test_user = create_test_user(db, name="Test User", api_key="test2")
        test_user_2 = create_test_user(db, name="Test User 2", api_key="test")
        db.commit()
        print("Users created and committed.")
    except Exception as e:
        print(f"Error during setup: {e}")
        raise e

    db.commit()

    yield test_user, test_user_2

    db.close()


@pytest.mark.asyncio
async def test_create_tweet(setup_and_teardown):
    test_user, _ = setup_and_teardown
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, app=app, base_url="http://localhost:8000/api") as client:
        response = await client.post(
            "/tweets",
            json={
                "tweet_data": "This is a test tweet",
                "tweet_media_ids": []
            },
            headers={"api-key": "test"},
        )
    print(response.json())
    assert response.status_code == 200
    assert response.json()["result"] == True

@pytest.mark.asyncio
async def test_upload_media(setup_and_teardown):
    test_user, _ = setup_and_teardown
    with open("test_image.png", "wb") as f:
        f.write(os.urandom(1024))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, app=app, base_url="http://localhost:8000/api") as client:
        with open("test_image.png", "rb") as f:
            response = await client.post(
                "/medias",
                files={"file": f},
                headers={"api-key": test_user.api_key},
            )
    os.remove("test_image.png")

    assert response.status_code == 200
    assert response.json()["result"] == True

@pytest.mark.asyncio
async def test_delete_tweet(setup_and_teardown):
    test_user, _ = setup_and_teardown
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, app=app, base_url="http://localhost:8000/api") as client:
        response = await client.post(
            "/tweets",
            json={
                "tweet_data": "This is a tweet to be deleted",
                "tweet_media_ids": []
            },
            headers={"api-key": test_user.api_key},
        )

        tweet_id = response.json()["tweet_id"]

        response = await client.delete(
            f"/tweets/{tweet_id}",
            headers={"api-key": test_user.api_key},
        )
    assert response.status_code == 200
    assert response.json()["result"] == True

@pytest.mark.asyncio
async def test_like_tweet(setup_and_teardown):
    test_user, _ = setup_and_teardown
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, app=app, base_url="http://localhost:8000/api") as client:
        response = await client.post(
            "/tweets",
            json={
                "tweet_data": "This is a tweet to be liked",
                "tweet_media_ids": []
            },
            headers={"api-key": test_user.api_key},
        )

        tweet_id = response.json()["tweet_id"]

        response = await client.post(
            f"/tweets/{tweet_id}/likes",
            headers={"api-key": test_user.api_key},
        )
    assert response.status_code == 200
    assert response.json()["result"] == True

@pytest.mark.asyncio
async def test_unlike_tweet(setup_and_teardown):
    test_user, _ = setup_and_teardown
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, app=app, base_url="http://localhost:8000/api") as client:
        response = await client.post(
            "/tweets",
            json={
                "tweet_data": "This is a tweet to be unliked",
                "tweet_media_ids": []
            },
            headers={"api-key": test_user.api_key},
        )
        tweet_id = response.json()["tweet_id"]

        like_response = await client.post(
            f"/tweets/{tweet_id}/likes",
            headers={"api-key": test_user.api_key},
        )

        assert like_response.status_code == 200

        response = await client.delete(
            f"/tweets/{tweet_id}/likes",
            headers={"api-key": test_user.api_key},
        )
    assert response.status_code == 200
    assert response.json()["result"] == True


@pytest.mark.asyncio
async def test_follow_user(setup_and_teardown):
    test_user, test_user_2 = setup_and_teardown
    user_id = test_user_2.id

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, app=app, base_url="http://localhost:8000/api") as client:
        response = await client.post(
            f"/users/{user_id}/follow",
            headers={"api-key": test_user.api_key},
        )
    assert response.status_code == 200
    assert response.json()["result"] == True


@pytest.mark.asyncio
async def test_unfollow_user(setup_and_teardown):
    test_user, test_user_2 = setup_and_teardown
    user_id = test_user_2.id

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, app=app, base_url="http://localhost:8000/api") as client:
        response = await client.delete(
            f"/users/{user_id}/follow",
            headers={"api-key": test_user.api_key},
        )
    assert response.status_code == 200
    assert response.json()["result"] == True

@pytest.mark.asyncio
async def test_get_feed():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, app=app, base_url="http://localhost:8000/api") as client:
        response = await client.get("/tweets")
    assert response.status_code == 200
    assert response.json()["result"] == True


@pytest.mark.asyncio
async def test_get_profile():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, app=app, base_url="http://localhost:8000/api") as client:
        response = await client.get("/users/me", headers={"api-key": "test2"})
    assert response.status_code == 200
    assert response.json()["result"] == "true"


@pytest.mark.asyncio
async def test_get_user_profile():
    user_id = 2

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, app=app, base_url="http://localhost:8000/api") as client:
        response = await client.get(f"/users/{user_id}", headers={"api-key": "test2"})
    assert response.status_code == 200
    assert response.json()["result"] == True
