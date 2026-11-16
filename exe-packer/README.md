# 大麦抢票助手 - exe 打包目录

## 目录结构

```
exe-packer/
├── 一键打包.bat        ← 双击即可打包（自动检查 Python + 依赖 + 清理 + 打包）
├── build.py            ← Python 打包脚本（检查依赖 → 检查源码 → 检查 zip → PyInstaller）
├── build.spec          ← PyInstaller 配置（onefile 模式，内嵌 env_bundle.zip）
├── bootstrap.py        ← exe 启动引导器（首次运行解压 env，带进度窗口）
├── install_env.py      ← 环境检测脚本（纯离线，从内嵌 zip 恢复 env）
├── env_bundle.zip      ← env 环境压缩包（97MB，含 node/appium/platform-tools）
└── README.md           ← 本文件
```

## 前提条件

### Python（需带 tkinter）

- Python 3.10+
- 安装时勾选 `tcl/tk`（官方安装包默认包含）
- bat 脚本会自动查找带 tkinter 的 Python，无需手动配置

### pip 依赖（需提前手动安装）

```bash
pip install pyinstaller psutil Appium-Python-Client selenium
```

bat 和 build.py 只检查依赖是否已安装，**不在线安装**（避免网络问题）。

### env_bundle.zip（必须提前放好）

`env_bundle.zip` 是已压缩好的 env 环境包，放到 `exe-packer/` 目录下，内含：

| 目录 | 内容 | 大小 |
|------|------|------|
| `node/` | Node.js（含 node.exe, npm） | ~103MB |
| `appium/` | Appium + uiautomator2 驱动 | ~153MB |
| `platform-tools/` | Android Platform Tools（含 adb.exe） | ~16MB |

压缩后约 97MB，打包时直接内嵌进 exe，不需要再压缩。

## 快速开始

### 双击 bat（推荐）

1. 确保 pip 依赖和 env_bundle.zip 已就绪
2. 双击 `一键打包.bat`
3. 等待打包完成，exe 输出到 `exe-packer/dist/抢票助手.exe`

bat 执行流程：

```
Step 1: Check Python Environment   ← 查找带 tkinter 的 Python
Step 2: Check pip Dependencies     ← 检查 4 个 pip 包是否已安装
Step 3: Clean previous build       ← 删除上次的 build/ 和 dist/
Step 4: Run build.py               ← PyInstaller 打包
```

每一步失败都会显示错误信息并暂停，不会继续执行。

### 命令行

```bash
cd exe-packer
python build.py
```

build.py 执行流程：

1. **查找 Python** — 从当前解释器 / PATH / 常见位置动态查找
2. **检查 pip 依赖** — 只检查，缺失则报错退出
3. **检查源码文件** — 验证 8 个源码文件是否齐全（gui_app.py / damai_app_v2.py 等）
4. **检查 env_bundle.zip** — 确认 zip 包存在
5. **PyInstaller 打包** — onefile 模式，env_bundle.zip 内嵌进 exe

## 输出

```
exe-packer/dist/抢票助手.exe  (约 117MB)
```

单个 exe 内含一切：
- Python 运行时 + tkinter GUI 框架
- 抢票逻辑源码（gui_app.py / damai_app_v2.py / config.py）
- psutil / selenium / appium-python-client 依赖库
- env_bundle.zip（Node.js + Appium + adb 运行环境）

## exe 运行机制

### 首次运行

双击 `抢票助手.exe` → 显示进度窗口：

```
┌─────────────────────────────────────┐
│         大麦抢票助手                 │
│                                     │
│   正在解压运行环境... (7500/15277)   │
│   ████████████░░░░░░░░  49%         │
│                                     │
│   首次启动需要解压运行环境，         │
│   请耐心等待约30秒                   │
└─────────────────────────────────────┘
```

env 解压到 exe 同级目录的 `env/` 文件夹，约 30 秒。

### 后续运行

env 已存在 → 直接启动 GUI，秒开。

### 环境损坏

点「一键检测环境」→ 从 exe 内嵌的 zip 重新解压恢复（纯离线，不联网）。

## 纯离线说明

- **打包时不联网**：不下载依赖、不下载 env、不压缩 env
- **运行时不联网**：env 从 exe 内嵌的 zip 解压
- **客户端网络不通也能正常使用**

## 环境变量（可选）

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `PYTHON` | 指定 Python 解释器路径 | `C:\Python312\python.exe` |

bat 会优先检查 `PYTHON` 环境变量，找不到再从常见位置搜索。
