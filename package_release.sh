#!/bin/bash
# 一键打包发布脚本

PROJECT_NAME="ParticleGame"
VERSION="1.0"
RELEASE_DIR="release"

echo "========================================"
echo "  $PROJECT_NAME - 一键打包发布"
echo "========================================"
echo ""

# 创建发布目录
mkdir -p $RELEASE_DIR
cd $PROJECT_NAME

# 1. 打包源代码
echo "📦 打包源代码..."
cd ..
zip -q -r $RELEASE_DIR/${PROJECT_NAME}_v${VERSION}_Source.zip $PROJECT_NAME \
    -x "*.pyc" -x "__pycache__/*" -x ".git/*" -x "*.spec" -x "build/*" -x "dist/*"
echo "✓ 源代码打包完成: $RELEASE_DIR/${PROJECT_NAME}_v${VERSION}_Source.zip"

# 2. 检查是否安装PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo ""
    echo "⚠️  PyInstaller 未安装，跳过可执行文件打包"
    echo "   如需打包可执行文件，请运行:"
    echo "   pip install pyinstaller"
    echo "   然后执行 build_game.sh"
else
    echo ""
    echo "📦 打包可执行文件..."
    cd $PROJECT_NAME
    pyinstaller --onefile --name "$PROJECT_NAME" --clean particle_game.py > /dev/null 2>&1

    if [ -f "dist/$PROJECT_NAME" ]; then
        # 创建可执行文件压缩包
        cd dist
        platform=$(uname)
        tar -czf ../../$RELEASE_DIR/${PROJECT_NAME}_v${VERSION}_${platform}.tar.gz $PROJECT_NAME
        cd ../..
        echo "✓ 可执行文件打包完成: $RELEASE_DIR/${PROJECT_NAME}_v${VERSION}_${platform}.tar.gz"
    else
        echo "✗ 可执行文件打包失败"
    fi
fi

echo ""
echo "========================================"
echo "  打包完成！"
echo "========================================"
echo ""
echo "📦 发布文件位于: $RELEASE_DIR/"
ls -lh $RELEASE_DIR/
echo ""
echo "分享建议："
echo "  - 给普通用户: ${PROJECT_NAME}_v${VERSION}_${platform:-Linux}.tar.gz"
echo "  - 给开发者: ${PROJECT_NAME}_v${VERSION}_Source.zip"
echo ""
