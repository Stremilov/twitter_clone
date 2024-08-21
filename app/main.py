import os

import uvicorn

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse

from app.database import engine
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
app.mount(
    "/",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static"), html=True),
    name="static",
)


Base.metadata.create_all(bind=engine)


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return HTMLResponse("index.html")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
