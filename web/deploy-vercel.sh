#!/bin/bash

echo "🚀 部署手势控制粒子游戏到 Vercel"
echo "================================"
echo ""

cd "$(dirname "$0")"

echo "📦 使用 npx 运行 Vercel（无需安装）..."
echo ""
echo "🔐 首次使用需要登录 Vercel："
echo "   1. 浏览器会自动打开登录页面"
echo "   2. 使用 GitHub/GitLab/Bitbucket 账号登录（免费）"
echo "   3. 授权后返回终端继续"
echo ""
echo "⚡ 开始部署..."
echo ""

npx vercel --prod

echo ""
echo "🎉 部署完成！"
echo ""
echo "📝 提示："
echo "   - 首次部署会要求配置项目"
echo "   - 直接按回车使用默认配置即可"
echo "   - 部署完成后会得到一个永久链接"
echo "   - 可以分享给任何人直接在浏览器玩！"
