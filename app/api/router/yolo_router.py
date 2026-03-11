import time

import cv2
import numpy as np
from fastapi import APIRouter
from starlette.responses import StreamingResponse

YoloRouter = APIRouter(prefix="/yolo")

def frame_generator(get_frame_func):
    """
    生成视频帧数据
    """
    while True:
        # 获取最新帧
        frame = get_frame_func()
        if frame is not None and isinstance(frame, np.ndarray):
            success, buffer = cv2.imencode('.jpg', frame)
            if success:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            else:
                time.sleep(0.1)
        else:
            empty_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            ret, buffer = cv2.imencode('.jpg', empty_frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.033)  # 约30fps

@YoloRouter.get("/original")
async def stream_original_frame():
    """
    流式传输原始帧
    """
    from app.handler.video_handler import get_original_frame
    return StreamingResponse(frame_generator(get_original_frame), media_type="multipart/x-mixed-replace; boundary=frame")

@YoloRouter.get("/identify")
async def stream_identify_frame():
    """
    流式传输识别帧
    """
    from app.handler.video_handler import get_identify_frame
    return StreamingResponse(frame_generator(get_identify_frame), media_type="multipart/x-mixed-replace; boundary=frame")