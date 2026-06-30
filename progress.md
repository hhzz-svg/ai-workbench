## 2026-06-16 - Task: API 优先运行、Windows 发布包与 README 首屏
### What was done
- 将任务执行路径调整为 API 优先：用户选择已保存 API 配置时，后端直连 OpenAI-compatible API 写入本地产物；未选择配置时才使用本机 Codex 环境。
- 将前端、安装脚本和快速启动文档改为“API 配置推荐，Codex CLI 可选检测”的表达。
- 生成 README 专用 10 秒演示视频，并重写 README 第一屏，让价值主张、适合人群、视频入口和快速开始更靠前。
- 新增 Windows 发布包脚本和示例资料，并生成本地 release 资产 `dist/release/ai-workbench-windows-0.1.0.zip`。

### Testing
- `npm run test:backend`：通过，50 passed。
- `npm run test:frontend-localization`：通过。
- `npm run build:web`：通过。
- 校验 `dist/release/ai-workbench-windows-0.1.0.zip` 包含 `install.bat`、`start.bat`、`README.md`、`examples/sample-paper-notes.md`、`landing-page/assets/readme-demo.mp4`。

### Notes
- `backend/app/api_runner.py`：新增 API 直连执行器，解析模型返回的 fenced file blocks 并写入本地产物。
- `backend/app/jobs.py`：接入 API runner 分支，并修复 `prompt.txt` 中 `NEEDS_INPUT` 被误判的问题。
- `backend/tests/test_api_runner.py`：新增 API 产物写入、安全路径和 fallback 测试。
- `backend/tests/test_jobs.py`：新增 API 分支执行测试和 `NEEDS_INPUT` 扫描测试。
- `frontend/src/main.tsx`：将运行配置改为保存 API 配置后默认选中，Codex 作为可选环境。
- `frontend/tests/localization.test.mjs`：同步前端中文文案断言。
- `install.bat`、`start.bat`：增加 Codex 可选检测和 API 配置提示。
- `README.md`：重写首屏、快速开始和模型配置说明，并链接 README 演示视频。
- `docs/ONE_CLICK_START.md`、`docs/QUICK_START.md`：同步 API 优先使用路径。
- `docs/WINDOWS_RELEASE.md`：新增 Windows 发布包说明。
- `scripts/package-windows.ps1`：新增 Windows zip 打包脚本。
- `examples/sample-paper-notes.md`：新增首次试跑示例资料。
- `landing-page/assets/readme-demo.mp4`：新增 README 专用演示视频。
- `dist/release/ai-workbench-windows-0.1.0.zip`：本地生成的发布资产，位于 git 忽略目录。
- 回滚方式：用 git revert/checkout 回退上述已跟踪文件；删除 `dist/release/ai-workbench-windows-0.1.0.zip` 可移除本地发布资产。

## 2026-06-16 - Task: 替换演示视频为新面板版本
### What was done
- 将旧界面演示视频替换为当前“创作工作台/生成看板”新面板画面，README 中的展示视频不再露出旧 UI。
- 重新生成 README 首屏视觉图，让首屏右侧预览也同步到新面板。
- 重新生成本地 Windows 发布包，确保下载包内包含新的演示视频素材。

### Testing
- 抽帧检查 `landing-page/assets/readme-demo.mp4` 和 `landing-page/assets/workbench-demo.mp4`：画面均为当前新面板。
- `ffprobe` 校验 `landing-page/assets/workbench-demo.mp4`：1920x1080，8 秒。
- `ffprobe` 校验 `landing-page/assets/readme-demo.mp4`：1280x720，10 秒。
- `npm run test:backend`：通过，50 passed。
- `npm run test:frontend-localization`：通过。
- `npm run build:web`：通过。
- 校验 `dist/release/ai-workbench-windows-0.1.0.zip` 包含新的 `landing-page/assets/readme-demo.mp4` 和 `landing-page/assets/workbench-demo.mp4`。

### Notes
- `landing-page/assets/workbench-console-wide.png`：更新为当前新面板截图，作为视频画面来源。
- `landing-page/assets/workbench-demo.mp4`：替换为当前新面板演示视频。
- `landing-page/assets/key-visual.png`：重新生成 README 首屏视觉图，右侧预览同步新面板。
- `landing-page/assets/readme-demo.mp4`：重新生成 README 内嵌演示视频。
- `dist/release/ai-workbench-windows-0.1.0.zip`：本地重新生成的发布资产，位于 git 忽略目录。
- `progress.md`：追加本轮替换演示视频与验证记录。
- 回滚方式：用 git revert 回退本轮提交；若只回退本地发布资产，删除 `dist/release/ai-workbench-windows-0.1.0.zip` 后重新运行打包脚本即可。

