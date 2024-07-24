from typing import Any, Type

from sqlalchemy.orm import Session
from . import models, schemas
from .models import User


def get_user_by_api_key(db: Session, api_key: str):
    return db.query(models.User).filter(models.User.api_key == api_key).first()

def create_tweet(db: Session, tweet: schemas.TweetCreate, user_id: int):
    db_tweet = models.Tweet(**tweet.dict(), author_id=user_id)
    db.add(db_tweet)
    db.commit()
    db.refresh(db_tweet)
    return db_tweet

def delete_tweet(db: Session, tweet_id: int, user_id: int):
    db_tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id, models.Tweet.author_id == user_id).first()
    if db_tweet:
        db.delete(db_tweet)
        db.commit()
        return True
    return False

def like_tweet(db: Session, tweet_id: int, user_id: int):
    db_tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_tweet and db_user:
        db_tweet.liked_by.append(db_user)
        db.commit()
        return True
    return False

def unlike_tweet(db: Session, tweet_id: int, user_id: int):
    db_tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_tweet and db_user:
        db_tweet.liked_by.remove(db_user)
        db.commit()
        return True
    return False

def follow_user(db: Session, follower_id: int, followed_id: int):
    follower = db.query(models.User).filter(models.User.id == follower_id).first()
    followed = db.query(models.User).filter(models.User.id == followed_id).first()
    if follower and followed:
        follower.followed.append(followed)
        db.commit()
        return True
    return False

def unfollow_user(db: Session, follower_id: int, followed_id: int):
    follower = db.query(models.User).filter(models.User.id == follower_id).first()
    followed = db.query(models.User).filter(models.User.id == followed_id).first()
    if follower and followed:
        follower.followed.remove(followed)
        db.commit()
        return True
    return False

def get_feed(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        tweets = db.query(models.Tweet).all()
        return tweets
    return []

def upload_media(db: Session, file_path: str, tweet_id: int):
    db_media = models.Media(file_path=file_path, tweet_id=tweet_id)
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    return db_media

def create_test_user(db: Session, name: str):
    # Проверка, существует ли пользователь с таким именем
    user = db.query(models.User).filter(models.User.name == name).first()

    if user:
        return user

    # Генерация уникального API ключа
    api_key = "test2"
    # Создание объекта пользователя
    user = models.User(name=name, api_key=api_key)
    # Добавление пользователя в сессию
    db.add(user)
    # Фиксация изменений
    db.commit()
    db.refresh(user)
    return user
