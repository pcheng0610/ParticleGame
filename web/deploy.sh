#!/bin/bash

echo "🚀 部署手势控制粒子游戏到 Vercel"
echo "================================"
echo ""

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装"
    echo "请先安装 Node.js："
    echo "  sudo apt update"
    echo "  sudo apt install nodejs npm"
    exit 1
fi

# 检查 Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "📦 正在安装 Vercel CLI..."
    sudo npm install -g vercel
fi

echo "✅ 准备就绪！"
echo ""
echo "🌐 开始部署..."
echo ""

cd "$(dirname "$0")"
vercel --prod

echo ""
echo "🎉 部署完成！"
echo "你的游戏现在已经在线了！"
echo ""
echo "📱 可以分享链接给朋友，让他们直接在浏览器玩！"
