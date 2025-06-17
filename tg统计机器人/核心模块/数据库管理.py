"""
数据库管理模块
处理SQLite数据库的连接、初始化和数据操作
"""

import sqlite3
import logging
import threading
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager
import pytz
from 配置管理 import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.timezone = pytz.timezone(Config.TIMEZONE)
        self._local = threading.local()
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接（线程安全）"""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                self.db_path, 
                check_same_thread=False,
                timeout=30.0
            )
            self._local.connection.row_factory = sqlite3.Row
            # 启用外键约束
            self._local.connection.execute("PRAGMA foreign_keys = ON")
        return self._local.connection
    
    @contextmanager
    def get_cursor(self):
        """获取数据库游标的上下文管理器"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            cursor.close()
    
    def init_database(self):
        """初始化数据库表结构"""
        try:
            with self.get_cursor() as cursor:
                # 创建号码记录表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS phone_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        phone_number TEXT NOT NULL,
                        telegram_username TEXT,
                        telegram_user_id INTEGER NOT NULL,
                        first_name TEXT,
                        message_timestamp DATETIME NOT NULL,
                        group_id INTEGER NOT NULL,
                        is_duplicate BOOLEAN NOT NULL DEFAULT 0,
                        original_message TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 创建索引以提高查询性能
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_phone_number 
                    ON phone_records(phone_number)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_user_id 
                    ON phone_records(telegram_user_id)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_group_id 
                    ON phone_records(group_id)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_timestamp 
                    ON phone_records(message_timestamp)
                ''')
                
                # 创建机器人配置表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS bot_config (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                logger.info("数据库初始化完成")
                
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def add_phone_record(self, phone_number: str, telegram_username: str, 
                        telegram_user_id: int, first_name: str, 
                        group_id: int, original_message: str) -> Tuple[int, bool]:
        """
        添加号码记录
        返回: (record_id, is_duplicate)
        """
        try:
            # 获取当前时间（UTC+8）
            current_time = datetime.now(self.timezone)
            
            # 检查是否为重复号码
            is_duplicate = self.is_duplicate_phone(phone_number)
            
            with self.get_cursor() as cursor:
                cursor.execute('''
                    INSERT INTO phone_records 
                    (phone_number, telegram_username, telegram_user_id, 
                     first_name, message_timestamp, group_id, is_duplicate, original_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (phone_number, telegram_username, telegram_user_id, 
                      first_name, current_time, group_id, is_duplicate, original_message))
                
                record_id = cursor.lastrowid
                logger.info(f"添加号码记录: {phone_number}, 用户: {first_name}, 重复: {is_duplicate}")
                return record_id, is_duplicate
                
        except Exception as e:
            logger.error(f"添加号码记录失败: {e}")
            raise
    
    def is_duplicate_phone(self, phone_number: str) -> bool:
        """检查号码是否已存在"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(
                    'SELECT COUNT(*) FROM phone_records WHERE phone_number = ?',
                    (phone_number,)
                )
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            logger.error(f"检查重复号码失败: {e}")
            return False

    def get_phone_history(self, phone_number: str) -> List[Dict]:
        """获取特定号码的所有提交历史"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute('''
                    SELECT telegram_username, telegram_user_id, first_name,
                           message_timestamp, original_message
                    FROM phone_records
                    WHERE phone_number = ?
                    ORDER BY message_timestamp ASC
                ''', (phone_number,))

                records = []
                for row in cursor.fetchall():
                    records.append({
                        'username': row['telegram_username'],
                        'user_id': row['telegram_user_id'],
                        'first_name': row['first_name'],
                        'timestamp': row['message_timestamp'],
                        'original_message': row['original_message']
                    })
                return records
        except Exception as e:
            logger.error(f"获取号码历史失败: {e}")
            return []

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        try:
            with self.get_cursor() as cursor:
                # 总记录数
                cursor.execute('SELECT COUNT(*) FROM phone_records')
                total_submissions = cursor.fetchone()[0]

                # 唯一号码数
                cursor.execute('SELECT COUNT(DISTINCT phone_number) FROM phone_records')
                unique_numbers = cursor.fetchone()[0]

                # 重复号码数（有多次提交的号码）
                cursor.execute('''
                    SELECT COUNT(*) FROM (
                        SELECT phone_number
                        FROM phone_records
                        GROUP BY phone_number
                        HAVING COUNT(*) > 1
                    )
                ''')
                duplicate_numbers = cursor.fetchone()[0]

                # 重复提交总数（除首次外的所有提交）
                cursor.execute('SELECT COUNT(*) FROM phone_records WHERE is_duplicate = 1')
                total_duplicates = cursor.fetchone()[0]

                return {
                    'total_submissions': total_submissions,
                    'unique_numbers': unique_numbers,
                    'duplicate_numbers': duplicate_numbers,
                    'total_duplicates': total_duplicates
                }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {
                'total_submissions': 0,
                'unique_numbers': 0,
                'duplicate_numbers': 0,
                'total_duplicates': 0
            }

    def get_first_submission(self, phone_number: str) -> Optional[Dict]:
        """获取号码的首次提交记录"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute('''
                    SELECT telegram_username, telegram_user_id, first_name, message_timestamp
                    FROM phone_records
                    WHERE phone_number = ?
                    ORDER BY message_timestamp ASC
                    LIMIT 1
                ''', (phone_number,))

                row = cursor.fetchone()
                if row:
                    return {
                        'username': row['telegram_username'],
                        'user_id': row['telegram_user_id'],
                        'first_name': row['first_name'],
                        'timestamp': row['message_timestamp']
                    }
                return None
        except Exception as e:
            logger.error(f"获取首次提交记录失败: {e}")
            return None

    def get_last_submission(self, phone_number: str) -> Optional[Dict]:
        """获取号码的最后一次提交记录（除当前外）"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute('''
                    SELECT telegram_username, telegram_user_id, first_name, message_timestamp
                    FROM phone_records
                    WHERE phone_number = ?
                    ORDER BY message_timestamp DESC
                    LIMIT 1 OFFSET 1
                ''', (phone_number,))

                row = cursor.fetchone()
                if row:
                    return {
                        'username': row['telegram_username'],
                        'user_id': row['telegram_user_id'],
                        'first_name': row['first_name'],
                        'timestamp': row['message_timestamp']
                    }
                return None
        except Exception as e:
            logger.error(f"获取最后提交记录失败: {e}")
            return None

    def get_submission_count(self, phone_number: str) -> int:
        """获取号码的提交次数"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(
                    'SELECT COUNT(*) FROM phone_records WHERE phone_number = ?',
                    (phone_number,)
                )
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"获取提交次数失败: {e}")
            return 0

    def search_records(self, keyword: str, limit: int = 50) -> List[Dict]:
        """搜索记录（按用户名、姓名或号码）"""
        try:
            with self.get_cursor() as cursor:
                # 搜索用户名、姓名或号码包含关键词的记录
                cursor.execute('''
                    SELECT phone_number, telegram_username, telegram_user_id,
                           first_name, message_timestamp, original_message, is_duplicate
                    FROM phone_records
                    WHERE phone_number LIKE ?
                       OR first_name LIKE ?
                       OR telegram_username LIKE ?
                       OR original_message LIKE ?
                    ORDER BY message_timestamp DESC
                    LIMIT ?
                ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', limit))

                records = []
                for row in cursor.fetchall():
                    records.append({
                        'phone_number': row['phone_number'],
                        'username': row['telegram_username'],
                        'user_id': row['telegram_user_id'],
                        'first_name': row['first_name'],
                        'timestamp': row['message_timestamp'],
                        'original_message': row['original_message'],
                        'is_duplicate': row['is_duplicate']
                    })
                return records
        except Exception as e:
            logger.error(f"搜索记录失败: {e}")
            return []

    def get_user_records(self, user_identifier: str, limit: int = 50) -> List[Dict]:
        """获取特定用户的所有记录"""
        try:
            with self.get_cursor() as cursor:
                # 按用户名或姓名搜索
                cursor.execute('''
                    SELECT phone_number, telegram_username, telegram_user_id,
                           first_name, message_timestamp, original_message, is_duplicate
                    FROM phone_records
                    WHERE first_name = ? OR telegram_username = ?
                    ORDER BY message_timestamp DESC
                    LIMIT ?
                ''', (user_identifier, user_identifier, limit))

                records = []
                for row in cursor.fetchall():
                    records.append({
                        'phone_number': row['phone_number'],
                        'username': row['telegram_username'],
                        'user_id': row['telegram_user_id'],
                        'first_name': row['first_name'],
                        'timestamp': row['message_timestamp'],
                        'original_message': row['original_message'],
                        'is_duplicate': row['is_duplicate']
                    })
                return records
        except Exception as e:
            logger.error(f"获取用户记录失败: {e}")
            return []

    def get_recent_records(self, limit: int = 20) -> List[Dict]:
        """获取最近的记录"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute('''
                    SELECT phone_number, telegram_username, telegram_user_id,
                           first_name, message_timestamp, original_message, is_duplicate
                    FROM phone_records
                    ORDER BY message_timestamp DESC
                    LIMIT ?
                ''', (limit,))

                records = []
                for row in cursor.fetchall():
                    records.append({
                        'phone_number': row['phone_number'],
                        'username': row['telegram_username'],
                        'user_id': row['telegram_user_id'],
                        'first_name': row['first_name'],
                        'timestamp': row['message_timestamp'],
                        'original_message': row['original_message'],
                        'is_duplicate': row['is_duplicate']
                    })
                return records
        except Exception as e:
            logger.error(f"获取最近记录失败: {e}")
            return []

    def export_all_records(self) -> List[Dict]:
        """导出所有记录"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute('''
                    SELECT phone_number, telegram_username, telegram_user_id,
                           first_name, message_timestamp, group_id,
                           original_message, is_duplicate
                    FROM phone_records
                    ORDER BY message_timestamp ASC
                ''')

                records = []
                for row in cursor.fetchall():
                    records.append({
                        'phone_number': row['phone_number'],
                        'username': row['telegram_username'],
                        'user_id': row['telegram_user_id'],
                        'first_name': row['first_name'],
                        'timestamp': row['message_timestamp'],
                        'group_id': row['group_id'],
                        'original_message': row['original_message'],
                        'is_duplicate': row['is_duplicate']
                    })
                return records
        except Exception as e:
            logger.error(f"导出记录失败: {e}")
            return []

    def close_connection(self):
        """关闭数据库连接"""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            delattr(self._local, 'connection')
