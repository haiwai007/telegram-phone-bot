#!/usr/bin/env python3
"""
Telegram客户号码统计机器人启动脚本
"""

import sys
import os
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

def main():
    """主函数"""
    try:
        print("🤖 启动Telegram客户号码统计机器人")
        print("=" * 50)
        
        # 导入机器人主程序
        from 核心模块 import main as bot_main
        
        # 启动机器人
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
