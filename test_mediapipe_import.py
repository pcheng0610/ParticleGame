"""测试MediaPipe导入是否正常"""
import sys

print("="*60)
print("测试MediaPipe导入...")
print("="*60)

try:
    print("1. 导入mediapipe...")
    import mediapipe as mp
    print(f"   ✓ MediaPipe {mp.__version__} 导入成功")

    print("\n2. 测试mp.solutions...")
    try:
        hands = mp.solutions.hands
        drawing = mp.solutions.drawing_utils
        styles = mp.solutions.drawing_styles
        print("   ✓ mp.solutions.* 可用（旧版API）")
        print(f"   - mp.solutions.hands: {hands}")
        print(f"   - mp.solutions.drawing_utils: {drawing}")
        print(f"   - mp.solutions.drawing_styles: {styles}")
    except AttributeError as e:
        print(f"   ✗ mp.solutions 不可用: {e}")

    print("\n3. 测试mediapipe.tasks...")
    try:
        from mediapipe.tasks.python import vision
        print("   ✓ mediapipe.tasks.python.vision 可用（新版API）")
        print(f"   - vision: {vision}")
    except ImportError as e:
        print(f"   ✗ mediapipe.tasks 不可用: {e}")

    print("\n4. 测试mediapipe.python.solutions...")
    try:
        from mediapipe.python.solutions import hands
        from mediapipe.python.solutions import drawing_utils
        from mediapipe.python.solutions import drawing_styles
        print("   ✓ mediapipe.python.solutions.* 可用")
        print(f"   - hands: {hands}")
        print(f"   - drawing_utils: {drawing_utils}")
        print(f"   - drawing_styles: {drawing_styles}")
    except ImportError as e:
        print(f"   ✗ mediapipe.python.solutions 不可用: {e}")

    print("\n5. 检查MediaPipe模块结构...")
    import pkgutil
    print("   可用的mediapipe子模块:")
    for importer, modname, ispkg in pkgutil.iter_modules(mp.__path__, mp.__name__ + "."):
        if not modname.startswith('mediapipe._'):
            print(f"   - {modname}")
            if modname == "mediapipe.solutions" or modname == "mediapipe.tasks":
                try:
                    submodule = __import__(modname, fromlist=[''])
                    for sub_importer, sub_modname, sub_ispkg in pkgutil.iter_modules(submodule.__path__, modname + "."):
                        if not sub_modname.split('.')[-1].startswith('_'):
                            print(f"     └─ {sub_modname}")
                except:
                    pass

    print("\n" + "="*60)
    print("MediaPipe导入测试完成！")
    print("="*60)

except ImportError as e:
    print(f"\n✗ 导入失败: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n✗ 发生错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n按任意键退出...")
try:
    input()
except:
    import time
    time.sleep(3)
