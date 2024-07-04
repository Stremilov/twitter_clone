import uvicorn
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from authlib.integrations.starlette_client import OAuth
from flask import url_for
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

import os
from .models import (Base, engine, session, Tweet, User, TweetCreate, FeedResponse, ErrorResponse, TweetResponse,
                     Author, Like, UserProfileResponse, Follower, Following, UserProfile, UserCreate)

app = FastAPI(
    title="Twitter API",
    description="API для управления твитами и пользователями",
    version="1.0.0",
    root_path="/api"
)

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Добавляем middleware для работы с сессиями
app.add_middleware(SessionMiddleware, secret_key="test")

# Настраиваем OAuth2
oauth = OAuth()
oauth.register(
    name='google',
    client_id='your_google_client_id',
    client_secret='your_google_client_secret',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri='http://localhost:8000/api/auth',
    client_kwargs={'scope': 'openid profile email'}
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def save_uploaded_file(file):
    upload_folder = 'uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    file_path = os.path.join(upload_folder, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    return file_path


@app.get("/api/auth")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    return {"email": user.email, "name": user.name}


@app.get("/api/login")
async def login(request: Request):
    redirect_uri = url_for('auth', _external=True)
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = session.query(User).filter(User.username == form_data.username).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/api/users/me", response_model=UserProfileResponse)
async def get_user_profile(token: str = Depends(oauth2_scheme)):
    user = session.query(User).filter(User.username == token).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_profile = UserProfile(
        id=user.id,
        name=user.name,
        last_name=user.last_name,
        age=user.age
    )
    return UserProfileResponse(result=True, user=user_profile)


@app.post("/api/tweets")
def create_tweet(tweet: TweetCreate):
    new_tweet = Tweet(tweet_data=tweet.tweet_data)
    session.add(new_tweet)
    session.commit()
    session.refresh(new_tweet)
    return {"result": True, "tweet_id": new_tweet.id}

@app.post("/api/medias")
async def upload_media(api_key: str, file: UploadFile = File(...)):
    if api_key != 'test':
        raise HTTPException(status_code=403, detail="Invalid API key")
    if file.filename == '':
        raise HTTPException(status_code=400, detail="No file selected")

    upload_folder = 'uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    file_path = os.path.join(upload_folder, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return {"result": True, "media_id": file_path}

@app.delete("/api/tweets/{tweet_id}")
def delete_tweet(tweet_id: int, api_key: str):
    if api_key != 'test':
        raise HTTPException(status_code=403, detail="Invalid API key")
    tweet = session.query(Tweet).filter(Tweet.id == tweet_id).first()
    if tweet:
        session.delete(tweet)
        session.commit()
        return {"result": True}
    else:
        raise HTTPException(status_code=404, detail="Tweet not found")

@app.post("/api/tweets/{tweet_id}/likes")
def like_tweet(tweet_id: int):
    tweet = session.query(Tweet).filter(Tweet.id == tweet_id).first()
    if tweet:
        Tweet.like(None, tweet)
        session.commit()
        return {"result": True}
    else:
        raise HTTPException(status_code=404, detail="Tweet not found")

@app.delete("/api/tweets/{tweet_id}/likes")
def unlike_tweet(tweet_id: int):
    tweet = session.query(Tweet).filter(Tweet.id == tweet_id).first()
    if tweet.getLikes() != 0:
        Tweet.unlike(None, tweet)
        session.commit()
        return {"result": True}
    else:
        raise HTTPException(status_code=404, detail="Tweet not found")

@app.post("/api/users/{user_id}/follow")
def follow_user(user_id: int, api_key: str):
    if api_key != 'your_api_key':
        raise HTTPException(status_code=401, detail="Invalid API key")
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"result": True, "message": "Successfully followed user"}

@app.post("/api/users/{user_id}/unfollow")
def unfollow_user(user_id: int, api_key: str):
    if api_key != 'test':
        raise HTTPException(status_code=401, detail="Invalid API key")
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"result": True, "message": "Successfully unfollowed user"}

@app.get("/api/tweets", response_model=FeedResponse, responses={500: {"model": ErrorResponse}})
def get_tweets(api_key: str):
    try:
        if api_key != 'test':
            raise HTTPException(status_code=403, detail="Invalid API key")
        tweets = session.query(Tweet).all()
        tweet_list = [TweetResponse(id=tweet.id, data=tweet.tweet_data, likes=tweet.likes) for tweet in tweets]
        return FeedResponse(result=True, tweets=tweet_list)
    except Exception as e:
        return ErrorResponse(result=False, error_type="internal_error", error_message=str(e))


@app.get("/api/users/{user_id}", response_model=UserProfileResponse, responses={500: {"model": ErrorResponse}})
def get_user(user_id: int):
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        followers_list = [Follower(id=follower.id, name=follower.name) for follower in user.followers]
        following_list = [Following(id=followee.id, name=followee.name) for followee in user.following]

        user_profile = UserProfile(
            id=user.id,
            name=user.name,
            followers=followers_list,
            following=following_list
        )
        return UserProfileResponse(result=True, user=user_profile)
    except Exception as e:
        return ErrorResponse(result=False, error_type="internal_error", error_message=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
