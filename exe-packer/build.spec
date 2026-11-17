# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec - 大麦抢票助手 单 exe 完整版
入口: bootstrap.py（首次运行自动解压 env_bundle.zip）
模式: onefile（所有内容打包成一个 exe）

注意：此 spec 文件放在 exe-packer/ 目录下运行
     需要的源码文件从 大麦抢票助手/ 和 damai_appium/ 读取
"""
import os
import glob
from PyInstaller.utils.hooks import copy_metadata

block_cipher = None

# exe-packer 目录
packer_dir = SPECPATH
# 项目根目录
project_root = os.path.normpath(os.path.join(packer_dir, '..'))
# 大麦抢票助手 目录（gui_app.py 等源码在这里）
gui_dir = os.path.join(project_root, 'gui')
# damai_appium 目录（核心抢票逻辑）
damai_appium_dir = os.path.join(project_root, 'damai_appium')
# env 压缩包
env_zip = os.path.join(packer_dir, 'env_bundle.zip')


def find_python_with_tkinter():
    """动态查找带 tkinter 的 Python（不写死路径）"""
    import subprocess, sys

    candidates = [sys.executable]

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
        try:
            result = subprocess.run([py, '-c', 'import tkinter'], capture_output=True, timeout=5)
            if result.returncode == 0:
                return py
        except Exception:
            continue

    return sys.executable


a = Analysis(
    [os.path.join(packer_dir, 'bootstrap.py')],
    pathex=[damai_appium_dir, packer_dir, gui_dir],
    binaries=[],
    datas=[
        # gui_app.py 源码（bootstrap 会 import 它）
        (os.path.join(gui_dir, 'gui_app.py'), '.'),
        # damai_appium 模块源码
        (os.path.join(damai_appium_dir, 'damai_app_v2.py'), '.'),
        (os.path.join(damai_appium_dir, 'config.py'), '.'),
        (os.path.join(damai_appium_dir, 'config.example.jsonc'), '.'),
        # 环境一键安装脚本
        (os.path.join(packer_dir, 'install_env.py'), '.'),
        # 使用说明
        (os.path.join(gui_dir, '使用说明.txt'), '.'),
        # 内嵌的 env 压缩包（首次运行自动解压）
        (env_zip, '.') if os.path.exists(env_zip) else (),
    ] + copy_metadata('Appium-Python-Client') + copy_metadata('selenium')
      + copy_metadata('certifi') + copy_metadata('urllib3') + copy_metadata('trio')
      + copy_metadata('trio-websocket') + copy_metadata('wsproto') + copy_metadata('PySocks')
      + copy_metadata('attrs') + copy_metadata('outcome') + copy_metadata('sniffio')
      + copy_metadata('sortedcontainers') + copy_metadata('typing_extensions'),
    hiddenimports=[
        'gui_app',
        'damai_app_v2',
        'config',
        'psutil',
        'selenium',
        'appium',
        'appium.webdriver',
        'appium.options.common.base',
        'appium.webdriver.common.appiumby',
        'selenium.webdriver.common.by',
        'selenium.webdriver.support.ui',
        'selenium.webdriver.support.expected_conditions',
        'selenium.common.exceptions',
        'zipfile',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest', 'unittest', 'pydoc', 'doctest', 'pdb',
        'matplotlib', 'numpy', 'pandas', 'PIL',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='抢票助手',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        'vcruntime140.dll', 'vcruntime140_1.dll',
        'python3.dll', 'python312.dll',
        '_tkinter.pyd', 'tcl86t.dll', 'tk86t.dll',
    ],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
