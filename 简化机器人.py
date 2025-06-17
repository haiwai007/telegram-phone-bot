#!/usr/bin/env python3
"""
简化版Telegram客户号码统计机器人
专为GitHub Actions部署优化
"""

import os
import sys
import logging
import sqlite3
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

# 导入Telegram相关库
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 导入环境变量库
from dotenv import load_dotenv
import pytz

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SimplePhoneBot:
    """简化版Telegram号码统计机器人"""
    
    def __init__(self):
        """初始化机器人"""
        # 加载环境变量
        self._load_config()
        
        # 初始化数据库
        self._init_database()
        
        # 设置时区
        self.timezone = pytz.timezone('Asia/Shanghai')
        
        # 号码检测正则表达式
        self.phone_pattern = re.compile(r'(?:号码|客户|电话|手机|联系方式|联系电话)[:：]?\s*([0-9\s\-\(\)\.]{8,20})')
        self.pure_number_pattern = re.compile(r'\b(\d{8,15})\b')
        
        logger.info("简化版机器人初始化完成")
    
    def _load_config(self):
        """加载配置"""
        # 尝试加载环境配置文件
        env_paths = [
            '配置文件/环境配置.env',
            '.env'
        ]
        
        for env_path in env_paths:
            if os.path.exists(env_path):
                load_dotenv(env_path)
                logger.info(f"已加载环境配置: {env_path}")
                break
        
        # 获取Bot Token
        self.bot_token = os.getenv('BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("BOT_TOKEN 未设置")
        
        logger.info("配置加载完成")
    
    def _init_database(self):
        """初始化数据库"""
        self.db_path = 'phone_records.db'
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS phone_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                username TEXT,
                user_id INTEGER NOT NULL,
                first_name TEXT,
                chat_id INTEGER NOT NULL,
                original_message TEXT,
                timestamp TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_phone_number ON phone_records(phone_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON phone_records(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON phone_records(timestamp)')
        
        conn.commit()
        conn.close()
        
        logger.info("数据库初始化完成")
    
    def _clean_phone_number(self, text: str) -> Optional[str]:
        """清理和验证号码"""
        if not text:
            return None
        
        # 移除所有非数字字符
        cleaned = re.sub(r'[^\d]', '', text)
        
        # 检查长度
        if len(cleaned) < 8 or len(cleaned) > 15:
            return None
        
        # 检查是否为无效号码
        if cleaned == '0' * len(cleaned):  # 全零
            return None
        if len(set(cleaned)) == 1:  # 重复数字
            return None
        
        return cleaned
    
    def detect_phone_number(self, text: str) -> Optional[str]:
        """检测号码"""
        if not text:
            return None
        
        # 1. 尝试关键词匹配
        keyword_match = self.phone_pattern.search(text)
        if keyword_match:
            phone = self._clean_phone_number(keyword_match.group(1))
            if phone:
                return phone
        
        # 2. 尝试纯数字匹配
        pure_matches = self.pure_number_pattern.findall(text)
        for match in pure_matches:
            phone = self._clean_phone_number(match)
            if phone:
                return phone
        
        return None
    
    def save_phone_record(self, phone_number: str, username: str, user_id: int, 
                         first_name: str, chat_id: int, original_message: str) -> bool:
        """保存号码记录"""
        try:
            # 获取当前时间
            now = datetime.now(self.timezone)
            timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO phone_records 
                (phone_number, username, user_id, first_name, chat_id, original_message, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (phone_number, username, user_id, first_name, chat_id, original_message, timestamp))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            logger.error(f"保存记录失败: {e}")
            return False
    
    def check_duplicate(self, phone_number: str) -> tuple:
        """检查重复号码"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT username, user_id, first_name, timestamp, COUNT(*) as count
                FROM phone_records 
                WHERE phone_number = ?
                ORDER BY timestamp ASC
            ''', (phone_number,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[4] > 0:  # count > 0
                return True, result
            return False, None
            
        except Exception as e:
            logger.error(f"检查重复失败: {e}")
            return False, None
    
    def get_statistics(self) -> dict:
        """获取统计信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 总记录数
            cursor.execute('SELECT COUNT(*) FROM phone_records')
            total_records = cursor.fetchone()[0]
            
            # 唯一号码数
            cursor.execute('SELECT COUNT(DISTINCT phone_number) FROM phone_records')
            unique_phones = cursor.fetchone()[0]
            
            # 今日新增
            today = datetime.now(self.timezone).strftime('%Y-%m-%d')
            cursor.execute('SELECT COUNT(*) FROM phone_records WHERE timestamp LIKE ?', (f'{today}%',))
            today_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_records': total_records,
                'unique_phones': unique_phones,
                'today_count': today_count,
                'duplicate_count': total_records - unique_phones
            }
        except Exception as e:
            logger.error(f"获取统计失败: {e}")
            return {}
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /start 命令"""
        welcome_message = """🎉 **欢迎使用客户号码统计机器人！**

🔍 **功能：**
• 🤖 自动识别和记录客户号码
• 🔄 检测重复号码提醒
• 📊 统计查询功能

📝 **支持格式：**
• 纯数字：`13812345678`
• 带关键词：`号码：138-1234-5678`

🚀 **开始使用：**
直接发送号码即可自动记录！

💡 发送 `/help` 查看更多命令"""
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        logger.info(f"用户 {update.message.from_user.id} 执行了 /start 命令")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /help 命令"""
        help_message = """📖 **使用帮助**

🔍 **号码识别：**
• 8-15位数字
• 支持关键词：号码、客户、电话、手机等

📊 **命令列表：**
• `/start` - 开始使用
• `/help` - 显示帮助
• `/stats` - 查看统计信息

✅ **示例：**
• `13812345678`
• `号码：138-1234-5678`
• `客户电话：(138) 1234.5678`"""
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
        logger.info(f"用户 {update.message.from_user.id} 执行了 /help 命令")
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理统计命令"""
        stats = self.get_statistics()
        
        if not stats:
            await update.message.reply_text("❌ 获取统计信息失败")
            return
        
        message = f"""📊 **统计信息**

📝 总记录数：{stats.get('total_records', 0)}
📱 唯一号码：{stats.get('unique_phones', 0)}
🔄 重复记录：{stats.get('duplicate_count', 0)}
📅 今日新增：{stats.get('today_count', 0)}

⏰ 更新时间：{datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S')}"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info(f"用户 {update.message.from_user.id} 查看了统计信息")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理普通消息"""
        try:
            message = update.message
            if not message or not message.text:
                return
            
            user = message.from_user
            chat = message.chat
            
            # 检测号码
            phone_number = self.detect_phone_number(message.text)
            
            if phone_number:
                # 检查重复
                is_duplicate, duplicate_info = self.check_duplicate(phone_number)
                
                # 保存记录
                success = self.save_phone_record(
                    phone_number, 
                    user.username, 
                    user.id, 
                    user.first_name or "未知用户",
                    chat.id, 
                    message.text
                )
                
                if success:
                    if is_duplicate and duplicate_info:
                        # 重复号码提醒
                        reply_message = f"""⚠️ **号码重复提示！**

📱 号码：`{phone_number}`
👤 本次提交：{user.first_name or '未知用户'}
📅 首次记录：{duplicate_info[3]} 由 {duplicate_info[2] or '未知用户'} 提交
📊 总提交次数：{duplicate_info[4] + 1} 次"""
                    else:
                        # 新号码记录
                        reply_message = f"""✅ **号码记录成功！**

📱 号码：`{phone_number}`
👤 提交人：{user.first_name or '未知用户'}
⏰ 记录时间：{datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S')}"""
                    
                    await message.reply_text(reply_message, parse_mode='Markdown')
                    
                    # 记录日志
                    status = "重复" if is_duplicate else "新增"
                    logger.info(f"号码{status}: {phone_number}, 用户: {user.first_name}({user.id})")
                else:
                    await message.reply_text("❌ 记录保存失败，请稍后重试")
            
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            await message.reply_text("❌ 处理失败，请稍后重试")
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """错误处理器"""
        logger.error(f"更新 {update} 引起错误: {context.error}")
    
    def run(self):
        """运行机器人"""
        try:
            logger.info("启动简化版Telegram机器人...")
            
            # 创建应用
            application = Application.builder().token(self.bot_token).build()
            
            # 添加处理器
            application.add_handler(CommandHandler("start", self.start_command))
            application.add_handler(CommandHandler("help", self.help_command))
            application.add_handler(CommandHandler("stats", self.stats_command))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            application.add_error_handler(self.error_handler)
            
            # 运行机器人
            application.run_polling(
                allowed_updates=["message"],
                drop_pending_updates=True,
                poll_interval=1.0,
                timeout=10
            )
            
        except KeyboardInterrupt:
            logger.info("收到停止信号，正在关闭机器人...")
        except Exception as e:
            logger.error(f"机器人运行失败: {e}")
            raise

def main():
    """主函数"""
    try:
        bot = SimplePhoneBot()
        bot.run()
        return 0
    except Exception as e:
        logger.error(f"启动失败: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
