# Telegram 机器人自动重启脚本
# PowerShell 版本

$Host.UI.RawUI.WindowTitle = "Telegram客户号码统计机器人"

Write-Host "🤖 Telegram客户号码统计机器人" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# 设置工作目录
Set-Location $PSScriptRoot

while ($true) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "🚀 启动机器人... [$timestamp]" -ForegroundColor Yellow
    
    try {
        # 启动机器人
        $process = Start-Process -FilePath "python" -ArgumentList "bot.py" -Wait -PassThru -NoNewWindow
        
        $exitCode = $process.ExitCode
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        
        if ($exitCode -eq 0) {
            Write-Host "✅ 机器人正常退出 [$timestamp]" -ForegroundColor Green
        } else {
            Write-Host "❌ 机器人异常退出 (代码: $exitCode) [$timestamp]" -ForegroundColor Red
        }
    }
    catch {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Write-Host "💥 启动失败: $($_.Exception.Message) [$timestamp]" -ForegroundColor Red
    }
    
    Write-Host "🔄 5秒后自动重启..." -ForegroundColor Cyan
    Start-Sleep -Seconds 5
    Write-Host ""
}
