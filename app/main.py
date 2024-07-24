import uvicorn

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse

from app import crud
from app.database import engine, SessionLocal
from app.models import Base
from app.routes import router

app = FastAPI(
    title="Twitter API",
    description="API для управления твитами и пользователями",
    version="1.0.0")

Base.metadata.create_all(bind=engine)

db: Session = SessionLocal()

test_user = crud.create_test_user(db, name="Test User 2")
print(f"Created test user: {test_user.name}, Id: {test_user.id}, API Key: {test_user.api_key}")

app.include_router(router=router)

app.mount(path="/static", app=StaticFiles(directory="app/static"), name="static")


templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
