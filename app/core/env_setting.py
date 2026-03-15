from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from ultralytics import YOLO

# 寻找项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # --- 配置加载设置 ---
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=False
    )

    # === 服务器配置 ===
    # 服务器标题
    SERVER_TITLE: str = Field(default="FastApi-QLL", validation_alias="SERVER_TITLE")
    # 服务器版本
    SERVER_VERSION: str = Field(default="1.0.0", validation_alias="SERVER_VERSION")
    # 服务器主机地址
    SERVER_HOST: str = Field(default="0.0.0.0", validation_alias="SERVER_HOST")
    # 服务器端口号
    SERVER_PORT: int = Field(default=19999, validation_alias="SERVER_PORT")
    # 文档相关
    DOCS_URL: str = Field(default="/docs", validation_alias="DOCS_URL")
    REDOC_URL: str = Field(default="/redoc", validation_alias="REDOC_URL")
    OPENAPI_URL: str = Field(default="/openapi.json", validation_alias="OPENAPI_URL")

    # === MQTT配置 ===
    # MQTT服务地址
    MQTT_BROKER_IP: str = Field(validation_alias="MQTT_BROKER_IP")
    # MQTT服务端口
    MQTT_BROKER_PORT: int = Field(default=1883, validation_alias="MQTT_BROKER_PORT")
    # MQTT连接账号
    MQTT_USERNAME: str = Field(default= "", validation_alias="MQTT_USERNAME")
    # MQTT连接密码
    MQTT_PASSWORD: str = Field(default= "", validation_alias="MQTT_PASSWORD")
    # MQTT客户端ID
    MQTT_CLIENT_ID: str = Field(validation_alias="MQTT_CLIENT_ID")

    # === 模型配置相关 ===
    # 视频源地址
    CAP_SOURCE: str = Field(validation_alias="CAP_SOURCE")
    # 当前使用的模型名称或地址
    MODEL_PATH: str = Field(validation_alias="MODEL_PATH")

    # === 接入设备配置 ===
    # 当前此服务产品ID
    PRODUCT_ID: str = Field(validation_alias="PRODUCT_ID")
    # 当前此服务设备ID
    DEVICE_ID: str = Field(validation_alias="DEVICE_ID")
    # 数据上报最小间隔时间(毫秒)
    REPORT_MIN_INTERVAL: int = Field(default=1000, validation_alias="REPORT_MIN_INTERVAL")
    # 上行主题规则
    UP_TOPIC_RULE: str = Field(validation_alias="UP_TOPIC_RULE")
    # 发布的Qos
    UP_QOS: int = Field(default=0, validation_alias="UP_QOS")
    # 发送消息的json配置文件地址
    SEND_MSG_CONFIG_FILE: str = Field(validation_alias="SEND_MSG_CONFIG_FILE")

    # === 摄像头设置 ===
    # 自动曝光设置
    CAP_PROP_AUTO_EXPOSURE: int = Field(default=1, validation_alias="CAP_PROP_AUTO_EXPOSURE")
    # 曝光时间设置
    CAP_PROP_EXPOSURE: int = Field(default=-6, validation_alias="CAP_PROP_EXPOSURE")

settings = Settings()

class GlobalInfo:
    """
    全局信息类
    """

    YOLO_MODEL_PATH: Path

    UP_TOPIC_RULE: str

    SEND_MSG_CONFIG_FILE: Path

    YOLO_MODEL: YOLO

    SEND_MSG_CONFIG: str

global_info = GlobalInfo()