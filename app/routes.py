from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import get_db
import os


router = APIRouter()


def save_uploaded_file(file: UploadFile):
    upload_folder = 'uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    file_path = os.path.join(upload_folder, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    return file_path


@router.post("/api/tweets", response_model=schemas.Tweet)
def create_tweet(tweet: schemas.TweetCreate, api_key: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key")
    db_tweet = crud.create_tweet(db, tweet, user.id)
    return {"result": True, "tweet_id": db_tweet.id}


@router.post("/api/medias")
async def upload_media(api_key: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    user = crud.get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key")
    file_path = save_uploaded_file(file)
    media = crud.upload_media(db, file_path, None)
    return {"result": True, "media_id": media.id}


@router.delete("/api/tweets/{tweet_id}")
def delete_tweet(tweet_id: int, api_key: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key")
    if not crud.delete_tweet(db, tweet_id, user.id):
        raise HTTPException(status_code=404, detail="Tweet not found or unauthorized")
    return {"result": True}


@router.post("/api/tweets/{tweet_id}/likes")
def like_tweet(tweet_id: int, api_key: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key")
    if not crud.like_tweet(db, tweet_id, user.id):
        raise HTTPException(status_code=404, detail="Tweet not found")
    return {"result": True}


@router.delete("/api/tweets/{tweet_id}/likes")
def unlike_tweet(tweet_id: int, api_key: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key")
    if not crud.unlike_tweet(db, tweet_id, user.id):
        raise HTTPException(status_code=404, detail="Tweet not found")
    return {"result": True}


@router.post("/api/users/{user_id}/follow")
def follow_user(user_id: int, api_key: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key")
    if not crud.follow_user(db, user.id, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"result": True}


@router.delete("/api/users/{user_id}/follow")
def unfollow_user(user_id: int, api_key: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key")
    if not crud.unfollow_user(db, user.id, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"result": True}


@router.get("/api/tweets", response_model=schemas.FeedResponse)
def get_feed(api_key: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key")
    tweets = crud.get_feed(db, user.id)
    return {"result": True, "tweets": tweets}


@router.get("/api/users/me", response_model=schemas.UserProfileResponse)
def get_profile(api_key: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return {"result": True, "user": user}


@router.get("/api/users/{user_id}", response_model=schemas.UserProfileResponse)
def get_user_profile(user_id: int, api_key: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key")
    user_profile = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")
    return {"result": True, "user": user_profile}
