#!/usr/bin/env python3
"""
手势控制粒子游戏 - 智能启动器
自动检查并安装依赖，然后启动游戏
"""
import subprocess
import sys
import os

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("错误：需要Python 3.7或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    return True

def check_dependencies():
    """检查并安装依赖"""
    print("检查依赖...")

    required = {
        'cv2': 'opencv-python',
        'mediapipe': 'mediapipe',
        'numpy': 'numpy'
    }

    missing = []

    for module, package in required.items():
        try:
            __import__(module)
            print(f"✓ {package} 已安装")
        except ImportError:
            print(f"✗ {package} 未安装")
            missing.append(package)

    if missing:
        print(f"\n正在安装缺失的依赖: {', '.join(missing)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--upgrade"
            ] + missing)
            print("\n依赖安装完成！")
        except subprocess.CalledProcessError:
            print("\n错误：依赖安装失败")
            print("请手动运行: pip install -r requirements.txt")
            return False
    else:
        print("\n所有依赖已就绪！")

    return True

def check_camera():
    """检查摄像头是否可用"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("\n警告：无法打开摄像头！")
            print("请确保：")
            print("1. 摄像头已连接")
            print("2. 摄像头权限已授予")
            print("3. 没有其他程序占用摄像头")
            cap.release()
            return False
        cap.release()
        print("✓ 摄像头检测正常")
        return True
    except Exception as e:
        print(f"\n摄像头检测失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("  手势控制粒子游戏 - 启动器")
    print("=" * 50)
    print()

    # 检查Python版本
    if not check_python_version():
        input("\n按Enter键退出...")
        sys.exit(1)

    # 检查依赖
    if not check_dependencies():
        input("\n按Enter键退出...")
        sys.exit(1)

    print()

    # 检查摄像头
    camera_ok = check_camera()
    if not camera_ok:
        response = input("\n摄像头检测失败，是否继续？(y/n): ")
        if response.lower() != 'y':
            sys.exit(1)

    print("\n" + "=" * 50)
    print("  启动游戏...")
    print("=" * 50)
    print()

    # 启动游戏
    try:
        import particle_game
        particle_game.main()
    except Exception as e:
        print(f"\n游戏启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("\n按Enter键退出...")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n游戏已退出")
    except Exception as e:
        print(f"\n发生错误: {e}")
        input("\n按Enter键退出...")
