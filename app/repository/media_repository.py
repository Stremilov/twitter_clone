from sqlalchemy.orm import Session
from app import models

class MediaRepository:
    def __init__(self, db: Session):
        self.db = db

    def upload_media(self, file_path: str) -> models.Media:
        media = models.Media(file_path=file_path)
        self.db.add(media)
        self.db.commit()
        self.db.refresh(media)
        return media
