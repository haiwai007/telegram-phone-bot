#!/usr/bin/env python3
"""
GitHub Actions 自动部署脚本
确保一次性成功部署 Telegram 机器人
"""

import subprocess
import time
import requests
from datetime import datetime

class GitHubDeployer:
    def __init__(self, repo_url, bot_token):
        self.repo_url = repo_url
        self.bot_token = bot_token
        self.repo_name = repo_url.split('/')[-1].replace('.git', '')
        self.username = repo_url.split('/')[-2]
        
    def check_bot_token(self):
        """验证机器人 Token"""
        print("🤖 验证机器人 Token...")
        try:
            response = requests.get(f'https://api.telegram.org/bot{self.bot_token}/getMe', timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['ok']:
                    bot_info = data['result']
                    print(f"✅ 机器人验证成功: @{bot_info['username']}")
                    return True
            print("❌ 机器人 Token 无效")
            return False
        except Exception as e:
            print(f"❌ 验证失败: {e}")
            return False
    
    def setup_git_remote(self):
        """设置 Git 远程仓库"""
        print("🔗 设置 Git 远程仓库...")
        try:
            subprocess.run(['git', 'remote', 'add', 'origin', self.repo_url], check=True)
            print("✅ 远程仓库设置成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 设置远程仓库失败: {e}")
            return False
    
    def push_code(self):
        """推送代码到 GitHub"""
        print("📤 推送代码到 GitHub...")
        try:
            subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True)
            print("✅ 代码推送成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 代码推送失败: {e}")
            print("💡 可能需要 GitHub 认证，请检查:")
            print("   - GitHub CLI: gh auth login")
            print("   - Personal Access Token")
            print("   - SSH 密钥设置")
            return False
    
    def wait_for_actions(self):
        """等待 GitHub Actions 开始运行"""
        print("⏳ 等待 GitHub Actions 启动...")
        actions_url = f"https://github.com/{self.username}/{self.repo_name}/actions"
        print(f"🔄 Actions 页面: {actions_url}")
        
        for i in range(30):  # 等待最多5分钟
            print(f"⏰ 等待中... ({i+1}/30)")
            time.sleep(10)
            
        print("✅ 请手动检查 Actions 页面")
        return True
    
    def deploy(self):
        """执行完整部署流程"""
        print("🚀 开始 GitHub Actions 自动部署")
        print("=" * 50)
        print(f"📁 仓库: {self.repo_url}")
        print(f"🤖 机器人: {self.bot_token[:10]}...")
        print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 步骤1: 验证机器人 Token
        if not self.check_bot_token():
            return False
        
        # 步骤2: 设置远程仓库
        if not self.setup_git_remote():
            return False
        
        # 步骤3: 推送代码
        if not self.push_code():
            return False
        
        # 步骤4: 等待 Actions 启动
        self.wait_for_actions()
        
        print("\n🎉 部署流程完成！")
        print("📋 下一步:")
        print(f"1. 访问: https://github.com/{self.username}/{self.repo_name}/settings/secrets/actions")
        print(f"2. 添加 Secret: BOT_TOKEN = {self.bot_token}")
        print(f"3. 监控: https://github.com/{self.username}/{self.repo_name}/actions")
        
        return True

def main():
    """主函数"""
    print("🤖 Telegram 机器人 GitHub Actions 自动部署")
    print("=" * 60)
    
    # 配置信息
    bot_token = "7951180702:AAFJVN7UonZIt1YkztuxUe4Hn0XUcWbvyj0"
    
    # 等待用户输入新仓库地址
    print("📝 请输入新创建的 GitHub 仓库地址:")
    print("格式: https://github.com/haiwai007/仓库名.git")
    repo_url = input("🔗 仓库地址: ").strip()
    
    if not repo_url:
        print("❌ 仓库地址不能为空")
        return 1
    
    # 创建部署器并执行部署
    deployer = GitHubDeployer(repo_url, bot_token)
    success = deployer.deploy()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
