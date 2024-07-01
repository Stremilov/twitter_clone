import uvicorn

from src.models import Base, engine
from src.routes import app


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    uvicorn.run(app, host="127.0.0.1", port=8000)