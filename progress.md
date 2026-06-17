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
