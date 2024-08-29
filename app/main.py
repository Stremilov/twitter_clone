import os

import uvicorn

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse

from app.database import SessionLocal, Base, engine
from app.models import User
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
app.mount(
    "/",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static"), html=True),
    name="static",
)

Base.metadata.create_all(bind=engine)

def create_test_user(db: Session, name: str, api_key):
    user = db.query(User).filter(User.name == name).first()

    if user:
        return user

    user = User(name=name, api_key=api_key)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

db: Session = SessionLocal()
create_test_user(db=db,name="test1", api_key="test")
create_test_user(db=db, name="test2", api_key="test2")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return HTMLResponse("index.html")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
