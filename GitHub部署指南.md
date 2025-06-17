# 🚀 GitHub Actions 免费部署指南

## 📋 概述
使用 GitHub Actions 实现 Telegram 机器人的完全免费托管，24/7 运行，无需任何服务器成本！

## 🎯 部署优势

### ✅ 完全免费
- GitHub Actions 每月提供 2000 分钟免费额度
- 公开仓库无限制使用
- 无需购买服务器或VPS

### 🔄 自动化运行
- 自动重启机制，避免6小时限制
- 多实例策略，确保连续运行
- 健康检查和故障恢复

### 📊 数据安全
- 自动数据备份
- 日志文件保存
- 版本控制管理

## 🛠️ 部署步骤

### 1. 准备 GitHub 仓库

```bash
# 1. 在 GitHub 创建新仓库
# 2. 克隆到本地
git clone https://github.com/你的用户名/你的仓库名.git
cd 你的仓库名

# 3. 复制项目文件到仓库
cp -r /path/to/tg统计机器人/* .

# 4. 提交代码
git add .
git commit -m "🤖 初始化 Telegram 机器人项目"
git push origin main
```

### 2. 配置 GitHub Secrets

在 GitHub 仓库设置中添加以下 Secrets：

#### 必需的 Secrets：
- `BOT_TOKEN`: 你的 Telegram Bot Token
  ```
  7951180702:AAFJVN7UonZIt1YkztuxUe4Hn0XUcWbvyj0
  ```

#### 可选的 Secrets：
- `AUTHORIZED_GROUPS`: 授权群组ID（逗号分隔）
  ```
  -1001234567890,-1001234567891
  ```

### 3. 启用 GitHub Actions

1. 进入仓库的 **Actions** 标签页
2. 启用 GitHub Actions
3. 工作流将自动开始运行

## 🔄 工作流说明

### 📋 主要工作流

#### 1. `deploy-bot.yml` - 主部署流程
- **触发条件**: 代码推送、PR、定时任务
- **运行时间**: 约6小时
- **功能**: 运行机器人主程序

#### 2. `keep-alive.yml` - 保持运行
- **触发条件**: 每5小时50分钟
- **策略**: 3个并行实例
- **功能**: 确保机器人连续运行

#### 3. `health-check.yml` - 健康检查
- **触发条件**: 每小时
- **功能**: 检查机器人API状态

#### 4. `backup-data.yml` - 数据备份
- **触发条件**: 每天凌晨2点
- **功能**: 备份数据库和日志

## 📊 运行策略

### 🔄 连续运行机制

```
时间轴示例：
00:00 ├─ 实例1启动 (6小时)
00:30 ├─ 实例2启动 (6小时)  
01:00 ├─ 实例3启动 (6小时)
05:50 ├─ 新一轮实例1启动
06:00 ├─ 原实例1结束
06:20 ├─ 新一轮实例2启动
06:30 ├─ 原实例2结束
...
```

### 🛡️ 故障处理
- **自动重启**: 超时或错误自动重启
- **多实例冗余**: 确保至少一个实例运行
- **健康监控**: 每小时检查状态

## 📈 监控和管理

### 📊 查看运行状态
1. 进入 GitHub 仓库
2. 点击 **Actions** 标签
3. 查看工作流运行状态

### 📋 查看日志
1. 点击具体的工作流运行
2. 展开步骤查看详细日志
3. 下载 Artifacts 获取完整日志

### 💾 数据备份
- 每日自动备份到 GitHub Artifacts
- 保留30天
- JSON格式，包含完整数据

## 🔧 自定义配置

### 修改运行频率
编辑 `.github/workflows/keep-alive.yml`:
```yaml
schedule:
  # 修改这里的 cron 表达式
  - cron: '50 */5 * * *'  # 每5小时50分钟
```

### 调整实例数量
编辑 `keep-alive.yml` 中的 matrix:
```yaml
strategy:
  matrix:
    instance: [1, 2, 3, 4, 5]  # 增加到5个实例
```

### 修改备份频率
编辑 `.github/workflows/backup-data.yml`:
```yaml
schedule:
  - cron: '0 2 * * *'  # 每天凌晨2点
```

## 🚨 注意事项

### ⚠️ GitHub Actions 限制
- 单个工作流最长运行6小时
- 每月2000分钟免费额度（公开仓库无限制）
- 并发任务数量限制

### 🔒 安全建议
- 使用 GitHub Secrets 存储敏感信息
- 定期更新 Bot Token
- 监控仓库访问权限

### 📊 资源优化
- 合理设置超时时间
- 及时清理旧的 Artifacts
- 监控使用量

## 🎉 部署完成

完成以上步骤后，你的 Telegram 机器人将：
- ✅ 24/7 免费运行
- ✅ 自动重启和故障恢复
- ✅ 数据自动备份
- ✅ 完整的监控和日志

享受你的免费 Telegram 机器人托管服务！🚀
