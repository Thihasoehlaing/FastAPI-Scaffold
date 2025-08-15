from fastapi import APIRouter
from .health import router as health_router
from .users import router as users_router
from .auth import router as auth_router
from .files import router as files_router

api_router_v1 = APIRouter(prefix="/v1")
api_router_v1.include_router(health_router)
api_router_v1.include_router(users_router)
api_router_v1.include_router(auth_router)
api_router_v1.include_router(files_router)
