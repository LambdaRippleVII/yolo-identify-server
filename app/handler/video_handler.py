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

    # 设置编码格式
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*settings.CAP_PROP_FOURCC))
    # 设置帧率
    cap.set(cv2.CAP_PROP_FPS, settings.CAP_PROP_FPS)
    # 设置宽高
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.CAP_PROP_FRAME_WIDTH)
    # 设置自动曝光
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, settings.CAP_PROP_AUTO_EXPOSURE)
    logger.info(f"自动曝光:{cap.get(cv2.CAP_PROP_AUTO_EXPOSURE)}")
    # 设置曝光值
    cap.set(cv2.CAP_PROP_EXPOSURE, settings.CAP_PROP_EXPOSURE)
    logger.info(f"曝光值:{cap.get(cv2.CAP_PROP_EXPOSURE)}")

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

            # 绘制图像
            identify_frame = frame
            for box in results[0].boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                conf = box.conf[0]
                cls = box.cls[0]
                cls_name = results[0].names[int(cls)]

                # 过滤盒子
                if global_info.MODEL_CONFIG and global_info.MODEL_CONFIG is not None:
                    if cls_name not in global_info.MODEL_CONFIG:
                        continue
                    if conf < global_info.MODEL_CONFIG[cls_name]:
                        continue

                cv2.rectangle(identify_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(identify_frame, f"{cls_name} {conf:.2f}", (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

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