from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import Settings
from . import models
from .database import engine
from .routers import post,user,auth,votes
models.Base.metadata.create_all(bind=engine)
app=FastAPI()
origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(votes.router)
@app.get("/")
async def get_posts():
    return {"dhop hop"}
