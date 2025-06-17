"""
Telegram机器人主程序
处理消息、命令和用户交互
"""

import logging
import os
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional
import pytz

from telegram import Update, Message
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, CallbackContext
)

from 配置管理 import Config, setup_logging
from 数据库管理 import DatabaseManager
from 号码检测器 import PhoneDetector
from 通知系统 import NotificationSystem
from 导出管理器 import ExportManager

# 设置日志
logger = setup_logging()

class TelegramPhoneBot:
    """Telegram号码统计机器人

    功能特性:
    - 智能号码检测和记录
    - 重复号码提醒
    - 统计查询和数据导出
    - 速率限制和权限控制
    """

    def __init__(self):
        """初始化机器人"""
        try:
            # 验证配置
            Config.validate_config()
            logger.info("配置验证通过")

            # 初始化核心组件
            self.db_manager = DatabaseManager()
            self.phone_detector = PhoneDetector()
            self.notification_system = NotificationSystem(self.db_manager)
            self.export_manager = ExportManager()
            self.timezone = pytz.timezone(Config.TIMEZONE)

            # 初始化控制组件
            self.rate_limiter = defaultdict(list)
            self.authorized_groups: Optional[set] = None
            if Config.AUTHORIZED_GROUPS and Config.AUTHORIZED_GROUPS[0]:
                self.authorized_groups = set(map(int, Config.AUTHORIZED_GROUPS))
                logger.info(f"已配置授权群组: {self.authorized_groups}")

            # 创建Telegram应用
            self.application = Application.builder().token(Config.BOT_TOKEN).build()
            self._setup_handlers()

            logger.info("机器人初始化完成")

        except Exception as e:
            logger.error(f"机器人初始化失败: {e}")
            raise
    
    def _setup_handlers(self):
        """设置消息和命令处理器"""
        try:
            # 基础命令处理器
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))

            # 查询命令处理器
            self.application.add_handler(CommandHandler(["stats", "statistics"], self.statistics_command))
            self.application.add_handler(CommandHandler("detail", self.detail_command))
            self.application.add_handler(CommandHandler("search", self.search_command))
            self.application.add_handler(CommandHandler("user", self.user_command))
            self.application.add_handler(CommandHandler("recent", self.recent_command))

            # 导出命令处理器
            self.application.add_handler(CommandHandler("export", self.export_command))
            self.application.add_handler(CommandHandler("report", self.report_command))

            # 管理命令处理器 (如果存在这些方法)
            if hasattr(self, 'cleanup_command'):
                self.application.add_handler(CommandHandler("cleanup", self.cleanup_command))
            if hasattr(self, 'status_command'):
                self.application.add_handler(CommandHandler("status", self.status_command))

            # 消息处理器（只处理文本消息）
            self.application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
            )

            # 错误处理器
            self.application.add_error_handler(self.error_handler)

            logger.info("命令处理器设置完成")

        except Exception as e:
            logger.error(f"设置处理器失败: {e}")
            raise
    
    def _is_authorized_group(self, chat_id: int) -> bool:
        """检查是否为授权群组

        Args:
            chat_id: 群组ID

        Returns:
            bool: 是否为授权群组
        """
        if self.authorized_groups is None:
            return True  # 如果没有设置授权群组，允许所有群组
        return chat_id in self.authorized_groups

    def _check_rate_limit(self, user_id: int) -> bool:
        """检查用户是否超过速率限制

        Args:
            user_id: 用户ID

        Returns:
            bool: 是否通过速率检查
        """
        try:
            now = datetime.now()
            user_messages = self.rate_limiter[user_id]

            # 清理过期的消息记录
            cutoff_time = now - timedelta(seconds=Config.RATE_LIMIT_WINDOW)
            user_messages[:] = [msg_time for msg_time in user_messages if msg_time > cutoff_time]

            # 检查是否超过限制
            if len(user_messages) >= Config.RATE_LIMIT_MESSAGES:
                logger.warning(f"用户 {user_id} 触发速率限制")
                return False

            # 记录当前消息
            user_messages.append(now)
            return True

        except Exception as e:
            logger.error(f"检查速率限制失败: {e}")
            return True  # 出错时允许通过
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /start 命令"""
        try:
            welcome_message = """🎉 **欢迎使用客户号码统计机器人！**

🔍 **核心功能：**
• 🤖 智能识别和记录客户号码
• 🔄 实时检测重复号码提醒
• 📊 提供详细统计和查询功能
• 📁 支持数据导出和报告生成

📝 **支持的号码格式：**
• 纯数字：`13812345678`
• 带关键词：`号码：138-1234-5678`
• 支持关键词：号码、客户、电话、手机、联系方式等

