@echo off
chcp 65001 >nul
title Telegram客户号码统计机器人

echo 🤖 Telegram客户号码统计机器人
echo ================================
echo.

:start
echo 🚀 启动机器人... [%date% %time%]
python bot.py

echo.
echo ⚠️  机器人已停止 [%date% %time%]
echo 🔄 5秒后自动重启...
timeout /t 5 /nobreak >nul

goto start
