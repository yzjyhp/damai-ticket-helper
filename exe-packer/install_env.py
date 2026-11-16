# -*- coding: UTF-8 -*-
"""
大麦抢票助手 - 环境检测脚本（纯离线，不下载任何东西）
检测 env 目录是否完整，缺失时提示用户从 exe 内嵌的 env_bundle.zip 解压。
"""
import os
import sys
import zipfile
import shutil
import time

# ---------- 路径 ----------
if getattr(sys, 'frozen', False):
    ROOT = os.environ.get('DMQ_DATA_DIR', os.path.dirname(sys.executable))
    ENV = os.environ.get('DMQ_ENV_DIR', os.path.join(ROOT, 'env'))
else:
    ROOT = os.path.dirname(os.path.abspath(__file__))
    ENV = os.path.join(ROOT, 'env')


def log(msg):
    print(msg, flush=True)


def check_node():
    return os.path.exists(os.path.join(ENV, 'node', 'node.exe'))


def check_appium():
    return os.path.exists(os.path.join(ENV, 'appium', 'build', 'lib', 'main.js'))


def check_uiautomator2():
    return os.path.exists(os.path.join(ENV, 'appium', '.appium', 'node_modules', 'appium-uiautomator2-driver'))


def check_adb():
    return os.path.exists(os.path.join(ENV, 'platform-tools', 'adb.exe'))


def check_all():
    """检查所有组件，返回 (是否完整, 缺失列表)"""
    missing = []
    checks = [
        ('node', 'Node.js', check_node),
        ('appium', 'Appium', check_appium),
        ('uiautomator2', 'uiautomator2驱动', check_uiautomator2),
        ('adb', 'Platform Tools (adb)', check_adb),
    ]
    for code, name, fn in checks:
        if fn():
            log(f"  {name}: OK")
        else:
            log(f"  {name}: 缺失")
            missing.append(name)
    return len(missing) == 0, missing


def find_bundled_zip():
    """查找 exe 内嵌的 env_bundle.zip"""
    meipass = getattr(sys, '_MEIPASS', None)
    if meipass:
        candidate = os.path.join(meipass, 'env_bundle.zip')
        if os.path.exists(candidate):
            return candidate
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(script_dir, 'env_bundle.zip')
    if os.path.exists(candidate):
        return candidate
    return None


def extract_env(zip_path, env_dir):
    """从 env_bundle.zip 解压到目标目录"""
    os.makedirs(os.path.dirname(env_dir), exist_ok=True)
    log(f"正在解压运行环境到: {env_dir}")
    log("（首次运行需要约30秒，请耐心等待...）")

    start = time.time()
    with zipfile.ZipFile(zip_path, 'r') as zf:
        total = len(zf.namelist())
        for i, name in enumerate(zf.namelist(), 1):
            zf.extract(name, env_dir)
            if i % 3000 == 0:
                log(f"  进度: {i}/{total} ({i*100//total}%)")
    elapsed = time.time() - start
    log(f"解压完成！耗时 {elapsed:.0f} 秒")


def restore_from_bundle():
    """从 exe 内嵌的 env_bundle.zip 恢复 env"""
    zip_path = find_bundled_zip()
    if not zip_path:
        log("未找到内置环境包 env_bundle.zip")
        return False

    log(f"发现内置环境包: {zip_path}")

    # 清理残留的不完整 env
    if os.path.exists(ENV):
        shutil.rmtree(ENV, ignore_errors=True)

    extract_env(zip_path, ENV)

    ok, missing = check_all()
    if ok:
        log("环境恢复成功！")
        return True
    else:
        log(f"解压后仍缺失: {', '.join(missing)}")
        return False


def main():
    os.makedirs(ENV, exist_ok=True)
    log("=" * 50)
    log("大麦抢票助手 - 环境检测")
    log("=" * 50)
    log("\n[检测中...]")
    ok, missing = check_all()

    if ok:
        log("\n所有环境组件就绪")
        return True

    log(f"\n缺失 {len(missing)} 个组件: {', '.join(missing)}")
    log("\n尝试从内置环境包恢复...")
    return restore_from_bundle()


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
