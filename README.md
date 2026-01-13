# 🎮 手势控制粒子游戏

一个使用手势控制粒子攻击怪物的互动游戏，支持波次挑战、连击系统和Boss战！

**🌐 现在支持 Web 版本！无需安装，直接在浏览器玩！**

![游戏截图](screenshot.png)

## 🎮 选择你的版本

| 版本 | 优势 | 劣势 | 适合人群 |
|------|------|------|----------|
| **🌐 Web 版** | ✅ 真正跨平台<br>✅ 无需安装<br>✅ 易于分享 | ⚠️ 性能略低<br>⚠️ 需要HTTPS | 推荐所有用户 |
| **🐍 Python 版** | ✅ 更好性能<br>✅ 更多粒子 | ❌ 需要安装Python<br>❌ 打包复杂 | 开发者/高级用户 |

## 🚀 快速开始

### 🌐 Web 版本（推荐）

**最简单的方式 - 3步开始玩：**

```bash
# 1. 进入 web 目录
cd web

# 2. 启动本地服务器
python -m http.server 8000

# 3. 在浏览器打开
# 访问 http://localhost:8000
```

**支持的平台：**
- ✅ Windows / Mac / Linux
- ✅ Chrome / Firefox / Edge / Safari
- ✅ 手机和平板（需要前置摄像头）

**在线部署：**
- [查看 Web 版本详细说明](web/README.md)
- 可部署到 GitHub Pages / Vercel / Netlify

### 🐍 Python 版本

#### 方法1：使用智能启动器（推荐）

```bash
# Linux/Mac
chmod +x launcher.py
python3 launcher.py

# Windows
python launcher.py
```

#### 方法2：手动安装

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行游戏
python particle_game.py
```

## ✨ 游戏特色

- 🖐️ **手势控制**：通过摄像头识别手势，控制粒子群
  - Web版：300个粒子
  - Python版：500个粒子
- 👾 **多种怪物**：普通、坦克、敏捷、Boss四种类型
- 🔥 **连击系统**：连续击中获得更高分数
- 🌊 **波次挑战**：难度逐步提升，每5波面对Boss
- 💥 **视觉特效**：击中特效、死亡动画、屏幕震动
- 🌐 **跨平台**：Web版支持所有设备和操作系统

## 🎯 操作说明

### 手势控制
- **食指和中指并拢**：粒子朝指向方向快速移动
- **握拳/双指合并**：粒子聚集并突然加速冲刺
- **手掌张开**：粒子围绕手掌圆周运动

### 键盘操作（Python版）
- **B键**：切换辅助线显示
- **R键**：重新开始游戏
- **Q/ESC/D键**：退出游戏

## 📦 打包成可执行文件（Python版）

⚠️ **注意**：由于跨平台打包的复杂性，推荐使用 **Web 版本** 进行分享！

如果仍想打包 Python 版本：

### Linux/Mac:
```bash
chmod +x build_game.sh
./build_game.sh
```

### Windows:
```bash
build_game.bat
```

打包完成后，可执行文件在 `dist/` 目录中。

详细说明请查看 [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)

## 📋 系统要求

- **Python**：3.7 或更高版本
- **摄像头**：支持标准USB摄像头或笔记本内置摄像头
- **内存**：建议 2GB 以上
- **操作系统**：Windows / Linux / macOS

### 依赖包
- opencv-python
- mediapipe
- numpy

## 🎮 游戏机制

### 怪物类型
| 类型 | 血量 | 速度 | 分数 | 特点 |
|------|------|------|------|------|
| 普通 | 10 | 中等 | 100 | 平衡型 |
| 坦克 | 20 | 慢速 | 200 | 高血量，蓝色 |
| 敏捷 | 5 | 快速 | 150 | 高速躲避，绿色 |
| Boss | 50 | 中速 | 1000 | 每5波出现，红色 |

### 得分系统
- 基础分数 = 怪物分值
- 实际得分 = 基础分数 × (1 + 连击数/10)
- 连击在2秒无击中后重置

### 波次系统
- 第1波：2个普通怪物
- 第2-4波：怪物数量和难度逐步增加
- 第5波：Boss战
- 每波之间有3秒休息时间

## 🛠️ 常见问题

### Q: 摄像头无法打开？
A: 检查：
1. 摄像头是否被其他程序占用
2. 是否授予了摄像头权限
3. Linux用户：是否在 video 用户组中

### Q: 手势识别不准确？
A: 建议：
1. 保证光线充足
2. 手部完整出现在画面中
3. 背景尽量简单

### Q: 游戏卡顿？
A: 优化方法：
1. 关闭其他占用资源的程序
2. 降低摄像头分辨率（修改代码中的配置）
3. 减少粒子数量（修改 Config.NUM_PARTICLES）

### Q: 打包文件太大？
A: 查看 BUILD_INSTRUCTIONS.md 中的优化方法

## 📝 开发说明

### 项目结构
```
.
├── web/                      # Web版本（推荐）
│   ├── index.html           # 游戏主页
│   ├── game.js              # 游戏逻辑
│   └── README.md            # Web版说明
├── particle_game.py          # Python版主文件
├── launcher.py               # 智能启动器
├── requirements.txt          # Python依赖
├── test_imports.py           # 依赖测试
├── test_mediapipe_import.py  # MediaPipe测试
└── README.md                # 本文件
```

### 修改游戏参数
编辑 `particle_game.py` 中的 `Config` 类：

```python
class Config:
    NUM_PARTICLES = 500        # 粒子数量
    MAX_SPEED = 15.0          # 最大速度
    WINDOW_WIDTH = 2560       # 窗口宽度
    WINDOW_HEIGHT = 1600      # 窗口高度
    # ... 更多配置
```

## 📄 开源协议

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请通过以下方式联系：
- GitHub Issues
- Email: your-email@example.com

## 🎉 鸣谢

- OpenCV - 计算机视觉库
- MediaPipe - 手势识别
- NumPy - 数值计算

---

⭐ 如果你喜欢这个游戏，请给个Star！
