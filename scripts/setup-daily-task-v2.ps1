# 设置每日日报数据自动获取任务（完整版）

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "设置每日日报数据自动获取任务" -ForegroundColor Cyan
Write-Host "包含：股票、新闻、政策、投融资" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "错误：需要以管理员身份运行此脚本！" -ForegroundColor Red
    Write-Host "请右键点击 PowerShell，选择'以管理员身份运行'" -ForegroundColor Yellow
    pause
    exit 1
}

$taskName = "DailyReportDataFetch"
$scriptPath = "C:\Users\Charl\daily-report\scripts\daily-fetch-all.ps1"

# 删除已有任务
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "检测到已有任务，正在更新..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "已删除旧任务" -ForegroundColor Green
}

Write-Host ""
Write-Host "请选择每日获取数据的时间：" -ForegroundColor Cyan
Write-Host "[1] 上午 8:00（推荐，美股收盘后）"
Write-Host "[2] 上午 9:00（A股开盘前）"
Write-Host "[3] 中午 12:00（午间）"
Write-Host "[4] 下午 18:00（A股收盘后）"
Write-Host "[5] 晚上 22:00（美股盘中）"
Write-Host "[6] 自定义时间"
Write-Host "[7] 早晚各一次（8:00 + 22:00）"

$choice = Read-Host "请输入选项 (1-7)"

switch ($choice) {
    "1" { $hour = 8; $minute = 0; $trigger = New-ScheduledTaskTrigger -Daily -At "08:00" }
    "2" { $hour = 9; $minute = 0; $trigger = New-ScheduledTaskTrigger -Daily -At "09:00" }
    "3" { $hour = 12; $minute = 0; $trigger = New-ScheduledTaskTrigger -Daily -At "12:00" }
    "4" { $hour = 18; $minute = 0; $trigger = New-ScheduledTaskTrigger -Daily -At "18:00" }
    "5" { $hour = 22; $minute = 0; $trigger = New-ScheduledTaskTrigger -Daily -At "22:00" }
    "6" {
        $hour = Read-Host "请输入小时 (0-23)"
        $minute = Read-Host "请输入分钟 (0-59)"
        $trigger = New-ScheduledTaskTrigger -Daily -At "$hour`:$($minute.ToString().PadLeft(2,'0'))"
    }
    "7" {
        $trigger = @(
            New-ScheduledTaskTrigger -Daily -At "08:00"
            New-ScheduledTaskTrigger -Daily -At "22:00"
        )
        Write-Host "已设置早晚各一次 (8:00, 22:00)" -ForegroundColor Green
    }
    default {
        Write-Host "无效选项，使用默认时间 8:00" -ForegroundColor Yellow
        $trigger = New-ScheduledTaskTrigger -Daily -At "08:00"
    }
}

Write-Host ""
Write-Host "正在创建定时任务..." -ForegroundColor Yellow

try {
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$scriptPath`""
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

    if ($trigger -is [System.Array]) {
        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
    } else {
        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
    }

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "任务创建成功！" -ForegroundColor Green
    Write-Host "任务名称: $taskName" -ForegroundColor Cyan
    if ($choice -eq "7") {
        Write-Host "执行时间: 每天 8:00, 22:00" -ForegroundColor Cyan
    } else {
        Write-Host "执行时间: 每天 $hour`:$($minute.ToString().PadLeft(2,'0'))" -ForegroundColor Cyan
    }
    Write-Host "执行脚本: $scriptPath" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "管理命令：" -ForegroundColor Gray
    Write-Host "  查看任务: Get-ScheduledTask -TaskName '$taskName'"
    Write-Host "  删除任务: Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false"
    Write-Host "  手动运行: Start-ScheduledTask -TaskName '$taskName'"
    Write-Host ""
}
catch {
    Write-Host "错误：任务创建失败！" -ForegroundColor Red
    Write-Host $_ -ForegroundColor Red
}

pause
