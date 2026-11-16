# 大麦抢票助手 - exe 打包目录

## 目录结构

```
exe-packer/
├── 一键打包.bat        ← 双击即可打包
├── build.py            ← 打包脚本（检查依赖→检查zip→PyInstaller打包）
├── build.spec          ← PyInstaller 配置（onefile 模式）
├── bootstrap.py        ← exe 启动引导器（首次运行从内嵌zip解压env）
├── install_env.py      ← 环境检测脚本（纯离线，只从内嵌zip恢复）
├── env_bundle.zip      ← env 环境压缩包（97MB，含 node/appium/platform-tools）
└── README.md           ← 本文件
```

## 前提条件

### Python 依赖（需提前手动安装）

```bash
pip install pyinstaller psutil Appium-Python-Client selenium
```

打包脚本只检查依赖是否已安装，不在线安装（避免网络问题）。

### env_bundle.zip（必须提前放好）

`env_bundle.zip` 是已压缩好的 env 环境包，内含：

- `node/` — Node.js（含 node.exe, npm）
- `appium/` — Appium（含 build/lib/main.js, .appium/node_modules/uiautomator2-driver）
- `platform-tools/` — Android Platform Tools（含 adb.exe）

打包时直接内嵌进 exe，不需要再压缩，打包更快。

## 快速开始

### 双击 bat（推荐）

1. 确保 Python 依赖和 env_bundle.zip 已就绪
2. 双击 `一键打包.bat`
3. 等待打包完成，exe 输出到 `exe-packer/dist/抢票助手.exe`

### 命令行

```bash
cd exe-packer
python build.py
```

## 打包流程

1. **查找 Python** — 从当前解释器 / PATH / 常见位置动态查找带 tkinter 的 Python
2. **检查 pip 依赖** — 只检查，缺失则报错退出（不在线安装）
3. **检查 env_bundle.zip** — 确认 zip 包存在
4. **PyInstaller 打包** — onefile 模式，env_bundle.zip 直接内嵌进 exe

## 输出

```
exe-packer/dist/抢票助手.exe  (约 118MB)
```

单个 exe 内含一切：Python 运行时 + GUI + 抢票逻辑 + env 压缩包。
首次双击运行时自动解压 env 到 exe 同级目录（约30秒），之后秒开。

## 纯离线说明

- 打包过程不联网（不下载依赖、不下载 env、不压缩 env）
- exe 运行时不联网（env 从 exe 内嵌的 zip 解压）
- 客户端网络不通也能正常使用
