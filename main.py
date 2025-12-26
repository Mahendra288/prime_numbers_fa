# ---- Explicit infrastructure bootstrap ----
from core.config import settings      # ensures config is loaded
from core.fast_api_otel import init_fastapi_otel

from fastapi import FastAPI

# Initial app setup
app = FastAPI(title=settings.APP_NAME)
init_fastapi_otel(app)

# Register routes
from api import api_router
app.include_router(api_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
