import paho.mqtt.client as mqtt
from loguru import logger
from app.core.env_setting import settings

# 初始化客户端
mqtt_client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id=settings.MQTT_CLIENT_ID
)

def on_connect(client, userdata, flags, reason_code, properties):
    """
    MQTT连接成功回调函数
    """
    if reason_code == 0:
        logger.info("MQTT连接成功")
    else:
        logger.error(f"MQTT连接失败, 错误码: {reason_code}")

def on_disconnect(client, userdata, flags, reason_code, properties):
    """
    MQTT断开连接回调函数
    """
    if reason_code == 0:
        logger.info("MQTT断开连接")
    else:
        logger.error(f"MQTT意外断开连接, 错误码: {reason_code}")

def on_publish(client, userdata, mid):
    """
    MQTT发布消息回调函数
    """
    logger.info(f"MQTT发布消息成功, mid: {mid}")

# 绑定回调函数
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect

def mqtt_connect():
    """
    连接MQTT服务器
    """
    if settings.MQTT_USERNAME and settings.MQTT_USERNAME != "":
        mqtt_client.username_pw_set(username=settings.MQTT_USERNAME, password=settings.MQTT_PASSWORD)

    try:
        mqtt_client.connect(settings.MQTT_BROKER_IP, settings.MQTT_BROKER_PORT)
        # 启动后台线程处理网络包
        mqtt_client.loop_start()
    except Exception as e:
        logger.error(f"MQTT连接发起失败: {e}")