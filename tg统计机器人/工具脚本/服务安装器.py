#!/usr/bin/env python3
"""
Windows 服务安装脚本
将 Telegram 机器人安装为 Windows 服务
"""

import os
import sys
import subprocess
from pathlib import Path

def install_nssm():
    """检查并安装 NSSM (Non-Sucking Service Manager)"""
    print("🔍 检查 NSSM...")
    
    try:
        subprocess.run(['nssm', 'version'], capture_output=True, check=True)
        print("✅ NSSM 已安装")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ NSSM 未安装")
        print("\n📥 请下载并安装 NSSM:")
        print("1. 访问: https://nssm.cc/download")
        print("2. 下载 nssm-2.24.zip")
        print("3. 解压到 C:\\nssm")
        print("4. 将 C:\\nssm\\win64 添加到系统 PATH")
        print("5. 重新运行此脚本")
        return False

def create_service():
    """创建 Windows 服务"""
    if not install_nssm():
        return False
    
    # 获取当前目录和 Python 路径
    current_dir = Path(__file__).parent.absolute()
    python_exe = sys.executable
    bot_script = current_dir / "bot.py"
    
    service_name = "TelegramPhoneBot"
    
    print(f"🔧 创建服务: {service_name}")
    print(f"📁 工作目录: {current_dir}")
    print(f"🐍 Python 路径: {python_exe}")
    print(f"📄 机器人脚本: {bot_script}")
    
    try:
        # 创建服务
        subprocess.run([
            'nssm', 'install', service_name, python_exe, str(bot_script)
        ], check=True)
        
        # 设置工作目录
        subprocess.run([
            'nssm', 'set', service_name, 'AppDirectory', str(current_dir)
        ], check=True)
        
        # 设置服务描述
        subprocess.run([
            'nssm', 'set', service_name, 'Description', 'Telegram客户号码统计机器人'
        ], check=True)
        
        # 设置启动类型为自动
        subprocess.run([
            'nssm', 'set', service_name, 'Start', 'SERVICE_AUTO_START'
        ], check=True)
        
        # 设置重启策略
        subprocess.run([
            'nssm', 'set', service_name, 'AppRestartDelay', '5000'
        ], check=True)
        
        print("✅ 服务创建成功!")
        print(f"\n🎯 管理命令:")
        print(f"启动服务: net start {service_name}")
        print(f"停止服务: net stop {service_name}")
        print(f"删除服务: nssm remove {service_name} confirm")
        print(f"查看状态: sc query {service_name}")
        
        # 询问是否立即启动
        start_now = input("\n🚀 是否立即启动服务? (y/n): ").lower().strip()
        if start_now in ['y', 'yes', '是']:
            subprocess.run(['net', 'start', service_name], check=True)
            print("✅ 服务已启动!")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 创建服务失败: {e}")
        return False

def main():
    """主函数"""
    print("🤖 Telegram 机器人 Windows 服务安装器")
    print("=" * 50)
    
    # 检查管理员权限
    try:
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("❌ 需要管理员权限!")
            print("请以管理员身份运行此脚本")
            input("按回车键退出...")
            return 1
    except:
        pass
    
    # 检查环境
    if not Path(".env").exists():
        print("❌ 未找到 .env 配置文件")
        print("请确保已正确配置机器人")
        return 1
    
    # 创建服务
    if create_service():
        print("\n🎉 安装完成!")
        print("机器人现在将作为 Windows 服务运行")
        print("系统重启后会自动启动")
    else:
        print("\n❌ 安装失败")
        return 1
    
    input("\n按回车键退出...")
    return 0

if __name__ == "__main__":
    exit(main())
