#!/bin/bash
# 使用Docker打包Windows EXE

echo "=========================================="
echo "  使用Docker打包Windows EXE"
echo "=========================================="
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装！"
    echo ""
    echo "请先安装Docker："
    echo "  Ubuntu: sudo apt-get install docker.io"
    echo "  其他: https://docs.docker.com/engine/install/"
    echo ""
    exit 1
fi

echo "✓ Docker已安装"
echo ""

# 构建Docker镜像（不使用缓存，确保使用最新的Dockerfile）
echo "📦 构建Docker镜像..."
docker build --no-cache -f Dockerfile.windows -t particlegame-windows .

# 创建容器并复制文件
echo ""
echo "📦 提取EXE文件..."
docker create --name temp-container particlegame-windows
docker cp temp-container:/src/dist/ParticleGame.exe ./ParticleGame.exe
docker rm temp-container

echo ""
echo "=========================================="
echo "  打包完成！"
echo "=========================================="
echo ""
echo "Windows EXE位置: ./ParticleGame.exe"
echo "大小: $(du -h ParticleGame.exe | cut -f1)"
echo ""
echo "现在可以将这个文件发送给Windows用户了！"
echo ""
