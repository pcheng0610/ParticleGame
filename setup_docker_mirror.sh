#!/bin/bash
# 配置Docker镜像加速器

echo "=========================================="
echo "  配置Docker镜像加速器"
echo "=========================================="
echo ""

# 检查是否已有配置
if [ -f /etc/docker/daemon.json ]; then
    echo "⚠️  检测到已有Docker配置文件"
    echo "   文件位置: /etc/docker/daemon.json"
    echo ""
    read -p "是否要备份并覆盖？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "已取消"
        exit 0
    fi
    sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.bak
    echo "✓ 已备份原配置"
fi

# 创建配置目录
sudo mkdir -p /etc/docker

# 配置镜像加速器
echo "📦 配置镜像加速器..."
sudo tee /etc/docker/daemon.json > /dev/null <<'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://registry.docker-cn.com",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
EOF

echo "✓ 配置完成"
echo ""

# 重启Docker服务
echo "🔄 重启Docker服务..."
sudo systemctl daemon-reload
sudo systemctl restart docker

echo ""
echo "=========================================="
echo "  配置完成！"
echo "=========================================="
echo ""
echo "现在可以运行打包脚本了："
echo "  sudo ./build_with_docker.sh"
echo ""
