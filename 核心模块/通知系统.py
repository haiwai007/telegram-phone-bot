"""
通知系统模块
处理成功记录和重复提醒的消息格式化
"""

import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
import pytz
from .配置管理 import Config
from .数据库管理 import DatabaseManager

logger = logging.getLogger(__name__)

class NotificationSystem:
    """通知系统"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.timezone = pytz.timezone(Config.TIMEZONE)
    
    def format_success_message(self, phone_number: str, first_name: str,
                             username: str, timestamp: datetime) -> str:
        """格式化成功记录消息"""
        # 确保时间戳是本地时区
        if timestamp.tzinfo is None:
            timestamp = self.timezone.localize(timestamp)
        elif timestamp.tzinfo != self.timezone:
            timestamp = timestamp.astimezone(self.timezone)

        formatted_time = timestamp.strftime('%m-%d %H:%M:%S')
        username_display = f"@{username}" if username else "👤"

        # 美化的成功消息
        message = f"""🎉 **号码记录成功！**

📱 **号码：** `{phone_number}`
👤 **提交人：** {first_name} {username_display}
⏰ **时间：** {formatted_time}

💡 *已自动保存到数据库*"""

        return message
    
    def format_duplicate_message(self, phone_number: str, current_submitter: Dict,
                               first_submitter: Dict, last_submitter: Optional[Dict],
                               submission_count: int) -> str:
        """格式化重复号码提醒消息"""

        # 格式化当前提交者信息
        current_username = f"@{current_submitter['username']}" if current_submitter['username'] else "👤"

        # 格式化首次提交者信息
        first_username = f"@{first_submitter['username']}" if first_submitter['username'] else "👤"
        first_time = self._format_timestamp(first_submitter['timestamp'])

        # 选择合适的警告图标
        warning_icon = "🔄" if submission_count <= 3 else "⚠️" if submission_count <= 5 else "🚨"

        message = f"""{warning_icon} **检测到重复号码！**

📱 **号码：** `{phone_number}`
👤 **本次提交：** {current_submitter['first_name']} {current_username}
🕐 **首次记录：** {self._format_timestamp_short(first_submitter['timestamp'])} 由 {first_submitter['first_name']} {first_username}"""

        # 如果有上次提交记录且不是首次提交者
        if last_submitter and submission_count > 2:
            last_username = f"@{last_submitter['username']}" if last_submitter['username'] else "👤"
            message += f"\n🔄 **上次提交：** {self._format_timestamp_short(last_submitter['timestamp'])} 由 {last_submitter['first_name']} {last_username}"

        # 添加统计信息
        message += f"\n\n📊 **统计：** 共提交 {submission_count} 次"

        # 添加友好提示
        if submission_count >= 5:
            message += "\n💡 *提示：此号码提交较为频繁，请注意核实*"

        return message
    
    def _format_timestamp(self, timestamp) -> str:
        """格式化时间戳（完整格式）"""
        if isinstance(timestamp, str):
            # 如果是字符串，尝试解析
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                return timestamp

        # 确保时间戳是本地时区
        if timestamp.tzinfo is None:
            timestamp = self.timezone.localize(timestamp)
        elif timestamp.tzinfo != self.timezone:
            timestamp = timestamp.astimezone(self.timezone)

        return timestamp.strftime('%Y-%m-%d %H:%M:%S')

    def _format_timestamp_short(self, timestamp) -> str:
        """格式化时间戳（简短格式）"""
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                return timestamp

        # 确保时间戳是本地时区
        if timestamp.tzinfo is None:
            timestamp = self.timezone.localize(timestamp)
        elif timestamp.tzinfo != self.timezone:
            timestamp = timestamp.astimezone(self.timezone)

        # 判断是否是今天
        now = datetime.now(self.timezone)
        if timestamp.date() == now.date():
            return timestamp.strftime('今天 %H:%M')
        elif (now - timestamp).days == 1:
            return timestamp.strftime('昨天 %H:%M')
        elif (now - timestamp).days < 7:
            weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            return f"{weekdays[timestamp.weekday()]} {timestamp.strftime('%H:%M')}"
        else:
            return timestamp.strftime('%m-%d %H:%M')
    
    def process_phone_submission(self, phone_number: str, telegram_username: str,
                               telegram_user_id: int, first_name: str,
                               group_id: int, original_message: str) -> Tuple[str, bool]:
        """
        处理号码提交并生成相应的通知消息
        返回: (notification_message, is_duplicate)
        """
        try:
            # 添加记录到数据库
            record_id, is_duplicate = self.db_manager.add_phone_record(
                phone_number, telegram_username, telegram_user_id,
                first_name, group_id, original_message
            )
            
            current_time = datetime.now(self.timezone)
            
            if not is_duplicate:
                # 首次提交，返回成功消息
                message = self.format_success_message(
                    phone_number, first_name, telegram_username, current_time
                )
                return message, False
            else:
                # 重复提交，生成重复提醒
                return self._generate_duplicate_notification(
                    phone_number, telegram_username, telegram_user_id, first_name
                ), True
                
        except Exception as e:
            logger.error(f"处理号码提交失败: {e}")
            return "❌ 处理号码时发生错误，请稍后重试。", False
    
    def _generate_duplicate_notification(self, phone_number: str, telegram_username: str,
                                       telegram_user_id: int, first_name: str) -> str:
        """生成重复号码通知"""
        try:
            # 获取当前提交者信息
            current_submitter = {
                'username': telegram_username,
                'user_id': telegram_user_id,
                'first_name': first_name
            }
            
            # 获取首次提交记录
            first_submitter = self.db_manager.get_first_submission(phone_number)
            if not first_submitter:
                logger.error(f"无法获取号码 {phone_number} 的首次提交记录")
                return "⚠️ 号码重复，但无法获取详细信息。"
            
            # 获取上次提交记录
            last_submitter = self.db_manager.get_last_submission(phone_number)
            
            # 获取提交次数
            submission_count = self.db_manager.get_submission_count(phone_number)
            
            # 生成重复消息
            return self.format_duplicate_message(
                phone_number, current_submitter, first_submitter,
                last_submitter, submission_count
            )
            
        except Exception as e:
            logger.error(f"生成重复通知失败: {e}")
            return "⚠️ 号码重复，但无法获取详细信息。"
    
    def format_statistics_message(self, stats: Dict) -> str:
        """格式化统计报告消息"""
        # 计算重复率
        duplicate_rate = 0
        if stats['total_submissions'] > 0:
            duplicate_rate = (stats['total_duplicates'] / stats['total_submissions']) * 100

        # 选择合适的图标
        if stats['total_submissions'] == 0:
            status_icon = "📝"
        elif duplicate_rate < 10:
            status_icon = "✅"
        elif duplicate_rate < 30:
            status_icon = "⚠️"
        else:
            status_icon = "🚨"

        message = f"""{status_icon} **数据统计报告**

