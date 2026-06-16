# 🚀 Cloudflare Pages 部署完全指南（小白版）

## 📖 第一步：理解三个网址

### 1. http://127.0.0.1:8080/ - 展示页面 ✅ 可以部署
**这是什么**：一个漂亮的静态介绍页面，给别人看你的项目
**内容**：项目介绍、功能列表、下载链接
**能否部署**：✅ 可以！这就是我们要部署的
**部署后访问**：`https://你的域名.com` 或 `https://ai-workbench.pages.dev`

### 2. http://127.0.0.1:5173/ - 完整应用前端 ⚠️ 需要后端
**这是什么**：实际的创作工具界面（React 应用）
**内容**：创建任务、上传文件、生成文档等功能
**能否部署**：⚠️ 可以部署，但需要单独部署后端才能正常使用
**建议**：暂时不部署，让用户下载到本地使用

### 3. http://127.0.0.1:8000/ - 后端 API ❌ Cloudflare Pages 不支持
**这是什么**：后端服务（FastAPI）
**内容**：处理任务、调用 AI、生成文件
**能否部署**：❌ Cloudflare Pages 只能部署静态网站，不能部署后端
**需要**：如果要在线提供服务，后端需要部署到其他平台（Railway、Render 等）

---

## 🎯 推荐方案：只部署展示页面

### 为什么只部署展示页面？
1. ✅ **最简单**：5分钟搞定，完全免费
2. ✅ **够用**：展示项目、提供下载链接
3. ✅ **省钱**：不需要付费服务器
4. ✅ **快速**：全球 CDN 加速

### 展示页面能做什么？
- 介绍项目功能
- 展示项目特色
- 提供 GitHub 链接
- 提供下载链接
- 让用户下载后本地运行（完整功能）

---

## 💰 第二步：域名选择

### 选项 1：使用免费的 Cloudflare Pages 域名 ✅ 推荐新手
**费用**：完全免费
**域名格式**：`https://ai-workbench.pages.dev`
**优点**：
- 免费
- 自动 HTTPS
- 全球 CDN
- 立即可用

**缺点**：
- 域名较长
- 包含 `.pages.dev`

**适合人群**：新手、测试、个人项目

---

### 选项 2：购买自定义域名 💰 适合正式项目
**费用**：约 ¥60-80/年（.com 域名）
**域名格式**：`https://ai-workbench.com` 或 `https://你的名字.com`

#### 2.1 在哪里买域名？

**推荐平台**：

1. **Cloudflare（推荐）** ⭐⭐⭐⭐⭐
   - 网址：https://www.cloudflare.com/products/registrar/
   - 价格：成本价（最便宜）
   - 优点：直接在 Cloudflare，配置最简单
   - .com 域名：约 $9-10/年（¥65 左右）

2. **阿里云（万网）** ⭐⭐⭐⭐
   - 网址：https://wanwang.aliyun.com/
   - 价格：.com 约 ¥55-78/年（首年可能有优惠）
   - 优点：中文界面，支持支付宝
   - 缺点：需要实名认证

3. **腾讯云** ⭐⭐⭐⭐
   - 网址：https://dnspod.cloud.tencent.com/
   - 价格：.com 约 ¥55-78/年
   - 优点：中文界面
   - 缺点：需要实名认证

4. **Namesilo（国外）** ⭐⭐⭐
   - 网址：https://www.namesilo.com/
   - 价格：.com 约 $10-12/年
   - 优点：支持支付宝，隐私保护免费
   - 缺点：英文界面

#### 2.2 域名命名建议

**好的域名**：
- ✅ `ai-workbench.com`
- ✅ `myworkbench.com`
- ✅ `aicraft.com`
- ✅ `你的名字-ai.com`

**注意事项**：
- 简短易记
- 容易拼写
- 避免数字和连字符（除非必要）
- 优先选择 .com

#### 2.3 域名购买步骤（以 Cloudflare 为例）

