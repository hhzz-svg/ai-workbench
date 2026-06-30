# 创作工作台 V2 更新文档

## 更新日期
2026年6月15日

## 问题修复 ✅

### 1. 快速配置按钮无效问题 ✅
**问题**：点击快速配置按钮（中文PPT、英文海报、网页演示）没有反应

**原因**：高级选项默认收起，配置更改后用户看不到效果

**解决方案**：
- 点击快速配置按钮时自动展开高级选项（`setShowAdvanced(true)`）
- 用户可以立即看到语言、格式和约束的变化

```typescript
const quickFillChinese = () => {
  setLanguage("zh-CN");
  setFormat("PPTX 演示文稿");
  setSelectedConstraints(["严格基于上传资料", "保留关键英文术语"]);
  setShowAdvanced(true); // 自动展开
};
```

### 2. 模板提示词覆盖问题 ✅
**问题**：切换快速开始模板时，提示词相互覆盖或累加

**原因**：原有逻辑会将新模板追加到现有提示词

**解决方案**：
- 改为替换模式：选择模板时直接替换整个提示词
- 再次点击同一模板可取消选择并清空提示词
- 用户可以在模板基础上自由修改

```typescript
const applyTemplate = (template: ProductTemplate) => {
  setSelectedTemplateId((current) => current === template.id ? null : template.id);
  if (selectedTemplateId === template.id) {
    setPrompt(""); // 取消选择时清空
    return;
  }
  setPrompt(template.prompt); // 直接替换
  setLanguage(template.language);
  setFormat(template.format);
  setSelectedConstraints(template.constraints);
};
```

## 新功能 🚀

### 3. 精简的产物展示 ✅
**需求**：非图片格式文件不需要预览，只显示文件信息和下载

**实现**：
- ✅ 移除所有预览功能（iframe、img）
- ✅ 显示文件完整路径（等宽字体）
- ✅ 清晰的下载按钮（绿色，带图标）
- ✅ 卡片式布局，信息一目了然

**效果**：
```
[图标] 文件名.pptx
       演示文稿 · 2.5 MB
       路径：C:\outputs\file.pptx
                            [下载] [添加注释]
```

### 4. 输出文件存储路径选择 ✅
**需求**：用户可以指定生成文件的保存位置

**实现**：
- ✅ 新增"输出文件存储路径"输入框
- ✅ 支持自定义路径（如 `C:\Users\Documents\outputs`）
- ✅ 留空则使用默认输出目录
- ✅ 路径信息会传递到后端 `options.outputPath`
- ✅ 后端校验绝对路径并在任务完成后复制最终产物

**UI**：
```
输出文件存储路径（可选）
┌────────────────────────────────────────┐
│ C:\Users\Documents\outputs             │
└────────────────────────────────────────┘
留空将使用默认输出目录
```

### 5. AI 二次处理（注释功能）✅
**需求**：对生成的文件可以添加注释，进行 AI 二次操作

**实现**：
- ✅ 每个产物卡片添加"添加注释"按钮
- ✅ 点击展开注释输入框
- ✅ 支持输入处理指令（如"改为蓝色系"、"生成演讲稿"）
- ✅ 提交按钮调用 AI 处理（框架已就绪）

**交互流程**：
1. 点击 **[添加注释]** 按钮
2. 展开输入框，输入指令：
   ```
   请将这个海报的配色改为蓝色系
   ```
3. 点击 **[提交处理]** 按钮
4. 后端创建新的二次处理任务，任务完成后生成新产物

**支持的文件类型**：
- ✅ 图片（image）
- ✅ HTML（html）
- ✅ PDF（pdf）
- ❌ 其他格式暂不支持注释

## 技术改进 🔧

### 状态管理
```typescript
const [outputPath, setOutputPath] = useState("");  // 输出路径
const [showAnnotation, setShowAnnotation] = useState(false);  // 注释框显示
const [annotation, setAnnotation] = useState("");  // 注释内容
const [processingAnnotation, setProcessingAnnotation] = useState(false);  // 处理中
```

### 新增组件
- `artifact-card-compact`：精简的产物卡片
- `artifact-header`：卡片头部（信息+操作）
- `artifact-info`：文件信息区域
- `artifact-path`：文件路径显示（等宽字体）
- `annotation-box`：注释输入区域
- `download-button-primary`：主下载按钮
- `secondary-button-small`：次要操作按钮

