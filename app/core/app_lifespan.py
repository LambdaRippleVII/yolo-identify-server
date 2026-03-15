import re
from contextlib import asynccontextmanager
from pathlib import Path

import yaml
from fastapi import FastAPI
from loguru import logger
from ultralytics import YOLO

from app.core.env_setting import global_info, settings
from app.core.mqtt_client import mqtt_client, mqtt_connect


def connect_mqtt():
    """
    连接MQTT服务器
    """
    mqtt_connect()

def disconnect_mqtt():
    """
    断开MQTT服务器
    """
    logger.info("正在断开 MQTT 连接...")
    try:
        # 先停止后台循环线程
        mqtt_client.loop_stop()
        # 再断开连接
        mqtt_client.disconnect()
        logger.info("MQTT 已安全断开")
    except Exception as e:
        logger.error(f"断开 MQTT 连接时发生错误: {e}")

def init_yolo_path():
    """ 初始化YOLO路径配置 """
    # 初始化yolo模型地址
    yolo_model_path = Path(settings.MODEL_PATH)
    if not yolo_model_path.exists():
        # 尝试按照名称寻找模型
        model_name = yolo_model_path.stem
        model_name = f"{model_name}.pt"
        yolo_model_path = Path(__file__).parent.parent.parent / "yolo_models" / model_name
    # 再次检查
    if not yolo_model_path.exists():
        logger.error(f"模型文件无法找到: {settings.MODEL_PATH}")
        # 退出程序
        exit(-1)

    # 记录信息到全局
    global_info.YOLO_MODEL_PATH = yolo_model_path

def init_send_msg_config_file_path():
    """ 初始化发送消息配置文件路径 """
    # 初始化发送消息配置文件地址
    send_msg_config_file_path = Path(settings.SEND_MSG_CONFIG_FILE)
    if not send_msg_config_file_path.exists():
        # 尝试按照名称寻找配置文件
        config_file_name = send_msg_config_file_path.stem
        config_file_name = f"{config_file_name}.json"
        send_msg_config_file_path = Path(__file__).parent.parent.parent / "send_msg_config" / config_file_name
    # 再次检查
    if not send_msg_config_file_path.exists():
        logger.error(f"发送消息配置文件无法找到: {settings.SEND_MSG_CONFIG_FILE}")
        # 退出程序
        exit(-1)

    # 记录信息到全局
    global_info.SEND_MSG_CONFIG_FILE = send_msg_config_file_path

def init_model_config_file_path():
    """ 初始化模型配置文件路径 """
    if settings.MODEL_CONFIG_PATH == "":
        return
    model_config_file_path = Path(settings.MODEL_CONFIG_PATH)
    if not model_config_file_path.exists():
        # 尝试按照名称寻找配置文件
        config_file_name = model_config_file_path.stem
        config_file_name = f"{config_file_name}.json"
        model_config_file_path = Path(__file__).parent.parent.parent / "model_config" / config_file_name
    # 再次检查
    if not model_config_file_path.exists():
        logger.error(f"模型配置文件无法找到: {settings.MODEL_CONFIG_PATH}")
        return

    # 记录信息到全局
    global_info.MODEL_CONFIG_PATH = model_config_file_path
    logger.info(f"已初始化模型配置文件,配置文件为: {global_info.MODEL_CONFIG_PATH.absolute()}")

def init_model_config():
    """ 初始化模型配置 """
    if global_info.MODEL_CONFIG_PATH:
        with open(global_info.MODEL_CONFIG_PATH, "r", encoding="utf-8") as f:
            global_info.MODEL_CONFIG = yaml.safe_load(f)
            if global_info.MODEL_CONFIG is None:
                global_info.MODEL_CONFIG = {}

def init_up_topic_rule():
    """ 初始化上行主题规则 """
    topic_info = settings.UP_TOPIC_RULE
    pattern = r"\{(.*?)\}"

    def replacer(match):
        # 获取括号内的字符串
        key = match.group(1)

        # 动态获取属性值
        try:
            value = getattr(settings, key)
            # 确保转换为字符串
            return str(value)
        except AttributeError:
            logger.warning(f"警告: Setting 类中未找到属性 '{key}'，保留原占位符。")
            return match.group(0)

    global_info.UP_TOPIC_RULE = re.sub(pattern, replacer, topic_info)

def init_yolo_model():
    """ 初始化YOLO模型 """
    global_info.YOLO_MODEL = YOLO(global_info.YOLO_MODEL_PATH)

def obtain_send_msg_config():
    """ 获取发送消息配置 """
    with open(global_info.SEND_MSG_CONFIG_FILE, "r", encoding="utf-8") as f:
        global_info.SEND_MSG_CONFIG = f.read()

def assignment_send_msg_config():
    """ 赋值发送消息配置 """
    config_info = global_info.SEND_MSG_CONFIG
    pattern = r"\$(.*?)\$"

    def replacer(match):
        # 获取括号内的字符串
        key: str = match.group(1)

        # 动态获取属性值
        try:
            value = getattr(settings, key.upper())
            # 确保转换为字符串
            return str(value)
        except AttributeError:
            return match.group(0)

    global_info.SEND_MSG_CONFIG = re.sub(pattern, replacer, config_info)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 连接MQTT服务器
    connect_mqtt()
    # === 初始化全局路径配置 ===
    # 初始化YOLO路径配置
    init_yolo_path()
    logger.info(f"已初始化YOLO模型,模型为: {global_info.YOLO_MODEL_PATH.absolute()}")
    # 初始化发送消息配置文件路径
    init_send_msg_config_file_path()
    logger.info(f"已初始化发送消息配置文件,配置文件为: {global_info.SEND_MSG_CONFIG_FILE.absolute()}")

    # 初始化上行主题规则
    init_up_topic_rule()
    logger.info(f"已初始化上行主题规则,上行主题为: {global_info.UP_TOPIC_RULE}")

    # 初始化模型配置文件路径
    init_model_config_file_path()

    # 初始化模型配置
    init_model_config()
    if global_info.MODEL_CONFIG_PATH:
        logger.info(f"已初始化模型配置文件,配置文件为: {global_info.MODEL_CONFIG_PATH.absolute()}")

    # 初始化YOLO模型
    init_yolo_model()
    logger.info(f"已加载模型: {global_info.YOLO_MODEL_PATH}")

    # 获取发送消息配置
    obtain_send_msg_config()
    assignment_send_msg_config()
    logger.info(f"已获取发送消息配置,配置为:\n{global_info.SEND_MSG_CONFIG}")

    # 启动视频捕获线程
    from app.handler.video_handler import start_video_capture
    start_video_capture()

    yield

    # 断开MQTT服务器
    disconnect_mqtt()

