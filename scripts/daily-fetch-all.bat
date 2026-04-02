@echo off
chcp 65001 >nul
echo ========================================
echo 明心战略新闻日报 - 每日数据自动获取
echo %date% %time%
echo ========================================
echo.

cd /d "%~dp0\.."

echo [开始] 运行完整数据抓取...
echo.

node scripts\fetch-all-v2.js

if %ERRORLEVEL% NEQ 0 (
    echo 错误：数据抓取失败！
    exit /b 1
)

echo.
echo ========================================
echo 数据获取完成！
echo ========================================
echo.
echo 生成的数据文件:
echo   - data\stocks-%date:~0,4%-%date:~5,2%-%date:~8,2%.json
echo   - data\politics-%date:~0,4%-%date:~5,2%-%date:~8,2%.json
echo   - data\ai-news-%date:~0,4%-%date:~5,2%-%date:~8,2%.json
echo   - data\investment-%date:~0,4%-%date:~5,2%-%date:~8,2%.json
echo   - data\summary-%date:~0,4%-%date:~5,2%-%date:~8,2%.json
echo.
