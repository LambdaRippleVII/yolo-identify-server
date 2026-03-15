import re
import time
from typing import Any

from app.core import settings, global_info
from app.core.mqtt_client import mqtt_client

SEND_MSG_CONFIG_DICT = {
    "$x1$": Any,
    "$y1$": Any,
    "$x2$": Any,
    "$y2$": Any,
    "$conf$": Any,
    "$cls$": Any,
    "$cls_name$": Any
}

last_send_time: int = 0

def get_cycle_config():
    """ 获取配置文件信息中循环体 """
    pattern = r"!(.*?)!"
    config_info = global_info.SEND_MSG_CONFIG

    cycle_info = re.findall(pattern, config_info, flags=re.DOTALL)

    if not cycle_info:
        return None

    return cycle_info[0]

def replacer(match, str_msg):
    """
    替换匹配项
    Args:
        match: 匹配项
        str_msg: 匹配项对应的字符串
    """
    # 获取括号内的字符串
    key: str = match.group(1)

    # 动态获取属性值
    try:
        value = getattr(settings, key.upper())
        # 确保转换为字符串
        return str(value)
    except AttributeError:
        return match.group(0)

def handle_send_msg(results):
    """
    处理发送消息
    Args:
        results: yolo识别结果
    """
    global last_send_time

    # 检查间隔时间
    timestamp = int(time.time() * 1000)
    if timestamp - last_send_time < settings.REPORT_MIN_INTERVAL:
        return

    last_send_time = timestamp

    # 获取配置文件信息中循环体
    cycle_config = get_cycle_config()

    # 如果没有循环配置，直接发送原始配置
    if cycle_config is None:
        send_msg = global_info.SEND_MSG_CONFIG
    else:
        cycle_items = []

        for box in results[0].boxes:
            cycle_info = cycle_config.replace("\n", "")

            x1, y1, x2, y2 = box.xyxy[0]
            SEND_MSG_CONFIG_DICT["$x1$"] = float(x1)
            SEND_MSG_CONFIG_DICT["$y1$"] = float(y1)
            SEND_MSG_CONFIG_DICT["$x2$"] = float(x2)
            SEND_MSG_CONFIG_DICT["$y2$"] = float(y2)
            conf = box.conf[0]
            SEND_MSG_CONFIG_DICT["$conf$"] = float(conf)
            cls = box.cls[0]
            SEND_MSG_CONFIG_DICT["$cls$"] = int(cls)
            cls_name = results[0].names[int(cls)]
            SEND_MSG_CONFIG_DICT["$cls_name$"] = cls_name

            # 过滤盒子
            if global_info.MODEL_CONFIG and  global_info.MODEL_CONFIG is not None:
                if cls_name not in global_info.MODEL_CONFIG:
                    continue
                if conf < global_info.MODEL_CONFIG[cls_name]:
                    continue

            for key, value in SEND_MSG_CONFIG_DICT.items():
                if value is None:
                    continue
                cycle_info = cycle_info.replace(key, str(value))
            
            cycle_items.append(cycle_info)

        # 构建循环消息，避免末尾逗号
        if cycle_items:
            cycle_msg = "[" + ",".join(cycle_items) + "]"
        else:
            # 如果没有识别结果，用空数组替换
            cycle_msg = "[]"

        send_msg = global_info.SEND_MSG_CONFIG.replace(cycle_config, cycle_msg).replace("!", "")

    mqtt_client.publish(global_info.UP_TOPIC_RULE, send_msg, qos=settings.UP_QOS)