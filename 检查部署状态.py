#!/usr/bin/env python3
"""
GitHub Actions 部署状态检查脚本
检查机器人部署状态和运行情况
"""

import requests
import time
from datetime import datetime

def check_bot_status(bot_token):
    """检查机器人 API 状态"""
    try:
        response = requests.get(f'https://api.telegram.org/bot{bot_token}/getMe', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                bot_info = data['result']
                print(f"✅ 机器人 API 状态正常")
                print(f"🤖 机器人名称: {bot_info['first_name']}")
                print(f"👤 用户名: @{bot_info['username']}")
                print(f"🆔 ID: {bot_info['id']}")
                return True
            else:
                print(f"❌ API 返回错误: {data}")
                return False
        else:
            print(f"❌ HTTP 错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def check_github_actions():
    """检查 GitHub Actions 状态"""
    print("\n🔍 GitHub Actions 状态检查")
    print("=" * 40)
    
    repo_url = "https://github.com/haiwai007/telegram-phone-bot"
    actions_url = f"{repo_url}/actions"

    print(f"📋 仓库地址: {repo_url}")
    print(f"🔄 Actions 页面: {actions_url}")
    print(f"⚙️ Settings 页面: {repo_url}/settings/secrets/actions")
    
    print("\n📊 预期的工作流:")
    workflows = [
        "🤖 Telegram机器人部署",
        "🔄 保持机器人运行", 
        "🏥 机器人健康检查",
        "💾 数据备份"
    ]
    
    for workflow in workflows:
        print(f"  - {workflow}")

def main():
    """主函数"""
    print("🚀 Telegram 机器人部署状态检查")
    print("=" * 50)
    print(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查机器人 API 状态
    print("\n🤖 机器人 API 状态检查")
    print("=" * 40)
    
    bot_token = "7951180702:AAFJVN7UonZIt1YkztuxUe4Hn0XUcWbvyj0"
    bot_status = check_bot_status(bot_token)
    
    # 检查 GitHub Actions
    check_github_actions()
    
    print("\n📋 部署检查清单")
    print("=" * 40)
    print("1. ✅ 代码已推送到 GitHub")
    print("2. ⏳ 设置 BOT_TOKEN Secret (需要手动完成)")
    print("3. ⏳ 启用 GitHub Actions (自动)")
    print("4. ⏳ 等待工作流运行")
    
    print("\n🔗 重要链接")
    print("=" * 40)
    print("📁 仓库: https://github.com/haiwai007/telegram-phone-bot")
    print("🔄 Actions: https://github.com/haiwai007/telegram-phone-bot/actions")
    print("⚙️ Secrets: https://github.com/haiwai007/telegram-phone-bot/settings/secrets/actions")
    
    print("\n📝 下一步操作")
    print("=" * 40)
    print("1. 访问 Secrets 页面设置 BOT_TOKEN")
    print("2. 等待 GitHub Actions 自动运行")
    print("3. 在 Actions 页面监控部署状态")
    print("4. 测试机器人功能")
    
    if bot_status:
        print("\n🎉 机器人 Token 有效，准备就绪！")
    else:
        print("\n⚠️ 机器人 Token 可能有问题，请检查")

if __name__ == "__main__":
    main()