1. 访问 https://dash.cloudflare.com/
2. 左侧菜单 → **Domain Registration**
3. 搜索你想要的域名
4. 选择可用的域名
5. 添加到购物车
6. 填写注册信息
7. 使用信用卡支付（约 $9-10/年）

---

## 🚀 第三步：部署到 Cloudflare Pages

### 3.1 创建 Cloudflare 账号

1. 访问：https://dash.cloudflare.com/sign-up
2. 填写邮箱和密码
3. 验证邮箱
4. 登录成功

### 3.2 连接 GitHub

1. 在 Cloudflare Dashboard 左侧菜单
2. 点击 **Workers & Pages**
3. 点击 **Create application** 按钮
4. 选择 **Pages** 标签
5. 点击 **Connect to Git**

### 3.3 授权 GitHub

1. 选择 **GitHub**
2. 点击 **Authorize Cloudflare**（授权）
3. 如果要求，输入 GitHub 密码
4. 选择授权方式：
   - **All repositories**（所有仓库）- 简单但不安全
   - **Only select repositories**（推荐）- 只选择 `ai-workbench`

### 3.4 选择仓库

1. 在仓库列表中找到 **hhzz-svg/ai-workbench**
2. 点击 **Begin setup**

### 3.5 配置构建设置（重要！）

填写以下信息（请严格按照这个填写）：

```
Project name（项目名称）:
ai-workbench

Production branch（生产分支）:
main

Framework preset（框架预设）:
None

Build command（构建命令）:
（留空，不要填）

Build output directory（构建输出目录）:
landing-page

Root Directory (optional)（根目录）:
（留空，不要填）
```

**关键点**：
- ✅ `Build output directory` 必须填写 `landing-page`
- ✅ 其他都留空

### 3.6 部署

1. 检查配置无误
2. 点击 **Save and Deploy** 按钮
3. 等待部署（约 1-2 分钟）
4. 看到 **Success!** 表示部署成功

### 3.7 获取网址

部署成功后会显示：
```
https://ai-workbench.pages.dev
```

这就是你的网站地址！点击访问查看效果。

---

## 🌐 第四步：绑定自定义域名（可选）

### 如果你购买了域名

#### 4.1 添加域名到 Cloudflare

**如果在 Cloudflare 购买的域名**：
- 自动添加，跳过此步骤

**如果在其他地方购买的域名**（阿里云、腾讯云等）：
1. 在 Cloudflare Dashboard
2. 点击 **Add a site**
3. 输入你的域名（如 `ai-workbench.com`）
4. 选择 **Free** 计划
5. Cloudflare 会显示两个 Nameserver（域名服务器）地址

**修改域名 DNS**：
1. 登录你购买域名的网站（阿里云/腾讯云）
2. 找到域名管理
3. 修改 DNS 服务器为 Cloudflare 提供的地址
4. 等待几小时到 24 小时生效

#### 4.2 绑定域名到 Pages

1. 进入你的 **ai-workbench** 项目
2. 点击 **Custom domains** 标签
3. 点击 **Set up a custom domain**
4. 输入域名：
   ```
   ai-workbench.com
   或
   www.ai-workbench.com
   ```
5. 点击 **Continue**
6. Cloudflare 会自动配置 DNS
7. 等待几分钟，看到 **Active** 表示成功

#### 4.3 访问你的网站

现在可以通过你的域名访问：
```
https://ai-workbench.com
```

自动启用 HTTPS，全球 CDN 加速！

---

## ✅ 第五步：验证部署

### 检查清单

访问你的网站（`https://ai-workbench.pages.dev` 或你的域名）

- [ ] 页面正常加载
- [ ] 渐变紫色背景显示
- [ ] 大标题 "AI Workbench" 清晰
- [ ] 🎨 图标有浮动动画
- [ ] 功能卡片显示（6 个）
- [ ] 卡片悬停时有动画
- [ ] GitHub 按钮可点击
- [ ] 下载按钮可点击
- [ ] HTTPS 绿锁显示
- [ ] 移动端访问正常

