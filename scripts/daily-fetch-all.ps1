#!/usr/bin/env pwsh
# 每日日报数据自动获取（完整版）
# 包含：股票、新闻、投融资

$date = Get-Date -Format "yyyy-MM-dd"
$time = Get-Date -Format "HH:mm:ss"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "明心战略新闻日报 - 每日数据自动获取" -ForegroundColor Cyan
Write-Host "$date $time" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $scriptDir
Set-Location $projectDir

# 运行完整数据抓取
Write-Host "[开始] 运行完整数据抓取..." -ForegroundColor Yellow
Write-Host ""

try {
    $output = node "$scriptDir\fetch-all-v2.js" 2>&1
    $output | ForEach-Object { Write-Host $_ }

    if ($LASTEXITCODE -ne 0) {
        throw "数据抓取脚本执行失败"
    }

    Write-Host ""
    Write-Host "[完成] 所有数据获取完成！" -ForegroundColor Green
    Write-Host ""
    Write-Host "生成的数据文件:" -ForegroundColor Gray
    Write-Host "  - data\stocks-$date.json" -ForegroundColor Gray
    Write-Host "  - data\politics-$date.json" -ForegroundColor Gray
    Write-Host "  - data\ai-news-$date.json" -ForegroundColor Gray
    Write-Host "  - data\investment-$date.json" -ForegroundColor Gray
    Write-Host "  - data\summary-$date.json" -ForegroundColor Gray
}
catch {
    Write-Host "错误: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "完成时间: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
