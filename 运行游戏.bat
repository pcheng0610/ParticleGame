@echo off
chcp 65001 >nul
title 手势控制粒子游戏
color 0A

echo ==========================================
echo   手势控制粒子游戏
echo ==========================================
echo.
echo 正在启动游戏...
echo 如果程序出错，错误信息会显示在这里
echo.
echo ==========================================
echo.

ParticleGame.exe

echo.
echo ==========================================
if %errorlevel% equ 0 (
    echo 程序正常退出
) else (
    echo 程序异常退出，错误代码: %errorlevel%
)
echo ==========================================
echo.
pause
