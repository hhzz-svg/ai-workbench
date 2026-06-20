import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const frontendRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const repoRoot = dirname(frontendRoot);

const main = readFileSync(join(frontendRoot, "src", "main.tsx"), "utf8");
const api = readFileSync(join(frontendRoot, "src", "api.ts"), "utf8");
const styles = readFileSync(join(frontendRoot, "src", "styles.css"), "utf8");
const startBat = readFileSync(join(repoRoot, "start.bat"), "utf8");

assert.ok(existsSync(join(repoRoot, "start.ps1")), "Expected start.ps1 to be included for start.bat");
assert.ok(existsSync(join(repoRoot, "start-lan.ps1")), "Expected start-lan.ps1 to be included for LAN startup");

const startPs1 = readFileSync(join(repoRoot, "start.ps1"), "utf8");
assert.ok(startBat.includes("start.ps1"), "start.bat should delegate to the PowerShell startup script");
assert.ok(startPs1.includes("/api/health"), "start.ps1 should wait for the backend health endpoint");
assert.ok(startPs1.includes("port 8000") && startPs1.includes("5173"), "start.ps1 should explain occupied startup ports");
assert.ok(startPs1.includes("Start-Process"), "start.ps1 should open the workbench after services are ready");

for (const text of [
  "无法连接到本地后端",
  "重新连接",
  "请保持 start.bat 窗口打开",
  "去设置 API"
]) {
  assert.ok(main.includes(text), `Expected first-run guidance in main.tsx: ${text}`);
}

for (const text of [
  "请先保存一个 API 配置",
  "普通用户建议先保存一个 OpenAI-compatible API 配置",
  "测试连接"
]) {
  assert.ok(main.includes(text), `Expected API setup guidance in main.tsx: ${text}`);
}

assert.ok(api.includes("buildApiErrorMessage"), "API client should normalize connection failures");
assert.ok(styles.includes(".connection-banner"), "Global API failure banner should have styling");
