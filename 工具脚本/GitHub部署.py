#!/usr/bin/env python3
"""
GitHub Actions 快速部署脚本
帮助用户快速设置 GitHub 仓库和部署机器人
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_git():
    """检查 Git 是否安装"""
    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Git 未安装，请先安装 Git")
        return False

def check_github_cli():
    """检查 GitHub CLI 是否安装"""
    try:
        subprocess.run(['gh', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  GitHub CLI 未安装，将使用手动方式")
        return False

def create_github_repo():
    """创建 GitHub 仓库"""
    print("🚀 GitHub 仓库创建向导")
    print("=" * 40)
    
    repo_name = input("📝 输入仓库名称 (默认: telegram-phone-bot): ").strip()
    if not repo_name:
        repo_name = "telegram-phone-bot"
    
    description = input("📄 输入仓库描述 (可选): ").strip()
    if not description:
        description = "Telegram客户号码统计机器人 - GitHub Actions免费托管"
    
    is_private = input("🔒 是否创建私有仓库? (y/N): ").lower().strip() == 'y'
    
    if check_github_cli():
        try:
            # 使用 GitHub CLI 创建仓库
            cmd = ['gh', 'repo', 'create', repo_name, '--description', description]
            if is_private:
                cmd.append('--private')
            else:
                cmd.append('--public')
            
            subprocess.run(cmd, check=True)
            print(f"✅ 仓库创建成功: https://github.com/$(gh api user --jq .login)/{repo_name}")
            return repo_name
        except subprocess.CalledProcessError as e:
            print(f"❌ 创建仓库失败: {e}")
            return None
    else:
        print("\n📋 手动创建仓库步骤:")
        print(f"1. 访问 https://github.com/new")
        print(f"2. 仓库名称: {repo_name}")
        print(f"3. 描述: {description}")
        print(f"4. 可见性: {'私有' if is_private else '公开'}")
        print(f"5. 点击 'Create repository'")
        
        input("\n按回车键继续（确认已创建仓库）...")
        return repo_name

def setup_git_repo(repo_name):
    """设置本地 Git 仓库"""
    print("\n🔧 设置本地 Git 仓库...")
    
    try:
        # 初始化 Git 仓库
        subprocess.run(['git', 'init'], check=True)
        print("✅ Git 仓库初始化完成")
        
        # 添加所有文件
        subprocess.run(['git', 'add', '.'], check=True)
        print("✅ 文件添加完成")
        
        # 提交
        subprocess.run(['git', 'commit', '-m', '🤖 初始化 Telegram 机器人项目'], check=True)
        print("✅ 初始提交完成")
        
        # 设置远程仓库
        github_username = input("👤 输入你的 GitHub 用户名: ").strip()
        remote_url = f"https://github.com/{github_username}/{repo_name}.git"
        
        subprocess.run(['git', 'remote', 'add', 'origin', remote_url], check=True)
        subprocess.run(['git', 'branch', '-M', 'main'], check=True)
        print(f"✅ 远程仓库设置完成: {remote_url}")
        
        return github_username, remote_url
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 设置失败: {e}")
        return None, None

def push_to_github():
    """推送到 GitHub"""
    print("\n📤 推送代码到 GitHub...")
    
    try:
        subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True)
        print("✅ 代码推送成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 推送失败: {e}")
        print("💡 可能需要设置 GitHub 认证")
        print("   - 使用 GitHub CLI: gh auth login")
        print("   - 或设置 Personal Access Token")
        return False

def setup_secrets_guide(github_username, repo_name, bot_token):
    """显示 Secrets 设置指南"""
    print("\n🔐 GitHub Secrets 设置指南")
    print("=" * 40)
    
    repo_url = f"https://github.com/{github_username}/{repo_name}"
    secrets_url = f"{repo_url}/settings/secrets/actions"
    
    print(f"📋 请访问: {secrets_url}")
    print("\n🔑 需要添加的 Secrets:")
    print("1. 点击 'New repository secret'")
    print("2. 添加以下 Secret:")
    print(f"   Name: BOT_TOKEN")
    print(f"   Value: {bot_token}")
    print("\n3. 可选 Secrets:")
    print("   Name: AUTHORIZED_GROUPS")
    print("   Value: 群组ID1,群组ID2 (逗号分隔)")
    
    print(f"\n🚀 完成后，访问 {repo_url}/actions 查看部署状态")

def main():
    """主函数"""
    print("🤖 Telegram 机器人 GitHub Actions 部署向导")
    print("=" * 50)
    
    # 检查环境
    if not check_git():
        return 1
    
    # 检查当前目录
    if not Path("启动机器人.py").exists():
        print("❌ 请在项目根目录运行此脚本")
        return 1
    
    # 获取 Bot Token
    bot_token = input("🤖 输入你的 Telegram Bot Token: ").strip()
    if not bot_token:
        print("❌ Bot Token 不能为空")
        return 1
    
    # 创建 GitHub 仓库
    repo_name = create_github_repo()
    if not repo_name:
        return 1
    
    # 设置 Git 仓库
    github_username, remote_url = setup_git_repo(repo_name)
    if not github_username:
        return 1
    
    # 推送代码
    if not push_to_github():
        print("\n⚠️  推送失败，请手动推送代码后继续")
        input("按回车键继续...")
    
    # 显示 Secrets 设置指南
    setup_secrets_guide(github_username, repo_name, bot_token)
    
    print("\n🎉 部署向导完成！")
    print("📋 下一步:")
    print("1. 设置 GitHub Secrets")
    print("2. 启用 GitHub Actions")
    print("3. 等待机器人自动部署")
    print("4. 在 Telegram 中测试机器人")
    
    return 0

if __name__ == "__main__":
    exit(main())
