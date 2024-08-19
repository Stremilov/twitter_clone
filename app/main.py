import os

import uvicorn

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse

from app import models
from app.database import engine, SessionLocal
from app.models import Base
from app.routes import router

app = FastAPI(
    title="Twitter API",
    version="1.0.0",
    description="API для управления пользователями и твитами",
)

app_api = FastAPI()

app_api.include_router(router)
app.include_router(router)

app.mount("/api", app_api)
app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static"), html=True), name="static")

def create_test_user(db: Session, name: str, api_key):
    user = db.query(models.User).filter(models.User.name == name).first()

    if user:
        return user

    user = models.User(name=name, api_key=api_key)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

Base.metadata.create_all(bind=engine)
#
db: Session = SessionLocal()
#
test_user = create_test_user(db, name="Test User", api_key="test2")
test_user_2 = create_test_user(db, name="Test User 2", api_key="test")
print(
    f"Created test user: {test_user.name}, Id: {test_user.id}, API Key: {test_user.api_key}"
)
print(
    f"Created test user: {test_user_2.name}, Id: {test_user_2.id}, API Key: {test_user_2.api_key}"
)


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return HTMLResponse("index.html")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
