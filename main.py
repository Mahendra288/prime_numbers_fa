# ---- Explicit infrastructure bootstrap ----
from core.config import settings      # ensures config is loaded
from db import session                # ensures engine is created

from fastapi import FastAPI
from api import api_router



from db.session import engine
from db.base import Base

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)
app.include_router(api_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
