import uvicorn

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse

from app.database import engine
from app.models import Base
from app.routes import router

app = FastAPI()
app_api = FastAPI(
    title="Twitter API",
    description="API для управления твитами и пользователями",
    version="1.0.0"
)

app.include_router(router=router)

app.mount(path="/static", app=StaticFiles(directory="app/static"), name="static")
app.mount(path="/api", app=app_api)

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
