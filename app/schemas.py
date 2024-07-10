from pydantic import BaseModel
from typing import List, Optional

class TweetBase(BaseModel):
    tweet_data: str

class TweetCreate(TweetBase):
    tweet_media_ids: Optional[List[int]] = None

class Tweet(TweetBase):
    id: int
    author_id: int

    class Config:
        orm_mode = True

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

class UserCreate(BaseModel):
    name: str
    api_key: str
