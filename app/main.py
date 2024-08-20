from fastapi import FastAPI
from . import models
from .database import engine
from .routers import users

# models.Base.metadata.create_all(bind=engine)
# sử sụng alembic nên không cần dòng lệnh này.

app = FastAPI()

app.include_router(users.router)

@app.get("/")
def thanh():
    return {"message": "hello thanh"}