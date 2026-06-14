# 贡献指南

感谢你对 Skill Workbench 的关注！我们欢迎各种形式的贡献。

## 如何贡献

### 报告 Bug

如果你发现了 Bug，请创建一个 Issue 并包含以下信息：

- **Bug 描述**：清晰简洁地描述问题
- **复现步骤**：详细的步骤说明
- **预期行为**：你期望发生什么
- **实际行为**：实际发生了什么
- **截图**：如果可能，附上截图
- **环境信息**：
  - 操作系统（Windows/macOS/Linux）
  - Python 版本
  - Node.js 版本
  - 浏览器版本

### 提出新功能

如果你有新功能建议：

1. 先检查 Issues 中是否已有类似建议
2. 创建一个新 Issue，标题以 `[Feature Request]` 开头
3. 详细描述功能需求和使用场景
4. 如果可能，提供 UI 设计或代码示例

### 提交代码

#### 开发流程

1. **Fork 仓库**
   ```bash
   git clone https://github.com/你的用户名/skill-workbench.git
   cd skill-workbench
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/my-new-feature
   # 或
   git checkout -b fix/my-bug-fix
   ```

3. **安装依赖**
   ```bash
   # 后端
   cd backend
   pip install -r requirements.txt
   
   # 前端
   cd frontend
   npm install
   ```

4. **进行修改**
   - 遵循现有代码风格
   - 添加必要的注释
   - 更新相关文档

5. **运行测试**
   ```bash
   # 后端测试
   cd backend
   pytest
   
   # 前端测试
   cd frontend
   npm test
   ```

6. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   # 或
   git commit -m "fix: 修复某个问题"
   ```

7. **推送到 GitHub**
   ```bash
   git push origin feature/my-new-feature
   ```

8. **创建 Pull Request**
   - 在 GitHub 上打开 Pull Request
   - 填写详细的描述
   - 关联相关的 Issue（如果有）

#### Commit 消息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>: <subject>

[optional body]

[optional footer]
```

**Type 类型：**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建、工具配置等

**示例：**
```
feat: 添加 AI 二次处理功能

实现了对已生成文件的注释和再加工功能。
用户可以输入修改要求，系统会创建新任务进行处理。

Closes #123
```

## 代码规范

### Python（后端）

- 遵循 PEP 8 规范
- 使用 `ruff` 进行代码检查
- 函数和类添加文档字符串
- 类型注解（Type Hints）

```python
def process_artifact(artifact_id: str, annotation: str) -> dict[str, Any]:
    """
    处理产物注释。

    Args:
        artifact_id: 产物 ID
        annotation: 注释内容

    Returns:
        包含新任务 ID 的字典
    """
    ...
```

### TypeScript/React（前端）

- 使用 ESLint 进行代码检查
- 优先使用函数组件和 Hooks
- 使用 TypeScript 类型
- 组件和函数添加 JSDoc 注释

```typescript
/**
 * 产物卡片组件
 * @param artifact - 产物数据
 */
function ArtifactCard({ artifact }: { artifact: Artifact }) {
  ...
}
```

### CSS

- 使用语义化的类名
- 保持样式模块化
- 使用 CSS 变量定义主题色

## 项目结构

### 后端目录

```
backend/
├── app/
│   ├── main.py           # FastAPI 应用和路由
│   ├── models.py         # Pydantic 模型
│   ├── store.py          # 数据库操作
│   ├── jobs.py           # 任务管理
│   ├── runner.py         # Codex 执行器
│   └── adapters.py       # Skill 适配器
└── tests/
    ├── test_api.py       # API 测试
    ├── test_store.py     # 数据库测试
    └── conftest.py       # 测试配置
```

### 前端目录

```
frontend/
├── src/
│   ├── main.tsx          # 主组件
│   ├── api.ts            # API 客户端
│   ├── types.ts          # TypeScript 类型
│   └── styles.css        # 全局样式
├── public/               # 静态资源
└── tests/                # 测试文件
```

## 开发建议

### 添加新的 Skill

1. 在 `backend/app/adapters.py` 中注册新 skill
2. 更新 `list_skills()` 函数
3. 在前端 `productTypes` 中添加显示名称
4. 添加相应的模板（如果需要）

### 添加新的 API 端点

1. 在 `backend/app/main.py` 的 `create_app()` 函数中添加路由
2. 定义相应的 Pydantic 模型（如果需要）
3. 在 `frontend/src/api.ts` 中添加客户端方法
4. 更新 TypeScript 类型定义

### UI 组件开发

1. 保持组件小而专注
2. 使用现有的样式类
3. 确保响应式设计
4. 添加必要的 aria 标签

## 测试

### 后端测试

```bash
cd backend

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_api.py

# 查看覆盖率
pytest --cov=app --cov-report=html
```

### 前端测试

```bash
cd frontend

# 运行测试
npm test

# 构建检查
npm run build
```

## 发布流程

1. 更新版本号（`package.json`, `pyproject.toml`）
2. 更新 `README.md` 和 `UPDATES_V2.md`
3. 创建 Git tag
4. 推送到 GitHub
5. 创建 Release

## 获取帮助

- 查看 [README.md](README.md) 了解项目基础
- 查看 [UPDATES_V2.md](UPDATES_V2.md) 了解最新更新
- 在 Issues 中提问
- 查看现有的 Pull Requests

## 行为准则

- 尊重他人
- 欢迎新手
- 建设性反馈
- 专注于技术讨论

---

再次感谢你的贡献！ 🎉