📈 **总体数据**
├ 📝 总记录数：{stats['total_submissions']}
├ 🔢 唯一号码：{stats['unique_numbers']}
├ 🔄 重复号码：{stats['duplicate_numbers']}
└ 📊 重复提交：{stats['total_duplicates']}

📊 **数据质量**
重复率：{duplicate_rate:.1f}%"""

        # 添加数据质量评估
        if duplicate_rate == 0:
            message += " 🎉 *数据质量优秀*"
        elif duplicate_rate < 10:
            message += " ✅ *数据质量良好*"
        elif duplicate_rate < 30:
            message += " ⚠️ *存在一定重复*"
        else:
            message += " 🚨 *重复率较高，建议核查*"

        message += f"""

🔧 **快捷操作**
• `/详情 [号码]` - 查看号码详情
• `/搜索 [关键词]` - 搜索相关记录
• `/导出` - 导出数据报告"""

        return message
    
    def format_phone_detail_message(self, phone_number: str, history: list) -> str:
        """格式化号码详情消息"""
        if not history:
            return f"""📋 **号码查询结果**

🔍 **查询号码：** `{phone_number}`
❌ **结果：** 未找到相关记录

💡 *请检查号码是否正确或尝试其他号码*"""

        count = len(history)

        # 分析提交模式
        first_time = self._format_timestamp_short(history[0]['timestamp'])
        last_time = self._format_timestamp_short(history[-1]['timestamp']) if count > 1 else first_time

        # 统计提交者
        submitters = set(record['first_name'] for record in history)
        submitter_count = len(submitters)

        message = f"""📋 **号码详细记录**

