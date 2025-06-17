# 🤖 Telegram客户号码统计机器人

[![部署状态](https://github.com/你的用户名/你的仓库名/workflows/🤖%20Telegram机器人部署/badge.svg)](https://github.com/你的用户名/你的仓库名/actions)
[![健康检查](https://github.com/你的用户名/你的仓库名/workflows/🏥%20机器人健康检查/badge.svg)](https://github.com/你的用户名/你的仓库名/actions)
[![数据备份](https://github.com/你的用户名/你的仓库名/workflows/💾%20数据备份/badge.svg)](https://github.com/你的用户名/你的仓库名/actions)

一个功能完整的 Telegram 机器人，用于在群聊中自动识别、记录和统计客户号码。支持 **GitHub Actions 免费托管**，24/7 运行无需服务器！

## 🚀 快速开始

### 🔧 本地运行
```bash
# 1. 克隆项目
git clone https://github.com/你的用户名/你的仓库名.git
cd 你的仓库名

# 2. 安装依赖
pip install -r 配置文件/依赖包列表.txt

# 3. 配置环境变量
cp 配置文件/环境配置模板.env 配置文件/环境配置.env
# 编辑 配置文件/环境配置.env，添加你的 BOT_TOKEN

# 4. 启动机器人
python 启动机器人.py
```

### ☁️ GitHub Actions 免费托管
1. Fork 这个仓库
2. 在 Settings > Secrets 中添加 `BOT_TOKEN`
3. 启用 GitHub Actions
4. 机器人将自动开始运行！

详细部署指南：[GitHub部署指南.md](GitHub部署指南.md)

## ✨ 功能特性

### 📱 智能号码识别
- 自动识别 8-15 位纯数字号码
- 支持关键词：号码、客户、电话、手机等
- 智能清理格式（空格、连字符、括号等）
- 拒绝无效号码（全零、重复数字等）

### 🔍 重复检测
- 实时检测重复提交的号码
- 显示首次提交者和提交历史
- 完整记录所有提交（包括重复）

### 📊 统计查询
- `/stats` - 查看统计信息
- `/detail [号码]` - 查看号码详情
- `/search [关键词]` - 搜索功能
- `/export` - 导出数据

### 🛡️ 安全特性
- 群组授权控制
- 速率限制防护
- 完善的错误处理

## 🏗️ 项目结构

```
tg统计机器人/
├── 📁 核心模块/           # 核心功能模块
│   ├── 机器人主程序.py     # 主机器人程序
│   ├── 配置管理.py         # 配置管理
│   ├── 数据库管理.py       # 数据库操作
│   ├── 号码检测器.py       # 号码检测
│   ├── 通知系统.py         # 通知系统
│   └── 导出管理器.py       # 导出功能
├── 📁 配置文件/           # 配置相关文件
├── 📁 工具脚本/           # 辅助工具
├── 📁 测试文件/           # 测试文件
├── 📁 .github/workflows/  # GitHub Actions 工作流
└── 启动机器人.py          # 主启动程序
```

## 🔄 GitHub Actions 工作流

### 🤖 主要工作流
- **deploy-bot.yml** - 主部署流程，运行机器人
- **keep-alive.yml** - 保持运行，多实例策略
- **health-check.yml** - 健康检查，每小时监控
- **backup-data.yml** - 数据备份，每日自动备份

### 📊 运行策略
- 🔄 自动重启机制，避免 6 小时限制
- 🔀 多实例并行，确保连续运行
- 🏥 健康监控，故障自动恢复
- 💾 数据备份，安全可靠

## 📈 使用统计

![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-免费托管-green)
![运行时间](https://img.shields.io/badge/运行时间-24/7-blue)
![成本](https://img.shields.io/badge/成本-完全免费-brightgreen)

## 🛠️ 配置说明

### 环境变量
```env
BOT_TOKEN=你的机器人Token
DATABASE_PATH=phone_records.db
LOG_LEVEL=INFO
TIMEZONE=Asia/Shanghai
AUTHORIZED_GROUPS=群组ID1,群组ID2
```

### GitHub Secrets
在仓库设置中添加：
- `BOT_TOKEN`: Telegram Bot Token（必需）
- `AUTHORIZED_GROUPS`: 授权群组ID（可选）

## 🧪 测试

```bash
# 运行所有测试
python 测试文件/测试运行器.py

# 功能演示
python 工具脚本/功能演示.py
```

## 📊 监控和管理

### 查看运行状态
1. 进入 GitHub 仓库的 Actions 页面
2. 查看工作流运行状态和日志
3. 下载 Artifacts 获取详细日志

### 数据备份
- 每日自动备份到 GitHub Artifacts
- 保留 30 天
- JSON 格式，包含完整数据

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [GitHub部署指南](GitHub部署指南.md)
- [项目结构说明](项目结构说明.md)
- [清理完成报告](清理完成报告.md)

---

⭐ 如果这个项目对你有帮助，请给个 Star！
