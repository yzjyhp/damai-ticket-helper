# 大麦抢票助手（damai-ticket-helper）

> 一个基于 Appium 的大麦网移动端抢票自动化工具，带可视化图形界面。

**⚠️ 免责声明：本项目仅供技术学习与研究使用，不保证能抢到票，请配合手动抢票。请遵守大麦网及相关平台的使用条款，合理使用，勿用于商业用途。使用本工具产生的任何后果由使用者自行承担。**

---

## 下载使用（推荐）

无需搭建环境，直接下载即用 → [**前往 Releases 下载**](https://github.com/Lzhimie/damai-ticket-helper/releases/latest)

| 文件 | 说明 |
|------|------|
| `抢票助手.exe` | 📦 **完整版单文件**（约 117MB）：内含 Python 运行时 + GUI + 抢票逻辑 + Node.js + Appium + adb 全部环境，双击即用 |
| `damai-ticket-helper-source.zip` | 💻 **源码版**：仅核心源码，开发者自行搭环境 |

**完整版步骤**：下载 `抢票助手.exe` → 手机开 USB 调试连电脑 → 双击 exe（首次自动解压环境约 30 秒）→ 点红色「一键检测环境」→ 填配置 → 点绿色「开售秒抢」。

> 单文件 exe 内含一切，无需额外下载或安装任何软件。首次运行自动解压运行环境到 exe 同级目录，之后秒开。

---

## 项目来源

本项目基于 [WECENG/ticket-purchase](https://github.com/WECENG/ticket-purchase) 二次开发，感谢原作者的开源贡献。

在原项目（Selenium + Appium 双端抢票）的基础上，新增了：

- ✅ 可视化图形界面（tkinter），一键操作
- ✅ 单文件打包（PyInstaller onefile，环境内嵌，双击即用）
- ✅ 适配新版大麦 APP（9.x）的界面结构
- ✅ 开售秒抢模式（等待开售/有票，检测到变化瞬间自动抢）
- ✅ 缺货自动刷新（切换场次刷新等待补货）
- ✅ 多观演人自动购票（人数 = 张数，上限 6 张）
- ✅ 间隔自定义（毫秒级调节各步骤速度）
- ✅ 提交订单循环重试（次数可配置，0 = 无限重试）
- ✅ 多配置管理（保存多套配置，下拉切换，另存为/删除）
- ✅ 进程级联清理（关闭 exe 时自动清理 Appium/Node/adb）
- ✅ 环境自动修复（路径自动适配，换目录不出错）

---

## 功能特性

- **双端支持**（继承原项目）：Web 端（Selenium）+ 移动端（Appium）
- **可视化界面**：状态检测、配置编辑、一键启动、实时日志
- **开售秒抢**：毫秒级轮询检测，开售/有票瞬间自动抢
- **缺货刷新**：缺货时自动切换场次刷新，等到有票
- **多观演人**：自动按观演人数设置购票张数
- **循环抢票**：已开售且票抢手时反复重试
- **提交重试**：提交订单失败时自动循环重试，次数可配置
- **环境自修复**：换目录/换电脑自动修正 Appium 驱动路径
- **进程管理**：关闭程序时级联清理所有子进程（Appium/Node/adb）

---

## 项目结构

```
damai-ticket-helper/
├── damai/                     # Web 端抢票（继承原项目）
│   ├── damai.py
│   ├── config.py              # 配置类
│   └── concert.py             # 抢票逻辑
├── damai_appium/              # 移动端抢票（核心）
│   ├── damai_app_v2.py        # 主程序
│   ├── damai_app.py           # 原版主程序
│   ├── config.py              # 配置类
│   └── config.example.jsonc   # 配置示例
├── 大麦抢票助手/              # 可视化软件
│   ├── gui_app.py             # GUI 源码
│   ├── 使用说明.txt
│   └── config.example.jsonc   # 配置示例
├── exe-packer/                # exe 打包工具
│   ├── 一键打包.bat           # 双击即可打包
│   ├── build.py               # 打包脚本
│   ├── build.spec             # PyInstaller 配置
│   ├── bootstrap.py           # exe 启动引导器（首次解压 env，带进度窗口）
│   ├── install_env.py         # 环境检测脚本（纯离线）
│   ├── env_bundle.zip         # env 环境压缩包（97MB）
│   └── README.md              # 打包说明
├── tests/                     # 测试
├── doc/                       # 文档
└── README.md
```

> 注：`env/`（运行环境）、`抢票助手.exe`（打包产物）等二进制/大文件不提交仓库，用户本地自行准备或通过 exe-packer 打包。

---

## 快速开始

### 方式一：完整版 exe（推荐，零配置）

1. 下载 `抢票助手.exe`（约 117MB）
2. 放到任意目录，双击运行
   - 首次运行：自动解压运行环境（约 30 秒，有进度窗口提示）
   - 后续运行：直接秒开
3. 手机 USB 连接电脑，开启「USB 调试」
4. 点红色「一键检测环境」→ 全绿
5. 填好演出配置 → 保存
6. 手机进大麦，停在目标演出页面
7. 点绿色「开售秒抢」挂机等待

### 方式二：源码运行

#### 1. 安装环境

```bash
# Python 3.9+（需带 tkinter）
# Node.js 20.19.0+
# Appium 3.1.0+
npm install -g appium
appium driver install uiautomator2

# Android SDK + 配置环境变量 ANDROID_HOME
```

#### 2. 安装 Python 依赖

```bash
pip install psutil selenium Appium-Python-Client
```

#### 3. 配置

```bash
cd damai_appium
cp config.example.jsonc config.jsonc
# 编辑 config.jsonc 填入演出信息
```

#### 4. 运行

```bash
# 启动 Appium 服务器
appium --port 4999

# 方式 A：GUI 界面运行
cd 大麦抢票助手
python gui_app.py

# 方式 B：命令行直接运行（需手机连接 + USB调试 + 安装大麦APP）
cd damai_appium
python damai_app_v2.py --wait-sale
```

### 方式三：自行打包 exe

```bash
cd exe-packer
# 1. 安装 pip 依赖
pip install pyinstaller psutil Appium-Python-Client selenium
# 2. 放好 env_bundle.zip（含 Node.js + Appium + adb 的压缩包）
# 3. 双击「一键打包.bat」
```

详见 [exe-packer/README.md](exe-packer/README.md)。

---

## 配置说明

### 多配置管理

GUI 支持保存多套配置，快速切换不同演出：

```
配置: [默认配置 ▼] [新建] [保存] [另存为] [删除]
```

| 操作 | 说明 |
|------|------|
| 下拉框选择 | 选择已有配置，自动加载到界面 |
| 新建 | 清空所有输入框，开始填写新配置 |
| 保存 | 覆盖当前配置（新建状态下提示输入名称） |
| 另存为 | 输入新名称存为新配置，不影响原配置 |
| 删除 | 删除当前配置（默认配置不可删） |

配置文件存储位置：
- `config.jsonc` — 默认配置（exe 同级目录）
- `configs/` 目录 — 自定义配置（每个 `.jsonc` 文件一套配置）

使用场景：同时关注多场演出 → 每场存一个配置快速切换；同场演出不同价位 → 存多个配置按需切换。

### 配置字段

| 字段 | 说明 | 默认值 |
|------|------|--------|
| server_url | Appium 服务器地址 | `http://127.0.0.1:4999` |
| keyword | 演出搜索关键词 | — |
| users | 观演人名单（几个买几张，上限 6） | — |
| city | 演出城市 | — |
| date | 演出日期（如 9.25） | — |
| session_index | 场次位置（第几个场次卡片，从 0 计数） | — |
| price | 票价（如 380） | — |
| price_index | 票价位置（第几个票价卡片，从 0 计数） | — |
| if_commit_order | 是否自动提交订单 | `true` |
| submit_max_retries | 提交订单最大重试次数（0 = 无限重试） | `10` |
| delays | 各步骤间隔（秒） | 见下表 |

### 间隔设置

| 字段 | 说明 | 默认值（秒） |
|------|------|-------------|
| poll | 开售检测轮询间隔 | 0.2 |
| refresh | 页面强制刷新间隔 | 2.0 |
| step | 步骤间间隔（选场次/票价/观演人） | 0.5 |
| click | 连续点击间隔（数量加号等） | 0.15 |
| scroll | 滚动后等待 | 0.6 |
| page_load | 页面加载等待 | 2.5 |

> **场次/票价位置说明**：大麦新版把日期和票价文字画成了图片，程序读不到，只能按位置点。`session_index` / `price_index` 是「第几个卡片，从 0 开始」。GUI 界面里填的是「第几个，从 1 开始」，会自动转换。

> **提交重试说明**：`submit_max_retries` 控制提交订单的循环次数。填 `0` 表示无限重试直到成功；填 `10` 表示最多尝试 10 次。抢票紧张时建议设 `0`。

---

## 三大抢票模式

| 模式 | 用途 |
|------|------|
| **开售秒抢** | 等开售/等有票，检测到「立即预定/立即购买」瞬间自动抢（主入口） |
| **循环抢票** | 已开售且票抢手，反复抢到成功为止 |
| （立即抢票已并入秒抢） | — |

### 开售秒抢检测机制

- 每 200ms 轮询按钮文字
- 每 2s 刷新页面（切前后台）+ 点击试探判断状态
- 是「已预约」→ 退回继续刷；是「立即预定」→ 点进去抢
- 缺货 → 切换场次刷新等待补货

---

## exe 运行机制

### 首次运行

双击 `抢票助手.exe` → 显示进度窗口（标题 + 进度条 + 百分比）→ 自动解压运行环境到 exe 同级目录 `env/`（约 30 秒）→ 自动修正 Appium 驱动路径 → 启动 GUI 主界面。

### 后续运行

env 已存在 → 直接启动 GUI，秒开。

### 环境损坏/换目录

点「一键检测环境」→ 从 exe 内嵌的 `env_bundle.zip` 重新解压恢复 → 自动修正路径。纯离线，不联网。

### 关闭程序

关闭 exe 时自动级联清理所有子进程：
1. 停止抢票线程
2. 杀 Appium 进程树（递归杀子进程）
3. 杀残留的 node.exe
4. 停止 adb server

---

## 环境要求

### 完整版 exe（推荐）

- **操作系统**：Windows 10/11
- **手机**：Android 真机，USB 调试，安装大麦 APP 并登录
- 其他一切（Python/Node.js/Appium/adb）都内嵌在 exe 里

### 源码运行

- **Python**：3.9+（需带 tkinter）
- **Node.js**：20.19.0+
- **Appium**：3.1.0+ + uiautomator2 驱动
- **Android**：真机或模拟器，安装大麦 APP 并登录
- **操作系统**：Windows / macOS / Linux

---

## 常见问题

### 端口 4999 被占用

程序自动在启动前清理残留进程，如果仍被占用：

```bash
taskkill /F /IM node.exe
# 重新运行程序
```

### 服务器「占着端口但无响应」

残留的 node 进程占用了端口，GUI 会自动用 psutil 递归杀进程树。如仍不行：

```bash
taskkill /F /IM node.exe
taskkill /F /IM adb.exe
# 重新运行程序
```

### 手机识别不到

1. 检查 USB 调试是否开启、USB 模式是否「文件传输」
2. 重新插拔 USB 线，手机弹授权窗口点「始终允许」
3. 换数据线/USB 口（有些线只能充电不能传数据）
4. 安装手机品牌的 USB 驱动
5. `adb kill-server && adb start-server` 重启 adb

### 首次启动慢

首次运行需要解压运行环境（约 97MB 压缩包 → 271MB），约 30 秒。会显示进度窗口，不是卡死。之后启动秒开。

### Appium 驱动找不到

如果换目录后报 `Could not find a driver for automationName 'UiAutomator2'`，程序会自动修正 `extensions.yaml` 中的路径。如仍不行，删除 exe 同级的 `env/` 目录，重新双击 exe 会自动重新解压。

---

## 打包说明

使用 `exe-packer/` 目录下的工具自行打包：

```
exe-packer/
├── 一键打包.bat        ← 双击即可打包
├── build.py            ← 打包脚本（检查依赖 → 检查源码 → 检查 zip → PyInstaller）
├── build.spec          ← PyInstaller 配置（onefile 模式）
├── bootstrap.py        ← exe 启动引导器（首次解压 env，带进度窗口，自动修正路径）
├── install_env.py      ← 环境检测脚本（纯离线）
├── env_bundle.zip      ← env 环境压缩包（97MB）
└── README.md           ← 详细说明
```

打包流程：
1. bat 自动查找带 tkinter 的 Python
2. 检查 pip 依赖（pyinstaller / psutil / Appium-Python-Client / selenium）
3. 清理上次构建产物
4. PyInstaller onefile 打包（env_bundle.zip 内嵌进 exe）
5. 输出 `dist/抢票助手.exe`（约 117MB）

纯离线打包：不下载依赖、不下载 env、不压缩 env。

---

## 许可

本项目仅供学习和研究使用，请勿用于商业用途。请遵守大麦网的使用条款。

基于 [WECENG/ticket-purchase](https://github.com/WECENG/ticket-purchase)，遵循原项目的使用原则。
