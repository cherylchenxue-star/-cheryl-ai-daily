#!/usr/bin/env pwsh
# 每日股票数据自动获取

$date = Get-Date -Format "yyyy-MM-dd"
$time = Get-Date -Format "HH:mm:ss"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "每日股票数据自动获取" -ForegroundColor Cyan
Write-Host "$date $time" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $scriptDir
Set-Location $projectDir

# 使用 Python SDK 获取真实股票数据
Write-Host "[1/2] 正在获取股票数据..." -ForegroundColor Yellow

try {
    $output = python "$scriptDir\fetch_real_sdk.py" 2>&1
    $output | ForEach-Object { Write-Host $_ }

    if ($LASTEXITCODE -ne 0) {
        throw "Python 脚本执行失败"
    }

    Write-Host ""
    Write-Host "[2/2] 数据获取完成！" -ForegroundColor Green
    Write-Host "文件保存位置: data\stocks-$date.json" -ForegroundColor Gray
}
catch {
    Write-Host "错误: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "完成时间: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
