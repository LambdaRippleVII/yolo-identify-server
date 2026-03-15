# YOLO识别系统

这是一个基于YOLO算法的实时识别系统，能够从视频流中检测和识别目标，并通过MQTT协议上报识别结果。

该系统特别适用于：
- 农业病虫害监测
- 工业缺陷检测
- 实时监控场景
- 智能安防应用
- 自动化检测系统

## 功能特性

- 实时视频流处理（支持USB摄像头和RTSP流）
- 基于YOLO模型的目标检测
- MQTT消息发布功能
- 灵活的配置系统
- Web API接口及文档
- 实时视频流展示

## 项目结构

```
.
├── app/
│   ├── api/
│   │   ├── router/
│   │   │   └── yolo_router.py     # API路由定义
│   │   └── api_main.py            # API入口
│   ├── config/                    # 配置模块
│   │   ├── __init__.py
│   │   ├── exception_config.py    # 异常配置
│   │   └── logger_config.py       # 日志配置
│   ├── core/                      # 核心模块
│   │   ├── __init__.py
│   │   ├── app_lifespan.py        # 应用生命周期管理
│   │   ├── env_setting.py         # 环境变量配置
│   │   └── mqtt_client.py         # MQTT客户端
│   ├── exceptions/                # 异常处理模块
│   ├── handler/                   # 业务处理模块
│   │   ├── send_msg_handler.py    # 消息发送处理
│   │   └── video_handler.py       # 视频处理
│   └── models/                    # 数据模型
│       └── result_model.py        # 结果模型
├── .env                          # 环境变量配置文件
├── main.py                       # 应用入口
├── README.md                     # 项目说明
├── sendMsgConfig.json            # 消息发送配置文件
└── .gitignore                    # Git忽略配置
```

## 系统架构

- **Web框架**: FastAPI
- **深度学习框架**: Ultralytics YOLO
- **消息协议**: MQTT
- **日志系统**: Loguru
- **视频处理**: OpenCV
- **并发处理**: Threading

## 视频处理机制

系统采用多线程方式处理视频流：
- 视频捕获线程负责视频采集和YOLO识别
- 识别后的结果同时用于显示和MQTT消息发送
- 两个视频流接口分别提供原始帧和识别帧的访问
- 支持多种视频源（USB摄像头、RTSP流等）

## 安装部署

### 1. 环境准备

确保已安装Python 3.10+，然后安装依赖包：

```bash
pip install -r requirements.txt
```

如果没有requirements.txt文件，请安装以下核心依赖：

```bash
pip install fastapi uvicorn pydantic-settings loguru ultralytics opencv-python paho-mqtt
```

**项目依赖说明**:
- `fastapi`: Web框架，提供API服务
- `uvicorn`: ASGI服务器，用于运行FastAPI应用
- `pydantic-settings`: 环境变量配置管理
- `loguru`: 日志记录工具
- `ultralytics`: YOLO模型库，提供目标检测功能
- `opencv-python`: OpenCV库，用于视频处理
- `paho-mqtt`: MQTT协议客户端，用于消息传输

### 2. 下载YOLO模型

将YOLO模型文件放置在项目根目录下的`yolo_models`文件夹中，或在环境变量中指定模型路径。

### 3. 准备视频源

根据`CAP_SOURCE`环境变量配置视频源：
- 本地摄像头：设置为摄像头编号（如0、1）
- RTSP流：设置为RTSP地址（如"rtsp://192.168.1.100:554/stream"）

### 4. 配置环境变量

复制`.env.example`文件并命名为`.env`，根据实际情况修改配置参数。

## 环境变量配置详解

系统的所有配置都通过环境变量进行管理，以下是详细的配置说明：

### 服务器配置

- `SERVER_TITLE`: 服务器标题（默认: "YOLO识别服务器"）
- `SERVER_VERSION`: 服务器版本（默认: "1.0.0"）
- `SERVER_HOST`: 服务器监听地址（默认: "0.0.0.0"）
- `SERVER_PORT`: 服务器端口号（默认: 18848）
- `DOCS_URL`: API文档路径（默认: "/yolo-api/docs-ui"）
- `REDOC_URL`: Redoc文档路径（默认: "/yolo-api/redoc-ui"）
- `OPENAPI_URL`: OpenAPI配置路径（默认: "/yolo-api/openapi-conf.json"）

### MQTT配置

- `MQTT_BROKER_IP`: MQTT服务器IP地址（必需）
- `MQTT_BROKER_PORT`: MQTT服务器端口（默认: 1883）
- `MQTT_USERNAME`: MQTT登录用户名（可选，默认为空，即匿名登录）
- `MQTT_PASSWORD`: MQTT登录密码（可选，默认为空，即匿名登录）
- `MQTT_CLIENT_ID`: MQTT客户端ID（必需）

### 模型配置

- `CAP_SOURCE`: 视频源地址（必需）
  - 本地摄像头：使用数字（如0、1）
  - RTSP流：使用完整URL（如"rtsp://192.168.1.100:554/stream"）
- `MODEL_PATH`: YOLO模型路径（必需），可以是：
  - 模型名称（如"yolo11n.pt"），系统将在`yolo_models`目录中查找
  - 模型绝对路径

### 接入设备配置

- `PRODUCT_ID`: 产品ID（必需）
- `DEVICE_ID`: 设备ID（必需）
- `REPORT_MIN_INTERVAL`: 数据上报最小间隔时间（毫秒，默认: 1000）
- `UP_TOPIC_RULE`: 上行主题规则（必需），支持变量替换，如`/{PRODUCT_ID}/{DEVICE_ID}/properties/report`
- `UP_QOS`: MQTT发布的QoS级别（默认: 0，可选0、1、2）
- `SEND_MSG_CONFIG_FILE`: 消息配置文件路径（必需）

