"""
数据库模块测试
测试数据库操作和数据完整性
"""

import unittest
import tempfile
import os
import sys
from datetime import datetime
import pytz

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    """数据库管理器测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时数据库文件
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # 初始化数据库管理器
        self.db_manager = DatabaseManager(self.temp_db.name)
        
        # 测试数据
        self.test_phone = "13812345678"
        self.test_username = "testuser"
        self.test_user_id = 12345
        self.test_first_name = "测试用户"
        self.test_group_id = -67890
        self.test_message = "号码：13812345678"
    
    def tearDown(self):
        """测试后清理"""
        try:
            self.db_manager.close_connection()
        except:
            pass

        # 删除临时数据库文件
        try:
            if os.path.exists(self.temp_db.name):
                os.unlink(self.temp_db.name)
        except PermissionError:
            # 在Windows上可能会有文件锁定问题，忽略这个错误
            pass
    
    def test_database_initialization(self):
        """测试数据库初始化"""
        # 检查表是否创建成功
        with self.db_manager.get_cursor() as cursor:
            # 检查phone_records表
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='phone_records'
            """)
            self.assertIsNotNone(cursor.fetchone())
            
            # 检查bot_config表
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='bot_config'
            """)
            self.assertIsNotNone(cursor.fetchone())
    
    def test_add_phone_record_new(self):
        """测试添加新号码记录"""
        record_id, is_duplicate = self.db_manager.add_phone_record(
            self.test_phone, self.test_username, self.test_user_id,
            self.test_first_name, self.test_group_id, self.test_message
        )
        
        # 验证返回值
        self.assertIsInstance(record_id, int)
        self.assertFalse(is_duplicate)
        
        # 验证数据库中的记录
        with self.db_manager.get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM phone_records WHERE id = ?",
                (record_id,)
            )
            record = cursor.fetchone()
            
            self.assertIsNotNone(record)
            self.assertEqual(record['phone_number'], self.test_phone)
            self.assertEqual(record['telegram_username'], self.test_username)
            self.assertEqual(record['telegram_user_id'], self.test_user_id)
            self.assertEqual(record['first_name'], self.test_first_name)
            self.assertEqual(record['group_id'], self.test_group_id)
            self.assertEqual(record['original_message'], self.test_message)
            self.assertFalse(record['is_duplicate'])
    
    def test_add_phone_record_duplicate(self):
        """测试添加重复号码记录"""
        # 先添加一条记录
        self.db_manager.add_phone_record(
            self.test_phone, self.test_username, self.test_user_id,
            self.test_first_name, self.test_group_id, self.test_message
        )
        
        # 再添加相同号码
        record_id, is_duplicate = self.db_manager.add_phone_record(
            self.test_phone, "another_user", 54321,
            "另一个用户", self.test_group_id, "重复号码：13812345678"
        )
        
        # 验证返回值
        self.assertIsInstance(record_id, int)
        self.assertTrue(is_duplicate)
        
        # 验证数据库中有两条记录
        with self.db_manager.get_cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM phone_records WHERE phone_number = ?",
                (self.test_phone,)
            )
            count = cursor.fetchone()[0]
            self.assertEqual(count, 2)
    
    def test_is_duplicate_phone(self):
        """测试重复号码检测"""
        # 新号码应该不重复
        self.assertFalse(self.db_manager.is_duplicate_phone(self.test_phone))
        
        # 添加号码后应该重复
        self.db_manager.add_phone_record(
            self.test_phone, self.test_username, self.test_user_id,
            self.test_first_name, self.test_group_id, self.test_message
        )
        self.assertTrue(self.db_manager.is_duplicate_phone(self.test_phone))
    
    def test_get_phone_history(self):
        """测试获取号码历史"""
        # 添加多条记录
        records_data = [
            ("user1", 111, "用户1", "消息1"),
            ("user2", 222, "用户2", "消息2"),
            ("user3", 333, "用户3", "消息3"),
        ]
        
        for username, user_id, first_name, message in records_data:
            self.db_manager.add_phone_record(
                self.test_phone, username, user_id,
                first_name, self.test_group_id, message
            )
        
        # 获取历史记录
        history = self.db_manager.get_phone_history(self.test_phone)
        
        # 验证记录数量和顺序
        self.assertEqual(len(history), 3)
        
        # 验证记录内容
        for i, (username, user_id, first_name, message) in enumerate(records_data):
            self.assertEqual(history[i]['username'], username)
            self.assertEqual(history[i]['user_id'], user_id)
            self.assertEqual(history[i]['first_name'], first_name)
            self.assertEqual(history[i]['original_message'], message)
    
    def test_get_statistics(self):
        """测试获取统计信息"""
        # 初始状态
        stats = self.db_manager.get_statistics()
        self.assertEqual(stats['total_submissions'], 0)
        self.assertEqual(stats['unique_numbers'], 0)
        self.assertEqual(stats['duplicate_numbers'], 0)
        self.assertEqual(stats['total_duplicates'], 0)
        
        # 添加一些测试数据
        phones = ["13812345678", "15012345678", "13812345678", "18812345678", "13812345678"]
        
        for i, phone in enumerate(phones):
            self.db_manager.add_phone_record(
                phone, f"user{i}", i, f"用户{i}",
                self.test_group_id, f"消息{i}"
            )
        
        # 重新获取统计信息
        stats = self.db_manager.get_statistics()
        
        # 验证统计结果
        self.assertEqual(stats['total_submissions'], 5)  # 总提交数
        self.assertEqual(stats['unique_numbers'], 3)     # 唯一号码数
        self.assertEqual(stats['duplicate_numbers'], 1)  # 有重复的号码数
        self.assertEqual(stats['total_duplicates'], 2)   # 重复提交数
    
    def test_get_first_submission(self):
        """测试获取首次提交记录"""
        # 没有记录时应该返回None
        first = self.db_manager.get_first_submission(self.test_phone)
        self.assertIsNone(first)
        
        # 添加记录
        self.db_manager.add_phone_record(
            self.test_phone, self.test_username, self.test_user_id,
            self.test_first_name, self.test_group_id, self.test_message
        )
        
        # 添加第二条记录
        self.db_manager.add_phone_record(
            self.test_phone, "user2", 222, "用户2",
            self.test_group_id, "第二条消息"
        )
        
        # 获取首次提交
        first = self.db_manager.get_first_submission(self.test_phone)
        
        self.assertIsNotNone(first)
        self.assertEqual(first['username'], self.test_username)
        self.assertEqual(first['user_id'], self.test_user_id)
        self.assertEqual(first['first_name'], self.test_first_name)
    
    def test_get_submission_count(self):
        """测试获取提交次数"""
        # 初始应该为0
        count = self.db_manager.get_submission_count(self.test_phone)
        self.assertEqual(count, 0)
        
        # 添加记录后应该增加
        for i in range(3):
            self.db_manager.add_phone_record(
                self.test_phone, f"user{i}", i, f"用户{i}",
                self.test_group_id, f"消息{i}"
            )
            
            count = self.db_manager.get_submission_count(self.test_phone)
            self.assertEqual(count, i + 1)
    
    def test_concurrent_access(self):
        """测试并发访问（简单测试）"""
        import threading
        
        results = []
        
        def add_record(phone_suffix):
            phone = f"1381234567{phone_suffix}"
            record_id, is_duplicate = self.db_manager.add_phone_record(
                phone, f"user{phone_suffix}", int(phone_suffix),
                f"用户{phone_suffix}", self.test_group_id, f"消息{phone_suffix}"
            )
            results.append((record_id, is_duplicate))
        
        # 创建多个线程同时添加记录
        threads = []
        for i in range(5):
            thread = threading.Thread(target=add_record, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        self.assertEqual(len(results), 5)
        for record_id, is_duplicate in results:
            self.assertIsInstance(record_id, int)
            self.assertFalse(is_duplicate)  # 都是不同的号码，应该都不重复

if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
