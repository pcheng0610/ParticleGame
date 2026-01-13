# 手势控制粒子游戏 - Web 版本

## 🎮 在线体验

Web 版本可以在任何现代浏览器中运行，支持：
- ✅ Windows / Mac / Linux
- ✅ Chrome / Firefox / Edge / Safari
- ✅ 手机和平板（需要前置摄像头）

## 🚀 快速开始

### 方法 1：使用 Python 内置服务器（推荐）

```bash
cd web
python -m http.server 8000
```

然后在浏览器打开：`http://localhost:8000`

### 方法 2：使用 Node.js

```bash
cd web
npx http-server -p 8000
```

### 方法 3：直接部署到 GitHub Pages

1. 将 `web` 文件夹推送到 GitHub
2. 在仓库设置中启用 GitHub Pages
3. 访问 `https://你的用户名.github.io/ParticleGame/`

## 📝 功能特点

### Web 版优势
- 🌐 **真正的跨平台**：任何设备都能玩
- 📱 **无需安装**：直接在浏览器运行
- 🔄 **自动更新**：刷新页面即可获取最新版本
- 🚀 **易于分享**：发送链接即可

### 技术栈
- **前端**：HTML5 + Canvas + JavaScript
- **手势识别**：MediaPipe Web (CDN)
- **摄像头**：WebRTC getUserMedia API
- **粒子系统**：Canvas 2D 渲染

## 🎯 游戏玩法

### 手势控制
1. **握拳/双指并拢**：粒子聚集并加速冲向目标
2. **手掌张开（3指以上）**：粒子围绕手掌旋转
3. **自由状态**：粒子自由漂浮

### 游戏目标
- 用粒子攻击怪物（彩色大球）
- 击败所有怪物进入下一波
- 获得更高分数和连击

## 🔧 浏览器兼容性

| 浏览器 | 版本要求 | 支持情况 |
|--------|---------|---------|
| Chrome | 70+ | ✅ 完美支持 |
| Firefox | 65+ | ✅ 完美支持 |
| Edge | 79+ | ✅ 完美支持 |
| Safari | 12+ | ⚠️ 需要 iOS 14.3+ |

**注意事项**：
- 需要 HTTPS 或 localhost 环境才能访问摄像头
- 首次访问需要授予摄像头权限
- 建议使用有线摄像头以获得更好的性能

## 🐛 故障排除

### 摄像头无法打开
1. 检查浏览器是否授予了摄像头权限
2. 确认摄像头未被其他应用占用
3. 尝试使用 HTTPS 或 localhost

### 手势识别不准确
1. 确保光线充足
2. 将手掌放在摄像头前方 30-50cm
3. 背景尽量简洁

### 性能问题
1. 关闭其他占用资源的标签页
2. 降低粒子数量（修改 `game.js` 中的 `NUM_PARTICLES`）
3. 使用性能更好的浏览器（推荐 Chrome）

## 📦 部署到云端

### Vercel 部署（推荐）
```bash
# 安装 Vercel CLI
npm i -g vercel

# 部署
cd web
vercel
```

### Netlify 部署
1. 将 `web` 文件夹拖到 [Netlify Drop](https://app.netlify.com/drop)
2. 自动生成访问链接

### GitHub Pages
```bash
# 创建 gh-pages 分支
git checkout -b gh-pages
git add web/*
git commit -m "Deploy web version"
git push origin gh-pages

# 在 GitHub 仓库设置中启用 GitHub Pages
```

## 🔄 与 Python 版本的对比

| 特性 | Python 版本 | Web 版本 |
|-----|-----------|---------|
| 跨平台 | ❌ 需要打包 | ✅ 真正跨平台 |
| 安装 | ❌ 需要 Python | ✅ 无需安装 |
| 性能 | ✅ 更好 | ⚠️ 依赖浏览器 |
| 分享 | ❌ 需要分发文件 | ✅ 发送链接 |
| 更新 | ❌ 需要重新下载 | ✅ 刷新页面 |
| 粒子数量 | ✅ 500+ | ⚠️ 300 左右 |

## 🎨 自定义

### 修改粒子效果
编辑 `game.js` 中的 `CONFIG` 对象：
```javascript
const CONFIG = {
    NUM_PARTICLES: 300,      // 粒子数量
    MAX_SPEED: 15,           // 最大速度
    PARTICLE_RADIUS: 2,      // 粒子半径
    PARTICLE_COLOR: '#64C8FF' // 粒子颜色
};
```

### 修改UI样式
编辑 `index.html` 中的 `<style>` 部分

## 📄 开源协议

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 🔗 相关链接

- [Python 版本](../particle_game.py)
- [MediaPipe 文档](https://google.github.io/mediapipe/)
- [Canvas API 参考](https://developer.mozilla.org/zh-CN/docs/Web/API/Canvas_API)
