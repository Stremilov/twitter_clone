from sqlalchemy.orm import Session
from app import models, schemas

class TweetRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_tweet(self, tweet: schemas.TweetCreate, user_id: int) -> models.Tweet:
        db_tweet = models.Tweet(tweet_data=tweet.tweet_data, author_id=user_id)
        self.db.add(db_tweet)
        self.db.commit()
        self.db.refresh(db_tweet)

        if tweet.tweet_media_ids:
            media_list = self.db.query(models.Media).filter(models.Media.id.in_(tweet.tweet_media_ids)).all()
            for media in media_list:
                media.tweet_id = db_tweet.id
            self.db.add_all(media_list)
            self.db.commit()

        return db_tweet

    def delete_tweet(self, tweet_id: int, user_id: int) -> bool:
        db_tweet = self.db.query(models.Tweet).filter(models.Tweet.id == tweet_id, models.Tweet.author_id == user_id).first()
        if db_tweet:
            self.db.delete(db_tweet)
            self.db.commit()
            return True
        return False

    def like_tweet(self, tweet_id: int, user_id: int) -> bool:
        db_tweet = self.db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
        db_user = self.db.query(models.User).filter(models.User.id == user_id).first()
        if db_tweet and db_user:
            db_tweet.liked_by.append(db_user)
            self.db.commit()
            return True
        return False

    def unlike_tweet(self, tweet_id: int, user_id: int) -> bool:
        db_tweet = self.db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
        db_user = self.db.query(models.User).filter(models.User.id == user_id).first()
        if db_tweet and db_user:
            db_tweet.liked_by.remove(db_user)
            self.db.commit()
            return True
        return False

    def get_feed(self):
        return self.db.query(models.Tweet).all()
