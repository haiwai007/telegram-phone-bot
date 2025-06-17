#!/usr/bin/env python3
"""
测试运行脚本
运行所有单元测试并生成报告
"""

import unittest
import sys
import os
from pathlib import Path

def discover_and_run_tests():
    """发现并运行所有测试"""
    # 设置项目根目录
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    print("🧪 Telegram客户号码统计机器人 - 测试套件")
    print("=" * 50)
    
    # 发现测试文件
    test_files = [
        'test_phone_detector.py',
        'test_database.py'
    ]
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 加载测试
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"📝 加载测试文件: {test_file}")
            try:
                module_name = test_file[:-3]  # 移除.py扩展名
                module = __import__(module_name)
                suite.addTests(loader.loadTestsFromModule(module))
            except Exception as e:
                print(f"❌ 加载 {test_file} 失败: {e}")
        else:
            print(f"⚠️  测试文件不存在: {test_file}")
    
    # 运行测试
    print("\n🚀 开始运行测试...")
    print("-" * 50)
    
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    result = runner.run(suite)
    
    # 输出测试结果摘要
    print("\n" + "=" * 50)
    print("📊 测试结果摘要")
    print("=" * 50)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    
    print(f"总测试数: {total_tests}")
    print(f"成功: {total_tests - failures - errors}")
    print(f"失败: {failures}")
    print(f"错误: {errors}")
    print(f"跳过: {skipped}")
    
    if result.wasSuccessful():
        print("\n✅ 所有测试通过！")
        return 0
    else:
        print("\n❌ 部分测试失败")
        
        if result.failures:
            print("\n💥 失败的测试:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        
        if result.errors:
            print("\n🚨 错误的测试:")
            for test, traceback in result.errors:
                print(f"  - {test}")
        
        return 1

def run_specific_test(test_name):
    """运行特定的测试"""
    print(f"🧪 运行特定测试: {test_name}")
    print("=" * 50)
    
    try:
        # 加载特定测试
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(test_name)
        
        # 运行测试
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return 0 if result.wasSuccessful() else 1
        
    except Exception as e:
        print(f"❌ 运行测试失败: {e}")
        return 1

def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 运行特定测试
        test_name = sys.argv[1]
        return run_specific_test(test_name)
    else:
        # 运行所有测试
        return discover_and_run_tests()

if __name__ == "__main__":
    exit(main())
