# 🚀 部署到 Cloudflare Pages 指南

## 📋 前提条件

- ✅ Cloudflare 账号（免费）
- ✅ 自定义域名（在 Cloudflare 管理 DNS）
- ✅ GitHub 仓库（https://github.com/hhzz-svg/ai-workbench）

## ⚠️ 重要说明

本项目是**全栈应用**（前端 React + 后端 FastAPI），Cloudflare Pages 只能部署**静态网站**。

提供两种部署方案：

### 方案 A：部署展示页面（推荐）✨
- 部署项目介绍页面到 Cloudflare Pages
- 展示功能特性、截图、文档链接
- 提供 GitHub 和下载链接

### 方案 B：前后端分离部署
- 前端 → Cloudflare Pages
- 后端 → Railway/Render/Fly.io
- 需要配置 API 端点和 CORS

---

## 🎯 方案 A：部署展示页面（5分钟搞定）

### 步骤 1：准备展示页面

展示页面已创建：`landing-page/index.html`

这是一个精美的单页网站，包含：
- ✨ 项目介绍
- 🎨 功能展示
- 🛠️ 技术栈
- 📥 下载链接
- 🚀 快速开始指南

### 步骤 2：推送到 GitHub

```bash
cd /c/Users/huzhe/Documents/Codex/2026-06-14/product-design-plugin-product-design-openai

# 添加展示页面
git add landing-page/
git add CLOUDFLARE_DEPLOYMENT.md

# 提交
git commit -m "feat: 添加 Cloudflare Pages 展示页面"

# 推送
git push
```

### 步骤 3：连接 Cloudflare Pages

1. **登录 Cloudflare**
   - 访问：https://dash.cloudflare.com/
   - 登录你的账号

2. **创建 Pages 项目**
   - 左侧菜单选择 **"Workers & Pages"**
   - 点击 **"Create application"**
   - 选择 **"Pages"** 标签
   - 点击 **"Connect to Git"**

3. **连接 GitHub**
   - 选择 **GitHub**
   - 授权 Cloudflare 访问你的仓库
   - 选择 **hhzz-svg/ai-workbench**

4. **配置构建设置**

填写以下信息：

```
Project name: ai-workbench
Production branch: main

Build settings:
  Framework preset: None
  Build command: (留空)
  Build output directory: landing-page
  Root directory: (留空)
```

**重要**：Build output directory 填写 `landing-page`

5. **保存并部署**
   - 点击 **"Save and Deploy"**
   - 等待部署完成（约 1-2 分钟）

6. **访问网站**
   - 部署完成后会显示：`https://ai-workbench.pages.dev`
   - 点击链接查看效果

### 步骤 4：绑定自定义域名

1. **添加自定义域名**
   - 在项目页面，点击 **"Custom domains"** 标签
   - 点击 **"Set up a custom domain"**

2. **输入你的域名**
   ```
   例如：ai.你的域名.com
   或：workbench.你的域名.com
   ```

3. **配置 DNS**
   - Cloudflare 会自动添加 CNAME 记录
   - 如果域名在 Cloudflare，自动配置
   - 如果域名不在 Cloudflare，按提示添加 DNS 记录

4. **等待生效**
   - DNS 传播需要几分钟到几小时
   - 部署完成后访问你的域名

### 步骤 5：配置 HTTPS

Cloudflare Pages 自动提供免费 HTTPS 证书，无需额外配置。

---

## 🔧 方案 B：完整应用部署（前后端分离）

### 架构
```
前端（Cloudflare Pages）
    ↓ API 请求
后端（Railway/Render）
```

### 后端部署选项

#### 选项 1：Railway（推荐）

1. **准备后端配置**
   
   在项目根目录创建 `Procfile`：
   ```
   web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

2. **访问 Railway**
   - https://railway.app/
   - 使用 GitHub 登录
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择 `ai-workbench` 仓库

3. **配置设置**
   - Root Directory: `backend`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **环境变量**
   ```
   PORT=8000
   PYTHONUNBUFFERED=1
   ```

5. **获取后端 URL**
   - 部署完成后：`https://your-app.railway.app`

#### 选项 2：Render

1. **访问 Render**
   - https://render.com/
   - 使用 GitHub 登录

