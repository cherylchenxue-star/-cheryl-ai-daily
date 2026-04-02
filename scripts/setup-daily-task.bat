@echo off
chcp 65001 >nul
echo ========================================
echo 设置每日股票数据自动获取任务
echo ========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 错误：需要以管理员身份运行此脚本！
    echo 请右键点击此脚本，选择"以管理员身份运行"
    pause
    exit /b 1
)

set "TASK_NAME=DailyStockDataFetch"
set "SCRIPT_PATH=C:\Users\Charl\daily-report\scripts\daily-fetch-stocks.bat"

REM 删除已有任务（如果存在）
schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo 检测到已有任务，正在更新...
    schtasks /delete /tn "%TASK_NAME%" /f >nul
    echo 已删除旧任务
)

echo.
echo 请选择每日获取数据的时间：
echo [1] 上午 9:00（开盘前）
echo [2] 中午 12:00（午间）
echo [3] 下午 16:00（美股开盘前）
echo [4] 下午 18:00（A股收盘后）
echo [5] 晚上 22:00（美股盘中）
echo [6] 自定义时间
set /p choice="请输入选项 (1-6): "

if "%choice%"=="1" set HOUR=09&set MINUTE=00
if "%choice%"=="2" set HOUR=12&set MINUTE=00
if "%choice%"=="3" set HOUR=16&set MINUTE=00
if "%choice%"=="4" set HOUR=18&set MINUTE=00
if "%choice%"=="5" set HOUR=22&set MINUTE=00
if "%choice%"=="6" (
    set /p HOUR="请输入小时 (0-23): "
    set /p MINUTE="请输入分钟 (0-59): "
)

echo.
echo 正在创建定时任务：每天 %HOUR%:%MINUTE% 执行...

REM 创建任务 - 每天执行
schtasks /create /tn "%TASK_NAME%" /tr "%SCRIPT_PATH%" /sc daily /st %HOUR%:%MINUTE% /f /rl LIMITED >nul 2>&1

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo 任务创建成功！
    echo 任务名称: %TASK_NAME%
    echo 执行时间: 每天 %HOUR%:%MINUTE%
    echo 执行脚本: %SCRIPT_PATH%
    echo ========================================
    echo.
    echo 你可以通过以下方式管理任务：
    echo   - 查看: schtasks /query /tn "%TASK_NAME%"
    echo   - 删除: schtasks /delete /tn "%TASK_NAME%" /f
    echo   - 手动运行: schtasks /run /tn "%TASK_NAME%"
    echo.
) else (
    echo.
    echo 错误：任务创建失败！
    echo 请检查权限和路径是否正确。
)

pause