🚀 **快速开始：**
直接发送号码即可自动记录！

💡 发送 `/help` 查看完整命令列表"""

            await update.message.reply_text(welcome_message, parse_mode='Markdown')
            logger.info(f"用户 {update.message.from_user.id} 执行了 /start 命令")

        except Exception as e:
            logger.error(f"处理 /start 命令失败: {e}")
            await self._send_error_message(update.message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /help 命令"""
        try:
            help_message = """📖 **使用帮助**

🔍 **号码识别规则：**
• 8-15位纯数字
• 支持关键词：号码、客户、电话、手机等
• 自动清理格式（空格、连字符等）

📊 **命令列表：**
• `/stats` `/statistics` - 查看统计信息
• `/detail [号码]` - 查看特定号码的提交历史
• `/search [关键词]` - 搜索号码或用户
• `/user [用户名]` - 查看用户提交记录
• `/recent [数量]` - 查看最近提交记录
• `/export [格式]` - 导出数据 (csv/json/txt)
• `/report` - 生成汇总报告
• `/help` - 显示此帮助信息

✅ **成功示例：**
• `13812345678`
• `号码：138-1234-5678`
• `客户电话：(138) 1234.5678`

❌ **无效示例：**
• `1234567` (太短)
• `00000000` (全零)
• `11111111` (重复数字)

💡 **提示：** 机器人会自动记录所有有效号码并检测重复提交。"""

            await update.message.reply_text(help_message, parse_mode='Markdown')
            logger.info(f"用户 {update.message.from_user.id} 执行了 /help 命令")

        except Exception as e:
            logger.error(f"处理 /help 命令失败: {e}")
            await self._send_error_message(update.message)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理普通消息"""
        try:
            message = update.message
            if not message or not message.text:
                return

            user = message.from_user
            chat = message.chat

            # 检查是否为授权群组
            if not self._is_authorized_group(chat.id):
                logger.warning(f"未授权群组尝试使用机器人: {chat.id} (群组名: {chat.title})")
                return

            # 检查速率限制
            if not self._check_rate_limit(user.id):
                await message.reply_text("⚠️ 发送消息过于频繁，请稍后再试。")
                return

            # 检测号码
            phone_number = self.phone_detector.detect_phone_number(message.text)

            if phone_number:
                # 处理号码提交
                await self._process_phone_submission(message, phone_number)
            else:
                # 记录非号码消息（调试用）
                logger.debug(f"未检测到号码的消息: {message.text[:50]}...")

        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            await self._send_error_message(update.message)
    
    async def _process_phone_submission(self, message: Message, phone_number: str):
        """处理号码提交

        Args:
            message: Telegram消息对象
            phone_number: 检测到的号码
        """
        try:
            user = message.from_user
            chat = message.chat

            # 获取用户信息
            username = user.username
            first_name = user.first_name or "未知用户"
            user_id = user.id

            # 处理提交并获取通知消息
            notification_message, is_duplicate = self.notification_system.process_phone_submission(
                phone_number, username, user_id, first_name, chat.id, message.text
            )

            # 发送通知
            await message.reply_text(notification_message, parse_mode='Markdown')

            # 记录详细日志
            status = "重复" if is_duplicate else "新增"
            group_name = chat.title or f"群组{chat.id}"
            logger.info(
                f"号码{status}: {phone_number}, "
                f"用户: {first_name}({user_id}), "
                f"群组: {group_name}({chat.id})"
            )

        except Exception as e:
            logger.error(f"处理号码提交失败: {e}")
            await self._send_error_message(message)

    async def statistics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理统计命令"""
        try:
            # 检查是否为授权群组
            if not self._is_authorized_group(update.message.chat.id):
                logger.warning(f"未授权群组尝试查看统计: {update.message.chat.id}")
                return

            # 发送处理中消息
            processing_msg = await update.message.reply_text("📊 正在生成统计信息...")

            # 获取统计信息
            stats = self.db_manager.get_statistics()

            # 格式化并发送消息
            message = self.notification_system.format_statistics_message(stats)
            await processing_msg.edit_text(message, parse_mode='Markdown')

            logger.info(f"用户 {update.message.from_user.id} 查看了统计信息")

        except Exception as e:
            logger.error(f"处理统计命令失败: {e}")
            await self._send_error_message(update.message)

    async def detail_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理详情查询命令"""
        try:
            # 检查是否为授权群组
            if not self._is_authorized_group(update.message.chat.id):
                return

            # 获取号码参数
            if not context.args:
                await update.message.reply_text(
                    "❌ 请提供要查询的号码\n💡 使用方法: `/详情 13812345678`",
                    parse_mode='Markdown'
                )
                return

            phone_number = context.args[0].strip()

            # 清理号码格式
            cleaned_phone = self.phone_detector._clean_number(phone_number)
            if not cleaned_phone:
                await update.message.reply_text("❌ 无效的号码格式")
                return

            # 获取号码历史
            history = self.db_manager.get_phone_history(cleaned_phone)

            # 格式化并发送消息
            message = self.notification_system.format_phone_detail_message(cleaned_phone, history)
            await update.message.reply_text(message, parse_mode='Markdown')

            logger.info(f"用户 {update.message.from_user.id} 查询了号码 {cleaned_phone} 的详情")

        except Exception as e:
            logger.error(f"处理详情命令失败: {e}")
            await self._send_error_message(update.message)

    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理搜索命令"""
        try:
            # 检查是否为授权群组
            if not self._is_authorized_group(update.message.chat.id):
                return

            # 获取搜索参数
            if not context.args:
                await update.message.reply_text(
                    "❌ 请提供搜索关键词\n💡 使用方法: `/搜索 138` 或 `/搜索 张三`",
                    parse_mode='Markdown'
                )
                return

            search_term = ' '.join(context.args).strip()

            # 搜索号码和用户
            results = self.db_manager.search_records(search_term)

            if not results:
                await update.message.reply_text(
                    f"� 未找到包含 `{search_term}` 的记录",
                    parse_mode='Markdown'
                )
                return

            # 格式化搜索结果
            message = self.notification_system.format_search_results(search_term, results)
            await update.message.reply_text(message, parse_mode='Markdown')

            logger.info(f"用户 {update.message.from_user.id} 搜索了: {search_term}")

        except Exception as e:
            logger.error(f"处理搜索命令失败: {e}")
            await self._send_error_message(update.message)

    async def user_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理用户查询命令"""
        try:
            # 检查是否为授权群组
            if not self._is_authorized_group(update.message.chat.id):
                return

            # 获取用户参数
            if not context.args:
                await update.message.reply_text(
                    "❌ 请提供用户名或用户ID\n💡 使用方法: `/用户 张三` 或 `/用户 123456789`",
                    parse_mode='Markdown'
                )
                return

            user_identifier = ' '.join(context.args).strip()

            # 查询用户记录
            user_records = self.db_manager.get_user_records(user_identifier)

            if not user_records:
                await update.message.reply_text(
                    f"� 未找到用户 `{user_identifier}` 的记录",
                    parse_mode='Markdown'
                )
                return

            # 格式化用户记录
            message = self.notification_system.format_user_records(user_identifier, user_records)
            await update.message.reply_text(message, parse_mode='Markdown')

            logger.info(f"用户 {update.message.from_user.id} 查询了用户: {user_identifier}")

        except Exception as e:
            logger.error(f"处理用户命令失败: {e}")
            await self._send_error_message(update.message)

    async def recent_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理最近记录命令"""
        try:
            # 检查是否为授权群组
            if not self._is_authorized_group(update.message.chat.id):
                return

            # 获取数量参数，默认10条
            limit = 10
            if context.args:
                try:
                    limit = int(context.args[0])
                    if limit <= 0 or limit > 50:
                        limit = 10
                except ValueError:
                    limit = 10

            # 获取最近记录
            recent_records = self.db_manager.get_recent_records(limit)

            if not recent_records:
                await update.message.reply_text("📝 暂无记录")
                return

            # 格式化最近记录
            message = self.notification_system.format_recent_records(recent_records, limit)
            await update.message.reply_text(message, parse_mode='Markdown')

            logger.info(f"用户 {update.message.from_user.id} 查看了最近 {limit} 条记录")

        except Exception as e:
            logger.error(f"处理最近记录命令失败: {e}")
            await self._send_error_message(update.message)

    async def export_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理导出命令"""
        try:
            # 检查是否为授权群组
            if not self._is_authorized_group(update.message.chat.id):
                return

            # 发送处理中消息
            processing_msg = await update.message.reply_text("📊 正在生成导出文件，请稍候...")

            # 获取导出格式参数
            export_format = 'csv'  # 默认CSV格式
            if context.args and context.args[0].lower() in ['csv', 'json', 'txt']:
                export_format = context.args[0].lower()

            # 获取所有记录
            all_records = self.db_manager.get_all_records()

            if not all_records:
                await processing_msg.edit_text("📝 暂无数据可导出")
                return

            # 根据格式导出
            try:
                if export_format == 'csv':
                    filepath = self.export_manager.export_to_csv(all_records)
                elif export_format == 'json':
                    filepath = self.export_manager.export_to_json(all_records)
                else:  # txt
                    filepath = self.export_manager.export_to_text(all_records)

                # 发送文件
                with open(filepath, 'rb') as file:
                    await update.message.reply_document(
                        document=file,
                        filename=os.path.basename(filepath),
                        caption=f"📊 数据导出完成\n📁 格式: {export_format.upper()}\n📝 记录数: {len(all_records)}"
                    )

                # 删除处理中消息
                await processing_msg.delete()

                # 清理临时文件
                try:
                    os.remove(filepath)
                except:
                    pass

                logger.info(f"用户 {update.message.from_user.id} 导出了 {export_format} 格式数据")

            except Exception as e:
                await processing_msg.edit_text(f"❌ 导出失败: {str(e)}")
                raise

        except Exception as e:
            logger.error(f"处理导出命令失败: {e}")
            await self._send_error_message(update.message)

    async def report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理报告命令"""
        try:
            # 检查是否为授权群组
            if not self._is_authorized_group(update.message.chat.id):
                return

            # 发送处理中消息
            processing_msg = await update.message.reply_text("📊 正在生成汇总报告，请稍候...")

            # 获取所有记录
            all_records = self.db_manager.get_all_records()

            if not all_records:
                await processing_msg.edit_text("📝 暂无数据可生成报告")
                return

            try:
                # 生成汇总报告
                filepath = self.export_manager.generate_summary_report(all_records)

                # 发送文件
                with open(filepath, 'rb') as file:
                    await update.message.reply_document(
                        document=file,
                        filename=os.path.basename(filepath),
                        caption=f"📊 汇总报告生成完成\n📝 记录数: {len(all_records)}"
                    )

                # 删除处理中消息
                await processing_msg.delete()

                # 清理临时文件
                try:
                    os.remove(filepath)
                except:
                    pass

                logger.info(f"用户 {update.message.from_user.id} 生成了汇总报告")

            except Exception as e:
                await processing_msg.edit_text(f"❌ 报告生成失败: {str(e)}")
                raise

        except Exception as e:
            logger.error(f"处理报告命令失败: {e}")
            await self._send_error_message(update.message)

    async def _send_error_message(self, message: Message):
        """发送错误消息

        Args:
            message: 要回复的消息对象
        """
        try:
            await message.reply_text(
                "❌ 处理请求时发生错误，请稍后重试。\n"
                "如果问题持续存在，请联系管理员。"
            )
        except Exception as e:
            logger.error(f"发送错误消息失败: {e}")

    async def error_handler(self, update: object, context: CallbackContext):
        """全局错误处理器

        Args:
            update: Telegram更新对象
            context: 回调上下文
        """
        error_msg = f"更新 {update} 引发错误: {context.error}"
        logger.error(error_msg)

        # 如果是更新对象且有消息，尝试发送错误提示
        if isinstance(update, Update) and update.message:
            try:
                await update.message.reply_text(
                    "❌ 系统发生错误，请稍后重试。"
                )
            except Exception as e:
                logger.error(f"发送错误提示失败: {e}")

    def run(self):
        """启动机器人"""
        try:
            logger.info("正在启动Telegram机器人...")
            logger.info(f"授权群组: {self.authorized_groups or '所有群组'}")

            self.application.run_polling(
                allowed_updates=["message", "callback_query"],
                drop_pending_updates=True,
                poll_interval=1.0,
                timeout=10
            )
        except KeyboardInterrupt:
            logger.info("收到停止信号，正在关闭机器人...")
        except Exception as e:
            logger.error(f"机器人运行失败: {e}")
            raise
        finally:
            self._cleanup()

    def _cleanup(self):
        """清理资源"""
        try:
            if hasattr(self, 'db_manager'):
                self.db_manager.close_connection()
            logger.info("机器人资源清理完成")
        except Exception as e:
            logger.error(f"清理资源失败: {e}")

def main():
    """主函数

    Returns:
        int: 退出代码，0表示成功，1表示失败
    """
    try:
        logger.info("=" * 50)
        logger.info("Telegram客户号码统计机器人启动中...")
        logger.info("=" * 50)

        # 创建并运行机器人
        bot = TelegramPhoneBot()
        bot.run()

        return 0

    except KeyboardInterrupt:
        logger.info("用户中断，机器人停止")
        return 0
    except Exception as e:
        logger.error(f"启动机器人失败: {e}")
        logger.exception("详细错误信息:")
        return 1

if __name__ == "__main__":
    exit(main())