2. **创建 Web Service**
   - 点击 "New +"
   - 选择 "Web Service"
   - 连接 GitHub
   - 选择 `ai-workbench` 仓库

3. **配置**
   ```
   Name: ai-workbench-api
   Root Directory: backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. **获取后端 URL**
   - `https://your-app.onrender.com`

### 前端部署

1. **修改 API 配置**

编辑 `frontend/src/api.ts`：

```typescript
export const API_BASE = import.meta.env.VITE_API_BASE || "";
```

2. **创建环境变量文件**

创建 `frontend/.env.production`：
```env
VITE_API_BASE=https://your-backend-url.railway.app
```

3. **部署到 Cloudflare Pages**

配置：
```
Project name: ai-workbench-app
Production branch: main

Build settings:
  Framework preset: Vite
  Build command: npm run build
  Build output directory: dist
  Root directory: frontend
  
Environment variables:
  VITE_API_BASE = https://your-backend-url.railway.app
```

4. **后端 CORS 配置**

修改 `backend/app/main.py` 中的 CORS 设置：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://your-domain.com",  # 你的自定义域名
        "https://ai-workbench.pages.dev"  # Cloudflare Pages 默认域名
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📝 推荐做法总结

### 方案 A - 展示页面（最简单）⭐
- ✅ 免费
- ✅ 5 分钟完成
- ✅ 适合项目展示
- ✅ 用户下载到本地运行
- **推荐用于开源项目展示**

### 方案 B - 完整应用
- ⚠️ 需要付费后端（或免费额度）
- ⚠️ 配置复杂
- ✅ 提供在线服务
- ✅ 用户可直接使用
- **推荐用于商业化运营**

---

## 🎯 立即开始：部署展示页面

### 执行命令

```bash
cd /c/Users/huzhe/Documents/Codex/2026-06-14/product-design-plugin-product-design-openai

# 添加文件
git add landing-page/ CLOUDFLARE_DEPLOYMENT.md
git commit -m "feat: 添加 Cloudflare Pages 展示页面和部署指南"
git push
```

### Cloudflare Pages 配置速查表

| 配置项 | 值 |
|--------|-----|
| Project name | `ai-workbench` |
| Production branch | `main` |
| Framework preset | `None` |
| Build command | (留空) |
| Build output directory | `landing-page` |
| Root directory | (留空) |

---

## 🌐 域名配置示例

### 子域名方式（推荐）
```
ai.yourdomain.com
workbench.yourdomain.com
```

### 主域名方式
```
yourdomain.com
www.yourdomain.com
```

配置完成后：
- HTTP 自动重定向到 HTTPS
- 免费 SSL 证书
- 全球 CDN 加速

---

## 🔗 相关资源

- [Cloudflare Pages 文档](https://developers.cloudflare.com/pages/)
- [Railway 文档](https://docs.railway.app/)
- [Render 文档](https://render.com/docs)
- [Vite 环境变量](https://vitejs.dev/guide/env-and-mode.html)

---

## ❓ 常见问题

**Q: 部署后显示 404？**  
A: 检查 Build output directory 是否设置为 `landing-page`

**Q: 如何更新网站内容？**  
A: 推送新代码到 GitHub，Cloudflare 会自动重新部署

**Q: Cloudflare Pages 完全免费吗？**  
A: 是的，展示页面部署完全免费

**Q: 自定义域名需要额外付费吗？**  
A: 不需要，Cloudflare Pages 免费提供域名绑定和 SSL

**Q: 如果想提供在线服务怎么办？**  
A: 参考方案 B，部署后端到 Railway（有免费额度）

**Q: 展示页面可以修改吗？**  
A: 可以，编辑 `landing-page/index.html` 后重新推送即可

---

## 📊 部署后检查清单

- [ ] 网站可以正常访问
- [ ] HTTPS 证书已生效
- [ ] 自定义域名已绑定
- [ ] 所有链接正常工作
- [ ] 移动端显示正常
- [ ] GitHub 链接正确
- [ ] 下载链接有效

---

祝部署成功！🚀

有问题欢迎在 GitHub Issues 提问：https://github.com/hhzz-svg/ai-workbench/issues
