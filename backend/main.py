from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import engine
from models import Base
from gmail_service import router as gmail_router



# Create tables at startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    Base.metadata.create_all(bind=engine)
    print("Tables created (if not exists)")
    
    yield  # Application runs here
    
    # Shutdown logic (optional)
    print("App shutting down")

app = FastAPI(lifespan=lifespan)

app.include_router(gmail_router)