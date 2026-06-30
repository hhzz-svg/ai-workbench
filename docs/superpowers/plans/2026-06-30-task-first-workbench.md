# Task-First Workbench Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the local AI workbench around a default task-management view, with separate full-width pages for task creation and settings.

**Architecture:** Keep the existing React component and API boundaries. Expand the top-level view state to `jobs | create | settings`, move the existing `CreateJob` and `SettingsPanel` components into the main workspace, and render the task list/detail as a responsive master-detail grid. No backend or task-protocol changes are required.

**Tech Stack:** React, TypeScript, Vite, CSS, Node.js built-in test runner, Playwright CLI.

---

## File map

- Create `frontend/tests/workbench-layout.test.mjs`: static contract for default view, three-page navigation, task master-detail layout, and responsive CSS.
- Modify `frontend/src/main.tsx`: top-level navigation and conditional page rendering; preserve all existing task, SSE, form, settings, and artifact behavior.
- Modify `frontend/src/styles.css`: compact 220px navigation, page header, status filters, responsive task list/detail grid, and full-width form pages.
- Modify `docs/UPDATES_V2.md`: describe the new default task-center workflow.
- Modify `progress.md`: append implementation and verification evidence.

### Task 1: Lock the new information architecture with a failing test

**Files:**
- Create: `frontend/tests/workbench-layout.test.mjs`

- [ ] **Step 1: Add the structural test**

Create the file with this complete content:

```js
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const main = readFileSync(join(root, "src", "main.tsx"), "utf8");
const styles = readFileSync(join(root, "src", "styles.css"), "utf8");

assert.ok(
  main.includes('useState<"jobs" | "create" | "settings">("jobs")'),
  "Task center should be the default page"
);

for (const text of ["任务中心", "新建任务", "设置"]) {
  assert.ok(main.includes(text), `Expected primary navigation item: ${text}`);
}

for (const contract of [
  'aria-label="主导航"',
  'className="task-layout"',
  'className="sidebar-status"',
  'setView("jobs")'
]) {
  assert.ok(main.includes(contract), `Expected workbench layout contract: ${contract}`);
}

for (const selector of [
  ".nav-list",
  ".page-header",
  ".task-layout",
  ".sidebar-status"
]) {
  assert.ok(styles.includes(selector), `Expected workbench style: ${selector}`);
}

assert.match(
  styles,
  /\.task-layout\s*\{[^}]*grid-template-columns:\s*minmax\(320px,[^;]+;/s,
  "Desktop task center should use a master-detail grid"
);
assert.match(
  styles,
  /@media \(max-width: 1180px\)[\s\S]*?\.task-layout\s*\{[^}]*grid-template-columns:\s*1fr;/,
  "Task center should stack below 1180px"
);
```

- [ ] **Step 2: Run the test and confirm the red state**

Run: `node frontend/tests/workbench-layout.test.mjs`

Expected: FAIL at `Task center should be the default page` because the current view type is only `create | settings` and defaults to `create`.

- [ ] **Step 3: Commit the test**

```bash
git add frontend/tests/workbench-layout.test.mjs
git commit -m "test: define task-first workbench layout"
```

### Task 2: Implement task-first page routing and master-detail content

**Files:**
- Modify: `frontend/src/main.tsx:211-428`
- Test: `frontend/tests/workbench-layout.test.mjs`
- Test: `frontend/tests/localization.test.mjs`

- [ ] **Step 1: Make task center the default view**

Replace the current view state with:

```tsx
const [view, setView] = useState<"jobs" | "create" | "settings">("jobs");
```

- [ ] **Step 2: Replace the old form-heavy sidebar with stable navigation**

The sidebar must contain the existing brand followed by this navigation and status block:

```tsx
<nav className="nav-list" aria-label="主导航">
  <button type="button" className={view === "jobs" ? "active" : ""} onClick={() => setView("jobs")}>
    <LayoutDashboard size={18} />
    <span><strong>任务中心</strong><small>查看进度与产物</small></span>
  </button>
  <button type="button" className={view === "create" ? "active" : ""} onClick={() => setView("create")}>
    <Play size={18} />
    <span><strong>新建任务</strong><small>选择方向并生成</small></span>
  </button>
  <button type="button" className={view === "settings" ? "active" : ""} onClick={() => setView("settings")}>
    <Settings size={18} />
    <span><strong>设置</strong><small>模型与运行配置</small></span>
  </button>
</nav>
<div className="sidebar-status">
  <span className={health?.ok ? "status-dot online" : "status-dot"} />
  <div>
    <strong>{health?.ok ? "本地服务已连接" : "等待本地服务"}</strong>
    <small>{health?.codex_available ? "Codex 环境可用" : "使用已保存的 API 配置"}</small>
  </div>
</div>
```

- [ ] **Step 3: Add a page header driven by the active view**

Immediately before the component return, define:

