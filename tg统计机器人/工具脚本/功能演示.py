#!/usr/bin/env python3
"""
功能演示脚本
展示机器人的核心功能，无需Telegram连接
"""

import sys
import os
import tempfile
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from phone_detector import PhoneDetector
from database import DatabaseManager
from notification_system import NotificationSystem

def demo_phone_detection():
    """演示号码检测功能"""
    print("🔍 号码检测功能演示")
    print("=" * 40)
    
    detector = PhoneDetector()
    
    test_messages = [
        "13812345678",
        "号码：138-1234-5678",
        "客户电话：(138) 1234.5678",
        "联系方式：+86 138 1234 5678",
        "这不是号码：123",
        "电话：00000000",
        "手机：15012345678 备注：VIP客户",
        "随便聊天，没有号码",
    ]
    
    for message in test_messages:
        result = detector.detect_phone_number(message)
        status = "✅ 检测到" if result else "❌ 未检测到"
        print(f"{status}: '{message}' -> {result}")
    
    print()

def demo_database_operations():
    """演示数据库操作"""
    print("🗄️ 数据库操作演示")
    print("=" * 40)
    
    # 创建临时数据库
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        db_manager = DatabaseManager(temp_db.name)
        
        # 添加测试数据
        test_records = [
            ("13812345678", "user1", 111, "张三", -12345, "号码：13812345678"),
            ("15012345678", "user2", 222, "李四", -12345, "客户：15012345678"),
            ("13812345678", "user3", 333, "王五", -12345, "重复号码：13812345678"),
            ("18812345678", "user4", 444, "赵六", -12345, "电话：18812345678"),
        ]
        
        print("📝 添加测试记录...")
        for phone, username, user_id, first_name, group_id, message in test_records:
            record_id, is_duplicate = db_manager.add_phone_record(
                phone, username, user_id, first_name, group_id, message
            )
            status = "重复" if is_duplicate else "新增"
            print(f"  {status}: {phone} (ID: {record_id})")
        
        # 获取统计信息
        print("\n📊 统计信息:")
        stats = db_manager.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # 查询号码历史
        print(f"\n📋 号码 13812345678 的提交历史:")
        history = db_manager.get_phone_history("13812345678")
        for i, record in enumerate(history, 1):
            print(f"  {i}. {record['first_name']} (@{record['username']}) - {record['timestamp']}")
        
        db_manager.close_connection()
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_db.name):
            os.unlink(temp_db.name)
    
    print()

def demo_notification_system():
    """演示通知系统"""
    print("📢 通知系统演示")
    print("=" * 40)
    
    # 创建临时数据库
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        db_manager = DatabaseManager(temp_db.name)
        notification_system = NotificationSystem(db_manager)
        
        # 模拟第一次提交
        print("📝 第一次提交号码...")
        message, is_duplicate = notification_system.process_phone_submission(
            "13812345678", "zhangsan", 111, "张三", -12345, "号码：13812345678"
        )
        print("机器人响应:")
        print(message)
        print()
        
        # 模拟重复提交
        print("📝 重复提交相同号码...")
        message, is_duplicate = notification_system.process_phone_submission(
            "13812345678", "lisi", 222, "李四", -12345, "客户：13812345678"
        )
        print("机器人响应:")
        print(message)
        print()
        
        # 统计报告
        print("📊 生成统计报告...")
        stats = db_manager.get_statistics()
        stats_message = notification_system.format_statistics_message(stats)
        print("统计报告:")
        print(stats_message)
        print()
        
        # 详情查询
        print("🔍 查询号码详情...")
        history = db_manager.get_phone_history("13812345678")
        detail_message = notification_system.format_phone_detail_message("13812345678", history)
        print("详情查询结果:")
        print(detail_message)
        
        db_manager.close_connection()
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_db.name):
            os.unlink(temp_db.name)
    
    print()

def main():
    """主函数"""
    print("🤖 Telegram客户号码统计机器人 - 功能演示")
    print("=" * 60)
    print()
    
    try:
        # 演示各个功能模块
        demo_phone_detection()
        demo_database_operations()
        demo_notification_system()
        
        print("✅ 演示完成！")
        print()
        print("💡 提示:")
        print("  - 运行 'python run_tests.py' 执行完整测试")
        print("  - 配置 .env 文件后运行 'python run.py' 启动机器人")
        print("  - 查看 README.md 了解详细使用说明")
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
