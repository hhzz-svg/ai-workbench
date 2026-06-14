# 🎨 Skill Workbench - 创作工作台

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)

本地 Web 工作台，把资料和需求生成演示文稿、学术润色稿、网页演示和海报。数据完全本地化，隐私安全可控。

## ✨ 功能特性

### 支持的创作类型
- 📊 **论文演示** - 论文、实验图转组会/答辩 PPT
- 📝 **学术润色** - 英文学术写作润色和修改说明
- 🌐 **网页演示** - 主题素材生成单页 HTML 展示
- 🖼️ **学术海报** - 会议海报和打印文件（PDF）
- 🎨 **视觉海报** - 活动、品牌创意海报和封面设计

### V2 新功能
- 🔄 **AI 二次处理** - 对生成的文件添加注释，进行 AI 再加工
- 📁 **自定义输出路径** - 指定文件保存位置
- ⚡ **快速配置按钮** - 一键设置中文PPT/英文海报/网页演示
- 📋 **高级选项折叠** - 简化界面，新用户更易上手
- 🎯 **智能模板切换** - 模板提示词直接替换，避免混乱

## 🚀 快速开始

### 安装依赖

```powershell
# 安装后端依赖
python -m pip install -r backend\requirements.txt

# 安装前端依赖
npm --prefix frontend install
```

### 本机使用

```powershell
.\start.ps1
```

打开 `http://127.0.0.1:5173`。

### 局域网使用

同一网络里的其他人要访问这台电脑上的工作台，可以运行：

```powershell
.\start-lan.ps1
```

脚本会显示可访问地址，例如 `http://192.168.1.20:5173`。别人只打开网页，真正的模型配置、任务执行和文件仍在这台电脑上。

## 📖 使用指南

### 1. 创建任务

**方式一：使用快速开始模板**
- 点击预设模板（论文演示、网页演示等）
- 模板会自动填充提示词和配置

**方式二：使用快速配置**
- 🇨🇳 **中文PPT**：中文演示文稿配置
- 🇬🇧 **英文海报**：英文学术海报配置
- 🌐 **网页演示**：HTML 展示配置

**方式三：自由配置**
- 展开高级选项
- 自定义语言、格式、约束等参数

### 2. 上传参考资料（可选）

支持上传论文 PDF、图片、笔记等参考文件。

### 3. 指定输出路径（可选）

在"输出文件存储路径"框中输入自定义保存路径，例如：
```
C:\Users\你的用户名\Documents\我的作品
```

留空则使用默认路径 `~/.skill-workbench/jobs/`。

### 4. AI 二次处理

对已生成的文件进行修改：

1. 在产物列表中找到文件
2. 点击"添加注释"按钮
3. 输入修改要求，例如：
   - "将配色改为蓝色系"
   - "添加公司 Logo"
   - "基于这个PPT生成演讲稿"
4. 点击"提交处理"
5. 系统会创建新任务进行 AI 再加工

## 📁 数据存储

默认只在本机运行。后端数据、上传文件、密钥和产物都保存在当前电脑的 `~/.skill-workbench`：

```
~/.skill-workbench/
├── app.db           # 任务和配置数据库
├── uploads/         # 上传的文件
├── jobs/            # 任务工作目录
└── keys/            # 加密存储的 API Key
```

## ⚙️ 模型配置

### 使用默认环境

如果安装了 Codex CLI，可以直接使用本机默认环境，无需额外配置。

### 自定义 API 配置

1. 进入"设置"页面
2. 填写配置信息：
   - **配置名称**：如"学校代理"
   - **Base URL**：API 端点地址
   - **模型**：模型名称
   - **API Key**：访问密钥
3. 点击"测试连接"验证配置
4. 保存后可在创建任务时选择

## 🏗️ 项目结构

```
skill-workbench/
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── main.py       # 主应用和 API 路由
│   │   ├── models.py     # 数据模型
│   │   ├── store.py      # SQLite 数据存储
│   │   ├── jobs.py       # 任务队列管理
│   │   └── runner.py     # Codex 执行器
│   └── tests/
├── frontend/          # React + Vite 前端
│   ├── src/
│   │   ├── main.tsx      # 主组件
│   │   ├── api.ts        # API 客户端
│   │   ├── types.ts      # TypeScript 类型
│   │   └── styles.css    # 样式
│   └── dist/             # 构建产物
├── start.ps1          # 本机启动脚本
├── start-lan.ps1      # 局域网启动脚本
└── README.md
```

## 🔌 API 文档

### 主要端点

- `POST /api/jobs` - 创建任务
- `GET /api/jobs` - 获取任务列表
- `GET /api/jobs/{job_id}/events` - 任务进度流（SSE）
- `GET /api/jobs/{job_id}/artifacts` - 获取任务产物
- `GET /api/artifacts/{artifact_id}/download` - 下载产物
- `POST /api/artifacts/{artifact_id}/annotate` - AI 二次处理 ✨新功能
- `POST /api/files` - 上传文件
- `GET /api/providers` - 模型配置管理

完整 API 文档：启动后访问 http://127.0.0.1:8000/docs

## 📝 更新日志

### V2.0.0 (2026-06-15)

**新功能：**
- ✅ AI 二次处理：对生成文件进行注释和再加工
- ✅ 自定义输出路径：指定文件保存位置
- ✅ 快速配置按钮：一键设置常用参数
- ✅ 高级选项折叠：简化界面

**改进：**
- ✅ 修复快速配置按钮无效问题
- ✅ 修复模板提示词覆盖问题
- ✅ 精简产物显示：去除预览，只显示文件信息和路径
- ✅ 改进 UI 动画和视觉效果

详见 [UPDATES_V2.md](./UPDATES_V2.md)

## ⚠️ 注意事项

生成耗时较长是正常的：一次任务会读取资料、规划结构、调用模型、写入产物并索引文件；演示、海报和图片类任务通常比普通聊天更久（数分钟）。

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 后端框架
- [React](https://react.dev/) - 前端框架
- [Vite](https://vitejs.dev/) - 构建工具
- [Lucide Icons](https://lucide.dev/) - 图标库

---

**⭐ 如果这个项目对你有帮助，请给一个 Star！**
