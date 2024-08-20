from sqlalchemy import Column, Integer, String, ForeignKey, Text, Table, ARRAY
from sqlalchemy.orm import relationship, backref, Session
from .database import Base

followers = Table(
    "followers",
    Base.metadata,
    Column("follower_id", Integer, ForeignKey("users.id")),
    Column("followed_id", Integer, ForeignKey("users.id")),
)

likes = Table(
    "likes",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("tweet_id", Integer, ForeignKey("tweets.id")),
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    api_key = Column(String, unique=True, index=True)
    tweets = relationship("Tweet", back_populates="author")
    followed = relationship(
        "User",
        secondary=followers,
        primaryjoin=id == followers.c.follower_id,
        secondaryjoin=id == followers.c.followed_id,
        backref=backref("followers", lazy="dynamic"),
    )

    likes = relationship("Tweet", secondary=likes, back_populates="liked_by")


class Tweet(Base):
    __tablename__ = "tweets"
    id = Column(Integer, primary_key=True, index=True)
    tweet_data = Column(Text, index=True)
    tweet_media_ids = Column(ARRAY(Integer), default=None)
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="tweets")
    liked_by = relationship("User", secondary=likes, back_populates="likes")
    media = relationship("Media", back_populates="tweet", cascade="all, delete-orphan")


class Media(Base):
    __tablename__ = "media"
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, index=True)
    tweet_id = Column(Integer, ForeignKey("tweets.id"))
    tweet = relationship("Tweet", back_populates="media")


def create_test_user(db: Session, name: str, api_key):
    user = db.query(User).filter(User.name == name).first()

    if user:
        return user

    user = User(name=name, api_key=api_key)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user