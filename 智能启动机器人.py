#!/usr/bin/env python3
"""
智能启动Telegram机器人
检测是否已有实例运行，避免冲突
"""

import sys
import os
import time
import requests
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

def check_bot_running(bot_token):
    """检查机器人是否已经在运行"""
    try:
        response = requests.get(
            f'https://api.telegram.org/bot{bot_token}/getUpdates',
            params={'timeout': 1, 'limit': 1},
            timeout=5
        )
        
        if response.status_code == 409:
            return True
        elif response.status_code == 200:
            return False
        else:
            print(f"⚠️ API返回异常状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️ 检查机器人状态失败: {e}")
        return False

def wait_for_slot(bot_token, max_wait_minutes=10):
    """等待机器人实例空闲"""
    print(f"⏳ 检测到其他实例正在运行，等待空闲...")
    
    for i in range(max_wait_minutes):
        if not check_bot_running(bot_token):
            print(f"✅ 检测到空闲，可以启动机器人")
            return True
        
        print(f"⏳ 等待中... ({i+1}/{max_wait_minutes} 分钟)")
        time.sleep(60)
    
    print(f"⚠️ 等待超时，其他实例可能长期运行")
    return False

def main():
    """主函数"""
    try:
        print("🤖 智能启动Telegram客户号码统计机器人")
        print("=" * 50)
        
        # 获取Bot Token
        from dotenv import load_dotenv
        if env_file.exists():
            load_dotenv(env_file)
        
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            print("❌ BOT_TOKEN 未设置")
            return 1
        
        # 检查是否已有实例运行
        print("🔍 检查是否已有机器人实例运行...")
        
        if check_bot_running(bot_token):
            print("⚠️ 检测到其他机器人实例正在运行")
            
            # 判断是否为备用实例启动
            is_backup = os.getenv('GITHUB_WORKFLOW', '').find('keep-alive') != -1
            
            if is_backup:
                print("🔄 这是备用实例，等待主实例结束...")
                if not wait_for_slot(bot_token, max_wait_minutes=15):
                    print("⏹️ 主实例仍在运行，备用实例退出")
                    return 0
            else:
                print("⏹️ 主实例检测到冲突，等待片刻后重试...")
                time.sleep(30)
                
                if check_bot_running(bot_token):
                    print("❌ 仍有冲突，主实例退出")
                    return 1
        
        print("🚀 启动机器人...")
        
        # 导入并启动机器人
        from 核心模块 import main as bot_main
        return bot_main()
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保所有文件都在正确的目录中")
        return 1
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
