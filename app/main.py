from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import users, auth, groupmembers, groups, posts

# models.Base.metadata.create_all(bind=engine)
# sử sụng alembic nên không cần dòng lệnh này.

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(groups.router)
app.include_router(posts.router)
app.include_router(groupmembers.router)

@app.get("/")
def thanh():
    return {"message": "hello thanh"}