### API 扩展点
```typescript
// 创建任务时传递输出路径
options.outputPath = outputPath.trim();

// 注释处理
async function handleAnnotationSubmit() {
  // POST /api/artifacts/{artifactId}/annotate
  // Body: { annotation: string }
}
```

## UI 改进 🎨

### 产物卡片布局
```
┌──────────────────────────────────────────────────────┐
│ [📄] 论文演示_最终版.pptx            [下载] [添加注释] │
│      演示文稿 · 2.5 MB                                │
│      路径：C:\outputs\presentation.pptx              │
├──────────────────────────────────────────────────────┤
│ AI 二次处理指令                                       │
│ ┌────────────────────────────────────────────────┐  │
│ │ 请将这个PPT的配色改为商务蓝色系                 │  │
│ └────────────────────────────────────────────────┘  │
│ [✨ 提交处理]                                        │
└──────────────────────────────────────────────────────┘
```

### 样式特点
- **等宽字体路径**：`Cascadia Code` 字体显示文件路径
- **渐变悬停效果**：卡片悬停时边框和阴影变化
- **垂直按钮布局**：下载和注释按钮纵向排列
- **灰色路径文字**：路径用浅灰色显示，不干扰主信息
- **响应式设计**：移动端按钮自动全宽

## 构建信息 📦

```
✓ TypeScript 编译通过
✓ Vite 构建完成（337ms）
✓ CSS: 17.49 KB (gzip: 4.15 KB)
✓ JS: 224.26 KB (gzip: 71.60 KB)
```

## 后续工作 📋

### 后端 API 已补齐

1. **输出路径支持**
   ```python
   # backend/app/main.py
   @router.post("/jobs")
   async def create_job(payload: JobPayload):
       output_path = payload.options.get("outputPath")
       if output_path:
           # 验证路径是否合法，并在任务完成后复制产物
           ...
   ```

2. **注释处理接口**
   ```python
   @router.post("/artifacts/{artifact_id}/annotate")
   async def annotate_artifact(artifact_id: str, annotation: str):
       # 读取原文件
       # 创建新的二次处理任务
       # 返回新任务 ID
       ...
   ```

### 仍建议继续加强

1. **注释历史记录**（可选）
   ```python
   # 记录每个产物的注释历史
   # 支持查看和回滚
   ```
2. **远端部署账号体系**（商业化需要）
3. **任务配额、支付和成本统计**（商业化需要）

## 使用指南 📖

### 快速配置使用
1. 点击快速配置按钮（如"🇨🇳 中文PPT"）
2. 高级选项自动展开，显示已设置的配置
3. 可在此基础上继续调整参数

### 自定义输出路径
1. 在"输出文件存储路径"框中输入完整路径
2. 例如：`C:\Users\你的用户名\Documents\我的作品`
3. 留空则使用系统默认路径（`./outputs`）

### 使用注释功能
1. 任务完成后，在产物列表找到文件
2. 点击"添加注释"按钮
3. 输入你的修改要求，如：
   - "将配色改为暖色调"
   - "生成 10 页的演讲稿"
   - "添加公司 Logo"
4. 点击"提交处理"，AI 将基于原文件重新生成

## 已知限制 ⚠️

1. **路径验证**：前端不验证路径合法性，由后端验证
2. **注释入口**：仅在 image/html/pdf 类型文件上显示
3. **并发处理**：多个注释任务需要排队处理
4. **完整在线商业化**：还需要登录、计费、任务隔离和云存储

## 版本对比

| 功能 | V1 | V2 |
|------|----|----|
| 快速配置生效 | ❌ | ✅ |
| 模板提示词 | 累加混乱 | 替换清晰 |
| 文件预览 | 全部预览 | 不预览 |
| 文件路径显示 | ❌ | ✅ |
| 自定义输出路径 | ❌ | ✅ |
| AI 二次处理 | ❌ | ✅ |
| 下载按钮 | 小图标 | 大按钮 |

---

**更新完成**：2026年6月15日  
**构建状态**：✅ 通过  
**准备部署**：✅ 是

## 2026年6月30日：任务优先工作台

- 工作台默认进入“任务中心”，优先展示任务状态、列表、运行记录和产物。
- “新建任务”和“设置”改为独立页面，不再长期挤占任务看板空间。
- 桌面端使用任务列表与详情双栏布局；窄屏自动改为单栏。
- 创建任务成功后自动返回任务中心并选中新任务。
