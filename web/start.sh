#!/bin/bash

echo "🎮 启动手势控制粒子游戏 - Web 版"
echo "================================"
echo ""

cd "$(dirname "$0")"

# 查找可用端口
PORT=8080
while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; do
    echo "⚠️  端口 $PORT 已被占用，尝试 $((PORT+1))..."
    PORT=$((PORT+1))
done

echo "✅ 使用端口: $PORT"
echo ""
echo "🌐 启动本地服务器..."
echo ""
echo "访问地址: http://localhost:$PORT"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

python3 -m http.server $PORT
