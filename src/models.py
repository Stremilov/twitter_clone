from typing import List

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///diplom.db")
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Tweet(Base):
    __tablename__ = "tweet"

    id = Column(Integer, primary_key=True)
    tweet_data = Column(String(255), nullable=False)
    # tweet_media_ids = Column(ARRAY(Integer), nullable=True)
    likes = Column(Integer, default=0)

    def like(self, tweet) -> None:
        tweet.likes += 1

    def unlike(self, tweet) -> None:
        tweet.likes -= 1

    def getId(self):
        return self.id

    def getData(self):
        return self.tweet_data

    def getLikes(self):
        return self.likes


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    age = Column(String(255), nullable=False)
    followers = Column(Integer, default=0)

    def getUserId(self):
        return self.id

    def getUserName(self):
        return self.name

    def getUserLastName(self):
        return self.last_name

    def getUserAge(self):
        return self.age

    def getUserFollowers(self):
        return self.followers

    def follow(self):
        # code here
        ...


class TweetCreate(BaseModel):
    tweet_data: str


# Pydantic модели
class Author(BaseModel):
    id: int
    name: str


class Like(BaseModel):
    user_id: int
    name: str


class TweetResponse(BaseModel):
    id: int
    content: str
    attachments: List[str]
    author: Author
    likes: List[Like]


class FeedResponse(BaseModel):
    result: bool
    tweets: List[TweetResponse]


class ErrorResponse(BaseModel):
    result: bool
    error_type: str
    error_message: str

# Pydantic модели
class Follower(BaseModel):
    id: int
    name: str

class Following(BaseModel):
    id: int
    name: str

class UserProfile(BaseModel):
    id: int
    name: str
    followers: List[Follower]
    following: List[Following]

class UserProfileResponse(BaseModel):
    result: bool
    user: UserProfile
