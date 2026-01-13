"""测试所有必要的导入是否正常"""
import sys
import platform

print("="*60)
print("测试导入所有依赖...")
print("="*60)
print(f"Python版本: {sys.version}")
print(f"平台: {platform.system()} {platform.release()}")
print("="*60)
print()

try:
    print("1. 测试 NumPy...")
    import numpy as np
    print(f"   ✓ NumPy {np.__version__} 导入成功")

    print("2. 测试 OpenCV...")
    import cv2
    print(f"   ✓ OpenCV {cv2.__version__} 导入成功")

    print("3. 测试 MediaPipe...")
    import mediapipe as mp
    print(f"   ✓ MediaPipe {mp.__version__} 导入成功")

    print("4. 测试 MediaPipe Solutions...")
    try:
        mp_hands = mp.solutions.hands
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        print("   ✓ MediaPipe Solutions 导入成功（标准方式）")
    except AttributeError:
        from mediapipe.python.solutions import hands as mp_hands
        from mediapipe.python.solutions import drawing_utils as mp_drawing
        from mediapipe.python.solutions import drawing_styles as mp_drawing_styles
        print("   ✓ MediaPipe Solutions 导入成功（兼容方式）")

    print("5. 测试 Platform 模块...")
    import platform
    print(f"   ✓ Platform 模块导入成功")

    print()
    print("="*60)
    print("所有依赖测试通过！✓")
    print("="*60)

except ImportError as e:
    print(f"\n✗ 导入失败: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n✗ 发生错误: {e}")
    sys.exit(1)

print("\n按任意键退出...")
try:
    input()
except:
    import time
    time.sleep(3)
