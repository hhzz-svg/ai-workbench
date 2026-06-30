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
