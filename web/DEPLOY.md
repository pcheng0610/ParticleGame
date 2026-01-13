# 🚀 部署到 Vercel - 完整指南

## 快速部署（3分钟上线）

### 步骤 1：运行部署脚本

```bash
cd ~/ParticleGame/web
./deploy-vercel.sh
```

### 步骤 2：首次登录 Vercel

脚本会自动打开浏览器，按提示操作：

1. **选择登录方式**（推荐使用 GitHub）
   - GitHub
   - GitLab
   - Bitbucket
   - Email

2. **授权 Vercel**
   - 点击 "Authorize" 授权
   - 完成后浏览器会显示 "Authorized"

3. **返回终端**
   - 登录成功后，自动继续部署

### 步骤 3：配置项目（首次部署）

终端会询问几个问题，**直接按回车使用默认值**即可：

```bash
? Set up and deploy "~/ParticleGame/web"? [Y/n] Y
? Which scope do you want to deploy to? [你的用户名]
? Link to existing project? [y/N] N
? What's your project's name? particle-game
? In which directory is your code located? ./
```

### 步骤 4：等待部署完成

部署过程大约需要 30-60 秒：

```
🔨 Building...
✓ Build complete
🚀 Deploying...
✓ Deployment complete

https://particle-game-xxx.vercel.app
```

## ✅ 部署成功！

你会得到一个永久链接，例如：
```
https://particle-game-abc123.vercel.app
```

### 分享链接

- ✅ 任何人都可以访问
- ✅ 支持所有平台（PC/手机/平板）
- ✅ 自动 HTTPS 加密
- ✅ 全球 CDN 加速

## 🔄 更新游戏

修改代码后，重新运行即可更新：

```bash
cd ~/ParticleGame/web
./deploy-vercel.sh
```

Vercel 会自动：
- 检测代码变化
- 构建新版本
- 自动发布（链接不变）

## 📱 自定义域名（可选）

在 Vercel 控制台可以：
- 添加自定义域名
- 查看访问统计
- 管理多个部署版本

访问：https://vercel.com/dashboard

## ⚡ 其他部署选项

### 选项 A：GitHub Pages（免费）

```bash
# 1. 创建 gh-pages 分支
git checkout -b gh-pages

# 2. 推送 web 目录
git subtree push --prefix web origin gh-pages

# 3. 在 GitHub 仓库设置中启用 Pages
# 访问：https://你的用户名.github.io/ParticleGame/
```

### 选项 B：Netlify（免费）

1. 访问 https://app.netlify.com/drop
2. 拖拽 `web` 文件夹到页面
3. 自动生成链接

### 选项 C：本地运行

```bash
cd ~/ParticleGame/web
./start.sh
```

## 🐛 故障排除

### 问题 1：登录失败
**解决**：确保浏览器能访问 vercel.com

### 问题 2：部署超时
**解决**：检查网络连接，重新运行脚本

### 问题 3：权限错误
**解决**：确保脚本有执行权限
```bash
chmod +x deploy-vercel.sh
```

### 问题 4：端口被占用（本地测试）
**解决**：使用 start.sh 自动查找可用端口
```bash
./start.sh
```

## 💡 提示

- Vercel 免费套餐完全够用
- 部署次数无限制
- 流量额度：每月 100GB
- 没有广告
- 自动 HTTPS

## 🔗 相关链接

- Vercel 文档：https://vercel.com/docs
- Vercel 控制台：https://vercel.com/dashboard
- 项目 README：[../README.md](../README.md)
