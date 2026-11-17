# -*- coding: UTF-8 -*-
"""
大麦抢票助手 - 启动引导器
职责：逐步校验/解压运行环境，显示带编号的进度窗口，然后启动 GUI。

纯离线：不下载任何东西，环境只从 exe 内嵌的 env_bundle.zip 解压。
"""
import os
import sys
import zipfile
import shutil
import time
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox


# ---------- 路径 ----------
def get_env_dir():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), 'env')
    else:
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'exe-packer', 'env')


def get_data_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'exe-packer')


def find_bundled_zip():
    meipass = getattr(sys, '_MEIPASS', None)
    if meipass:
        candidate = os.path.join(meipass, 'env_bundle.zip')
        if os.path.exists(candidate):
            return candidate
    return None


# ---------- 校验函数 ----------
def _check_node(env_dir):
    node_exe = os.path.join(env_dir, 'node', 'node.exe')
    if not os.path.isfile(node_exe):
        return False, "node.exe 不存在"
    try:
        r = subprocess.run([node_exe, '--version'], capture_output=True, text=True, timeout=10,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if r.returncode != 0:
            return False, "执行失败"
        return True, r.stdout.strip()
    except Exception as e:
        return False, f"执行异常 ({e})"


def _check_appium(env_dir):
    appium_js = os.path.join(env_dir, 'appium', 'build', 'lib', 'main.js')
    if not os.path.isfile(appium_js):
        return False, "main.js 不存在"
    return True, "OK"


def _check_uiautomator2(env_dir):
    driver_path = os.path.join(env_dir, 'appium', '.appium', 'node_modules', 'appium-uiautomator2-driver')
    if not os.path.isdir(driver_path):
        return False, "驱动目录不存在"
    pkg_json = os.path.join(driver_path, 'package.json')
    if not os.path.isfile(pkg_json):
        return False, "package.json 不存在"
    return True, "OK"


def _check_adb(env_dir):
    adb_exe = os.path.join(env_dir, 'platform-tools', 'adb.exe')
    if not os.path.isfile(adb_exe):
        return False, "adb.exe 不存在"
    try:
        r = subprocess.run([adb_exe, 'version'], capture_output=True, text=True, timeout=10,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if r.returncode != 0:
            return False, "执行失败"
        return True, "OK"
    except Exception as e:
        return False, f"执行异常 ({e})"


# ---------- 模块解压 ----------
# env_bundle.zip 内每个模块对应的顶层目录名
MODULE_ZIP_NAMES = {
    'node': 'node',
    'appium': 'appium',
    'platform-tools': 'platform-tools',
}


def _extract_module(zip_path, env_dir, module_name, splash):
    """从 env_bundle.zip 中只解压指定模块的文件，显示子进度"""
    module_prefix = MODULE_ZIP_NAMES.get(module_name, module_name) + '/'

    with zipfile.ZipFile(zip_path, 'r') as zf:
        # 筛选属于该模块的文件
        member_names = [n for n in zf.namelist() if n.startswith(module_prefix)]
        total = len(member_names)
        if total == 0:
            return False

        # 先删除旧的模块目录
        module_dir = os.path.join(env_dir, module_name)
        if os.path.exists(module_dir):
            shutil.rmtree(module_dir, ignore_errors=True)

        for i, name in enumerate(member_names, 1):
            zf.extract(name, env_dir)
            if i % 200 == 0 or i == total:
                splash.update_sub_progress(i, total)


# ---------- 路径修复 ----------
def _fix_extensions_paths(env_dir):
    yaml_paths = [
        os.path.join(env_dir, 'appium', '.appium', 'node_modules', '.cache', 'appium', 'extensions.yaml'),
        os.path.join(env_dir, 'appium', 'node_modules', '.cache', 'appium', 'extensions.yaml'),
    ]
    correct_appium_home = os.path.join(env_dir, 'appium', '.appium').replace('/', '\\')
    for yaml_path in yaml_paths:
        if not os.path.isfile(yaml_path):
            continue
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            changed = False
            for i, line in enumerate(lines):
                if 'installPath' in line and '.appium' in line:
                    idx = line.find('.appium')
                    after_appium = line[idx + len('.appium'):]
                    lines[i] = f'    installPath: {correct_appium_home}{after_appium}'
                    changed = True
            if changed:
                with open(yaml_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
        except Exception:
            pass


# ---------- 进度窗口 ----------
class SplashWindow:
    """带步骤列表 + 双进度条的启动窗口"""

    # 检查项定义：(编号, 名称, 检查函数, 模块名(用于解压))
    STEPS = [
        (1, "Node.js 运行环境", _check_node, 'node'),
        (2, "Appium 自动化服务", _check_appium, 'appium'),
        (3, "uiautomator2 驱动", _check_uiautomator2, 'appium'),  # 和 appium 同包
        (4, "Android Debug Bridge (adb)", _check_adb, 'platform-tools'),
    ]

    def __init__(self, subtitle=""):
        self.root = tk.Tk()
        self.root.title("大麦抢票助手")
        self.root.geometry("480x360")
        self.root.eval('tk::PlaceWindow . center')
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        self.root.resizable(False, False)

        tk.Label(self.root, text="大麦抢票助手", font=("Microsoft YaHei", 16, "bold")).pack(pady=(15, 3))
        if subtitle:
            tk.Label(self.root, text=subtitle, font=("Microsoft YaHei", 8), fg="#888").pack(pady=(0, 5))

        # 步骤列表区
        steps_frame = ttk.Frame(self.root)
        steps_frame.pack(fill="x", padx=20, pady=5)
        self.step_labels = {}
        for num, name, _, _ in self.STEPS:
            row = ttk.Frame(steps_frame)
            row.pack(fill="x", pady=2)
            lbl = tk.Label(row, text=f"  {num}. {name}", font=("Microsoft YaHei", 10), fg="#666")
            lbl.pack(side="left")
            mark = tk.Label(row, text="", font=("Microsoft YaHei", 10))
            mark.pack(side="right")
            self.step_labels[num] = (lbl, mark)

        # 主进度条
        ttk.Label(self.root, text="", ).pack(pady=(5, 0))
        self.status_var = tk.StringVar(value="")
        tk.Label(self.root, textvariable=self.status_var, font=("Microsoft YaHei", 9)).pack(pady=(2, 2))
        self.progress = ttk.Progressbar(self.root, length=420, mode='determinate')
        self.progress.pack(pady=2)

        # 子进度条（模块解压时用）
        self.sub_status_var = tk.StringVar(value="")
        self.sub_status_lbl = tk.Label(self.root, textvariable=self.sub_status_var, font=("Microsoft YaHei", 8), fg="#888")
        self.sub_status_lbl.pack(pady=(2, 0))
        self.sub_progress = ttk.Progressbar(self.root, length=420, mode='determinate')
        self.sub_progress.pack(pady=2)

        self._alive = True
        self.root.update()

    def set_step_status(self, step_num, status, ok=None):
        """更新某步骤的状态标记: status='checking'/'ok'/'fail'/'extracting'"""
        if not self._alive or step_num not in self.step_labels:
            return
        lbl, mark = self.step_labels[step_num]
        if status == 'checking':
            lbl.config(fg="#1565C0")  # 蓝色=正在检查
            mark.config(text="...", fg="#1565C0")
        elif status == 'ok':
            lbl.config(fg="#2E7D32")  # 绿色=通过
            mark.config(text="OK", fg="#2E7D32")
        elif status == 'fail':
            lbl.config(fg="#C62828")  # 红色=失败
            mark.config(text="FAIL", fg="#C62828")
        elif status == 'extracting':
            lbl.config(fg="#E65100")  # 橙色=正在解压
            mark.config(text="解压中...", fg="#E65100")
        elif status == 'extracted':
            lbl.config(fg="#2E7D32")
            mark.config(text="已修复", fg="#2E7D32")
        self.root.update_idletasks()

    def update_progress(self, current, total, status=None):
        if not self._alive:
            return
        percent = int(current * 100 / total) if total > 0 else 0
        self.progress['value'] = percent
        if status:
            self.status_var.set(status)
        self.root.update_idletasks()

    def update_sub_progress(self, current, total, status=None):
        """更新子进度条（模块解压进度）"""
        if not self._alive:
            return
        percent = int(current * 100 / total) if total > 0 else 0
        self.sub_progress['value'] = percent
        if status:
            self.sub_status_var.set(status)
        else:
            self.sub_status_var.set(f"解压中... {current}/{total}")
        self.root.update_idletasks()

    def hide_sub_progress(self):
        if not self._alive:
            return
        self.sub_progress['value'] = 0
        self.sub_status_var.set("")
        self.root.update_idletasks()

    def set_status(self, text):
        if not self._alive:
            return
        self.status_var.set(text)
        self.root.update_idletasks()

    def close(self):
        if not self._alive:
            return
        self._alive = False
        try:
            self.root.destroy()
        except Exception:
            pass


# ---------- 主流程 ----------
def ensure_env():
    """逐步校验 + 按需解压，带编号进度窗口"""
    env_dir = get_env_dir()
    zip_path = find_bundled_zip()
    os.makedirs(env_dir, exist_ok=True)

    splash = SplashWindow("正在检查运行环境，请稍候...")

    all_ok = True
    failures = []
    total_steps = len(SplashWindow.STEPS)

    try:
        for idx, (num, name, check_fn, module_name) in enumerate(SplashWindow.STEPS):
            # 1. 标记为正在检查
            splash.update_progress(idx, total_steps, f"步骤 {num}/{total_steps}: 正在校验 {name}...")
            splash.set_step_status(num, 'checking')
            time.sleep(0.3)

            # 2. 执行检查
            ok, msg = check_fn(env_dir)

            if ok:
                # 校验通过
                splash.set_step_status(num, 'ok')
                splash.update_progress(idx + 1, total_steps, f"步骤 {num}/{total_steps}: {name} - OK")
                time.sleep(0.2)
            else:
                # 校验失败 → 尝试解压该模块
                splash.set_step_status(num, 'extracting')
                splash.update_progress(idx, total_steps, f"步骤 {num}/{total_steps}: {name} 缺失，正在解压...")

                if zip_path:
                    # 解压该模块（显示子进度）
                    _extract_module(zip_path, env_dir, module_name, splash)

                    # 如果是 appium 模块，修复路径
                    if module_name == 'appium':
                        splash.sub_status_var.set("修复驱动路径...")
                        _fix_extensions_paths(env_dir)
                        time.sleep(0.2)

                    splash.hide_sub_progress()

                    # 重新校验
                    splash.set_step_status(num, 'checking')
                    splash.update_progress(idx, total_steps, f"步骤 {num}/{total_steps}: 重新校验 {name}...")
                    time.sleep(0.3)
                    ok2, msg2 = check_fn(env_dir)

                    if ok2:
                        splash.set_step_status(num, 'extracted')
                        splash.update_progress(idx + 1, total_steps, f"步骤 {num}/{total_steps}: {name} - 已修复")
                        time.sleep(0.2)
                    else:
                        splash.set_step_status(num, 'fail')
                        splash.update_progress(idx + 1, total_steps, f"步骤 {num}/{total_steps}: {name} - FAIL")
                        failures.append(f"{num}. {name}: {msg2}")
                        all_ok = False
                        time.sleep(0.3)
                else:
                    splash.set_step_status(num, 'fail')
                    splash.update_progress(idx + 1, total_steps, f"步骤 {num}/{total_steps}: {name} - 无法修复")
                    failures.append(f"{num}. {name}: {msg}（无内置环境包）")
                    all_ok = False
                    time.sleep(0.3)

        # 汇总
        if all_ok:
            splash.update_progress(total_steps, total_steps, "所有环境校验通过！正在启动...")
            time.sleep(0.8)
        else:
            splash.update_progress(total_steps, total_steps, f"校验完成: {len(failures)} 项失败")
            time.sleep(1)
    finally:
        splash.close()

    if not all_ok:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("大麦抢票助手",
                             "环境校验未通过：\n\n" + "\n".join(failures) +
                             "\n\n请重新下载完整的 exe")
        root.destroy()

    return env_dir


def main():
    # 1. 逐步校验 + 按需解压
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
