import cv2

# 将下面的URL替换为你实际的HTTP视频流地址
url = 'http://127.0.0.1:18848/yolo/identify'

# 创建VideoCapture对象
cap = cv2.VideoCapture(url)

# 检查视频流是否成功打开
if not cap.isOpened():
    print("错误：无法打开视频流")
    exit()

# 循环读取并显示视频帧
while True:
    # 读取一帧
    ret, frame = cap.read()

    # 如果读取成功，则显示该帧
    if ret:
        cv2.imshow('HTTP Video Stream', frame)

        # 按下 'q' 键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        print("无法接收帧 (stream end?). Exiting ...")
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()