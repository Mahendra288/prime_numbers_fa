# ---- Explicit infrastructure bootstrap ----
from core.config import settings      # ensures config is loaded
from core.fast_api_otel import init_fastapi_otel
from db import session                # ensures engine is created

from fastapi import FastAPI

# Initial app setup
app = FastAPI(title=settings.APP_NAME)
init_fastapi_otel(app)

# Create DB tables, can be improved using alembic full migrations support to track & apply table changes
from db.session import engine
from db.base import Base
Base.metadata.create_all(bind=engine)

# Register routes
from api import api_router
app.include_router(api_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
