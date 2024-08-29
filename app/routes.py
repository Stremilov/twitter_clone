import json
import logging
import os

from fastapi import APIRouter, HTTPException, Depends, Header, UploadFile, File
from sqlalchemy.orm import Session
from app import schemas, models
from app.repository.user_repository import UserRepository
from app.repository.tweet_repository import TweetRepository
from app.repository.media_repository import MediaRepository
from app.database import get_db

import redis


router = APIRouter()

redis_client = redis.StrictRedis(host="redis", port="6379")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def save_uploaded_file(file: UploadFile):
    upload_folder = "app/static"
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    file_path = os.path.join(upload_folder, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    logger.info(f"Uploaded file saved at {file_path}")
    return file.filename


def update_feed_cache(db: Session):
    """Update the Redis cache for the tweet feed."""
    tweet_repo = TweetRepository(db)
    tweets_data = tweet_repo.get_feed()

    if not tweets_data:
        raise HTTPException(status_code=404, detail="No tweets found")

    tweets = []
    for tweet in tweets_data:
        media = [media.file_path for media in tweet.media]
        likes = [{"user_id": user.id, "name": user.name} for user in tweet.liked_by]
        tweet_dict = {
            "id": tweet.id,
            "content": tweet.tweet_data,
            "attachments": media,
            "author": {"id": tweet.author.id, "name": tweet.author.name},
            "likes": likes,
        }
        tweets.append(tweet_dict)

    redis_client.set("Feed", json.dumps(tweets))
    logger.info("Feed cache updated in Redis with key: Feed")


@router.post("/tweets", response_model=schemas.TweetCreateResponse)
def make_tweet(
    tweet: schemas.TweetCreate,
    api_key: str = Header(...),
    db: Session = Depends(get_db),
):
    user_repo = UserRepository(db)
    tweet_repo = TweetRepository(db)

    user = user_repo.get_user_by_api_key(api_key)

    if not user:
        logger.warning(f"Invalid API key: {api_key}")
        raise HTTPException(status_code=403, detail="Invalid API key")

    db_tweet = tweet_repo.create_tweet(tweet, user.id)
    logger.info(f"Tweet created with ID: {db_tweet.id}")

    update_feed_cache(db)

    return {"result": True, "tweet_id": db_tweet.id}


@router.post("/medias")
def upload_media(
    api_key: str = Header(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    user_repo = UserRepository(db)
    media_repo = MediaRepository(db)

    user = user_repo.get_user_by_api_key(api_key)
    if not user:
        logger.warning(f"Invalid API key: {api_key}")
        raise HTTPException(status_code=403, detail="Invalid API key")

    file_path = save_uploaded_file(file)
    media = media_repo.upload_media(file_path)
    logger.info(f"Media uploaded with ID: {media.id}")

    redis_client.set(f"Media: {media.id}", file_path)
    logger.info(f"Media cached in Redis with key: Media: {media.id}")

    redis_client.delete("Feed")
    update_feed_cache(db)

    return {"result": True, "media_id": media.id}


@router.delete("/tweets/{tweet_id}")
def delete_tweet(
    tweet_id: int, api_key: str = Header(...), db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    tweet_repo = TweetRepository(db)

    user = user_repo.get_user_by_api_key(api_key)
    if not user:
        logger.warning(f"Invalid API key: {api_key}")
        raise HTTPException(status_code=403, detail="Invalid API key")

    if not tweet_repo.delete_tweet(tweet_id, user.id):
        logger.warning(
            f"Tweet not found or unauthorized delete attempt for tweet ID: {tweet_id}"
        )
        raise HTTPException(status_code=404, detail="Tweet not found or unauthorized")

    redis_client.delete(f"Tweet: {tweet_id}")

    update_feed_cache(db)

    return {"result": True}


@router.post("/tweets/{tweet_id}/likes")
def like_tweet(
    tweet_id: int, api_key: str = Header(...), db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    tweet_repo = TweetRepository(db)

    user = user_repo.get_user_by_api_key(api_key)
    if not user:
        logger.warning(f"Invalid API key: {api_key}")
        raise HTTPException(status_code=403, detail="Invalid API key")

    if not tweet_repo.like_tweet(tweet_id, user.id):
        logger.warning(
            f"Tweet not found or unauthorized like attempt for tweet ID: {tweet_id}"
        )
        raise HTTPException(status_code=404, detail="Tweet not found")

    redis_client.delete(f"Tweet: {tweet_id}")
    logger.info(
        f"Tweet removed from Redis cache after like with key: Tweet: {tweet_id}"
    )

    update_feed_cache(db)

    return {"result": True}


@router.delete("/tweets/{tweet_id}/likes")
def unlike_tweet(
    tweet_id: int, api_key: str = Header(...), db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    tweet_repo = TweetRepository(db)

    user = user_repo.get_user_by_api_key(api_key)
    if not user:
        logger.warning(f"Invalid API key: {api_key}")
        raise HTTPException(status_code=403, detail="Invalid API key")

    if not tweet_repo.unlike_tweet(tweet_id, user.id):
        logger.warning(
            f"Tweet not found or unauthorized unlike attempt for tweet ID: {tweet_id}"
        )
        raise HTTPException(status_code=404, detail="Tweet not found")

    redis_client.delete(f"Tweet: {tweet_id}")
    logger.info(
        f"Tweet removed from Redis cache after unlike with key: Tweet: {tweet_id}"
    )

    update_feed_cache(db)

    return {"result": True}


@router.post("/users/{user_id}/follow")
def follow_user(
    user_id: int, api_key: str = Header(...), db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)

    user = user_repo.get_user_by_api_key(api_key)
    if not user:
        logger.warning(f"Invalid API key: {api_key}")
        raise HTTPException(status_code=403, detail="Invalid API key")

    if not user_repo.follow_user(user.id, user_id):
        logger.warning(f"User not found for follow attempt, user ID: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    redis_client.delete(f"User: {user_id}")
    logger.info(
        f"User profile removed from Redis cache after follow with key: User: {user_id}"
    )

    return {"result": True}


@router.delete("/users/{user_id}/follow")
def unfollow_user(
    user_id: int, api_key: str = Header(...), db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)

    user = user_repo.get_user_by_api_key(api_key)
    if not user:
        logger.warning(f"Invalid API key: {api_key}")
        raise HTTPException(status_code=403, detail="Invalid API key")

    if not user_repo.unfollow_user(user.id, user_id):
        logger.warning(f"User not found for unfollow attempt, user ID: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    return {"result": True}


@router.get("/tweets", response_model=schemas.TweetResponse)
async def get_feed(db: Session = Depends(get_db)):
    cached_tweets = redis_client.get("Feed")

    if cached_tweets:
        logger.info("Returning feed from Redis cache")
        cached_tweets = json.loads(cached_tweets.decode("utf-8"))
        return {"result": True, "tweets": cached_tweets}

    tweet_repo = TweetRepository(db)

    tweets_data = tweet_repo.get_feed()

    if not tweets_data:
        raise HTTPException(status_code=404, detail="No tweets found")

    tweets = []
    for tweet in tweets_data:
        media = [media.file_path for media in tweet.media]
        likes = [{"user_id": user.id, "name": user.name} for user in tweet.liked_by]
        tweet_dict = {
            "id": tweet.id,
            "content": tweet.tweet_data,
            "attachments": media,
            "author": {"id": tweet.author.id, "name": tweet.author.name},
            "likes": likes,
        }
        tweets.append(tweet_dict)

    await redis_client.set("Feed", json.dumps(tweets))
    logger.info("Feed cached in Redis with key: Feed")

    return {"result": True, "tweets": tweets}


@router.get("/users/me")
def get_profile(api_key: str = Header(...), db: Session = Depends(get_db)):
    cached_profile = redis_client.get(f"Profile: {api_key}")

    if cached_profile:
        logger.info(f"Returning profile from Redis cache for API key: {api_key}")
        cached_profile = json.loads(cached_profile.decode("utf-8"))
        return cached_profile

    user_data = db.query(models.User).filter(models.User.api_key == api_key).first()

    if user_data:
        following_list = [{"id": u.id, "name": u.name} for u in user_data.followed]
        followers_list = [{"id": u.id, "name": u.name} for u in user_data.followers]

        profile = {
            "user": {
                "id": user_data.id,
                "name": user_data.name,
                "following": following_list,
                "followers": followers_list,
            },
        }

        redis_client.set(f"Profile: {api_key}", json.dumps(profile))
        logger.info(f"Profile cached in Redis with key: Profile: {api_key}")

        return {"result": "true", "user": profile}


@router.get("/users/{user_id}", response_model=schemas.UserProfileResponse)
def get_user_profile(
    user_id: int, api_key: str = Header(...), db: Session = Depends(get_db)
):
    cached_profile = redis_client.get(f"User: {user_id}")

    if cached_profile:
        logger.info(f"Returning user profile from Redis cache for user ID: {user_id}")
        cached_profile = json.loads(cached_profile.decode("utf-8"))
        return cached_profile

    user_repo = UserRepository(db)

    user = user_repo.get_user_by_api_key(api_key)

    if not user:
        logger.warning(f"Invalid API key: {api_key}")
        raise HTTPException(status_code=403, detail="Invalid API key")

    user_profile = db.query(models.User).filter(models.User.id == user_id).first()

    if not user_profile:
        logger.warning(f"User profile not found for user ID: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    user_data = schemas.User.from_orm(user_profile)

    profile = {"result": True, "user": user_data}
    redis_client.set(
        f"User: {user_id}", json.dumps(profile, default=lambda o: o.dict())
    )
    logger.info(f"User profile cached in Redis with key: User: {user_id}")

    return profile
