from fastapi import APIRouter

from app.api.router.yolo_router import YoloRouter

api_router = APIRouter()
api_router.include_router(YoloRouter)