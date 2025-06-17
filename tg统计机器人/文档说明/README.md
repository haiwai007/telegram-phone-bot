# Telegram客户号码统计机器人

一个功能完整的Telegram机器人，用于在群聊中自动识别、记录和统计客户号码，支持重复检测和数据查询。

## 🚀 功能特性

### 📱 号码识别与记录
- **智能识别**: 自动识别纯数字号码（8-15位）和带关键词的号码
- **关键词支持**: 号码、客户、电话、手机、联系方式等
- **数据清理**: 自动移除空格、连字符、括号等格式字符
- **格式验证**: 拒绝无效号码（全零、重复数字、长度不符等）

### 🔍 重复检测
- **实时检测**: 立即识别重复提交的号码
- **详细提醒**: 显示首次提交者、上次提交者和总提交次数
- **完整记录**: 保存所有提交记录，包括重复提交

### 📊 统计查询
- **统计报告**: 总记录数、唯一号码数、重复号码数等
- **详情查询**: 查看特定号码的完整提交历史
- **时间记录**: 精确到秒的UTC+8时间戳

### 🛡️ 安全特性
- **群组授权**: 支持限制特定群组使用
- **速率限制**: 防止消息轰炸
- **错误处理**: 完善的异常处理和日志记录

## 📦 安装部署

### 环境要求
- Python 3.8+
- SQLite 3
- 稳定的网络连接

### 1. 克隆项目
```bash
git clone <repository-url>
cd tg统计机器人
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
nano .env
```

必需配置：
```env
BOT_TOKEN=your_bot_token_here
```

可选配置：
```env
DATABASE_PATH=phone_records.db
LOG_LEVEL=INFO
TIMEZONE=Asia/Shanghai
AUTHORIZED_GROUPS=group_id1,group_id2
```

### 4. 启动机器人
```bash
python bot.py
```

## 🤖 获取Bot Token

1. 在Telegram中找到 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称和用户名
4. 获取Bot Token并配置到 `.env` 文件

## 📖 使用说明

### 支持的号码格式
```
✅ 有效格式：
13812345678
号码：138-1234-5678
客户：(138) 1234.5678
电话：138 1234 5678

❌ 无效格式：
1234567 (太短)
00000000 (全零)
11111111 (重复数字)
```

### 机器人命令
- `/start` - 查看欢迎信息
- `/help` - 查看使用帮助
- `/统计` `/汇总` `/查重报告` - 查看统计报告
- `/详情 [号码]` - 查看号码详细记录

### 响应示例

**成功记录：**
```
✅ 号码已成功记录：13812345678
📝 提交人：张三 (@zhangsan)
🕐 记录时间：2024-01-15 14:30:25 (UTC+8)
```

**重复提醒：**
```
⚠️ 号码重复提示！
📱 号码：13812345678
👤 本次提交人：李四 (@lisi)
📅 首次记录于：2024-01-15 14:30:25 (UTC+8) 由 张三 提交
📊 总提交次数：2 次
```

## 🗄️ 数据库结构

### phone_records 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| phone_number | TEXT | 清理后的号码 |
| telegram_username | TEXT | 用户名 |
| telegram_user_id | INTEGER | 用户ID |
| first_name | TEXT | 用户姓名 |
| message_timestamp | DATETIME | 消息时间 |
| group_id | INTEGER | 群组ID |
| is_duplicate | BOOLEAN | 是否重复 |
| original_message | TEXT | 原始消息 |

## 🔧 配置说明

### 环境变量
| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| BOT_TOKEN | 必需 | Telegram Bot Token |
| DATABASE_PATH | phone_records.db | 数据库文件路径 |
| LOG_LEVEL | INFO | 日志级别 |
| TIMEZONE | Asia/Shanghai | 时区设置 |
| MAX_PHONE_LENGTH | 15 | 号码最大长度 |
| MIN_PHONE_LENGTH | 8 | 号码最小长度 |
| RATE_LIMIT_MESSAGES | 10 | 速率限制消息数 |
| RATE_LIMIT_WINDOW | 60 | 速率限制时间窗口(秒) |
| AUTHORIZED_GROUPS | 空 | 授权群组ID列表 |

## 📝 日志记录

机器人会记录详细的操作日志：
- 号码识别和记录
- 重复检测结果
- 用户操作记录
- 错误和异常信息

日志文件：`bot.log`

## 🛠️ 开发和测试

### 运行测试
```bash
python -m pytest tests/
```

### 调试模式
设置环境变量 `LOG_LEVEL=DEBUG` 启用详细日志。

## 📄 许可证

本项目采用 MIT 许可证。

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 支持

如有问题，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至项目维护者
