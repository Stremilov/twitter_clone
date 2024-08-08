import os

from fastapi import APIRouter, HTTPException, Depends, Header, UploadFile, File
from sqlalchemy import desc
from sqlalchemy.orm import Session
from . import schemas, models

from app import crud
from app.database import get_db

router = APIRouter()


def save_uploaded_file(file: UploadFile):
    upload_folder = "app/static"
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    file_path = os.path.join(upload_folder, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    return file.filename


@router.post("/tweets", response_model=schemas.TweetCreateResponse)
def make_tweet(
    tweet: schemas.TweetCreate,
    api_key: str = Header(...),
    db: Session = Depends(get_db),
):
    user = crud.get_user_by_api_key(db, api_key)

    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key")

    db_tweet = crud.create_tweet(db, tweet, user.id)

    return {"result": True, "tweet_id": db_tweet.id}


@router.post("/medias")
async def upload_media(
    api_key: str = Header(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    user = crud.get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key")
    file_path = save_uploaded_file(file)
    media = crud.upload_media(db, file_path)
    return {"result": True, "media_id": media.id}


@router.delete("/tweets/{tweet_id}")
def delete_tweet(
    tweet_id: int, api_key: str = Header(...), db: Session = Depends(get_db)
):
    user = crud.get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key")
    if not crud.delete_tweet(db, tweet_id, user.id):
        raise HTTPException(status_code=404, detail="Tweet not found or unauthorized")
    return {"result": True}


@router.post("/tweets/{tweet_id}/likes")
def like_tweet(
    tweet_id: int, api_key: str = Header(...), db: Session = Depends(get_db)
):
    user = crud.get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key")
    if not crud.like_tweet(db, tweet_id, user.id):
        raise HTTPException(status_code=404, detail="Tweet not found")
    return {"result": True}


@router.delete("/tweets/{tweet_id}/likes")
def unlike_tweet(
    tweet_id: int, api_key: str = Header(...), db: Session = Depends(get_db)
):
    user = crud.get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key")
    if not crud.unlike_tweet(db, tweet_id, user.id):
        raise HTTPException(status_code=404, detail="Tweet not found")
    return {"result": True}


@router.post("/users/{user_id}/follow")
def follow_user(
    user_id: int, api_key: str = Header(...), db: Session = Depends(get_db)
):
    user = crud.get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key")
    if not crud.follow_user(db, user.id, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"result": True}


@router.delete("/users/{user_id}/follow")
def unfollow_user(
    user_id: int, api_key: str = Header(...), db: Session = Depends(get_db)
):
    user = crud.get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key")
    if not crud.unfollow_user(db, user.id, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"result": True}


@router.get("/tweets", response_model=schemas.TweetResponse)
def get_feed(db: Session = Depends(get_db)):
    tweets_data = db.query(models.Tweet).all()

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
    return {"result": True, "tweets": tweets}


@router.get("/users/me")
def get_profile(api_key: str = Header(...), db: Session = Depends(get_db)):
    user_data = db.query(models.User).filter(models.User.api_key == api_key).first()
    if user_data:
        following_list = [{"id": u.id, "name": u.name} for u in user_data.followed]
        followers_list = [{"id": u.id, "name": u.name} for u in user_data.followers]

        return {
            "result": "true",
            "user": {
                "id": user_data.id,
                "name": user_data.name,
                "following": following_list,
                "followers": followers_list,
            },
        }


@router.get("/users/{user_id}", response_model=schemas.UserProfileResponse)
def get_user_profile(
    user_id: int, api_key: str = Header(...), db: Session = Depends(get_db)
):
    user = crud.get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key")
    user_profile = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")
    return {"result": True, "user": user_profile}
