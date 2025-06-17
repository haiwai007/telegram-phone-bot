#!/usr/bin/env python3
"""
机器人监控脚本
监控机器人状态并自动重启
"""

import os
import sys
import time
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class BotMonitor:
    """机器人监控器"""
    
    def __init__(self):
        self.bot_script = Path(__file__).parent / "bot.py"
        self.python_exe = sys.executable
        self.process = None
        self.restart_count = 0
        self.max_restarts = 10  # 最大重启次数
        self.restart_delay = 5  # 重启延迟(秒)
        
    def start_bot(self):
        """启动机器人"""
        try:
            logger.info("🚀 启动机器人...")
            self.process = subprocess.Popen(
                [self.python_exe, str(self.bot_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            logger.info(f"✅ 机器人已启动 (PID: {self.process.pid})")
            return True
        except Exception as e:
            logger.error(f"❌ 启动机器人失败: {e}")
            return False
    
    def is_bot_running(self):
        """检查机器人是否运行"""
        if self.process is None:
            return False
        
        poll = self.process.poll()
        return poll is None
    
    def stop_bot(self):
        """停止机器人"""
        if self.process and self.is_bot_running():
            logger.info("🛑 停止机器人...")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning("强制终止机器人...")
                self.process.kill()
            self.process = None
    
    def restart_bot(self):
        """重启机器人"""
        logger.info("🔄 重启机器人...")
        self.stop_bot()
        time.sleep(self.restart_delay)
        
        if self.start_bot():
            self.restart_count += 1
            logger.info(f"✅ 机器人重启成功 (第{self.restart_count}次)")
            return True
        else:
            logger.error("❌ 机器人重启失败")
            return False
    
    def monitor(self):
        """监控循环"""
        logger.info("🔍 开始监控机器人...")
        
        # 首次启动
        if not self.start_bot():
            logger.error("❌ 初始启动失败")
            return
        
        try:
            while True:
                time.sleep(30)  # 每30秒检查一次
                
                if not self.is_bot_running():
                    exit_code = self.process.returncode if self.process else None
                    logger.warning(f"⚠️  机器人已停止 (退出代码: {exit_code})")
                    
                    if self.restart_count >= self.max_restarts:
                        logger.error(f"❌ 达到最大重启次数 ({self.max_restarts})")
                        break
                    
                    if not self.restart_bot():
                        logger.error("❌ 重启失败，停止监控")
                        break
                else:
                    logger.debug("✅ 机器人运行正常")
                    
        except KeyboardInterrupt:
            logger.info("👋 收到停止信号")
        except Exception as e:
            logger.error(f"💥 监控异常: {e}")
        finally:
            self.stop_bot()
            logger.info("🏁 监控结束")

def main():
    """主函数"""
    print("🤖 Telegram 机器人监控器")
    print("=" * 30)
    
    # 检查环境
    if not Path(".env").exists():
        print("❌ 未找到 .env 配置文件")
        return 1
    
    # 启动监控
    monitor = BotMonitor()
    monitor.monitor()
    
    return 0

if __name__ == "__main__":
    exit(main())
