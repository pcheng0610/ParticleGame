#!/bin/bash
# 粒子游戏打包脚本

echo "====================================="
echo "  手势控制粒子游戏 - 打包工具"
echo "====================================="
echo ""

# 检查是否安装了pyinstaller
if ! command -v pyinstaller &> /dev/null
then
    echo "未检测到 PyInstaller，正在安装..."
    pip install pyinstaller
fi

echo "开始打包游戏..."
echo ""

# 使用PyInstaller打包
# --onefile: 打包成单个可执行文件
# --name: 设置可执行文件名称
# --add-data: 如果有数据文件需要添加
# --windowed: 如果想隐藏控制台窗口（可选）
# --clean: 清理临时文件

pyinstaller --onefile \
    --name "ParticleGame" \
    --clean \
    particle_game.py

echo ""
echo "====================================="
echo "打包完成！"
echo "可执行文件位置: dist/ParticleGame"
echo "====================================="
echo ""
echo "使用说明："
echo "1. 将 dist/ParticleGame 文件分享给其他人"
echo "2. Linux用户直接运行: ./ParticleGame"
echo "3. 需要确保目标机器有摄像头"
echo ""
