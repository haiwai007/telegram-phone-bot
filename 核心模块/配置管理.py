"""
配置管理模块
管理机器人的所有配置参数和环境变量
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_file = os.environ.get('ENV_FILE_PATH')
if env_file and os.path.exists(env_file):
    load_dotenv(env_file)
else:
    # 尝试从配置文件目录加载
    config_dir = Path(__file__).parent.parent / "配置文件"
    env_file = config_dir / "环境配置.env"
    if env_file.exists():
        load_dotenv(env_file)
    else:
        load_dotenv()  # 默认加载

class Config:
    """机器人配置类"""
    
    # Telegram Bot配置
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # 数据库配置
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'phone_records.db')
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'bot.log')
    
    # 时区配置
    TIMEZONE = os.getenv('TIMEZONE', 'Asia/Shanghai')
    
    # 号码验证配置
    MAX_PHONE_LENGTH = int(os.getenv('MAX_PHONE_LENGTH', 15))
    MIN_PHONE_LENGTH = int(os.getenv('MIN_PHONE_LENGTH', 8))
    
    # 速率限制配置
    RATE_LIMIT_MESSAGES = int(os.getenv('RATE_LIMIT_MESSAGES', 10))
    RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', 60))
    
    # 授权群组配置
    AUTHORIZED_GROUPS = os.getenv('AUTHORIZED_GROUPS', '').split(',') if os.getenv('AUTHORIZED_GROUPS') else []
    
    # 号码检测关键词
    PHONE_KEYWORDS = [
        '号码：', '号码:', '客户：', '客户:', 
        '电话：', '电话:', '手机：', '手机:',
        '联系方式：', '联系方式:', '联系电话：', '联系电话:'
    ]
    
    @classmethod
    def validate_config(cls):
        """验证配置的有效性"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN 环境变量未设置")
        
        if cls.MIN_PHONE_LENGTH >= cls.MAX_PHONE_LENGTH:
            raise ValueError("MIN_PHONE_LENGTH 必须小于 MAX_PHONE_LENGTH")
        
        return True

# 设置日志配置
def setup_logging():
    """设置日志配置"""
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    
    # 创建日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 设置根日志器
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # 清除现有的处理器
    logger.handlers.clear()
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 添加文件处理器
    if Config.LOG_FILE:
        file_handler = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