```tsx
const pageCopy = {
  jobs: { eyebrow: "本地创作中心", title: "任务中心", description: "集中查看生成进度、运行记录和交付产物。" },
  create: { eyebrow: "开始创作", title: "新建任务", description: "选择创作方向，补充需求和资料后开始生成。" },
  settings: { eyebrow: "工作台配置", title: "设置", description: "管理模型连接和本机运行能力。" }
} as const;
```

Render this header below the connection banner:

```tsx
<header className="page-header">
  <div>
    <span className="eyebrow"><LayoutDashboard size={14} /> {pageCopy[view].eyebrow}</span>
    <h2>{pageCopy[view].title}</h2>
    <p>{pageCopy[view].description}</p>
  </div>
  <div className="page-actions">
    {view === "jobs" ? (
      <>
        <button className="ghost-button" type="button" onClick={clearFailed} disabled={unfinishedCount === 0}>
          <Trash2 size={17} /> 清理未完成
        </button>
        <button className="icon-button" type="button" onClick={() => refresh()} title="刷新">
          <RefreshCcw size={18} />
        </button>
        <button className="primary-button compact" type="button" onClick={() => setView("create")}>
          <Play size={17} /> 新建任务
        </button>
      </>
    ) : (
      <button className="ghost-button" type="button" onClick={() => setView("jobs")}>
        <CornerLeftUp size={17} /> 返回任务中心
      </button>
    )}
  </div>
</header>
```

- [ ] **Step 4: Render one page at a time**

Wrap the existing summary, job list, and detail in the `jobs` branch. Place the list and detail inside `<div className="task-layout">`. Use this empty state so the page has a direct creation path:

```tsx
<div className="empty-state">
  <WandSparkles size={24} />
  <strong>还没有任务</strong>
  <span>创建第一个任务后，这里会集中显示进度、记录和产物。</span>
  <button className="primary-button compact" type="button" onClick={() => setView("create")}>
    <Play size={17} /> 新建任务
  </button>
</div>
```

Render the other two branches with the existing components:

```tsx
{view === "create" && (
  <div className="page-content form-page">
    <CreateJob
      providers={providers}
      codexAvailable={health?.codex_available ?? false}
      onConfigureApi={() => setView("settings")}
      onCreated={(job) => {
        setSelectedJobId(job.id);
        setView("jobs");
        refresh();
      }}
    />
  </div>
)}
{view === "settings" && (
  <div className="page-content form-page">
    <SettingsPanel skills={skills} onSaved={refresh} providers={providers} />
  </div>
)}
```

- [ ] **Step 5: Update old layout-dependent copy**

Change `还没有任务，从左侧新建一个开始。` to `还没有任务，点击右上角“新建任务”开始。`. Remove the old sidebar-only segmented control and the old topbar badges.

- [ ] **Step 6: Run focused tests**

Run: `node frontend/tests/workbench-layout.test.mjs && node frontend/tests/localization.test.mjs`

Expected: The layout test may still fail on missing CSS selectors; localization must pass.

### Task 3: Implement the compact visual system and responsive layout

**Files:**
- Modify: `frontend/src/styles.css:147-240,626-900,1390-1545`
- Test: `frontend/tests/workbench-layout.test.mjs`

- [ ] **Step 1: Replace the application shell and sidebar styles**

Use these base rules:

```css
.app-shell {
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr);
  min-height: 100vh;
}

.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  background: var(--surface);
  border-right: 1px solid var(--border);
  padding: var(--s4);
  display: flex;
  flex-direction: column;
  gap: var(--s4);
}

.nav-list {
  display: grid;
  gap: 4px;
}

.nav-list button {
  width: 100%;
  border: 0;
  border-radius: var(--radius);
  background: transparent;
  color: var(--muted);
  padding: 10px;
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: center;
  gap: 10px;
  text-align: left;
}

.nav-list button:hover { background: var(--surface-2); color: var(--text); }
.nav-list button.active { background: var(--brand-tint); color: var(--brand-strong); }
.nav-list button span { display: grid; gap: 2px; }
.nav-list button strong { font-size: 13px; font-weight: 600; }
.nav-list button small { color: var(--muted); font-size: 11px; }

.sidebar-status {
  margin-top: auto;
  border-top: 1px solid var(--border);
  padding-top: var(--s3);
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: center;
  gap: 9px;
}

.sidebar-status div { display: grid; gap: 2px; }
.sidebar-status strong { font-size: 12px; }
.sidebar-status small { color: var(--muted); font-size: 11px; line-height: 1.35; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--st-pending-fg); }
.status-dot.online { background: var(--st-success-fg); box-shadow: 0 0 0 3px var(--st-success-bg); }
```

- [ ] **Step 2: Replace the topbar and metric-card treatment**

Use a border-bottom page header and compact filters:

