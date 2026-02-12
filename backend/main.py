from fastapi import FastAPI
from database import Base, engine
from gmail_auth import router as gmail_router

Base.metadata.create_all(bind=engine)

app = FastAPI()


