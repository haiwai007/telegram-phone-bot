#!/usr/bin/env python3
"""
检查代码问题脚本
检查所有Python文件的语法错误和导入问题
"""

import os
import sys
import ast
import importlib.util
from pathlib import Path

def check_syntax(file_path):
    """检查Python文件语法"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查语法
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"语法错误: {e}"
    except Exception as e:
        return False, f"其他错误: {e}"

def check_imports(file_path):
    """检查导入问题"""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析AST
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    try:
                        importlib.import_module(alias.name)
                    except ImportError:
                        issues.append(f"无法导入模块: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    try:
                        importlib.import_module(node.module)
                    except ImportError:
                        issues.append(f"无法导入模块: {node.module}")
    except Exception as e:
        issues.append(f"检查导入时出错: {e}")
    
    return issues

def main():
    """主函数"""
    print("🔍 检查代码问题...")
    print("=" * 50)
    
    # 要检查的文件
    files_to_check = [
        "启动机器人.py",
        "智能启动机器人.py",
        "核心模块/配置管理.py",
        "核心模块/数据库管理.py",
        "核心模块/号码检测器.py",
        "核心模块/通知系统.py",
        "核心模块/导出管理器.py",
        "核心模块/机器人主程序.py"
    ]
    
    total_issues = 0
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            total_issues += 1
            continue
        
        print(f"\n📁 检查文件: {file_path}")
        
        # 检查语法
        syntax_ok, syntax_error = check_syntax(file_path)
        if not syntax_ok:
            print(f"  ❌ {syntax_error}")
            total_issues += 1
        else:
            print(f"  ✅ 语法检查通过")
        
        # 检查导入
        import_issues = check_imports(file_path)
        if import_issues:
            for issue in import_issues:
                print(f"  ⚠️ {issue}")
                total_issues += 1
        else:
            print(f"  ✅ 导入检查通过")
    
    print("\n" + "=" * 50)
    if total_issues == 0:
        print("🎉 所有检查通过，没有发现问题！")
    else:
        print(f"❌ 发现 {total_issues} 个问题需要修复")
    
    return total_issues

if __name__ == "__main__":
    exit(main())
