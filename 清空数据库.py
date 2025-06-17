#!/usr/bin/env python3
"""
清空数据库脚本
安全地清空所有数据库表中的数据
"""

import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

# 添加核心模块路径
project_root = Path(__file__).parent
core_modules = project_root / "核心模块"
config_dir = project_root / "配置文件"
sys.path.insert(0, str(core_modules))

# 设置环境变量文件路径
env_file = config_dir / "环境配置.env"
if env_file.exists():
    os.environ.setdefault('ENV_FILE_PATH', str(env_file))

def backup_database(db_path):
    """备份数据库"""
    try:
        if not os.path.exists(db_path):
            print(f"📝 数据库文件不存在: {db_path}")
            return None
        
        # 创建备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{db_path}.backup_{timestamp}"
        
        # 复制数据库文件
        import shutil
        shutil.copy2(db_path, backup_path)
        
        print(f"💾 数据库已备份到: {backup_path}")
        return backup_path
        
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return None

def get_table_stats(db_path):
    """获取表统计信息"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        stats = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            stats[table_name] = count
        
        conn.close()
        return stats
        
    except Exception as e:
        print(f"❌ 获取统计信息失败: {e}")
        return {}

def clear_database(db_path):
    """清空数据库"""
    try:
        if not os.path.exists(db_path):
            print(f"📝 数据库文件不存在: {db_path}")
            return True
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("📝 数据库中没有表")
            conn.close()
            return True
        
        # 清空每个表
        for table in tables:
            table_name = table[0]
            print(f"🗑️ 清空表: {table_name}")
            cursor.execute(f"DELETE FROM {table_name}")
        
        # 重置自增ID
        cursor.execute("DELETE FROM sqlite_sequence")
        
        # 提交更改
        conn.commit()
        conn.close()
        
        print("✅ 数据库清空完成")
        return True
        
    except Exception as e:
        print(f"❌ 清空数据库失败: {e}")
        return False

def main():
    """主函数"""
    print("🗑️ 数据库清空工具")
    print("=" * 50)
    
    # 获取数据库路径
    from 核心模块 import Config
    db_path = Config.DATABASE_PATH
    
    print(f"📁 数据库路径: {db_path}")
    
    # 检查数据库是否存在
    if not os.path.exists(db_path):
        print("📝 数据库文件不存在，无需清空")
        return 0
    
    # 获取清空前的统计信息
    print("\n📊 清空前的数据统计:")
    before_stats = get_table_stats(db_path)
    total_records = 0
    for table_name, count in before_stats.items():
        print(f"  📋 {table_name}: {count} 条记录")
        total_records += count
    
    if total_records == 0:
        print("📝 数据库已经是空的，无需清空")
        return 0
    
    print(f"\n📊 总记录数: {total_records}")
    
    # 创建备份
    print("\n💾 创建数据库备份...")
    backup_path = backup_database(db_path)
    
    if not backup_path:
        print("❌ 备份失败，为安全起见，取消清空操作")
        return 1
    
    # 清空数据库
    print("\n🗑️ 开始清空数据库...")
    if clear_database(db_path):
        # 验证清空结果
        print("\n📊 清空后的数据统计:")
        after_stats = get_table_stats(db_path)
        total_after = 0
        for table_name, count in after_stats.items():
            print(f"  📋 {table_name}: {count} 条记录")
            total_after += count
        
        if total_after == 0:
            print("\n🎉 数据库清空成功！")
            print(f"💾 备份文件: {backup_path}")
            print(f"🗑️ 已删除 {total_records} 条记录")
            return 0
        else:
            print(f"\n⚠️ 清空不完整，仍有 {total_after} 条记录")
            return 1
    else:
        print("\n❌ 数据库清空失败")
        return 1

if __name__ == "__main__":
    exit(main())
