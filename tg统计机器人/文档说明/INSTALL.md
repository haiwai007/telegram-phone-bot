# 安装和部署指南

## 快速开始

### 1. 环境准备

确保您的系统满足以下要求：
- Python 3.8 或更高版本
- pip 包管理器
- 稳定的网络连接

### 2. 下载项目

```bash
# 如果使用Git
git clone <repository-url>
cd tg统计机器人

# 或者直接下载ZIP文件并解压
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 创建Telegram机器人

1. 在Telegram中搜索并打开 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 命令
3. 按提示输入机器人名称（例如：客户号码统计机器人）
4. 输入机器人用户名（例如：customer_phone_stats_bot）
5. 复制获得的Bot Token

### 5. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件（使用您喜欢的编辑器）
notepad .env  # Windows
nano .env     # Linux/Mac
```

在 `.env` 文件中设置您的Bot Token：
```env
BOT_TOKEN=your_bot_token_here
```

### 6. 启动机器人

```bash
# 使用启动脚本（推荐）
python run.py

# 或直接运行机器人
python bot.py
```

### 7. 测试机器人

1. 在Telegram中搜索您的机器人用户名
2. 发送 `/start` 命令
3. 尝试发送一个号码，如：`13812345678`
4. 查看机器人的响应

## 高级配置

### 群组授权

如果您想限制机器人只在特定群组中工作：

1. 将机器人添加到目标群组
2. 获取群组ID（可以使用 [@userinfobot](https://t.me/userinfobot)）
3. 在 `.env` 文件中设置：
```env
AUTHORIZED_GROUPS=-123456789,-987654321
```

### 日志配置

调整日志级别：
```env
LOG_LEVEL=DEBUG  # 详细日志
LOG_LEVEL=INFO   # 标准日志（默认）
LOG_LEVEL=ERROR  # 只记录错误
```

### 号码验证配置

自定义号码长度限制：
```env
MIN_PHONE_LENGTH=8   # 最小长度
MAX_PHONE_LENGTH=15  # 最大长度
```

### 速率限制

防止消息轰炸：
```env
RATE_LIMIT_MESSAGES=10  # 每个时间窗口的最大消息数
RATE_LIMIT_WINDOW=60    # 时间窗口（秒）
```

## 部署到服务器

### 使用systemd（Linux）

1. 创建服务文件：
```bash
sudo nano /etc/systemd/system/telegram-phone-bot.service
```

2. 添加以下内容：
```ini
[Unit]
Description=Telegram Phone Statistics Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/tg统计机器人
ExecStart=/usr/bin/python3 /path/to/tg统计机器人/run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. 启用并启动服务：
```bash
sudo systemctl enable telegram-phone-bot
sudo systemctl start telegram-phone-bot
sudo systemctl status telegram-phone-bot
```

### 使用Docker

1. 创建 Dockerfile：
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "run.py"]
```

2. 构建和运行：
```bash
docker build -t telegram-phone-bot .
docker run -d --name phone-bot --env-file .env telegram-phone-bot
```

## 故障排除

### 常见问题

**Q: 机器人无响应**
A: 检查Bot Token是否正确，网络连接是否正常

**Q: 数据库错误**
A: 确保有写入权限，检查磁盘空间

**Q: 号码识别不准确**
A: 查看日志文件，调整关键词配置

**Q: 权限错误**
A: 检查文件权限，确保Python有读写权限

### 查看日志

```bash
# 查看实时日志
tail -f bot.log

# 查看错误日志
grep ERROR bot.log
```

### 测试功能

```bash
# 运行单元测试
python run_tests.py

# 测试特定功能
python run_tests.py test_phone_detector.TestPhoneDetector.test_pure_number_detection
```

## 备份和恢复

### 备份数据库

```bash
# 复制数据库文件
cp phone_records.db phone_records_backup_$(date +%Y%m%d).db
```

### 恢复数据库

```bash
# 停止机器人
# 替换数据库文件
cp phone_records_backup_20240115.db phone_records.db
# 重启机器人
```

## 更新机器人

1. 停止机器人
2. 备份数据库
3. 更新代码
4. 安装新依赖（如有）
5. 重启机器人

```bash
# 停止机器人
sudo systemctl stop telegram-phone-bot

# 备份
cp phone_records.db backup/

# 更新代码
git pull origin main

# 安装依赖
pip install -r requirements.txt

# 重启
sudo systemctl start telegram-phone-bot
```
