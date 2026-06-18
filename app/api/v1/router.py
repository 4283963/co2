from fastapi import APIRouter
from app.api.v1.dispatch import router as dispatch_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(dispatch_router)
