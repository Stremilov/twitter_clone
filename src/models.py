from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Date, Float, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import ARRAY

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import sessionmaker, declarative_base, relationship



engine = create_engine("sqlite:///diplom.db")
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()



class Tweet(Base):
    __tablename__ = "tweet"

    __id = Column(Integer, primary_key=True)
    __tweet_data = Column(String(255), nullable=False)
    # tweet_media_ids = Column(ARRAY(Integer), nullable=True)
    __likes = Column(Integer, default=0)


    def like(self, tweet) -> None:
        tweet.__likes += 1

    def unlike(self, tweet) -> None:
        tweet.__likes -= 1

    def getId(self):
        return self.id

    def getData(self):
        return self.tweet_data


class User(Base):
    __tablename__ = "user"

    __id = Column(Integer, primary_key=True)
    __name = Column(String(255), nullable=False)
    __last_name = Column(String(255), nullable=False)
    __age = Column(String(255), nullable=False)
    __followers = Column(Integer, default=0)


    def getUserId(self):
        return self.__id

    def getUserName(self):
        return self.__name

    def getUserLastName(self):
        return self.__last_name

    def getUserAge(self):
        return self.__age

    def getUserFollowers(self):
        return self.__followers

    def follow(self):
        #code here
        ...
