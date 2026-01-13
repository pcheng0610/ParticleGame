#!/bin/bash

echo "🚀 部署手势控制粒子游戏到 Vercel"
echo "================================"
echo ""

cd "$(dirname "$0")"

# 检查是否已登录
if ! npx vercel whoami &>/dev/null; then
    echo "🔐 首次使用需要登录 Vercel"
    echo ""
    echo "步骤："
    echo "1. 运行 'npx vercel login'"
    echo "2. 输入你的邮箱地址"
    echo "3. 在邮箱中点击验证链接"
    echo "4. 返回终端，重新运行此脚本"
    echo ""
    echo "或者使用 GitHub 登录："
    echo "1. 访问 https://vercel.com/login"
    echo "2. 用 GitHub 登录"
    echo "3. 在终端运行 'npx vercel login' 并使用邮箱验证"
    echo ""
    read -p "按回车开始登录..."
    npx vercel login
    echo ""
    echo "✅ 登录完成！请重新运行此脚本进行部署。"
    exit 0
fi

echo "✅ 已登录到 Vercel"
echo ""
echo "⚡ 开始部署..."
echo ""

npx vercel --prod

echo ""
echo "🎉 部署完成！"
echo ""
echo "📱 可以分享链接给朋友，让他们直接在浏览器玩！"
