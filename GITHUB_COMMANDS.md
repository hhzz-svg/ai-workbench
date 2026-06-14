# 🚀 GitHub 发布命令（直接复制执行）

## 第一步：初始化 Git 仓库

```bash
cd "C:/Users/huzhe/Documents/Codex/2026-06-14/product-design-plugin-product-design-openai"

# 初始化 Git
git init

# 添加所有文件
git add .

# 第一次提交
git commit -m "feat: V2.0.0 初始版本

新功能：
- AI 二次处理功能 - 对生成文件进行注释和再加工
- 自定义输出路径 - 指定文件保存位置
- 快速配置按钮 - 一键设置常用参数
- 高级选项折叠 - 简化界面

改进：
- 修复快速配置按钮无效问题
- 修复模板提示词覆盖问题
- 精简产物显示 - 去除预览，显示文件路径
- UI 优化 - 动画效果和视觉改进"
```

## 第二步：创建 GitHub 仓库

1. 打开浏览器访问：https://github.com/new

2. 填写信息：
   - **Repository name**: `skill-workbench`
   - **Description**: `🎨 本地 AI 创作工具 - 生成演示文稿、学术海报、网页展示和文档`
   - **Visibility**: Public（推荐）
   - **不要勾选** "Initialize this repository with a README"

3. 点击 "Create repository"

## 第三步：连接远程仓库并推送

```bash
# 添加远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/skill-workbench.git

# 重命名主分支为 main
git branch -M main

# 推送代码
git push -u origin main
```

## 第四步：添加 Topics

在 GitHub 仓库页面：

1. 点击右侧 "About" 旁边的齿轮图标
2. 在 "Topics" 输入框中添加：
   ```
   ai, react, fastapi, typescript, python, presentation, poster, generator, local-first, productivity
   ```
3. 保存

## 第五步：创建 Release

1. 在仓库页面点击右侧的 "Releases"
2. 点击 "Create a new release"
3. 填写信息：
   - **Choose a tag**: 输入 `v2.0.0` 并选择 "Create new tag: v2.0.0 on publish"
   - **Release title**: `V2.0.0 - AI 二次处理与 UI 优化`
   - **Description**: 复制以下内容

```markdown
## ✨ 新功能

### AI 二次处理
对已生成的文件进行注释和再加工：
- 点击产物的"添加注释"按钮
- 输入修改要求（如"改为蓝色系"、"生成演讲稿"）
- AI 会创建新任务进行处理

### 自定义输出路径
- 在创建任务时指定文件保存位置
- 支持任意绝对路径
- 自动创建目录

### 快速配置按钮
一键设置常用参数组合：
- 🇨🇳 中文PPT - 中文演示文稿配置
- 🇬🇧 英文海报 - 英文学术海报配置
- 🌐 网页演示 - HTML 展示配置

### 高级选项折叠
- 默认收起高级选项，界面更简洁
- 新用户更易上手
- 点击即可展开/收起

## 🔧 改进

### Bug 修复
- ✅ 修复快速配置按钮点击无效问题
- ✅ 修复模板提示词累加混乱问题

### UI 优化
- ✅ 精简产物显示 - 去除预览，只显示文件信息和路径
- ✅ 改进动画效果 - 按钮悬停、卡片交互
- ✅ 优化下载按钮 - 更大更明显
- ✅ 响应式设计改进

## 📦 技术栈

- **后端**: FastAPI + Python 3.10+
- **前端**: React 18 + TypeScript + Vite
- **数据库**: SQLite
- **UI**: 自定义 CSS，无第三方 UI 库

## 📖 快速开始

```bash
# 安装依赖
python -m pip install -r backend/requirements.txt
npm --prefix frontend install

# 启动服务
.\start.ps1

# 访问
http://127.0.0.1:5173
```

## 🔗 文档

- [README](https://github.com/YOUR_USERNAME/skill-workbench/blob/main/README.md) - 完整项目介绍
- [贡献指南](https://github.com/YOUR_USERNAME/skill-workbench/blob/main/CONTRIBUTING.md)
- [快速启动](https://github.com/YOUR_USERNAME/skill-workbench/blob/main/QUICK_START.md)
- [更新日志](https://github.com/YOUR_USERNAME/skill-workbench/blob/main/UPDATES_V2.md)

---

**⭐ 如果这个项目对你有帮助，请给一个 Star！**
```

4. 点击 "Publish release"

## 第六步：更新 README 中的链接

用你的 GitHub 用户名替换 README.md 中的占位符：

```bash
# 用文本编辑器打开 README.md
# 将所有 "YOUR_USERNAME" 替换为你的 GitHub 用户名
# 或使用命令（Linux/Mac）：
sed -i 's/YOUR_USERNAME/你的用户名/g' README.md

# 提交更改
git add README.md
git commit -m "docs: 更新仓库链接"
git push
```

## ✅ 完成！

你的项目已成功发布到 GitHub！

### 下一步（可选）

1. **添加截图**
   ```bash
   mkdir docs
   # 将截图放到 docs/ 目录
   git add docs/
   git commit -m "docs: 添加项目截图"
   git push
   ```

2. **分享到社区**
   - Twitter/X
   - Reddit (r/Python, r/reactjs)
   - Hacker News
   - 掘金/知乎

3. **设置 GitHub Pages**（如果需要演示站点）
   - 在仓库设置中启用 GitHub Pages
   - 选择 `gh-pages` 分支或 `/docs` 目录

4. **添加 Badges**
   在 README.md 顶部已有：
   - License badge
   - Python version badge
   - Node.js version badge

---

**仓库地址**: `https://github.com/YOUR_USERNAME/skill-workbench`

恭喜！🎉 你的开源项目已经上线了！
