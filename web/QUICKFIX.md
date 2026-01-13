# 🔧 快速修复指南

## 问题：浏览器无法访问摄像头

### ✅ 解决方案

刚刚已经修复了代码！请按以下步骤操作：

1. **清除浏览器缓存**（重要！）
   - **Chrome/Edge**: 按 `Ctrl+Shift+Delete` → 清除缓存
   - **Firefox**: 按 `Ctrl+Shift+Delete` → 清除缓存
   - 或者按 `Ctrl+Shift+R` 强制刷新页面

2. **重新启动本地服务器**
   ```bash
   cd ~/ParticleGame/web
   ./start.sh
   ```

3. **在浏览器打开**
   - 访问显示的地址（例如 http://localhost:8081）
   - 允许摄像头权限
   - 点击"开始游戏"

### 🌐 部署到 Vercel（推荐，避免本地问题）

部署到 Vercel 后，通过 HTTPS 访问可以解决很多权限问题。

#### 步骤 1：登录 Vercel

```bash
cd ~/ParticleGame/web
npx vercel login
```

会提示输入邮箱，然后：
- 在邮箱中点击验证链接
- 返回终端继续

#### 步骤 2：部署

```bash
npx vercel --prod
```

按提示操作：
```
? Set up and deploy? Yes
? Which scope? [你的用户名]
? Link to existing project? No
? What's your project's name? particle-game
? In which directory is your code located? ./
```

#### 步骤 3：完成

会得到一个永久链接：
```
✅ Production: https://particle-game-xxx.vercel.app
```

## 🐛 如果还是不行

### 检查清单

1. **浏览器兼容性**
   - ✅ Chrome 70+
   - ✅ Firefox 65+
   - ✅ Edge 79+
   - ⚠️ Safari 需要 12+

2. **摄像头权限**
   - 浏览器地址栏左侧有摄像头图标
   - 点击 → 允许访问

3. **HTTPS 或 localhost**
   - `http://localhost:xxxx` ✅
   - `http://127.0.0.1:xxxx` ✅
   - `http://192.168.x.x:xxxx` ❌（需要 HTTPS）

4. **摄像头未被占用**
   - 关闭其他使用摄像头的应用
   - 检查是否有其他标签页在用摄像头

## 📱 最简单的方法

**直接部署到 Vercel！**

一行命令搞定：
```bash
cd ~/ParticleGame/web && npx vercel login && npx vercel --prod
```

这样：
- ✅ 自动 HTTPS
- ✅ 全球访问
- ✅ 无需本地服务器
- ✅ 手机也能玩

## 💡 临时方案

如果急着测试，可以先用 Python 版本：

```bash
cd ~/ParticleGame
python3 particle_game.py
```

Python 版本不需要 HTTPS，可以直接访问摄像头。
