#!/usr/bin/env python3
"""
Telegram客户号码统计机器人 - 智能启动脚本
支持冲突检测、自动重试、健康检查等功能
"""

import sys
import os
import time
import requests
import argparse
from pathlib import Path

# 添加核心模块路径
project_root = Path(__file__).parent
core_modules = project_root / "核心模块"
config_dir = project_root / "配置文件"
sys.path.insert(0, str(core_modules))

# 设置环境变量文件路径
env_file = config_dir / "环境配置.env"
if env_file.exists():
    os.environ.setdefault('ENV_FILE_PATH', str(env_file))

def print_banner():
    """打印启动横幅"""
    print("🤖 Telegram客户号码统计机器人")
    print("=" * 50)
    print("📱 智能号码识别 | 📊 实时统计 | 🔄 24/7运行")
    print("🚀 GitHub Actions部署 | 💾 自动备份")
    print("=" * 50)

def check_bot_running(bot_token, timeout=5):
    """检查机器人是否已经在运行"""
    try:
        response = requests.get(
            f'https://api.telegram.org/bot{bot_token}/getUpdates',
            params={'timeout': 1, 'limit': 1},
            timeout=timeout
        )

        if response.status_code == 409:
            return True, "检测到其他实例正在运行"
        elif response.status_code == 200:
            return False, "API连接正常，可以启动"
        elif response.status_code == 401:
            return False, "Bot Token无效"
        else:
            return False, f"API返回状态码: {response.status_code}"

    except requests.exceptions.Timeout:
        return False, "API连接超时"
    except requests.exceptions.ConnectionError:
        return False, "网络连接失败"
    except Exception as e:
        return False, f"检查失败: {e}"

def wait_for_slot(bot_token, max_wait_minutes=10):
    """等待机器人实例空闲"""
    print(f"⏳ 等待其他实例结束 (最多等待 {max_wait_minutes} 分钟)...")

    for i in range(max_wait_minutes):
        is_running, message = check_bot_running(bot_token)
        if not is_running:
            print(f"✅ {message}")
            return True

        print(f"⏳ 等待中... ({i+1}/{max_wait_minutes} 分钟) - {message}")
        time.sleep(60)

    print(f"⚠️ 等待超时，其他实例可能长期运行")
    return False

def get_startup_mode():
    """获取启动模式"""
    # 检查环境变量
    workflow = os.getenv('GITHUB_WORKFLOW', '')
    if 'keep-alive' in workflow.lower():
        return 'backup'
    elif 'deploy' in workflow.lower():
        return 'main'
    else:
        return 'local'

def main():
    """主函数"""
    try:
        # 解析命令行参数
        parser = argparse.ArgumentParser(description='Telegram客户号码统计机器人')
        parser.add_argument('--force', action='store_true', help='强制启动，忽略冲突检测')
        parser.add_argument('--check-only', action='store_true', help='仅检查状态，不启动机器人')
        parser.add_argument('--wait', type=int, default=10, help='等待其他实例的最大分钟数')
        args = parser.parse_args()

        print_banner()

        # 获取Bot Token
        from dotenv import load_dotenv
        if env_file.exists():
            load_dotenv(env_file)

        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            print("❌ BOT_TOKEN 未设置")
            print("💡 请在 配置文件/环境配置.env 中设置 BOT_TOKEN")
            return 1

        # 获取启动模式
        startup_mode = get_startup_mode()
        mode_names = {
            'main': '主实例',
            'backup': '备用实例',
            'local': '本地实例'
        }
        print(f"🔧 启动模式: {mode_names.get(startup_mode, '未知')}")

        # 检查机器人状态
        print("🔍 检查机器人状态...")
        is_running, message = check_bot_running(bot_token)
        print(f"📊 状态检查: {message}")

        # 如果只是检查状态
        if args.check_only:
            if is_running:
                print("✅ 机器人正在运行中")
                return 0
            else:
                print("⏹️ 机器人未运行")
                return 1

        # 处理冲突
        if is_running and not args.force:
            if startup_mode == 'backup':
                print("🔄 备用实例检测到主实例运行，等待接管...")
                if not wait_for_slot(bot_token, args.wait):
                    print("⏹️ 主实例仍在运行，备用实例退出")
                    return 0
            elif startup_mode == 'main':
                print("⚠️ 主实例检测到冲突，等待片刻后重试...")
                time.sleep(30)

                is_running, message = check_bot_running(bot_token)
                if is_running:
                    print("❌ 仍有冲突，主实例退出")
                    return 1
            else:
                print("⚠️ 检测到其他实例正在运行")
                user_input = input("是否强制启动? (y/N): ").lower()
                if user_input != 'y':
                    print("⏹️ 用户取消启动")
                    return 0

        print("🚀 启动机器人...")
        print(f"⏰ 启动时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        # 导入并启动机器人
        from 核心模块 import main as bot_main
        return bot_main()

    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保所有文件都在正确的目录中")
        return 1
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断启动")
        return 0
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
