#!/usr/bin/env python3
"""
机器人启动脚本
提供更好的启动体验和错误处理
"""

import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_requirements():
    """检查必要的依赖和配置"""
    try:
        # 检查Python版本
        if sys.version_info < (3, 8):
            print("❌ 错误: 需要Python 3.8或更高版本")
            return False
        
        # 检查必要的包
        required_packages = [
            'telegram',
            'python-dotenv',
            'pytz'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ 错误: 缺少必要的包: {', '.join(missing_packages)}")
            print("请运行: pip install -r requirements.txt")
            return False
        
        # 检查配置文件
        env_file = project_root / '.env'
        if not env_file.exists():
            print("❌ 错误: 未找到 .env 配置文件")
            print("请复制 .env.example 为 .env 并配置Bot Token")
            return False
        
        # 检查Bot Token
        from dotenv import load_dotenv
        load_dotenv()
        
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            print("❌ 错误: 未设置 BOT_TOKEN")
            print("请在 .env 文件中设置您的Telegram Bot Token")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 检查环境时发生错误: {e}")
        return False

def main():
    """主函数"""
    print("🤖 Telegram客户号码统计机器人")
    print("=" * 40)
    
    # 检查环境
    print("🔍 检查运行环境...")
    if not check_requirements():
        return 1
    
    print("✅ 环境检查通过")
    
    try:
        # 导入并启动机器人
        print("🚀 正在启动机器人...")
        from bot import main as bot_main
        return bot_main()
        
    except KeyboardInterrupt:
        print("\n👋 机器人已停止")
        return 0
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        logging.exception("启动机器人时发生异常")
        return 1

if __name__ == "__main__":
    exit(main())