```css
.workspace { min-width: 0; padding: var(--s6); display: flex; flex-direction: column; gap: var(--s4); }
.page-header { display: flex; justify-content: space-between; align-items: flex-end; gap: var(--s4); padding-bottom: var(--s4); border-bottom: 1px solid var(--border); }
.page-header h2 { margin: 3px 0 0; font-size: 24px; line-height: 1.16; font-weight: 600; }
.page-header p { margin: 5px 0 0; color: var(--muted); font-size: 13px; }
.page-actions { display: flex; align-items: center; justify-content: flex-end; gap: 8px; flex-wrap: wrap; }
.primary-button.compact { width: auto; min-height: 38px; padding: 0 14px; }
.summary-grid { display: grid; grid-template-columns: repeat(4, minmax(110px, 1fr)); gap: 8px; }
.metric { min-height: 44px; padding: 9px 12px; border-radius: var(--radius-sm); }
.metric strong { font-size: 18px; }
```

- [ ] **Step 3: Add the task master-detail and form-page rules**

```css
.task-layout {
  display: grid;
  grid-template-columns: minmax(320px, 0.8fr) minmax(520px, 1.4fr);
  gap: var(--s4);
  align-items: start;
}

.task-layout .job-list { max-height: calc(100vh - 188px); overflow: auto; }
.task-layout .detail { min-width: 0; }
.form-page { width: min(100%, 960px); }
.form-page .panel { width: 100%; }
```

- [ ] **Step 4: Replace responsive shell rules**

```css
@media (max-width: 1180px) {
  .task-layout { grid-template-columns: 1fr; }
  .task-layout .job-list { max-height: none; }
  .detail-grid { grid-template-columns: 1fr; }
}

@media (max-width: 760px) {
  .app-shell { grid-template-columns: 1fr; }
  .sidebar { position: static; width: auto; height: auto; border-right: 0; border-bottom: 1px solid var(--border); padding: 12px; }
  .brand p, .sidebar-status { display: none; }
  .nav-list { grid-template-columns: repeat(3, 1fr); }
  .nav-list button { grid-template-columns: 1fr; justify-items: center; text-align: center; padding: 8px; }
  .nav-list button small { display: none; }
  .workspace { padding: 14px; }
  .page-header { align-items: stretch; flex-direction: column; }
  .page-actions { justify-content: stretch; }
  .page-actions .primary-button, .page-actions .ghost-button { flex: 1; }
  .summary-grid { grid-template-columns: repeat(2, 1fr); }
}
```

- [ ] **Step 5: Run frontend tests and build**

Run: `npm --prefix frontend test && npm run build:web`

Expected: all Node tests pass; TypeScript and Vite build complete successfully.

- [ ] **Step 6: Commit implementation**

```bash
git add frontend/src/main.tsx frontend/src/styles.css frontend/tests/workbench-layout.test.mjs
git commit -m "feat: make task center the default workbench"
```

### Task 4: Browser QA, documentation, and completion evidence

**Files:**
- Modify: `docs/UPDATES_V2.md`
- Modify: `progress.md`

- [ ] **Step 1: Run the local frontend and backend**

Run the existing development commands and confirm both endpoints respond:

```powershell
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
npm --prefix frontend run dev -- --host 127.0.0.1
```

Expected: `/api/health` returns `ok: true`; `http://127.0.0.1:5173` returns HTTP 200.

- [ ] **Step 2: Verify the three pages with Playwright CLI**

At 1440px, verify the default page exposes `任务中心`, `新建任务`, `设置`, and a `.task-layout` whose computed `grid-template-columns` has two tracks when a detail exists. Navigate to 新建任务 and 设置 and confirm only the chosen page content is visible.

At 768px, verify `document.documentElement.scrollWidth <= window.innerWidth`, the navigation stays usable, and task content is stacked.

Expected: no console errors, horizontal overflow, clipped primary actions, or overlapping panels.

- [ ] **Step 3: Update user-facing documentation**

Append a “2026年6月30日：任务优先工作台” section to `docs/UPDATES_V2.md` explaining:

```markdown
## 2026年6月30日：任务优先工作台

- 工作台默认进入“任务中心”，优先展示任务状态、列表、运行记录和产物。
- “新建任务”和“设置”改为独立页面，不再长期挤占任务看板空间。
- 桌面端使用任务列表与详情双栏布局；窄屏自动改为单栏。
- 创建任务成功后自动返回任务中心并选中新任务。
```

- [ ] **Step 4: Append the required progress record**

Append one `progress.md` entry using the repository format. Record the information-architecture change under `What was done`, exact commands and browser checks under `Testing`, changed files and an executable `git revert <implementation-commit>` rollback under `Notes`.

- [ ] **Step 5: Run the completion suite**

Run:

```powershell
npm --prefix frontend test
npm run build:web
npm run test:backend
git diff --check
```

Expected: all frontend tests pass, Vite build passes, backend tests pass, and `git diff --check` reports no errors.

- [ ] **Step 6: Commit documentation and evidence**

```bash
git add docs/UPDATES_V2.md progress.md
git commit -m "docs: record task-first workbench rollout"
```

