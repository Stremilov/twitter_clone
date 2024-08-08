from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# from .config import settings

# SQLALCHEMY_DATABASE_URL = (
#     f"postgresql://{settings.db_user}:{settings.db_password}@"
#     f"{settings.db_host}:{settings.db_port}/{settings.db_name}"
# )

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@db:5432/twitterClone"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    db
    try:
        yield db
    finally:
        db.close()
