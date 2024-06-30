import uvicorn
from fastapi import HTTPException, FastAPI, File, UploadFile
import os

from src.models import Base, engine, session, Tweet, User, TweetCreate, FeedResponse, ErrorResponse, TweetResponse, \
    Author, Like, UserProfileResponse, Follower, Following, UserProfile

app = FastAPI(
    title="Twitter API",
    description="API для управления твитами и пользователями",
    version="1.0.0"
)


def save_uploaded_file(file):
    upload_folder = 'uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)
    return file_path


@app.post("/api/tweets")
def create_tweet(tweet: TweetCreate):
    new_tweet = Tweet(tweet_data=tweet.tweet_data)
    session.add(new_tweet)
    session.commit()
    session.refresh(new_tweet)
    return {"result": True, "tweet_id": new_tweet.id}

@app.post("/api/medias")
async def upload_media(api_key: str, file: UploadFile = File(...)):
    if api_key != 'your_api_key':
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
    if api_key != '1234':
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

    # Placeholder for follow user logic
    # if user.getUserId() not in ...:
    #     #code here
    #     ...

    return {"result": True, "message": "Successfully followed user"}

@app.post("/api/users/{user_id}/unfollow")
def unfollow_user(user_id: int, api_key: str):
    if api_key != 'your_api_key':
        raise HTTPException(status_code=401, detail="Invalid API key")
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Placeholder for unfollow user logic
    # if user.getUserId() not in ...:
    #     #code here
    #     ...

    return {"result": True, "message": "Successfully unfollowed user"}

@app.get("/api/tweets", response_model=FeedResponse, responses={500: {"model": ErrorResponse}})
def get_tweets(api_key: str):
    try:
        # Проверка api-key (измените логику проверки в соответствии с вашим приложением)
        if api_key != 'your_api_key':
            raise HTTPException(status_code=403, detail="Invalid API key")

        # Получение твитов из базы данных
        tweets = session.query(Tweet).all()

        tweet_list = []
        for tweet in tweets:
            tweet_list.append(TweetResponse(
                id=tweet.id,
                content=tweet.content,
                attachments=[attachment.url for attachment in tweet.attachments],
                author=Author(id=tweet.author.id, name=tweet.author.name),
                likes=[Like(user_id=like.user_id, name=like.user_name) for like in tweet.likes]
            ))

        return FeedResponse(result=True, tweets=tweet_list)
    except Exception as e:
        return ErrorResponse(result=False, error_type="internal_error", error_message=str(e))


@app.get("/api/users/me", response_model=UserProfileResponse, responses={500: {"model": ErrorResponse}})
def get_user_profile(api_key: str):
    try:
        if api_key != 'your_api_key':
            raise HTTPException(status_code=403, detail="Invalid API key")

        user = session.query(User).filter(User.api_key == api_key).first()
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


@app.get("/api/users/{user_id}", response_model=UserProfileResponse, responses={500: {"model": ErrorResponse}})
def get_user(user_id: int):
    try:
        # Получение пользователя по ID
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
    Base.metadata.create_all(bind=engine)
    uvicorn.run(app, host="127.0.0.1", port=8000)
