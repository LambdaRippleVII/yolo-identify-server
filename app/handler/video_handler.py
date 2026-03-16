import logging
import threading
import time
import platform

import cv2
from loguru import logger

from app.core.env_setting import global_info, settings
from app.handler.send_msg_handler import handle_send_msg

logging.getLogger('ultralytics').setLevel(logging.ERROR)

identify_frame = None
cap_frame = None

# 上一次识别结果
last_results = None
# 帧计数
frame_count = 0

cap: cv2.VideoCapture
cap_retry_count = 0

def init_video_capture():
    """
    初始化视频捕获
    """
    global cap

    # 获取摄像头源
    cap_source = settings.CAP_SOURCE
    try:
        cap_source = int(cap_source)
    except ValueError:
        # 如果不是数字，保持为字符串（如 RTSP 流）
        pass

    # 根据平台选择合适的后端
    if platform.system() == "Windows":
        # Windows 平台优先使用 DSHOW 后端，避免 MSMF 问题
        cap = cv2.VideoCapture(cap_source, cv2.CAP_DSHOW)
        if not cap.isOpened():
            # 如果 DSHOW 失败，尝试 MSMF
            cap = cv2.VideoCapture(cap_source, cv2.CAP_MSMF)
    elif platform.system() == "Linux":
        # Linux 平台使用 V4L2
        cap = cv2.VideoCapture(cap_source, cv2.CAP_V4L2)
    else:
        # 其他平台使用默认后端
        cap = cv2.VideoCapture(cap_source)

    if not cap.isOpened():
        logger.error(f"无法打开视频源: {cap_source}")
        return False

    # 设置摄像头参数
    try:
        # 设置编码格式
        fourcc_value = cv2.VideoWriter_fourcc(*settings.CAP_PROP_FOURCC)
        cap.set(cv2.CAP_PROP_FOURCC, fourcc_value)

        # 设置帧率
        cap.set(cv2.CAP_PROP_FPS, settings.CAP_PROP_FPS)

        # 设置宽高
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.CAP_PROP_FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.CAP_PROP_FRAME_HEIGHT)

        # 设置自动曝光 - Windows 平台特殊处理
        if platform.system() == "Windows":
            # Windows 上通常使用 0.25 表示手动模式，0.75 表示自动模式
            # 但不同驱动可能不同，这里先尝试标准值
            auto_exposure_val = 0.25 if settings.CAP_PROP_AUTO_EXPOSURE == 0 else 0.75
            cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, auto_exposure_val)
        else:
            # Linux/Mac 使用标准 0/1
            cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, float(settings.CAP_PROP_AUTO_EXPOSURE))

        logger.info(f"自动曝光设置: {cap.get(cv2.CAP_PROP_AUTO_EXPOSURE)}")

        # 设置曝光值
        cap.set(cv2.CAP_PROP_EXPOSURE, float(settings.CAP_PROP_EXPOSURE))
        logger.info(f"曝光值设置: {cap.get(cv2.CAP_PROP_EXPOSURE)}")

    except Exception as e:
        logger.warning(f"设置摄像头参数时出错: {e}")
        # 继续运行，即使参数设置失败

    return True

def web_cap_thread():
    global identify_frame, cap_frame, last_results, frame_count, cap, cap_retry_count

    while True:
        try:
            # 初始化摄像头
            if cap_retry_count > 5 or cap_retry_count == 0:
                cap_retry_count = 1
                if not init_video_capture():
                    logger.error("摄像头初始化失败, 1秒后尝试重连")
                    time.sleep(1)
                    continue

            if not cap.isOpened():
                logger.error("无法打开USB摄像头, 1秒后尝试重连")
                time.sleep(1)
                continue

            success, frame = cap.read()
            if not success:
                logger.warning("无法获取到USB摄像头视频流, 1秒后重试")
                # 释放当前摄像头资源
                if cap is not None:
                    cap.release()
                time.sleep(1)
                continue

            # 保存当前视频帧
            cap_frame = frame

            # 模型识别
            if frame_count >= settings.SKIP_FRAME_NUM:
                results = global_info.YOLO_MODEL(frame)
                last_results = results
                frame_count = 0
            else:
                frame_count += 1

            if last_results is None:
                continue

            # 绘制图像
            identify_frame = frame.copy()  # 使用 copy 避免修改原始帧
            for box in last_results[0].boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                conf = box.conf[0]
                cls = box.cls[0]
                cls_name = last_results[0].names[int(cls)]

                # 过滤盒子
                if global_info.MODEL_CONFIG and global_info.MODEL_CONFIG is not None:
                    if cls_name not in global_info.MODEL_CONFIG:
                        continue
                    if conf < global_info.MODEL_CONFIG[cls_name]:
                        continue

                cv2.rectangle(identify_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(identify_frame, f"{cls_name} {conf:.2f}", (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # 发送消息
            handle_send_msg(last_results)

        except Exception as e:
            logger.error(f"USB摄像头异常:{e}")
            # 确保释放摄像头资源
            if 'cap' in locals() and cap is not None:
                cap.release()
            time.sleep(1)
            cap_retry_count += 1

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
