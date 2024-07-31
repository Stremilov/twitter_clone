# import dotenv
# from pydantic_settings import BaseSettings
# import os
#
# class Settings(BaseSettings):
#     dotenv.load_dotenv()
#     db_user: str = os.getenv("DB_USER")
#     db_password: str = os.getenv("DB_PASSWORD")
#     db_host: str = os.getenv("DB_HOST")
#     db_port: int = os.getenv("5432")
#     db_name: str = os.getenv("twitterClone")
#
#     class Config:
#         env_file = ".env"
#
# settings = Settings()
