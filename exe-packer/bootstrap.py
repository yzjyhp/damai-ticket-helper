# -*- coding: UTF-8 -*-
"""
大麦抢票助手 - 启动引导器
职责：检查 env 是否已解压到本地，没有则从 exe 内嵌的 env_bundle.zip 解压，
然后启动 GUI（gui_app.py 的 main）。

首次运行解压 env 时会显示进度窗口，避免用户以为程序卡死。
纯离线：不下载任何东西，环境只从 exe 内嵌的 zip 解压。
"""
import os
import sys
import zipfile
import shutil
import time
import threading
import tkinter as tk
from tkinter import ttk


def get_env_dir():
    """env 目标路径：exe 所在目录下的 env"""
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), 'env')
    else:
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'exe-packer', 'env')


def get_data_dir():
    """数据目录：exe 所在目录"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'exe-packer')


def env_is_complete(env_dir):
    """检查 env 目录是否完整"""
    checks = [
        os.path.join(env_dir, 'node', 'node.exe'),
        os.path.join(env_dir, 'appium', 'build', 'lib', 'main.js'),
        os.path.join(env_dir, 'appium', '.appium', 'node_modules', 'appium-uiautomator2-driver'),
        os.path.join(env_dir, 'platform-tools', 'adb.exe'),
    ]
    return all(os.path.exists(p) for p in checks)


def find_bundled_zip():
    """查找 exe 内嵌的 env_bundle.zip"""
    meipass = getattr(sys, '_MEIPASS', None)
    if meipass:
        candidate = os.path.join(meipass, 'env_bundle.zip')
        if os.path.exists(candidate):
            return candidate
    return None


class SplashWindow:
    """启动进度窗口：首次解压 env 时显示进度，避免用户以为程序卡死"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("大麦抢票助手")
        self.root.geometry("420x200")
        # 居中显示
        self.root.eval('tk::PlaceWindow . center')
        # 禁止关闭（解压过程中不能中断）
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        self.root.resizable(False, False)

        # 标题
        tk.Label(self.root, text="大麦抢票助手", font=("Microsoft YaHei", 16, "bold")).pack(pady=(20, 5))
        # 提示文字
        self.status_var = tk.StringVar(value="正在准备运行环境...")
        tk.Label(self.root, textvariable=self.status_var, font=("Microsoft YaHei", 10)).pack(pady=(0, 10))
        # 进度条
        self.progress = ttk.Progressbar(self.root, length=360, mode='determinate')
        self.progress.pack(pady=5)
        # 百分比文字
        self.percent_var = tk.StringVar(value="0%")
        tk.Label(self.root, textvariable=self.percent_var, font=("Microsoft YaHei", 9)).pack(pady=(0, 10))
        # 底部提示
        tk.Label(self.root, text="首次启动需要解压运行环境，请耐心等待约30秒",
                 font=("Microsoft YaHei", 8), fg="#888").pack(pady=(0, 5))

        self._alive = True
        self.root.update()

    def update_progress(self, current, total):
        """更新进度条（在主线程调用）"""
        if not self._alive:
            return
        percent = int(current * 100 / total) if total > 0 else 0
        self.progress['value'] = percent
        self.percent_var.set(f"{percent}%")
        self.status_var.set(f"正在解压运行环境... ({current}/{total})")
        self.root.update_idletasks()

    def set_status(self, text):
        """更新状态文字"""
        if not self._alive:
            return
        self.status_var.set(text)
        self.root.update_idletasks()

    def close(self):
        """关闭进度窗口"""
        if not self._alive:
            return
        self._alive = False
        try:
            self.root.destroy()
        except Exception:
            pass


def extract_env_with_splash(zip_path, env_dir):
    """带进度窗口解压 env_bundle.zip"""
    splash = SplashWindow()

    try:
        os.makedirs(os.path.dirname(env_dir), exist_ok=True)

        # 先清理残留
        if os.path.exists(env_dir):
            splash.set_status("清理旧环境...")
            shutil.rmtree(env_dir, ignore_errors=True)

        # 解压
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            total = len(names)
            for i, name in enumerate(names, 1):
                zf.extract(name, env_dir)
                if i % 500 == 0 or i == total:
                    splash.update_progress(i, total)

        splash.set_status("环境准备完成！")
        time.sleep(0.5)
    finally:
        splash.close()


def ensure_env():
    """确保 env 已解压到本地，首次解压时显示进度窗口"""
    env_dir = get_env_dir()

    # 已完整 → 直接用，不显示窗口
    if env_is_complete(env_dir):
        return env_dir

    # 不完整 → 从 exe 内嵌 zip 解压（带进度窗口）
    zip_path = find_bundled_zip()
    if zip_path:
        extract_env_with_splash(zip_path, env_dir)
        if env_is_complete(env_dir):
            return env_dir
        # 解压后仍不完整
        tk.messagebox.showerror("大麦抢票助手", "环境解压后仍不完整，请重新下载 exe") if hasattr(tk, 'messagebox') else None
    else:
        # 没有内嵌 zip，弹窗提示
        root = tk.Tk()
        root.withdraw()
        from tkinter import messagebox
        messagebox.showerror("大麦抢票助手", "未找到内置环境包 env_bundle.zip\n请重新下载完整的 exe")
        root.destroy()

    return env_dir


def main():
    # 1. 确保 env 就绪（首次解压会显示进度窗口）
    env_dir = ensure_env()

    # 2. 设置路径
    data_dir = get_data_dir()
    if data_dir not in sys.path:
        sys.path.insert(0, data_dir)
    os.chdir(data_dir)

    # 3. 首次运行创建默认配置文件
    os.makedirs(data_dir, exist_ok=True)
    config_file = os.path.join(data_dir, 'config.jsonc')
    if not os.path.exists(config_file):
        meipass = getattr(sys, '_MEIPASS', None)
        example = None
        if meipass:
            example = os.path.join(meipass, 'config.example.jsonc')
        if example and os.path.exists(example):
            shutil.copy2(example, config_file)
        else:
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write('{\n  "server_url": "http://127.0.0.1:4999",\n'
                        '  "deviceName": "",\n  "platformVersion": "",\n'
                        '  "keyword": "",\n  "users": [],\n  "city": "",\n'
                        '  "date": "",\n  "session_index": 0,\n  "price": "",\n'
                        '  "price_index": 0,\n  "if_commit_order": true,\n'
                        '  "submit_max_retries": 10,\n  "delays": {}\n}\n')

    # 4. 设置环境变量供 gui_app 读取
    if getattr(sys, 'frozen', False):
        os.environ['DMQ_ENV_DIR'] = env_dir
        os.environ['DMQ_DATA_DIR'] = data_dir

    # 5. 启动 GUI
    from gui_app import main as gui_main
    gui_main()


if __name__ == '__main__':
    main()
