#!/bin/bash
# 在Linux上打包Windows EXE文件的脚本

echo "=========================================="
echo "  在Linux上打包Windows EXE文件"
echo "=========================================="
echo ""

# 检查Wine是否安装
if ! command -v wine &> /dev/null; then
    echo "❌ Wine未安装！"
    echo ""
    echo "请先安装Wine："
    echo "  Ubuntu/Debian: sudo apt-get install wine wine64"
    echo "  Fedora: sudo dnf install wine"
    echo "  Arch: sudo pacman -S wine"
    echo ""
    exit 1
fi

echo "✓ Wine已安装"
echo ""

# 检查是否安装了Windows版Python
WINE_PYTHON="$HOME/.wine/drive_c/Python39/python.exe"

if [ ! -f "$WINE_PYTHON" ]; then
    echo "⚠️  需要在Wine中安装Python"
    echo ""
    echo "步骤："
    echo "1. 下载Windows版Python: https://www.python.org/downloads/windows/"
    echo "2. 运行: wine python-3.9.x.exe"
    echo "3. 安装到默认位置: C:\\Python39"
    echo ""
    echo "或者使用Docker方法（见下方说明）"
    exit 1
fi

echo "✓ Wine中的Python已安装"
echo ""

# 在Wine环境中安装PyInstaller和依赖
echo "📦 安装依赖包..."
wine "$WINE_PYTHON" -m pip install pyinstaller opencv-python mediapipe numpy

# 打包
echo ""
echo "📦 开始打包..."
wine "$WINE_PYTHON" -m PyInstaller --onefile --name "ParticleGame" --clean particle_game.py

echo ""
echo "=========================================="
echo "  打包完成！"
echo "=========================================="
echo ""
echo "Windows EXE位置: dist/ParticleGame.exe"
echo ""