## 上报消息配置详解

系统的消息格式通过`sendMsgConfig.json`文件进行配置。该配置文件采用JSON格式，但支持模板变量和循环结构。

### 消息配置文件格式

```json
{
  "product_id": "$product_id$",
  "device_id": "$device_id$",
  "server_title": "$server_title$",
  "server_version": "$server_version$",
  "yolo_identify": !{
    "xlt": "$x1$",
    "ylt": "$y1$",
    "xrb": "$x2$",
    "yrb": "$y2$",
    "conf": "$conf$",
    "cls_name": "$cls_name$",
    "cls": "$cls$"
  }!
}
```

### 模板变量说明

- `$product_id$`, `$device_id$`: 从环境变量中获取的产品ID和设备ID
- `$server_title$`, `$server_version$`: 从环境变量中获取的服务器标题和版本
- `$x1$`, `$y1$`: 检测框左上角X、Y坐标
- `$x2$`, `$y2$`: 检测框右下角X、Y坐标
- `$conf$`: 检测置信度
- `$cls_name$`: 检测类别名称
- `$cls$`: 检测类别ID

### 循环结构说明

配置文件中使用 `!{...}!` 包围的部分称为循环结构，它会为每个检测到的目标重复生成。当检测到多个目标时，循环部分会被替换为一个数组，每个元素对应一个检测目标。

例如，如果有两个检测目标，最终生成的消息可能是：

```json
{
  "product_id": "11111",
  "device_id": "22222",
  "server_title": "YOLO识别服务器",
  "server_version": "1.0.0",
  "yolo_identify": [
    {
      "xlt": 100.5,
      "ylt": 200.3,
      "xrb": 150.2,
      "yrb": 250.1,
      "conf": 0.95,
      "cls_name": "病害A",
      "cls": 0
    },
    {
      "xlt": 300.1,
      "ylt": 400.7,
      "xrb": 350.9,
      "yrb": 450.5,
      "conf": 0.87,
      "cls_name": "病害B",
      "cls": 1
    }
  ]
}
```

### 配置文件路径

消息配置文件可以放置在以下位置之一：
1. 项目根目录
2. 通过`SEND_MSG_CONFIG_FILE`环境变量指定的绝对路径
3. 在`send_msg_config`目录中（如果在环境变量中指定了文件名）

## 启动服务

配置完成后，运行主程序启动服务：

```bash
python main.py
```

服务启动后将自动：
1. 连接到MQTT服务器
2. 加载YOLO模型
3. 初始化消息配置
4. 启动视频捕获线程
5. 开始实时检测和识别

服务启动后，可以通过浏览器访问API文档：
- Swagger UI: http://localhost:18848/yolo-api/docs-ui
- ReDoc: http://localhost:18848/yolo-api/redoc-ui

## API接口

系统提供了以下API接口：

### 1. 原始视频流接口

**接口地址**: `GET /yolo/original`

**功能描述**: 
- 提供未经处理的原始视频流
- 适用于查看未经YOLO模型处理的原始画面
- 帧率为约30fps

**使用方法**:
- 在浏览器中访问 `http://<服务器地址>:<服务器端口>/yolo/original`
- 例如: `http://localhost:18848/yolo/original`

### 2. 识别视频流接口

**接口地址**: `GET /yolo/identify`

**功能描述**:
- 提供经过YOLO模型处理的识别视频流
- 在视频中实时绘制检测框、置信度和标签，显示识别结果
- 适用于查看YOLO模型的实时检测效果
- 每次识别后会根据配置自动向MQTT服务器发送检测结果
- 帧率为约30fps

**使用方法**:
- 在浏览器中访问 `http://<服务器地址>:<服务器端口>/yolo/identify`
- 例如: `http://localhost:18848/yolo/identify`

**应用场景**:
- 实时监控YOLO模型检测效果
- 观察病害识别的准确性
- 验证模型在实际场景中的表现

### 3. API文档接口

系统还提供了API文档接口：
- Swagger UI: `http://<服务器地址>:<服务器端口><DOCS_URL>` (默认: `http://localhost:18848/yolo-api/docs-ui`)
- ReDoc: `http://<服务器地址>:<服务器端口><REDOC_URL>` (默认: `http://localhost:18848/yolo-api/redoc-ui`)

**注意**: 将 `<服务器地址>`、`<服务器端口>` 和其他变量替换为实际的配置值。

## 故障排除

1. **找不到模型文件**: 确认`MODEL_PATH`环境变量指向正确的模型文件
2. **MQTT连接失败**: 检查MQTT服务器配置是否正确
3. **视频源无法打开**: 验证`CAP_SOURCE`配置是否正确
4. **配置文件解析错误**: 确认`sendMsgConfig.json`格式正确
5. **视频流无法显示**: 
   - 检查视频源是否正常工作
   - 确认摄像头权限是否已授予
   - 验证`CAP_SOURCE`配置是否正确
6. **识别效果不佳**: 
   - 检查光照条件是否充足
   - 确认目标是否在摄像头视野内
   - 验证YOLO模型是否适合当前识别任务
7. **API接口无响应**: 
   - 检查服务器是否正常启动
   - 确认端口是否被占用
   - 验证API路径是否正确

## 注意事项

- 确保YOLO模型文件存在且可读
- MQTT服务器需处于运行状态
- 视频源需可访问
- 环境变量配置需符合要求
- 消息配置文件需使用正确的模板语法
- 根据实际硬件性能调整视频帧率和模型大小
- 在生产环境中确保API接口的安全性
- 定期检查和维护YOLO模型以保证识别精度