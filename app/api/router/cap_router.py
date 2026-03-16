import cv2
from fastapi import APIRouter

CapRouter = APIRouter(prefix="/cap")

@CapRouter.api_route("/set/exposure", methods=["POST", "GET"])
async def set_exposure(exposure: float):
    """
    设置曝光时间
    """
    from app.handler.video_handler import cap
    cap.set(cv2.CAP_PROP_EXPOSURE, exposure)
    return {"message": "设置成功"}