import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const main = readFileSync(join(root, "src", "main.tsx"), "utf8");
const api = readFileSync(join(root, "src", "api.ts"), "utf8");
const html = readFileSync(join(root, "index.html"), "utf8");

for (const text of [
  "创作工作台",
  "生成看板",
  "开始生成",
  "清理未完成",
  "删除任务",
  "任务列表",
  "清除筛选",
  "选择输出文件夹",
  "选定此处",
  "风格细化",
  "项目风格",
  "参考风格",
  "上传资料",
  "移除文件",
  "产物",
  "中文",
  "英语",
  "快速开始",
  "不要编造",
  "本机 Codex（可选，无需在此配置 Key）",
  "API 模型配置（推荐）",
  "生成时间",
  "测试连接"
]) {
  assert.ok(main.includes(text), `Expected main.tsx to include Chinese UI text: ${text}`);
}

for (const text of ["自动 Skill", "Skill 路由", "Codex Skill 生成器"]) {
  assert.ok(!main.includes(text), `Product UI should not expose internal wording: ${text}`);
}
assert.ok(html.includes('lang="zh-CN"'), "Expected index.html to use zh-CN language");
assert.ok(html.includes("<title>创作工作台</title>"), "Expected document title to be Chinese");
assert.ok(api.includes("import.meta.env.VITE_API_BASE"), "Expected API client to support VITE_API_BASE for hosted frontends");