### 测试链接

- GitHub 链接：https://github.com/hhzz-svg/ai-workbench
- Releases 链接：https://github.com/hhzz-svg/ai-workbench/releases

---

## 🔄 第六步：更新网站

### 如何更新内容？

只需要修改代码并推送到 GitHub：

```bash
# 1. 修改 landing-page/index.html
# 2. 提交更改
git add landing-page/index.html
git commit -m "update: 更新展示页面"
git push

# 3. Cloudflare 会自动检测并重新部署（约 1-2 分钟）
```

### 查看部署历史

1. 进入 Cloudflare Pages 项目
2. 点击 **Deployments** 标签
3. 查看所有部署记录

---

## 💡 常见问题

### Q1: 部署失败怎么办？
**A**: 检查 `Build output directory` 是否填写 `landing-page`

### Q2: 显示 404 错误？
**A**: 确认 `landing-page/index.html` 文件存在于 GitHub

### Q3: 域名多久生效？
**A**: Cloudflare 域名：立即生效
外部域名：几小时到 24 小时

### Q4: 可以部署完整应用吗？
**A**: 需要额外部署后端，建议新手暂时只部署展示页面

### Q5: 费用是多少？
**A**: 
- Cloudflare Pages：完全免费
- .pages.dev 域名：完全免费
- 自定义域名：约 ¥60-80/年（可选）

### Q6: 可以更换域名吗？
**A**: 可以，随时在 Custom domains 中添加/删除

### Q7: 流量有限制吗？
**A**: Cloudflare Pages 免费版限制：
- 无限请求
- 500 次构建/月
- 20,000 次请求/天（通常足够）

---

## 📊 方案对比

### 方案 A：免费方案（推荐新手）
- 费用：¥0
- 域名：`https://ai-workbench.pages.dev`
- 功能：展示页面
- 用户：下载到本地使用完整功能
- 适合：个人项目、学习、展示

### 方案 B：自定义域名
- 费用：¥60-80/年（域名）
- 域名：`https://你的域名.com`
- 功能：展示页面
- 用户：下载到本地使用完整功能
- 适合：正式项目、品牌展示

### 方案 C：完整在线服务（高级）
- 费用：¥60-80/年（域名）+ ¥50-100/月（后端服务器）
- 域名：`https://你的域名.com`
- 功能：完整在线服务
- 用户：直接在线使用
- 适合：商业化、提供服务

---

## 🎯 小白推荐路线

### 第一次部署（今天）
1. ✅ 使用 Cloudflare Pages 免费域名
2. ✅ 只部署展示页面
3. ✅ 5 分钟完成
4. ✅ 总费用：¥0

### 如果想要专业域名（以后）
1. 购买域名（¥60-80/年）
2. 绑定到已部署的项目
3. 10 分钟完成

### 如果想提供在线服务（更以后）
1. 学习后端部署
2. 使用 Railway/Render
3. 配置前后端连接

---

## 📝 快速操作步骤（小白版）

### 步骤 1：注册 Cloudflare
1. 访问 https://dash.cloudflare.com/sign-up
2. 填写邮箱、密码
3. 验证邮箱

### 步骤 2：开始部署
1. 点击 **Workers & Pages**
2. 点击 **Create application**
3. 点击 **Pages**
4. 点击 **Connect to Git**

### 步骤 3：连接 GitHub
1. 点击 **GitHub**
2. 授权 Cloudflare
3. 选择 **ai-workbench** 仓库

### 步骤 4：配置（重要！）
```
Project name: ai-workbench
Production branch: main
Build output directory: landing-page
其他：留空
```

### 步骤 5：部署
1. 点击 **Save and Deploy**
2. 等待 1-2 分钟
3. 完成！

### 步骤 6：访问网站
点击显示的网址，例如：
`https://ai-workbench.pages.dev`

---

**准备好了吗？现在就开始部署吧！** 🚀

有任何问题随时问我！