## 2026-06-17 - Task: 配置 GitHub Release 自动发布
### What was done
- 新增 GitHub Actions Release workflow，推送 `v*` 标签时自动运行 Windows 打包脚本并上传 zip 到 GitHub Release。
- 补充 Windows 发版文档，说明通过 `git tag` 和 `git push origin <tag>` 发布。
- 处理 Chrome 页面上传本地 zip 受扩展权限限制的问题，改用 GitHub 远端自动打包上传，避免手动改浏览器扩展权限。

### Testing
- 已确认本地 `dist/release/ai-workbench-windows-0.1.0.zip` 存在。
- 已确认当前仓库没有 `v0.1.0` 标签，可用于触发首个 Release。
- 已推送 `v0.1.0` 标签并确认 GitHub Actions Release workflow 成功完成。
- 已确认 GitHub Release `AI Workbench v0.1.0` 存在，并包含 `ai-workbench-windows-0.1.0.zip` 资产。

### Notes
- `.github/workflows/release.yml`：新增 tag 触发的 Release workflow，使用 `scripts/package-windows.ps1` 生成 Windows zip 并通过 `softprops/action-gh-release@v2` 上传。
- `docs/WINDOWS_RELEASE.md`：新增 GitHub Release 自动发布步骤。
- `progress.md`：追加本轮发布流程配置记录。
- 回滚方式：删除远端 `v0.1.0` 标签和对应 Release 后，用 git revert 回退本轮提交。

## 2026-06-17 - Task: README 增加 Release 下载入口
### What was done
- 在 README 首屏演示视频下方新增 Windows 发布包直达链接。
- 将 Windows 快速开始里的下载入口改为 `AI Workbench v0.1.0 Release`，并明确 zip 文件名。

### Testing
- 检查 README 中已出现 `https://github.com/hhzz-svg/ai-workbench/releases/tag/v0.1.0`。

### Notes
- `README.md`：新增正式 Release 下载入口，并更新 Windows 快速开始下载说明。
- `progress.md`：追加本轮 README 链接更新记录。
- 回滚方式：用 git revert 回退本轮提交，或从 README 删除本轮新增的 Release 链接文本。

## 2026-06-17 - Task: 修复前端启动脚本
### What was done
- 修复 `start.ps1` 和 `start-lan.ps1` 的脚本根目录解析，避免前端路径被解析到错误位置。
- 将 PowerShell 启动脚本中的 `npm` 调用改为 `npm.cmd`，避免 Windows 执行策略拦截 `npm.ps1`。
- 简化 `start.bat`，让它委托 `start.ps1` 启动，避免 cmd 直接解析中文提示时出错。

### Testing
- 复现原问题：`start.ps1` 缺失时，`start.bat` 调用 PowerShell 启动失败，前端不会监听 `5173`。
- 运行修复后的 `start.bat`，确认输出 `Opening browser on http://127.0.0.1:5173`。
- 请求 `http://127.0.0.1:5173` 返回 `200`。
- 通过 Chrome 打开 `http://127.0.0.1:5173/`，确认页面标题为 `创作工作台`，页面包含工作台首屏内容。

### Notes
- `start.ps1`：新增稳定的 `$root` 解析，并改用 `npm.cmd`。
- `start-lan.ps1`：同步 `$root` 和 `npm.cmd` 修复。
- `start.bat`：改为 ASCII 启动壳，先检查依赖，再调用 `start.ps1`。
- `progress.md`：追加本轮前端启动修复记录。
- 回滚方式：用 git revert 回退本轮提交。

## 2026-06-20 - Task: 补完整 Windows 首次启动体验
### What was done
- 恢复并加固 Windows 本机和局域网启动脚本，确保 `start.bat` 委托的 `start.ps1` 存在，并在服务就绪后打开工作台。
- 让 `install.bat` 和 `start.bat` 从脚本所在目录运行，并在缺少前端或后端依赖时先自动进入安装流程。
- 为前端增加全局后端断连提示和“重新连接”入口；首次无 API 配置时增加“去设置 API”引导。
- 后端在没有 API 配置且本机没有 Codex CLI 时即时拒绝创建任务，避免新用户任务排队后才失败。
- 同步 README 和快速启动文档，补充断连处理、API 配置要求和启动脚本行为。

### Testing
- `node frontend/tests/startup-experience.test.mjs`：先失败于 `start.ps1` 缺失；修复后通过。
- `npm --prefix frontend test`：通过，2 个前端测试文件全部通过。
- `npm run test:backend`：通过，51 passed。
- `npm run build:web`：通过，Vite 构建成功。
- PowerShell 脚本解析检查：`start.ps1` 和 `start-lan.ps1` 均通过 `scriptblock` 解析。
- `cmd /c "echo.|start.bat"`：通过，输出 `Opening browser on http://127.0.0.1:5173`；验证后已停止本轮拉起的项目后台进程。

