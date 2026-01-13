# 手势控制粒子游戏 - 打包说明

## 🎮 游戏介绍

这是一个使用手势控制粒子攻击怪物的互动游戏，支持波次挑战、连击系统、多种怪物类型和Boss战。

## 📦 打包方法

### 方法1：使用打包脚本（推荐）

#### Linux/Mac:
```bash
chmod +x build_game.sh
./build_game.sh
```

#### Windows:
```bash
build_game.bat
```

### 方法2：手动打包

#### 1. 安装依赖
```bash
pip install pyinstaller opencv-python mediapipe numpy
```

#### 2. 打包命令

**Linux/Mac:**
```bash
pyinstaller --onefile --name "ParticleGame" particle_game.py
```

**Windows:**
```bash
pyinstaller --onefile --name "ParticleGame" --icon=icon.ico particle_game.py
```

**Mac (App包):**
```bash
pyinstaller --onefile --windowed --name "ParticleGame" particle_game.py
```

#### 3. 找到可执行文件
打包完成后，可执行文件在 `dist/` 目录中：
- Linux: `dist/ParticleGame`
- Windows: `dist/ParticleGame.exe`
- Mac: `dist/ParticleGame.app`

## 🚀 分发给他人

### 方案A：单个可执行文件（简单但体积大）

1. 使用上述打包方法生成可执行文件
2. 直接分享 `dist/ParticleGame` 或 `ParticleGame.exe`
3. 用户双击即可运行（需要有摄像头）

**优点：** 一个文件，简单方便
**缺点：** 文件较大（约200-300MB），包含了整个Python运行时

### 方案B：Docker容器（跨平台）

创建 `Dockerfile`:
```dockerfile
FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1

# 安装Python依赖
RUN pip install opencv-python mediapipe numpy

# 复制游戏文件
COPY particle_game.py /app/particle_game.py
WORKDIR /app

# 运行游戏
CMD ["python", "particle_game.py"]
```

运行命令：
```bash
docker build -t particle-game .
docker run -it --device=/dev/video0 -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix particle-game
```

### 方案C：在线分发（最方便）

#### 1. GitHub Releases
```bash
# 1. 创建Git仓库
git init
git add particle_game.py README.md requirements.txt
git commit -m "Initial commit"

# 2. 推送到GitHub
git remote add origin <your-github-repo>
git push -u origin main

# 3. 创建Release并上传打包好的可执行文件
```

#### 2. 提供安装脚本

创建 `install.sh`:
```bash
#!/bin/bash
echo "正在安装手势控制粒子游戏..."
pip install opencv-python mediapipe numpy
wget https://github.com/your-repo/particle_game.py
python particle_game.py
```

### 方案D：Web版本（最先进）

使用 Streamlit 或 Gradio 将游戏转换为Web应用：

```python
# web_game.py
import streamlit as st
# ... 将游戏改造为Web版本
```

部署到：
- Streamlit Cloud（免费）
- Heroku
- Railway
- Render

## 📋 依赖列表

创建 `requirements.txt`:
```
opencv-python==4.8.0.74
mediapipe==0.10.3
numpy==1.24.3
```

用户可以通过以下命令安装：
```bash
pip install -r requirements.txt
```

## 🎯 不同平台的注意事项

### Windows
- 可能需要安装 Visual C++ Redistributable
- 确保摄像头驱动正常
- 某些杀毒软件可能会误报，需要添加信任

### Linux
- 需要安装摄像头驱动 (v4l2)
- 可能需要给予摄像头权限: `sudo usermod -a -G video $USER`

### Mac
- 首次运行需要授予摄像头权限
- M1/M2芯片可能需要使用 Rosetta

## 📊 文件大小对比

| 方式 | 文件大小 | 优点 | 缺点 |
|------|---------|------|------|
| 源代码 | ~60KB | 最小 | 需要Python环境 |
| PyInstaller单文件 | ~250MB | 独立运行 | 体积大 |
| Docker镜像 | ~800MB | 隔离环境 | 需要Docker |
| Web应用 | 0（云端） | 无需安装 | 需要网络 |

## 🔧 优化打包体积

如果觉得打包文件太大，可以使用以下方法优化：

```bash
# 排除不必要的模块
pyinstaller --onefile \
    --exclude-module matplotlib \
    --exclude-module pandas \
    --exclude-module scipy \
    particle_game.py

# 使用UPX压缩（需要安装UPX）
pyinstaller --onefile --upx-dir=/usr/bin particle_game.py
```

## 🌐 推荐分发方式

### 给普通用户（首选）
1. **Windows用户**：打包成 `.exe` 文件
2. **Mac用户**：打包成 `.app` 文件
3. **Linux用户**：提供 `.AppImage` 格式

### 给开发者
提供源代码 + requirements.txt，让他们自行运行

### 给所有人（最佳）
创建一个简单的网站：
- 提供各平台的可执行文件下载
- 提供在线Web版本
- 提供源代码链接

## 🎮 启动器脚本

创建一个简单的启动器，自动检查依赖：

```python
# launcher.py
import subprocess
import sys

def check_dependencies():
    """检查并安装依赖"""
    required = ['cv2', 'mediapipe', 'numpy']
    missing = []

    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"正在安装缺失的依赖: {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] +
                            ['opencv-python' if p == 'cv2' else p for p in missing])

if __name__ == "__main__":
    check_dependencies()
    import particle_game
    particle_game.main()
```

## 📞 支持与反馈

打包完成后，建议提供：
1. 简单的使用说明（README）
2. 常见问题解答（FAQ）
3. 反馈渠道（GitHub Issues、邮箱等）
4. 演示视频或GIF

祝你的游戏分享顺利！🎉
