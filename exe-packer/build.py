# -*- coding: UTF-8 -*-
"""
大麦抢票助手 - 一键打包脚本
用法: python build.py

功能:
  1. 查找带 tkinter 的 Python
  2. 检查 pip 依赖是否已安装（不在线安装，缺失则报错提示）
  3. 检查 env_bundle.zip 是否存在（env 环境已预先打好 zip 包）
  4. PyInstaller 打包 → 单文件 exe（env_bundle.zip 内嵌进 exe）
  5. 输出到 dist/抢票助手.exe

前提:
  - Python 已安装 pyinstaller / psutil / Appium-Python-Client / selenium
  - exe-packer/env_bundle.zip 已存在（含 node / appium / platform-tools 的压缩包）
"""
import os
import sys
import glob
import subprocess

# ---------- 路径 ----------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
GUI_DIR = os.path.join(PROJECT_ROOT, 'gui')
DAMAI_APPIUM_DIR = os.path.join(PROJECT_ROOT, 'damai_appium')
DIST_DIR = os.path.join(SCRIPT_DIR, 'dist')
SPEC_FILE = os.path.join(SCRIPT_DIR, 'build.spec')
ENV_BUNDLE = os.path.join(SCRIPT_DIR, 'env_bundle.zip')


# ---------- 自动切换到带 tkinter 的 Python ----------
def _has_tkinter(py):
    try:
        r = subprocess.run([py, '-c', 'import tkinter'], capture_output=True, timeout=5)
        return r.returncode == 0
    except Exception:
        return False


def _find_python_with_tkinter():
    """查找带 tkinter 的 Python（不写死路径）"""
    candidates = []

    # PYTHON 环境变量
    env_python = os.environ.get('PYTHON')
    if env_python:
        candidates.append(env_python)

    # PATH 中的 python.exe
    for d in os.environ.get('PATH', '').split(os.pathsep):
        p = os.path.join(d, 'python.exe')
        if os.path.isfile(p):
            candidates.append(p)

    # 常见安装位置（通配符）
    for pattern in [
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Python', 'Python3*', 'python.exe'),
        r'C:\Python3*\python.exe',
    ]:
        candidates.extend(glob.glob(pattern))

    # 去重
    seen = set()
    unique = []
    for c in candidates:
        c_norm = os.path.normpath(c)
        if c_norm not in seen and os.path.isfile(c_norm):
            seen.add(c_norm)
            unique.append(c_norm)

    for py in unique:
        if _has_tkinter(py):
            return py
    return None


# 如果当前 Python 没有 tkinter，自动用有 tkinter 的 Python 重新执行本脚本
# 用 subprocess.run 而非 os.execv，确保 stdout/stderr 正确输出到 cmd 窗口
if not _has_tkinter(sys.executable):
    good_python = _find_python_with_tkinter()
    if good_python and os.path.normpath(good_python) != os.path.normpath(sys.executable):
        print(f"切换到带 tkinter 的 Python: {good_python}")
        result = subprocess.run([good_python] + sys.argv)
        sys.exit(result.returncode)
    else:
        print("ERROR: 当前 Python 没有 tkinter，且找不到其他带 tkinter 的 Python")
        print("请安装 Python 时勾选 tcl/tk，或设置 PYTHON 环境变量指向正确的 python.exe")
        sys.exit(1)

REQUIRED_PACKAGES = ['pyinstaller', 'psutil', 'Appium-Python-Client', 'selenium']


def find_python():
    """动态查找带 tkinter 的 Python（不写死路径）"""
    candidates = [sys.executable]

    env_python = os.environ.get('PYTHON')
    if env_python:
        candidates.append(env_python)

    for d in os.environ.get('PATH', '').split(os.pathsep):
        p = os.path.join(d, 'python.exe')
        if os.path.isfile(p):
            candidates.append(p)

    for pattern in [
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Python', 'Python3*', 'python.exe'),
        r'C:\Python3*\python.exe',
    ]:
        candidates.extend(glob.glob(pattern))

    seen = set()
    unique = []
    for c in candidates:
        c_norm = os.path.normpath(c)
        if c_norm not in seen and os.path.isfile(c_norm):
            seen.add(c_norm)
            unique.append(c_norm)

    for py in unique:
        try:
            result = subprocess.run([py, '-c', 'import tkinter'], capture_output=True, timeout=5)
            if result.returncode == 0:
                return py
        except Exception:
            continue

    return sys.executable


def step(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}")


