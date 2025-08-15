from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config.settings import settings
from app.api import api_router
from app.config.logging import setup_logging
from app.middlewares.error_handler import ErrorHandlerMiddleware
from app.middlewares.request_id_middleware import RequestIDMiddleware
from app.middlewares.max_body_size import MaxBodySizeMiddleware
from pathlib import Path

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.APP_DEBUG,
)

if settings.STORAGE_DRIVER == "local":
    upload_dir = Path(settings.LOCAL_UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.mount(
        "/static",
        StaticFiles(directory=str(upload_dir), check_dir=False),
        name="static",
    )

# Middlewares
app.add_middleware(RequestIDMiddleware)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(MaxBodySizeMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(o) for o in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers (v1 prefix is in the router package)
app.include_router(api_router)
