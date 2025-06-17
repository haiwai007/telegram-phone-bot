#!/usr/bin/env python3
"""
Windows 任务计划程序脚本
创建自动启动任务
"""

import os
import sys
import subprocess
from pathlib import Path

def create_scheduled_task():
    """创建计划任务"""
    current_dir = Path(__file__).parent.absolute()
    python_exe = sys.executable
    bot_script = current_dir / "bot.py"
    
    task_name = "TelegramPhoneBot"
    
    # 创建 XML 任务定义
    task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2024-01-01T00:00:00</Date>
    <Author>System</Author>
    <Description>Telegram客户号码统计机器人</Description>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>3</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{python_exe}</Command>
      <Arguments>"{bot_script}"</Arguments>
      <WorkingDirectory>{current_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""
    
    # 保存 XML 文件
    xml_file = current_dir / "task.xml"
    with open(xml_file, 'w', encoding='utf-16') as f:
        f.write(task_xml)
    
    try:
        # 创建任务
        subprocess.run([
            'schtasks', '/create', '/tn', task_name, 
            '/xml', str(xml_file), '/f'
        ], check=True)
        
        print("✅ 计划任务创建成功!")
        print(f"\n🎯 管理命令:")
        print(f"启动任务: schtasks /run /tn {task_name}")
        print(f"停止任务: schtasks /end /tn {task_name}")
        print(f"删除任务: schtasks /delete /tn {task_name} /f")
        print(f"查看状态: schtasks /query /tn {task_name}")
        
        # 清理临时文件
        xml_file.unlink()
        
        # 询问是否立即启动
        start_now = input("\n🚀 是否立即启动任务? (y/n): ").lower().strip()
        if start_now in ['y', 'yes', '是']:
            subprocess.run(['schtasks', '/run', '/tn', task_name], check=True)
            print("✅ 任务已启动!")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 创建任务失败: {e}")
        return False

def main():
    """主函数"""
    print("🤖 Telegram 机器人任务计划器")
    print("=" * 40)
    
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
        return 1
    
    # 创建任务
    if create_scheduled_task():
        print("\n🎉 设置完成!")
        print("机器人将在系统启动时自动运行")
    else:
        print("\n❌ 设置失败")
        return 1
    
    input("\n按回车键退出...")
    return 0

if __name__ == "__main__":
    exit(main())
