#!/bin/bash
# 使用Wine在Linux上打包Windows EXE（改进版）

echo "=========================================="
echo "  使用Wine打包Windows EXE"
echo "=========================================="
echo ""

# 检查Wine是否安装
if ! command -v wine &> /dev/null; then
    echo "❌ Wine未安装！"
    echo ""
    echo "正在安装Wine..."
    sudo apt-get update
    sudo apt-get install -y wine wine64 winetricks
    if [ $? -ne 0 ]; then
        echo "❌ Wine安装失败，请手动安装："
        echo "  sudo apt-get install wine wine64"
        exit 1
    fi
    echo "✓ Wine安装完成"
    echo ""
fi

echo "✓ Wine已安装"
echo ""

# 检查Wine环境是否初始化
if [ ! -d "$HOME/.wine" ]; then
    echo "📦 初始化Wine环境..."
    winecfg &
    sleep 3
    pkill -f winecfg
    echo "✓ Wine环境初始化完成"
    echo ""
fi

# 检查是否安装了Windows版Python
WINE_PYTHON_PATHS=(
    "$HOME/.wine/drive_c/Python39/python.exe"
    "$HOME/.wine/drive_c/Python310/python.exe"
    "$HOME/.wine/drive_c/Python311/python.exe"
    "$HOME/.wine/drive_c/Python312/python.exe"
    "$HOME/.wine/drive_c/python/python.exe"
)

WINE_PYTHON=""
for path in "${WINE_PYTHON_PATHS[@]}"; do
    if [ -f "$path" ]; then
        WINE_PYTHON="$path"
        echo "✓ 找到Python: $path"
        break
    fi
done

if [ -z "$WINE_PYTHON" ]; then
    echo "⚠️  Wine中未安装Python"
    echo ""
    echo "请按以下步骤安装："
    echo ""
    echo "方法1：自动下载并安装（推荐）"
    echo "  1. 下载Python安装包："
    echo "     cd /tmp"
    echo "     wget https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe"
    echo ""
    echo "  2. 在Wine中安装："
    echo "     wine /tmp/python-3.9.13-amd64.exe"
    echo ""
    echo "  3. 安装时选择："
    echo "     - ✅ Add Python to PATH"
    echo "     - ✅ Install for all users"
    echo "     - 安装路径保持默认: C:\\Python39"
    echo ""
    echo "方法2：手动下载"
    echo "  访问: https://www.python.org/downloads/windows/"
    echo "  下载Python 3.9.x 64位版本"
    echo "  运行: wine python-3.9.x-amd64.exe"
    echo ""
    exit 1
fi

echo ""

# 获取Python版本
PYTHON_VERSION=$(wine "$WINE_PYTHON" --version 2>&1 | head -1)
echo "Python版本: $PYTHON_VERSION"
echo ""

# 检查并安装依赖
echo "📦 检查依赖包..."
wine "$WINE_PYTHON" -m pip list 2>&1 | grep -q pyinstaller
if [ $? -ne 0 ]; then
    echo "正在安装PyInstaller..."
    wine "$WINE_PYTHON" -m pip install --upgrade pip
    wine "$WINE_PYTHON" -m pip install pyinstaller
fi

# 检查项目依赖
echo "正在安装项目依赖..."
wine "$WINE_PYTHON" -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "⚠️  依赖安装可能有问题，但继续尝试打包..."
fi

echo ""

# 清理之前的构建
if [ -d "dist" ]; then
    echo "🧹 清理旧的构建文件..."
    rm -rf dist build *.spec
fi

# 打包
echo "📦 开始打包..."
echo "这可能需要几分钟时间..."
echo ""

wine "$WINE_PYTHON" -m PyInstaller \
    --onefile \
    --name "ParticleGame" \
    --clean \
    --noconfirm \
    particle_game.py

if [ $? -eq 0 ] && [ -f "dist/ParticleGame.exe" ]; then
    echo ""
    echo "=========================================="
    echo "  ✅ 打包成功！"
    echo "=========================================="
    echo ""
    echo "Windows EXE位置: dist/ParticleGame.exe"
    EXE_SIZE=$(du -h dist/ParticleGame.exe | cut -f1)
    echo "文件大小: $EXE_SIZE"
    echo ""
    echo "现在可以将这个文件发送给Windows用户了！"
    echo ""
    
    # 复制到当前目录方便使用
    cp dist/ParticleGame.exe ./ParticleGame.exe 2>/dev/null
    if [ -f "./ParticleGame.exe" ]; then
        echo "已复制到: ./ParticleGame.exe"
    fi
else
    echo ""
    echo "=========================================="
    echo "  ❌ 打包失败"
    echo "=========================================="
    echo ""
    echo "请检查错误信息，常见问题："
    echo "1. 依赖包安装不完整"
    echo "2. PyInstaller版本问题"
    echo "3. Wine环境配置问题"
    echo ""
    exit 1
fi