def check_packages(python):
    """检查 pip 依赖是否已安装，缺失则报错退出（不在线安装）"""
    step("检查 pip 依赖")
    missing = []
    for pkg in REQUIRED_PACKAGES:
        result = subprocess.run(
            [python, '-m', 'pip', 'show', pkg],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"  {pkg}: OK")
        else:
            missing.append(pkg)
            print(f"  {pkg}: MISSING")

    if missing:
        print(f"\n  缺少依赖: {', '.join(missing)}")
        print(f"  请手动安装: pip install {' '.join(missing)}")
        return False
    return True


def check_sources():
    """检查源码文件是否齐全"""
    step("检查源码文件")
    required_files = [
        ("GUI 源码", os.path.join(GUI_DIR, 'gui_app.py')),
        ("Appium 抢票逻辑", os.path.join(DAMAI_APPIUM_DIR, 'damai_app_v2.py')),
        ("Appium 配置类", os.path.join(DAMAI_APPIUM_DIR, 'config.py')),
        ("配置示例", os.path.join(DAMAI_APPIUM_DIR, 'config.example.jsonc')),
        ("使用说明", os.path.join(GUI_DIR, '使用说明.txt')),
        ("启动引导器", os.path.join(SCRIPT_DIR, 'bootstrap.py')),
        ("环境检测脚本", os.path.join(SCRIPT_DIR, 'install_env.py')),
        ("PyInstaller 配置", os.path.join(SCRIPT_DIR, 'build.spec')),
    ]
    all_ok = True
    for name, path in required_files:
        if os.path.isfile(path):
            print(f"  {name}: OK")
        else:
            print(f"  {name}: MISSING ({path})")
            all_ok = False

    if not all_ok:
        print("\n  源码文件不完整，请检查项目目录结构")
        return False
    return True


def check_env_bundle():
    """检查 env_bundle.zip 是否存在"""
    step("检查 env_bundle.zip")
    if not os.path.isfile(ENV_BUNDLE):
        print(f"  MISSING: {ENV_BUNDLE}")
        print("  请将 env 环境（node / appium / platform-tools）压缩成 env_bundle.zip")
        print("  放到 exe-packer/ 目录下")
        return False

    size_mb = os.path.getsize(ENV_BUNDLE) / 1024 / 1024
    print(f"  OK: {ENV_BUNDLE} ({size_mb:.0f} MB)")
    return True


def build_exe(python):
    """PyInstaller 打包（实时输出日志和错误到 cmd 窗口）"""
    step("PyInstaller 打包")

    # --clean 会删除 build 目录，PyInstaller 有时不自动重建子目录导致报错
    # 提前确保 build 和 dist 目录存在
    os.makedirs(os.path.join(SCRIPT_DIR, 'build'), exist_ok=True)
    os.makedirs(DIST_DIR, exist_ok=True)

    cmd = [python, '-m', 'PyInstaller', SPEC_FILE, '--noconfirm', '--clean']
    print(f"  > {' '.join(cmd)}")
    print()
    # 不 capture stdout/stderr，让 PyInstaller 输出直接显示在 cmd 窗口
    result = subprocess.run(cmd, cwd=SCRIPT_DIR, timeout=600)
    print()
    if result.returncode != 0:
        print(f"  PyInstaller 退出码: {result.returncode}")
    return result.returncode == 0


def main():
    print("=" * 60)
    print("  大麦抢票助手 - 一键打包工具")
    print("=" * 60)

    # 1. 查找 Python
    python = find_python()
    print(f"\nPython: {python}")

    # 2. 检查 pip 依赖（只检查，不在线安装）
    if not check_packages(python):
        sys.exit(1)

    # 3. 检查源码文件
    if not check_sources():
        sys.exit(1)

    # 4. 检查 env_bundle.zip
    if not check_env_bundle():
        sys.exit(1)

    # 5. PyInstaller 打包
    if not build_exe(python):
        print("\n============================================================")
        print("  BUILD FAILED!")
        print("  请查看上方 PyInstaller 的错误输出")
        print("============================================================")
        sys.exit(1)

    # 6. 结果
    exe_path = os.path.join(DIST_DIR, '抢票助手.exe')
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / 1024 / 1024
        step("BUILD OK!")
        print(f"  exe: {exe_path}")
        print(f"  size: {size_mb:.0f} MB")
    else:
        print(f"\n  ERROR: exe not found: {exe_path}")
        sys.exit(1)


if __name__ == '__main__':
    main()