### Notes
- `install.bat`：固定工作目录到脚本所在目录，并增加项目结构检查。
- `start.bat`：启动前检查前端与后端依赖，缺失时自动运行安装脚本。
- `start.ps1`：恢复并加固本机启动脚本，等待 API/UI 就绪，输出端口占用提示。
- `start-lan.ps1`：恢复并加固局域网启动脚本，等待 API/UI 就绪后输出局域网访问地址。
- `frontend/src/api.ts`：统一 API 连接失败提示，并让下载地址和事件流支持 `VITE_API_BASE`。
- `frontend/src/main.tsx`：增加后端断连横幅、重连入口、健康检查和首次 API 配置引导。
- `frontend/src/styles.css`：新增断连横幅和首次配置提示样式，适配移动端。
- `frontend/src/types.ts`：新增健康检查返回类型。
- `frontend/tests/startup-experience.test.mjs`：新增首次启动体验静态验证。
- `backend/app/jobs.py`：增加本机 Codex 可用性判断。
- `backend/app/main.py`：无 API 配置且无 Codex CLI 时即时返回可理解错误。
- `backend/tests/test_api.py`：补充无配置/无 Codex 的拒绝测试，并固定相关测试环境假设。
- `README.md`、`docs/ONE_CLICK_START.md`、`docs/QUICK_START.md`：同步首次启动、API 配置和断连处理说明。
- `progress.md`：追加本轮启动体验补全和验证记录。
- 回滚方式：用 `git revert` 回退本轮提交；若尚未提交，可用 `git checkout -- <上述文件>` 并删除 `frontend/tests/startup-experience.test.mjs`。

## 2026-06-20 - Task: 重新发布 Windows 首启修复版本
### What was done
- 将项目版本号更新为 `2.0.1`，用于发布包含 Windows 首次启动修复的新版包。
- 更新 README 下载入口和 GitHub Release 文案，使发布包名称与 `ai-workbench-windows-2.0.1.zip` 对齐。
- 本地生成 Windows 发布包预检，确认打包脚本能产出新版 zip。

### Testing
- `npm --prefix frontend test`：通过，2 个前端测试文件全部通过。
- `npm run test:backend`：通过，51 passed。
- `npm run build:web`：通过，Vite 构建成功。
- PowerShell 脚本解析检查：`start.ps1` 和 `start-lan.ps1` 均通过 `scriptblock` 解析。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\package-windows.ps1`：通过，生成 `dist\release\ai-workbench-windows-2.0.1.zip`。

### Notes
- `package.json`：版本号更新为 `2.0.1`。
- `README.md`：下载入口和 zip 文件名更新到 `v2.0.1`。
- `.github/workflows/release.yml`：Release 说明更新为本轮首启体验修复内容。
- `dist/release/ai-workbench-windows-2.0.1.zip`：本地预检生成的发布资产，位于 git 忽略目录。
- `progress.md`：追加本轮重新发布准备记录。
- 回滚方式：用 `git revert` 回退本轮提交；若只清理本地预检资产，删除 `dist/release/ai-workbench-windows-2.0.1.zip`。

## 2026-06-20 - Task: 校验 Windows 2.0.1 发布包内容
### What was done
- 检查本地预检 zip 的关键文件清单，确认新版发布包包含 Windows 启动脚本和前端源码。

### Testing
- 检查 `dist\release\ai-workbench-windows-2.0.1.zip`：包含 `start.bat`、`start.ps1`、`start-lan.ps1`、`install.bat`、`package.json`、`frontend/src/main.tsx`。

### Notes
- `progress.md`：追加本轮发布包内容校验记录。
- 回滚方式：用 `git revert` 回退本轮提交；本地 zip 可删除 `dist/release/ai-workbench-windows-2.0.1.zip` 后重新生成。

## 2026-06-30 - Task: 调研并确定任务优先的工作台 UI 改造设计
### What was done
- 审计当前工作台的信息架构与浏览器实况，确认创建表单常驻左栏、任务列表与详情纵向堆叠是界面臃肿的主要原因。
- 调研 Dify、n8n、Open WebUI 与 Plane 的工作区、执行记录和对象管理模式，比较三种改造方案。
- 确定“任务中心 + 独立新建页 + 独立设置页”为采用方案，并明确布局、响应式规则、数据流、实现边界和验收标准。
### Testing
- 对照当前 `frontend/src/main.tsx` 和 `frontend/src/styles.css` 完成设计可行性检查；方案复用现有组件与 API，不涉及后端协议、数据库或任务执行规则。
- 使用 Playwright 打开 `http://127.0.0.1:5173` 并读取页面结构，确认当前首屏同时包含完整创建表单、任务指标、任务列表和详情区域。
- 自检设计文档，无 `TBD`、`TODO`、占位条目、范围矛盾或未决方案。
### Notes
- `docs/superpowers/specs/2026-06-30-task-first-workbench-design.md`：新增任务优先工作台调研与设计规范。
- `progress.md`：追加本轮调研、设计与验证记录。
- 回滚方式：提交后使用 `git revert <本轮设计提交>`；未提交时删除设计文档并回退 `progress.md` 本轮追加段落。
