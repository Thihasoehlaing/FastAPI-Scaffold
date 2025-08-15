from fastapi import APIRouter
from app.routes.v1 import api_router_v1

api_router = APIRouter()
api_router.include_router(api_router_v1)  # v1 owns its own prefix
