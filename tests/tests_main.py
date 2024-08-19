import sys
import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app, create_test_user


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"



engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@pytest.fixture(scope="module")
def setup_and_teardown():
    db = TestingSessionLocal()

    test_user = create_test_user(db, name="Test User", api_key="test2")
    test_user_2 = create_test_user(db, name="Test User 2", api_key="test")

    db.commit()

    yield test_user, test_user_2

    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.mark.asyncio
async def test_create_tweet(setup_and_teardown):
    test_user, _ = setup_and_teardown
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, app=app, base_url="http://localhost:8000/api") as client:
        response = await client.post(
            "/tweets",
            json={"tweet_data": "This is a test tweet"},
            headers={"api_key": test_user.api_key},
        )
    assert response.status_code == 200
    assert response.json()["result"] == True

@pytest.mark.asyncio
async def test_upload_media(setup_and_teardown):
    test_user, _ = setup_and_teardown
    with open("tests/test_image.png", "wb") as f:
        f.write(os.urandom(1024))  # create a dummy file

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, app=app, base_url="http://localhost:8000/api") as client:
        with open("tests/test_image.png", "rb") as f:
            response = await client.post(
                "/medias",
                files={"file": f},
                headers={"api_key": test_user.api_key},
            )
    os.remove("tests/test_image.png")  # clean up the dummy file

    assert response.status_code == 200
    assert response.json()["result"] == True

@pytest.mark.asyncio
async def test_delete_tweet(setup_and_teardown):
    test_user, _ = setup_and_teardown
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, app=app, base_url="http://localhost:8000/api") as client:
        response = await client.post(
            "/tweets",
            json={"tweet_data": "This is a tweet to be deleted"},
            headers={"api_key": test_user.api_key},
        )
        tweet_id = response.json()["tweet_id"]

        response = await client.delete(
            f"/tweets/{tweet_id}",
            headers={"api_key": test_user.api_key},
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
            json={"tweet_data": "This is a tweet to be liked"},
            headers={"api_key": test_user.api_key},
        )
        tweet_id = response.json()["tweet_id"]

        response = await client.post(
            f"/tweets/{tweet_id}/likes",
            headers={"api_key": test_user.api_key},
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
            json={"tweet_data": "This is a tweet to be unliked"},
            headers={"api_key": test_user.api_key},
        )
        tweet_id = response.json()["tweet_id"]

        await client.post(
            f"/tweets/{tweet_id}/likes",
            headers={"api_key": test_user.api_key},
        )
        response = await client.delete(
            f"/tweets/{tweet_id}/likes",
            headers={"api_key": test_user.api_key},
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
            headers={"api_key": test_user.api_key},
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
            headers={"api_key": test_user.api_key},
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
        response = await client.get("/users/me", headers={"api_key": "test2"})
    assert response.status_code == 200
    assert response.json()["result"] == True

@pytest.mark.asyncio
async def test_get_user_profile():
    user_id = 2

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, app=app, base_url="http://localhost:8000/api") as client:
        response = await client.get(f"/users/{user_id}", headers={"api_key": "test2"})
    assert response.status_code == 200
    assert response.json()["result"] == True
