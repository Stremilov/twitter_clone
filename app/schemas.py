from pydantic import BaseModel
from typing import List, Optional


class TweetCreateResponse(BaseModel):
    result: bool
    tweet_id: int


class TweetCreate(BaseModel):
    tweet_data: str
    tweet_media_ids: Optional[List[int]]


class Tweet(BaseModel):
    id: int
    content: str

    class Config:
        orm_mode = True


class Author(BaseModel):
    id: int
    name: str

class MediaResponse(BaseModel):
    file_path: str


class LikeResponse(BaseModel):
    user_id: int
    name: str

class TweetData(BaseModel):
    id: int
    content: str
    attachments: List[str]
    author: Author
    likes: List[LikeResponse]


class TweetResponse(BaseModel):
    result: bool
    tweets: List[TweetData]


class Media(BaseModel):
    id: int
    file_path: str

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class FeedResponse(BaseModel):
    result: bool
    tweets: List[Tweet]


class ErrorResponse(BaseModel):
    result: bool
    error_type: str
    error_message: str


class UserProfileResponse(BaseModel):
    result: bool
    user: User
