import logging
import threading
import time

import cv2
from loguru import logger

from app.core.env_setting import global_info, settings
from app.handler.send_msg_handler import handle_send_msg

logging.getLogger('ultralytics').setLevel(logging.ERROR)

identify_frame = None
cap_frame = None

def web_cap_thread():
    global identify_frame, cap_frame

    # 打开网络摄像头
    cap = cv2.VideoCapture(0)

    while True:
        try:
            if not cap.isOpened():
                logger.error("无法打开USB摄像头, 1秒后尝试重连")
                time.sleep(1)
                continue

            success, frame = cap.read()
            if not success:
                logger.warning("无法获取到USB摄像头视频流, 1秒后重试")
                time.sleep(1)
                continue

            # 保存当前视频帧
            cap_frame = frame

            # 模型识别
            results = global_info.YOLO_MODEL(frame)
            # 保存最新帧
            identify_frame = results[0].plot()

            # 发送消息
            handle_send_msg(results)

        except Exception as e:
            logger.error(f"USB摄像头异常:{e}")
            time.sleep(1)

def start_video_capture():
    """
    启动视频捕获线程
    """
    thread = threading.Thread(target=web_cap_thread)
    thread.daemon = True
    thread.start()

def get_original_frame():
    """
    获取原始帧
    """
    global cap_frame
    return cap_frame

def get_identify_frame():
    """
    获取识别帧
    """
    global identify_frame
    return identify_frame