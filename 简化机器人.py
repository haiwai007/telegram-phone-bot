#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Telegram客户号码统计机器人 - 简化版
基于成功测试环境的快速部署版本
"""

import os
import re
import json
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Set
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# 加载环境变量
load_dotenv('配置文件/环境配置.env')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimplePhoneBot:
    """简化版电话号码统计机器人"""
    
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("❌ BOT_TOKEN 未设置")
            
        # 简单的内存存储
        self.phone_records: Dict[str, List[Dict]] = {}
        self.user_stats: Dict[int, Dict] = {}
        
        # 中国时区
        self.tz = timezone(timedelta(hours=8))
        
        logger.info("🤖 简化版机器人初始化完成")
    
    def is_valid_phone(self, text: str) -> bool:
        """验证是否为有效手机号"""
        # 移除所有非数字字符
        phone = re.sub(r'\D', '', text)
        
        # 中国手机号规则：11位，1开头
        if len(phone) == 11 and phone.startswith('1'):
            return True
        
        # 国际号码：8-15位数字
        if 8 <= len(phone) <= 15:
            return True
            
        return False
    
    def extract_phones(self, text: str) -> List[str]:
        """从文本中提取手机号"""
        # 匹配各种手机号格式
        patterns = [
            r'1[3-9]\d{9}',  # 中国手机号
            r'\+?\d{1,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}',  # 国际格式
            r'\d{8,15}'  # 简单数字串
        ]
        
        phones = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                clean_phone = re.sub(r'\D', '', match)
                if self.is_valid_phone(clean_phone):
                    phones.append(clean_phone)
        
        return list(set(phones))  # 去重
    
    def save_phone_record(self, user_id: int, username: str, phones: List[str]):
        """保存手机号记录"""
        user_key = str(user_id)
        current_time = datetime.now(self.tz).isoformat()
        
        if user_key not in self.phone_records:
            self.phone_records[user_key] = []
        
        # 添加记录
        record = {
            'timestamp': current_time,
            'username': username,
            'phones': phones,
            'count': len(phones)
        }
        
        self.phone_records[user_key].append(record)
        
        # 更新用户统计
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {
                'username': username,
                'total_messages': 0,
                'total_phones': 0,
                'unique_phones': set(),
                'first_seen': current_time
            }
        
        stats = self.user_stats[user_id]
        stats['total_messages'] += 1
        stats['total_phones'] += len(phones)
        stats['unique_phones'].update(phones)
        stats['last_seen'] = current_time
        
        logger.info(f"📱 用户 {username}({user_id}) 提交了 {len(phones)} 个号码")
    
    def get_user_stats(self, user_id: int) -> Dict:
        """获取用户统计信息"""
        if user_id not in self.user_stats:
            return None
        
        stats = self.user_stats[user_id].copy()
        stats['unique_phones'] = len(stats['unique_phones'])
        return stats
    
    def get_global_stats(self) -> Dict:
        """获取全局统计信息"""
        total_users = len(self.user_stats)
        total_messages = sum(stats['total_messages'] for stats in self.user_stats.values())
        total_phones = sum(stats['total_phones'] for stats in self.user_stats.values())
        
        all_unique_phones = set()
        for stats in self.user_stats.values():
            all_unique_phones.update(stats['unique_phones'])
        
        return {
            'total_users': total_users,
            'total_messages': total_messages,
            'total_phones': total_phones,
            'unique_phones': len(all_unique_phones),
            'duplicate_count': total_phones - len(all_unique_phones)
        }

# 创建机器人实例
bot = SimplePhoneBot()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """开始命令"""
    welcome_text = """
🤖 **Telegram客户号码统计机器人** - 简化版

📱 **功能说明：**
• 自动识别并统计消息中的手机号码
• 支持中国和国际号码格式
• 实时统计和数据分析

📋 **使用方法：**
• 直接发送包含手机号的消息
• 使用 /stats 查看个人统计
• 使用 /global 查看全局统计

🚀 **开始使用：**
发送任何包含手机号的消息即可开始统计！
    """
    
    keyboard = [
        [InlineKeyboardButton("📊 个人统计", callback_data="user_stats")],
        [InlineKeyboardButton("🌍 全局统计", callback_data="global_stats")],
        [InlineKeyboardButton("❓ 帮助", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理普通消息"""
    user = update.effective_user
    message_text = update.message.text
    
    if not message_text:
        return
    
    # 提取手机号
    phones = bot.extract_phones(message_text)
    
    if phones:
        # 保存记录
        bot.save_phone_record(user.id, user.username or user.first_name, phones)
        
        # 回复确认
        response = f"✅ **检测到 {len(phones)} 个手机号码**\n\n"
        for i, phone in enumerate(phones[:5], 1):  # 最多显示5个
            response += f"📱 {i}. `{phone}`\n"
        
        if len(phones) > 5:
            response += f"... 还有 {len(phones) - 5} 个号码\n"
        
        response += f"\n📊 使用 /stats 查看统计信息"
        
        await update.message.reply_text(response, parse_mode='Markdown')
    else:
        await update.message.reply_text("🔍 未检测到有效的手机号码")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """个人统计命令"""
    user_id = update.effective_user.id
    stats = bot.get_user_stats(user_id)
    
    if not stats:
        await update.message.reply_text("📊 您还没有提交过任何手机号码")
        return
    
    response = f"""
📊 **个人统计信息**

👤 **用户：** {stats['username']}
📨 **提交消息数：** {stats['total_messages']}
📱 **总号码数：** {stats['total_phones']}
🔢 **唯一号码数：** {stats['unique_phones']}
🔄 **重复号码数：** {stats['total_phones'] - stats['unique_phones']}
⏰ **首次使用：** {stats['first_seen'][:19]}
🕐 **最后使用：** {stats['last_seen'][:19]}
    """
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def global_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """全局统计命令"""
    stats = bot.get_global_stats()
    
    response = f"""
🌍 **全局统计信息**

👥 **总用户数：** {stats['total_users']}
📨 **总消息数：** {stats['total_messages']}
📱 **总号码数：** {stats['total_phones']}
🔢 **唯一号码数：** {stats['unique_phones']}
🔄 **重复号码数：** {stats['duplicate_count']}
📈 **去重率：** {(stats['unique_phones']/stats['total_phones']*100):.1f}% (如果有数据)

⏰ **统计时间：** {datetime.now(bot.tz).strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理按钮回调"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "user_stats":
        await stats_command(update, context)
    elif query.data == "global_stats":
        await global_command(update, context)
    elif query.data == "help":
        await start_command(update, context)

async def main():
    """主函数"""
    logger.info("🚀 启动简化版Telegram机器人...")
    
    # 创建应用
    application = Application.builder().token(bot.bot_token).build()
    
    # 添加处理器
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("global", global_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ 机器人启动成功，开始轮询...")
    
    # 启动机器人
    await application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 机器人已停止")
    except Exception as e:
        logger.error(f"❌ 机器人运行错误: {e}")
        raise
