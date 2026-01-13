@echo off
chcp 65001 >nul
echo ==========================================
echo   手势控制粒子游戏
echo ==========================================
echo.
echo 正在启动游戏...
echo.

ParticleGame.exe

if %errorlevel% neq 0 (
    echo.
    echo ==========================================
    echo   程序异常退出，错误代码: %errorlevel%
    echo ==========================================
    echo.
    pause
)
