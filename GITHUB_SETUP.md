# 🚀 GitHub Actions 打包设置指南

## 步骤1：在GitHub上创建仓库

1. 访问 https://github.com/new
2. 仓库名称：`ParticleGame`（或其他你喜欢的名字）
3. 选择 **Public** 或 **Private**（都可以）
4. **不要**勾选"Initialize this repository with a README"
5. 点击 "Create repository"

## 步骤2：连接本地仓库到GitHub

复制GitHub给你的仓库地址（例如：`https://github.com/你的用户名/ParticleGame.git`），然后运行：

```bash
cd /home/pc/ParticleGame

# 添加远程仓库（替换为你的实际地址）
git remote add origin https://github.com/你的用户名/ParticleGame.git

# 推送代码
git branch -M main
git push -u origin main
```

## 步骤3：触发打包

有两种方式：

### 方式1：创建Release（推荐，会自动创建下载链接）

1. 在GitHub仓库页面，点击右侧的 **"Releases"**
2. 点击 **"Create a new release"**
3. 在"Choose a tag"中输入：`v1.0`
4. Release title：`v1.0` 或 `第一个版本`
5. 点击 **"Publish release"**

GitHub Actions会自动开始打包，大约3-5分钟后完成。

### 方式2：手动触发（不需要创建Release）

1. 在GitHub仓库页面，点击 **"Actions"** 标签
2. 选择左侧的 **"打包Windows EXE"** 工作流
3. 点击 **"Run workflow"** 按钮
4. 选择分支（通常是 `main`）
5. 点击 **"Run workflow"**

## 步骤4：下载EXE文件

### 如果使用Release方式：
- 打包完成后，回到 **"Releases"** 页面
- 点击最新版本
- 下载 `ParticleGame.exe` 文件

### 如果使用手动触发：
- 在 **"Actions"** 页面，点击运行中的工作流
- 等待完成后，在"Artifacts"部分下载 `ParticleGame-Windows`

## ✅ 完成！

现在你有了一个可以在Windows上运行的EXE文件！

---

## 🔄 后续更新

以后每次需要重新打包时：

```bash
# 修改代码后
git add .
git commit -m "更新说明"
git push

# 然后创建新的Release标签，或手动触发工作流
```

---

## ❓ 常见问题

**Q: 打包失败怎么办？**
A: 在Actions页面查看错误日志，通常是依赖问题。

**Q: 可以同时打包多个平台吗？**
A: 可以！我可以帮你添加Linux和Mac的打包配置。

**Q: 需要付费吗？**
A: 不需要！GitHub Actions对公开仓库完全免费。
