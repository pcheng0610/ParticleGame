#!/bin/bash
# 简化的跨平台打包方案（不需要Docker）

echo "=========================================="
echo "  粒子游戏 - 多平台打包"
echo "=========================================="
echo ""

PROJECT_DIR="$(pwd)"
DIST_DIR="$PROJECT_DIR/dist_all_platforms"

# 创建发布目录
mkdir -p "$DIST_DIR"

echo "📦 当前平台打包..."
echo ""

# 检查PyInstaller是否安装
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "安装PyInstaller..."
    pip3 install pyinstaller --user
fi

# 打包当前平台（Linux）
echo "正在打包 Linux 版本..."
pyinstaller --onefile --name "ParticleGame_Linux" --clean particle_game.py

if [ -f "dist/ParticleGame_Linux" ]; then
    mv dist/ParticleGame_Linux "$DIST_DIR/"
    echo "✓ Linux版本打包完成"
fi

echo ""
echo "=========================================="
echo "  打包完成！"
echo "=========================================="
echo ""
echo "Linux版本位置: $DIST_DIR/ParticleGame_Linux"
echo ""
echo "📝 关于Windows和Mac版本："
echo ""
echo "由于跨平台限制，建议使用以下方法之一："
echo ""
echo "方法1: 使用GitHub Actions（推荐）"
echo "  - 将代码推送到GitHub"
echo "  - 创建tag: git tag v1.0 && git push origin v1.0"
echo "  - GitHub会自动打包三个平台"
echo ""
echo "方法2: 使用虚拟机/双系统"
echo "  - 在Windows上运行: build_game.bat"
echo "  - 在Mac上运行: ./build_game.sh"
echo ""
echo "方法3: 使用Docker（需要sudo权限）"
echo "  - sudo docker run -v \$(pwd):/src cdrx/pyinstaller-windows"
echo ""
echo "方法4: 在线打包服务"
echo "  - 使用GitHub Actions（免费、自动）"
echo "  - 使用AppVeyor（免费）"
echo "  - 使用Travis CI（免费）"
echo ""