📱 **号码：** `{phone_number}`
📊 **统计：** 共 {count} 次提交，{submitter_count} 人提交
⏰ **时间跨度：** {first_time}"""

        if count > 1:
            message += f" 至 {last_time}"

        message += f"\n\n📝 **提交历史：**"

        # 限制显示数量，避免消息过长
        display_count = min(count, 10)
        for i, record in enumerate(history[:display_count], 1):
            username_display = f"@{record['username']}" if record['username'] else "👤"
            formatted_time = self._format_timestamp_short(record['timestamp'])

            # 标记重复提交者
            is_repeat = sum(1 for r in history[:i] if r['first_name'] == record['first_name']) > 1
            repeat_mark = " 🔄" if is_repeat else ""

            message += f"\n{i}. {formatted_time} - {record['first_name']} {username_display}{repeat_mark}"

        # 如果记录太多，显示省略提示
        if count > display_count:
            message += f"\n... *还有 {count - display_count} 条记录*"

        # 添加操作提示
        message += f"\n\n💡 *使用 `/搜索 {history[0]['first_name']}` 查看该用户的所有提交*"

        return message

    def format_search_results(self, keyword: str, results: list) -> str:
        """格式化搜索结果消息"""
        if not results:
            return f"""🔍 **搜索结果**

🔎 **关键词：** `{keyword}`
❌ **结果：** 未找到相关记录

💡 *尝试使用其他关键词或检查拼写*"""

        count = len(results)
        message = f"""🔍 **搜索结果**

🔎 **关键词：** `{keyword}`
📊 **找到：** {count} 条记录

📝 **搜索结果：**"""

        # 限制显示数量
        display_count = min(count, 10)
        for i, record in enumerate(results[:display_count], 1):
            username_display = f"@{record['username']}" if record['username'] else "👤"
            formatted_time = self._format_timestamp_short(record['timestamp'])
            duplicate_mark = " 🔄" if record['is_duplicate'] else ""

            message += f"\n{i}. `{record['phone_number']}` - {record['first_name']} {username_display}"
            message += f"\n   ⏰ {formatted_time}{duplicate_mark}"

        if count > display_count:
            message += f"\n\n... *还有 {count - display_count} 条记录*"

        message += f"\n\n💡 *使用 `/详情 [号码]` 查看具体号码的详细信息*"

        return message

    def format_user_records(self, user_identifier: str, records: list) -> str:
        """格式化用户记录消息"""
        if not records:
            return f"""👤 **用户记录查询**

🔎 **用户：** `{user_identifier}`
❌ **结果：** 未找到相关记录

💡 *请检查用户名或姓名是否正确*"""

        count = len(records)
        first_record = records[0]

        # 统计用户信息
        unique_phones = set(record['phone_number'] for record in records)
        duplicate_count = sum(1 for record in records if record['is_duplicate'])

        message = f"""👤 **用户记录详情**

🔎 **用户：** {first_record['first_name']} (@{first_record['username'] or '无'})
📊 **统计：** 提交 {count} 次，{len(unique_phones)} 个不同号码
🔄 **重复：** {duplicate_count} 次重复提交

📝 **提交记录：**"""

        # 按号码分组显示
        phone_groups = {}
        for record in records:
            phone = record['phone_number']
            if phone not in phone_groups:
                phone_groups[phone] = []
            phone_groups[phone].append(record)

        display_count = 0
        for phone, phone_records in phone_groups.items():
            if display_count >= 8:  # 限制显示数量
                break

            phone_count = len(phone_records)
            latest_time = self._format_timestamp_short(phone_records[0]['timestamp'])

            if phone_count == 1:
                message += f"\n• `{phone}` - {latest_time}"
            else:
                message += f"\n• `{phone}` - {latest_time} (共{phone_count}次)"

            display_count += 1

        if len(phone_groups) > display_count:
            message += f"\n... *还有 {len(phone_groups) - display_count} 个号码*"

        return message

    def format_recent_records(self, records: list) -> str:
        """格式化最近记录消息"""
        if not records:
            return """📋 **最近记录**

❌ **结果：** 暂无记录

💡 *开始提交号码后这里会显示最近的记录*"""

        count = len(records)
        message = f"""📋 **最近记录** (最新{count}条)

📝 **记录列表：**"""

        for i, record in enumerate(records, 1):
            username_display = f"@{record['username']}" if record['username'] else "👤"
            formatted_time = self._format_timestamp_short(record['timestamp'])
            duplicate_mark = " 🔄" if record['is_duplicate'] else ""

            message += f"\n{i}. `{record['phone_number']}` - {record['first_name']} {username_display}"
            message += f"\n   ⏰ {formatted_time}{duplicate_mark}"

        message += f"\n\n💡 *使用 `/搜索 [关键词]` 搜索特定记录*"

        return message
