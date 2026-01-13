@echo off
REM 粒子游戏打包脚本 - Windows版本

echo =====================================
echo   手势控制粒子游戏 - 打包工具
echo =====================================
echo.

REM 检查是否安装了pyinstaller
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo 未检测到 PyInstaller，正在安装...
    pip install pyinstaller
)

echo 开始打包游戏...
echo.

REM 使用PyInstaller打包
pyinstaller --onefile --name "ParticleGame" --clean particle_game.py

echo.
echo =====================================
echo 打包完成！
echo 可执行文件位置: dist\ParticleGame.exe
echo =====================================
echo.
echo 使用说明：
echo 1. 将 dist\ParticleGame.exe 文件分享给其他人
echo 2. Windows用户直接双击运行即可
echo 3. 需要确保目标机器有摄像头
echo.
pause
