@echo off
chcp 65001 >nul
echo ========================================
echo 每日股票数据自动获取
echo %date% %time%
echo ========================================

cd /d "C:\Users\Charl\daily-report"

REM 使用 Python SDK 获取真实股票数据
echo [1/2] 正在获取股票数据...
python scripts\fetch_real_sdk.py

if %ERRORLEVEL% NEQ 0 (
    echo 股票数据获取失败！
    exit /b 1
)

echo.
echo [2/2] 数据获取完成！
echo 文件保存位置: data\stocks-%date:~0,4%-%date:~5,2%-%date:~8,2%.json
echo.
echo ========================================
echo 完成时间: %time%
echo ========================================
