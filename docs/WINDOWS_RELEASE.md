# Windows Release 打包说明

## 生成发布包

在仓库根目录运行：

```powershell
.\scripts\package-windows.ps1
```

默认会读取根目录 `package.json` 的版本号，并生成：

```text
dist\release\ai-workbench-windows-<version>.zip
```

这个压缩包可作为 GitHub Release 的 Windows 下载资产上传。

## 发布到 GitHub Release

仓库已配置 GitHub Actions。推送版本标签即可在 GitHub 上自动生成 Release，并上传 Windows zip：

```powershell
git tag v0.1.0
git push origin v0.1.0
```

后续版本先更新 `package.json` 的版本号，再推送对应的 `v<version>` 标签。

## 包内内容

- `install.bat`：检测 Python、Node.js，安装前后端依赖，并提示 Codex CLI 为可选环境。
- `start.bat`：启动本地后端和前端，并打开工作台。
- `backend/`、`frontend/`：完整应用源码。
- `docs/`：使用、部署和发版说明。
- `examples/`：新用户可直接上传试跑的示例资料。
- `landing-page/`：项目展示页和演示素材。

## 使用路径

普通用户：

1. 解压 `ai-workbench-windows-<version>.zip`
2. 双击 `install.bat`
3. 双击 `start.bat`
4. 在「设置」里保存 API Base URL、模型和 API Key
5. 回到「新建」创建任务

已经安装 Codex CLI 的用户也可以不保存 API 配置，直接使用本机 Codex 环境。

## 验证清单

发布前至少确认：

```powershell
npm run test:backend
npm run test:frontend-localization
npm run build:web
.\scripts\package-windows.ps1
```

然后解压生成的 zip，确认根目录存在 `install.bat`、`start.bat`、`README.md`、`examples/sample-paper-notes.md`。
