from sqlalchemy.orm import Session
from app import models


class UserRepository:
    def __init__(self, db):
        self.db = db

    def get_user_by_api_key(self, api_key: str):
        return self.db.query(models.User).filter(models.User.api_key == api_key).first()

    def get_user_by_id(self, user_id: int):
        return self.db.query(models.User).filter(models.User.id == user_id).first()

    def follow_user(self, follower_id: int, followed_id: int) -> bool:
        follower = self.get_user_by_id(follower_id)
        followed = self.get_user_by_id(followed_id)
        if follower and followed:
            follower.followed.append(followed)
            self.db.commit()
            return True
        return False

    def unfollow_user(self, follower_id: int, followed_id: int) -> bool:
        follower = self.get_user_by_id(follower_id)
        followed = self.get_user_by_id(followed_id)
        if follower and followed:
            follower.followed.remove(followed)
            self.db.commit()
            return True
        return False
