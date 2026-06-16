# 🚀 一键启动指南

> **给新用户**: 下载后只需两步就能使用 AI Workbench!

## Windows 用户(推荐)

### 第一次使用

1. **双击运行** `install.bat`
   - 自动检测 Python 和 Node.js
   - 自动安装所有依赖
   - 大约需要 2-3 分钟

2. **双击运行** `start.bat`
   - 自动启动后端和前端
   - 自动打开浏览器
   - 开始使用!

### 后续使用

直接双击 `start.bat` 即可。

### 停止服务

关闭两个最小化的黑色窗口(标题为"AI Workbench - 后端"和"AI Workbench - 前端")。

---

## 手动启动(所有平台)

如果你更喜欢手动控制,或使用 macOS/Linux:

### 安装依赖

```bash
# 后端
python -m pip install -r backend/requirements.txt

# 前端
cd frontend
npm install
cd ..
```

### 启动服务

```bash
# 方法 1: 使用 PowerShell 脚本 (Windows)
.\start.ps1

# 方法 2: 手动启动两个服务
# 终端 1 - 后端
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000

# 终端 2 - 前端
cd frontend
npm run dev
```

然后打开 http://127.0.0.1:5173

---

## 常见问题

### 提示"未检测到 Python"

1. 下载安装 Python 3.10+: https://www.python.org/downloads/
2. **重要**: 安装时勾选 "Add Python to PATH"
3. 重启命令行窗口后重试

### 提示"未检测到 Node.js"

1. 下载安装 Node.js 20+: https://nodejs.org/
2. 重启命令行窗口后重试

### 端口被占用

如果提示 8000 或 5173 端口已被占用:
- 关闭其他正在运行的 AI Workbench 实例
- 或修改 `start.bat` 里的端口号

### 浏览器没有自动打开

手动打开浏览器访问: http://127.0.0.1:5173

---

## 技术说明

- `install.bat`: 环境检测 + 依赖安装脚本
- `start.bat`: 一键启动脚本(自动启动后端+前端+打开浏览器)
- `start.ps1`: PowerShell 启动脚本(需要手动打开浏览器)
- `start-lan.ps1`: 局域网共享模式(其他设备可访问)
