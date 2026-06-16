import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  BookOpenText,
  Brush,
  CheckCircle2,
  ChevronRight,
  CircleStop,
  ClipboardCheck,
  Clock3,
  CornerLeftUp,
  Download,
  ListFilter,
  FileArchive,
  FileText,
  FileUp,
  Folder,
  FolderOpen,
  Globe2,
  HardDrive,
  Image as ImageIcon,
  KeyRound,
  Layers3,
  LayoutDashboard,
  MonitorCheck,
  Play,
  PlugZap,
  RefreshCcw,
  Settings,
  ShieldCheck,
  Sparkles,
  Trash2,
  Upload,
  WandSparkles,
  Wifi,
  X
} from "lucide-react";
import { api } from "./api";
import type {
  Artifact,
  DirectoryListing,
  FilesystemRoot,
  Job,
  JobEvent,
  JobStatus,
  ProviderPayload,
  ProviderProfile,
  SkillInfo,
  UploadedFile
} from "./types";
import "./styles.css";

const statusLabels: Record<JobStatus, string> = {
  pending: "排队中",
  running: "生成中",
  needs_input: "待补充",
  succeeded: "已交付",
  failed: "未完成",
  canceled: "已取消"
};

const productTypes: Record<string, string> = {
  auto: "自动生成",
  "nature-paper2ppt": "论文演示",
  "nature-polishing": "学术润色",
  "guizang-ppt-skill": "网页演示",
  "make-poster": "学术海报",
  "mondo-poster-design": "视觉海报"
};

const artifactKindLabels: Record<string, string> = {
  markdown: "文稿",
  html: "网页",
  presentation: "演示文稿",
  pdf: "PDF",
  image: "图片",
  json: "配置",
  file: "文件"
};

const constraintChoices = [
  "不要编造信息",
  "严格基于上传资料",
  "保留关键英文术语",
  "生成检查报告",
  "优先输出可编辑文件",
  "适合演讲或打印"
];

const formatChoices = [
  "按需求自动匹配",
  "PPTX 演示文稿",
  "单页网页演示",
  "PDF 学术海报",
  "PNG 视觉海报",
  "Markdown 文稿"
];

type StyleOptionGroup = {
  key: string;
  label: string;
  hint: string;
  choices: string[];
};

const styleOptionGroups: StyleOptionGroup[] = [
  {
    key: "projectStyle",
    label: "项目风格",
    hint: "整体设计调性",
    choices: ["极简", "商务", "学术", "科技感", "杂志编辑", "活泼"]
  },
  {
    key: "colorScheme",
    label: "配色偏好",
    hint: "主色调方向",
    choices: ["蓝调", "暖调", "黑白", "莫兰迪", "品牌色"]
  },
  {
    key: "iconStyle",
    label: "图标风格",
    hint: "图标与装饰元素",
    choices: ["线性", "填色", "手绘", "拟物", "无图标"]
  }
];

const languageLabels: Record<string, string> = {
  auto: "自动判断",
  "zh-CN": "中文",
  en: "英语"
};

const emptyProviderForm: ProviderPayload = {
  name: "",
  provider: "proxy",
  base_url: "https://api.openai.com/v1",
  model: "gpt-5.5",
  wire_api: "responses",
  api_key: ""
};

type Notice = { kind: "success" | "error" | "info"; text: string };

type ProductTemplate = {
  id: string;
  title: string;
  subtitle: string;
  prompt: string;
  language: string;
  format: string;
  constraints: string[];
};

const productTemplates: ProductTemplate[] = [
  {
    id: "paper-talk",
    title: "论文演示",
    subtitle: "论文、实验图和笔记转成组会或答辩演示",
    prompt:
      "请基于我上传的论文、实验图表和补充笔记，生成一份中文学术演示。需要包含研究背景、核心问题、方法设计、关键结果、创新点、局限、后续计划和答辩问答准备。",
    language: "zh-CN",
    format: "PPTX 演示文稿",
    constraints: ["严格基于上传资料", "保留关键英文术语", "生成检查报告"]
  },
  {
    id: "web-deck",
    title: "网页演示",
    subtitle: "主题、素材和图片整理为可浏览的单页演示",
    prompt:
      "请根据我提供的主题、文字素材和图片，生成一份适合横向翻页展示的网页演示。需要有清晰章节、强视觉节奏、适合现场汇报，并输出可预览的 HTML。",
    language: "zh-CN",
    format: "单页网页演示",
    constraints: ["适合演讲或打印", "优先输出可编辑文件"]
  },
  {
    id: "paper-poster",
    title: "学术海报",
    subtitle: "论文资料生成会议海报和打印文件",
    prompt:
      "请基于上传的论文、图表、项目说明和参考风格，生成一张英文学术会议海报。请突出研究问题、方法、关键发现、图表说明、结论和联系方式占位。",
    language: "en",
    format: "PDF 学术海报",
    constraints: ["严格基于上传资料", "适合演讲或打印", "优先输出可编辑文件"]
  },
  {
    id: "visual-poster",
    title: "视觉海报",
    subtitle: "活动、封面或品牌主题的英文创意海报",
    prompt:
      "请根据我的主题和受众，生成一套英文视觉海报方案。需要包含核心文案、画面构图、色彩和字体建议，并尽可能输出可预览图片或可复制的高质量生成提示词。",
    language: "en",
    format: "PNG 视觉海报",
    constraints: ["适合演讲或打印", "优先输出可编辑文件"]
  },
  {
    id: "polish",
    title: "学术润色",
    subtitle: "章节、摘要或回复信改成期刊风格表达",
    prompt:
      "请润色我提供的学术段落或章节，提升逻辑、表达和专业度。请保留原意，标出关键修改理由，并给出适合投稿或回复审稿的版本。",
    language: "auto",
    format: "Markdown 文稿",
    constraints: ["不要编造信息", "保留关键英文术语", "生成检查报告"]
  }
];

function App() {
  const [skills, setSkills] = useState<SkillInfo[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [providers, setProviders] = useState<ProviderProfile[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [events, setEvents] = useState<JobEvent[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [view, setView] = useState<"create" | "settings">("create");
  const [statusFilter, setStatusFilter] = useState<JobStatus | "all">("all");
  const selectedJob = jobs.find((job) => job.id === selectedJobId) ?? jobs[0] ?? null;

  const refresh = async () => {
    const [skillRows, jobRows, providerRows] = await Promise.all([api.skills(), api.jobs(), api.providers()]);
    setSkills(skillRows);
    setJobs(jobRows);
    setProviders(providerRows);
    if (!selectedJobId || !jobRows.some((job) => job.id === selectedJobId)) {
      setSelectedJobId(jobRows[0]?.id ?? null);
    }
  };

  useEffect(() => {
    refresh().catch(console.error);
  }, []);

  useEffect(() => {
    if (!selectedJob) {
      setArtifacts([]);
      return;
    }
    api.artifacts(selectedJob.id).then(setArtifacts).catch(() => setArtifacts([]));
    if (selectedJob.status !== "running" && selectedJob.status !== "pending") return;
    const source = new EventSource(`/api/jobs/${selectedJob.id}/events`);
    source.onmessage = (message) => {
      const event = JSON.parse(message.data) as JobEvent;
      setEvents((current) => [...current.slice(-120), event]);
      if (event.type === "stream.end" || event.type.startsWith("job.")) {
        refresh().catch(console.error);
        api.artifacts(selectedJob.id).then(setArtifacts).catch(() => setArtifacts([]));
      }
    };
    source.onerror = () => source.close();
    return () => source.close();
  }, [selectedJob?.id, selectedJob?.status]);

  const grouped = useMemo(() => {
    const groups: Record<JobStatus, Job[]> = {
      pending: [],
      running: [],
      needs_input: [],
      succeeded: [],
      failed: [],
      canceled: []
    };
    for (const job of jobs) groups[job.status].push(job);
    return groups;
  }, [jobs]);

  const visibleJobs = useMemo(() => {
    const rows = statusFilter === "all" ? jobs : jobs.filter((job) => job.status === statusFilter);
    return [...rows].sort((a, b) => (a.updated_at < b.updated_at ? 1 : -1));
  }, [jobs, statusFilter]);

  const clearFailed = async () => {
    await api.clearFailedJobs();
    setSelectedJobId(null);
    setEvents([]);
    await refresh();
  };

  const deleteJob = async (jobId: string) => {
    await api.deleteJob(jobId);
    setSelectedJobId(null);
    setEvents([]);
    await refresh();
  };

  const unfinishedCount = grouped.failed.length + grouped.canceled.length;

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><Sparkles size={22} /></div>
          <div>
            <h1>创作工作台</h1>
            <p>资料到演示、海报和学术文稿</p>
          </div>
        </div>
        <div className="segmented" aria-label="页面切换">
          <button type="button" className={view === "create" ? "active" : ""} onClick={() => setView("create")}>
            <Play size={16} /> 新建
          </button>
          <button type="button" className={view === "settings" ? "active" : ""} onClick={() => setView("settings")}>
            <Settings size={16} /> 设置
          </button>
        </div>
        {view === "create" ? (
          <CreateJob providers={providers} onCreated={(job) => { setSelectedJobId(job.id); refresh(); }} />
        ) : (
          <SettingsPanel skills={skills} onSaved={refresh} providers={providers} />
        )}
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <span className="eyebrow"><LayoutDashboard size={14} /> 本地创作中心</span>
            <h2>生成看板</h2>
            <p>把需求、资料、进度和成果放在同一个工作流里。</p>
          </div>
          <div className="topbar-right">
            <div className="run-badges">
              <span><ShieldCheck size={15} /> 本机运行</span>
              <span><Clock3 size={15} /> 队列处理</span>
            </div>
            <div className="toolbar">
              <button className="ghost-button" type="button" onClick={clearFailed} disabled={unfinishedCount === 0}>
                <Trash2 size={17} /> 清理未完成
              </button>
              <button className="icon-button" type="button" onClick={() => refresh()} title="刷新">
                <RefreshCcw size={18} />
              </button>
            </div>
          </div>
        </header>

        <section className="summary-grid" aria-label="任务概览">
          <Metric label="待处理" value={grouped.pending.length + grouped.needs_input.length} tone="amber"
            active={statusFilter === "pending"}
            onClick={() => setStatusFilter((current) => (current === "pending" ? "all" : "pending"))} />
          <Metric label="生成中" value={grouped.running.length} tone="blue"
            active={statusFilter === "running"}
            onClick={() => setStatusFilter((current) => (current === "running" ? "all" : "running"))} />
          <Metric label="已交付" value={grouped.succeeded.length} tone="green"
            active={statusFilter === "succeeded"}
            onClick={() => setStatusFilter((current) => (current === "succeeded" ? "all" : "succeeded"))} />
          <Metric label="可清理" value={unfinishedCount} tone="red"
            active={statusFilter === "failed"}
            onClick={() => setStatusFilter((current) => (current === "failed" ? "all" : "failed"))} />
        </section>

        <section className="job-list" aria-label="任务列表">
          <div className="job-list-head">
            <h3><ListFilter size={16} /> 任务列表</h3>
            {statusFilter === "all" ? (
              <span className="filter-state">{visibleJobs.length} 个任务</span>
            ) : (
              <button type="button" className="clear-filter" onClick={() => setStatusFilter("all")}>
                仅看「{statusLabels[statusFilter]}」· 清除筛选
              </button>
            )}
          </div>
          {visibleJobs.length === 0 ? (
            <p className="job-list-empty">
              {statusFilter === "all" ? "还没有任务，从左侧新建一个开始。" : "该状态下暂无任务。"}
            </p>
          ) : (
            visibleJobs.map((job) => (
              <button
                key={job.id}
                type="button"
                className={`job-row ${selectedJob?.id === job.id ? "selected" : ""}`}
                onClick={() => { setSelectedJobId(job.id); setEvents([]); }}
              >
                <span className={`job-status ${job.status}`}>{statusLabels[job.status]}</span>
                <span className="job-row-main">
                  <strong>{typeName(job.skill_type)}</strong>
                  <small>{job.prompt.slice(0, 140)}</small>
                </span>
                <span className="job-row-time">{formatDate(job.updated_at)}</span>
                <span className="job-row-caret"><ChevronRight size={16} /></span>
              </button>
            ))
          )}
        </section>

        {selectedJob ? (
          <JobDetail
            job={selectedJob}
            artifacts={artifacts}
            events={events}
            onCancel={async () => { await api.cancelJob(selectedJob.id); refresh(); }}
            onDelete={() => deleteJob(selectedJob.id)}
          />
        ) : (
          <div className="empty-state">
            <WandSparkles size={24} />
            <span>新建一个任务后，这里会显示进度、记录和产物。</span>
            <span className="empty-cta">在左侧选择一个方向、补充需求，点击「开始生成」。</span>
          </div>
        )}
      </section>
    </main>
  );
}

function Metric({
  label,
  value,
  tone,
  active,
  onClick
}: {
  label: string;
  value: number;
  tone: "blue" | "green" | "red" | "amber";
  active?: boolean;
  onClick?: () => void;
}) {
  return (
    <button
      type="button"
      className={`metric ${tone} ${active ? "active" : ""}`}
      onClick={onClick}
      aria-pressed={active}
      title={`筛选：${label}`}
    >
      <span>{label}</span>
      <strong>{value}</strong>
    </button>
  );
}

function DirectoryPicker({
  initialPath,
  onSelect,
  onClose
}: {
  initialPath?: string;
  onSelect: (path: string) => void;
  onClose: () => void;
}) {
  const [listing, setListing] = useState<DirectoryListing | null>(null);
  const [roots, setRoots] = useState<FilesystemRoot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastPath, setLastPath] = useState<string | undefined>(undefined);

  const friendlyError = (raw: string) => {
    const text = (raw || "").toLowerCase();
    if (!raw || text.includes("bad gateway") || text.includes("502") || text.includes("failed to fetch") || text.includes("networkerror")) {
      return "无法连接到本地服务。请确认后端已启动（运行 start.bat，或本地 8000 端口的服务在运行）后重试。";
    }
    return raw;
  };

  const load = async (path?: string) => {
    setLoading(true);
    setError(null);
    setLastPath(path);
    try {
      const result = await api.listDirectory(path);
      setListing(result);
    } catch (err) {
      setError(friendlyError(err instanceof Error ? err.message : ""));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    api.listRoots().then((r) => setRoots(r.roots)).catch(() => setRoots([]));
    load(initialPath && initialPath.trim() ? initialPath.trim() : undefined).catch(() => undefined);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" onClick={onClose}>
      <div className="modal-card dir-picker" onClick={(event) => event.stopPropagation()}>
        <div className="modal-head">
          <strong><FolderOpen size={18} /> 选择输出文件夹</strong>
          <button type="button" className="icon-button" onClick={onClose} aria-label="关闭"><X size={18} /></button>
        </div>

        {roots.length > 0 && (
          <div className="dir-roots">
            {roots.map((root) => (
              <button type="button" key={root.path} className="dir-root-chip" onClick={() => load(root.path)} title={root.path}>
                <HardDrive size={14} /> {root.name}
              </button>
            ))}
          </div>
        )}

        <div className="dir-current" title={listing?.path}>
          <span className="dir-current-path">{listing?.path ?? (loading ? "读取中…" : "—")}</span>
        </div>

        <div className="dir-list">
          {!loading && !error && listing?.parent && (
            <button type="button" className="dir-row up" onClick={() => load(listing.parent ?? undefined)}>
              <CornerLeftUp size={16} /> <span>上级目录</span>
            </button>
          )}
          {loading && <p className="dir-empty">读取中…</p>}
          {error && (
            <div className="dir-error">
              <p>{error}</p>
              <button type="button" className="secondary-button" onClick={() => load(lastPath)}>
                <RefreshCcw size={15} /> 重试
              </button>
            </div>
          )}
          {!loading && !error && listing && listing.entries.length === 0 && (
            <p className="dir-empty">该文件夹下没有子文件夹</p>
          )}
          {!loading && !error && listing?.entries.map((entry) => (
            <button type="button" className="dir-row" key={entry.path} onClick={() => load(entry.path)}>
              <Folder size={16} /> <span>{entry.name}</span>
              <ChevronRight size={14} className="dir-row-caret" />
            </button>
          ))}
        </div>

        <div className="modal-foot">
          <button type="button" className="ghost-button" onClick={onClose}>取消</button>
          <button
            type="button"
            className="primary-button"
            disabled={!listing?.path}
            onClick={() => { if (listing?.path) { onSelect(listing.path); onClose(); } }}
          >
            <CheckCircle2 size={16} /> 选定此处
          </button>
        </div>
      </div>
    </div>
  );
}

function CreateJob({ providers, onCreated }: { providers: ProviderProfile[]; onCreated: (job: Job) => void }) {
  const [providerId, setProviderId] = useState<string>("");
  const [prompt, setPrompt] = useState("");
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [busy, setBusy] = useState(false);
  const [language, setLanguage] = useState("auto");
  const [format, setFormat] = useState(formatChoices[0]);
  const [selectedConstraints, setSelectedConstraints] = useState<string[]>(["不要编造信息"]);
  const [customConstraints, setCustomConstraints] = useState("");
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [outputPath, setOutputPath] = useState("");
  const [showPicker, setShowPicker] = useState(false);
  const [styleChoices, setStyleChoices] = useState<Record<string, string>>({});
  const [styleCustom, setStyleCustom] = useState<Record<string, string>>({});
  const [referenceNote, setReferenceNote] = useState("");
  const [referenceFiles, setReferenceFiles] = useState<UploadedFile[]>([]);

  useEffect(() => {
    if (!providerId && providers.length > 0) {
      setProviderId(providers[0].id);
    }
  }, [providerId, providers]);

  const uploadFiles = async (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;
    setBusy(true);
    try {
      const uploaded = await Promise.all(Array.from(fileList).map((file) => api.uploadFile(file)));
      setFiles((current) => [...current, ...uploaded]);
    } catch (error) {
      alert(`文件上传失败：${error instanceof Error ? error.message : "未知错误"}`);
    } finally {
      setBusy(false);
    }
  };

  const removeFile = (fileId: string) => {
    setFiles((current) => current.filter((file) => file.id !== fileId));
  };

  const toggleConstraint = (choice: string) => {
    setSelectedConstraints((current) =>
      current.includes(choice) ? current.filter((item) => item !== choice) : [...current, choice]
    );
  };

  const toggleStyleChoice = (groupKey: string, choice: string) => {
    setStyleChoices((current) => {
      const next = { ...current };
      if (next[groupKey] === choice) {
        delete next[groupKey];
      } else {
        next[groupKey] = choice;
      }
      return next;
    });
  };

  const uploadReference = async (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;
    setBusy(true);
    try {
      const uploaded = await Promise.all(Array.from(fileList).map((file) => api.uploadFile(file)));
      setReferenceFiles((current) => [...current, ...uploaded]);
    } catch (error) {
      alert(`参考图上传失败：${error instanceof Error ? error.message : "未知错误"}`);
    } finally {
      setBusy(false);
    }
  };

  const applyTemplate = (template: ProductTemplate) => {
    setSelectedTemplateId((current) => current === template.id ? null : template.id);
    if (selectedTemplateId === template.id) {
      // 取消选择，清空提示词中该模板的部分
      setPrompt("");
      return;
    }
    // 应用新模板，替换整个提示词
    setPrompt(template.prompt);
    setLanguage(template.language);
    setFormat(template.format);
    setSelectedConstraints(template.constraints);
  };

  const quickFillChinese = () => {
    setLanguage("zh-CN");
    setFormat("PPTX 演示文稿");
    setSelectedConstraints(["严格基于上传资料", "保留关键英文术语"]);
    setShowAdvanced(true); // 自动展开高级选项以显示效果
  };

  const quickFillEnglish = () => {
    setLanguage("en");
    setFormat("PDF 学术海报");
    setSelectedConstraints(["严格基于上传资料", "适合演讲或打印"]);
    setShowAdvanced(true);
  };

  const quickFillWeb = () => {
    setLanguage("zh-CN");
    setFormat("单页网页演示");
    setSelectedConstraints(["优先输出可编辑文件", "适合演讲或打印"]);
    setShowAdvanced(true);
  };

  const resetForm = () => {
    setPrompt("");
    setFiles([]);
    setLanguage("auto");
    setFormat(formatChoices[0]);
    setSelectedConstraints(["不要编造信息"]);
    setCustomConstraints("");
    setSelectedTemplateId(null);
    setStyleChoices({});
    setStyleCustom({});
    setReferenceNote("");
    setReferenceFiles([]);
  };

  const submit = async () => {
    if (!prompt.trim()) {
      return;
    }
    setBusy(true);
    try {
      const constraints = [...selectedConstraints, customConstraints.trim()].filter(Boolean);
      const options: Record<string, unknown> = {
        language,
        format,
        constraints,
        routing: "auto",
        template: selectedTemplateId
      };

      // 结构化风格选项：选中推荐项或填了自定义才进 options，否则保持默认
      for (const group of styleOptionGroups) {
        const picked = styleChoices[group.key];
        const custom = (styleCustom[group.key] ?? "").trim();
        const value = custom || picked;
        if (value) options[group.key] = value;
      }
      if (referenceNote.trim()) {
        options.referenceNote = referenceNote.trim();
      }

      // 如果指定了输出路径，添加到 options
      if (outputPath.trim()) {
        options.outputPath = outputPath.trim();
      }

      // 参考图作为资料一并提交
      const allFileIds = [...files, ...referenceFiles].map((file) => file.id);

      const job = await api.createJob({
        skillType: "auto",
        prompt,
        fileIds: allFileIds,
        options,
        providerProfileId: providerId || null
      });
      setPrompt("");
      setFiles([]);
      setSelectedTemplateId(null);
      setShowAdvanced(false);
      setOutputPath("");
      setStyleChoices({});
      setStyleCustom({});
      setReferenceNote("");
      setReferenceFiles([]);
      onCreated(job);
    } catch (error) {
      alert(`创建任务失败：${error instanceof Error ? error.message : "未知错误"}`);
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="panel create-panel" onSubmit={(event) => { event.preventDefault(); submit(); }}>
      <section className="quick-start" aria-label="快速开始">
        <div className="section-heading">
          <span><WandSparkles size={16} /> 快速开始</span>
          <small>选一个方向，再补充你的具体要求</small>
        </div>
        <div className="template-grid">
          {productTemplates.map((template) => (
            <button
              className={`template-card ${selectedTemplateId === template.id ? "active" : ""}`}
              key={template.id}
              type="button"
              onClick={() => applyTemplate(template)}
            >
              {templateIcon(template.id)}
              <span>
                <strong>{template.title}</strong>
                <small>{template.subtitle}</small>
              </span>
            </button>
          ))}
        </div>
      </section>

      <div className="quick-config-bar">
        <span className="quick-config-label"><Settings size={14} /> 快速配置</span>
        <button type="button" className="quick-config-btn" onClick={quickFillChinese} title="中文演示文稿">
          🇨🇳 中文PPT
        </button>
        <button type="button" className="quick-config-btn" onClick={quickFillEnglish} title="英文学术海报">
          🇬🇧 英文海报
        </button>
        <button type="button" className="quick-config-btn" onClick={quickFillWeb} title="网页展示">
          🌐 网页演示
        </button>
        <button type="button" className="quick-config-btn reset" onClick={resetForm} title="重置表单">
          <RefreshCcw size={14} /> 重置
        </button>
      </div>

      <label>
        运行配置
        <select value={providerId} onChange={(event) => setProviderId(event.target.value)}>
          <option value="">本机 Codex（可选，无需在此配置 Key）</option>
          {providers.map((provider) => (
            <option key={provider.id} value={provider.id}>{provider.name} · {provider.model}</option>
          ))}
        </select>
        <small className="input-hint">推荐在设置中保存 API 配置；不选配置时才使用本机 Codex 环境。</small>
      </label>

      <label>
        具体需求
        <textarea
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          rows={8}
          placeholder="例如：根据论文和实验图，生成一份 12 页中文答辩演示；或做一张 A0 英文学术海报。"
        />
      </label>

      <label>
        输出文件存储路径（可选）
        <div className="path-input-row">
          <input
            type="text"
            value={outputPath}
            onChange={(event) => setOutputPath(event.target.value)}
            placeholder="例如：C:\Users\Documents\outputs 或留空使用默认路径"
          />
          <button type="button" className="secondary-button path-browse" onClick={() => setShowPicker(true)}>
            <FolderOpen size={16} /> 浏览
          </button>
        </div>
        <small className="input-hint">留空将使用默认输出目录，或点「浏览」直接在磁盘里选择文件夹</small>
      </label>

      {showPicker && (
        <DirectoryPicker
          initialPath={outputPath}
          onSelect={(path) => setOutputPath(path)}
          onClose={() => setShowPicker(false)}
        />
      )}

      <button
        type="button"
        className="advanced-toggle"
        onClick={() => setShowAdvanced(!showAdvanced)}
      >
        {showAdvanced ? "收起高级选项" : "展开高级选项"} {showAdvanced ? "▲" : "▼"}
      </button>

      {showAdvanced && (
        <>
          <div className="grid-fields">
            <label>
              语言
              <select value={language} onChange={(event) => setLanguage(event.target.value)}>
                <option value="auto">自动判断</option>
                <option value="zh-CN">中文</option>
                <option value="en">英语</option>
              </select>
            </label>
            <label>
              目标格式
              <select value={format} onChange={(event) => setFormat(event.target.value)}>
                {formatChoices.map((choice) => <option key={choice} value={choice}>{choice}</option>)}
              </select>
            </label>
          </div>

          <fieldset className="constraint-box">
            <legend>硬性要求</legend>
            {constraintChoices.map((choice) => (
              <label className="check-row" key={choice}>
                <input type="checkbox" checked={selectedConstraints.includes(choice)} onChange={() => toggleConstraint(choice)} />
                <span>{choice}</span>
              </label>
            ))}
            <input value={customConstraints} onChange={(event) => setCustomConstraints(event.target.value)} placeholder="补充其他要求" />
          </fieldset>

          <fieldset className="constraint-box style-options">
            <legend>风格细化（不选则默认）</legend>
            {styleOptionGroups.map((group) => (
              <div className="option-group" key={group.key}>
                <div className="option-group-head">
                  <strong>{group.label}</strong>
                  <small>{group.hint}</small>
                </div>
                <div className="option-chips">
                  {group.choices.map((choice) => (
                    <button
                      type="button"
                      key={choice}
                      className={`option-chip ${styleChoices[group.key] === choice ? "active" : ""}`}
                      onClick={() => toggleStyleChoice(group.key, choice)}
                    >
                      {choice}
                    </button>
                  ))}
                </div>
                <input
                  className="option-custom"
                  value={styleCustom[group.key] ?? ""}
                  onChange={(event) => setStyleCustom((current) => ({ ...current, [group.key]: event.target.value }))}
                  placeholder={`自定义${group.label}（优先于上方选择）`}
                />
              </div>
            ))}

            <div className="option-group">
              <div className="option-group-head">
                <strong>参考风格</strong>
                <small>上传参考图或描述想要的风格</small>
              </div>
              <input
                className="option-custom"
                value={referenceNote}
                onChange={(event) => setReferenceNote(event.target.value)}
                placeholder="例如：参考苹果发布会风格 / 这个链接的排版"
              />
              <label className="upload-zone reference-upload">
                <ImageIcon size={16} />
                <span>{referenceFiles.length ? `已添加 ${referenceFiles.length} 张参考图` : "上传参考图（可选）"}</span>
                <input type="file" accept="image/*" multiple onChange={(event) => uploadReference(event.target.files)} />
              </label>
            </div>
          </fieldset>
        </>
      )}

      <label className="upload-zone">
        <Upload size={18} />
        <span>{files.length ? `继续上传资料（已有 ${files.length} 个文件）` : "上传资料"}</span>
        <input type="file" multiple onChange={(event) => uploadFiles(event.target.files)} />
      </label>

      {files.length > 0 && (
        <div className="file-list" aria-label="已上传资料">
          {files.map((file) => (
            <div className="file-row" key={file.id}>
              <FileText size={16} />
              <span>
                <strong>{file.name}</strong>
                <small>{formatBytes(file.size)}</small>
              </span>
              <button type="button" className="icon-button" onClick={() => removeFile(file.id)} title={`移除文件 ${file.name}`} aria-label={`移除文件 ${file.name}`}>
                <X size={16} />
              </button>
            </div>
          ))}
        </div>
      )}

      <button className="primary-button" disabled={busy || !prompt.trim()}>
        <Play size={18} /> {busy ? "创建中..." : "开始生成"}
      </button>
    </form>
  );
}

function SettingsPanel({ providers, skills, onSaved }: { providers: ProviderProfile[]; skills: SkillInfo[]; onSaved: () => void }) {
  const [form, setForm] = useState<ProviderPayload>(emptyProviderForm);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<Notice | null>(null);

  const save = async () => {
    const localError = validateProviderForm(form);
    if (localError) return setNotice({ kind: "error", text: localError });
    setBusy(true);
    try {
      await api.createProvider(form);
      setForm({ ...emptyProviderForm, base_url: form.base_url, model: form.model, wire_api: form.wire_api });
      setNotice({ kind: "success", text: "配置已保存。" });
      onSaved();
    } catch (error) {
      setNotice({ kind: "error", text: error instanceof Error ? error.message : "保存失败。" });
    } finally {
      setBusy(false);
    }
  };

  const testCurrent = async () => {
    const localError = validateProviderForm(form);
    if (localError) return setNotice({ kind: "error", text: localError });
    setBusy(true);
    setNotice({ kind: "info", text: "正在测试当前接口..." });
    try {
      const result = await api.validateProvider(form);
      setNotice({ kind: result.ok ? "success" : "error", text: result.message });
    } catch (error) {
      setNotice({ kind: "error", text: error instanceof Error ? error.message : "测试连接失败。" });
    } finally {
      setBusy(false);
    }
  };

  const testDefault = async () => {
    setBusy(true);
    setNotice({ kind: "info", text: "正在检查本机运行环境..." });
    try {
      const result = await api.validateDefaultProvider();
      setNotice({ kind: result.ok ? "success" : "error", text: result.message });
    } catch (error) {
      setNotice({ kind: "error", text: error instanceof Error ? error.message : "测试失败。" });
    } finally {
      setBusy(false);
    }
  };

  const testSaved = async (provider: ProviderProfile) => {
    setBusy(true);
    setNotice({ kind: "info", text: `正在测试 ${provider.name}...` });
    try {
      const result = await api.validateSavedProvider(provider.id);
      setNotice({ kind: result.ok ? "success" : "error", text: `${provider.name}：${result.message}` });
    } catch (error) {
      setNotice({ kind: "error", text: error instanceof Error ? error.message : "测试连接失败。" });
    } finally {
      setBusy(false);
    }
  };

  const remove = async (providerId: string) => {
    setBusy(true);
    try {
      await api.deleteProvider(providerId);
      setNotice({ kind: "success", text: "配置已删除。" });
      onSaved();
    } catch (error) {
      setNotice({ kind: "error", text: error instanceof Error ? error.message : "删除失败。" });
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="panel settings-panel">
      <div className="default-card">
        <div>
          <strong><MonitorCheck size={17} /> 本机 Codex 环境（可选）</strong>
          <span>适合已经安装 Codex CLI 的用户；普通用户保存下方 API 配置即可运行任务。</span>
        </div>
        <button className="secondary-button" disabled={busy} onClick={testDefault} type="button">
          <CheckCircle2 size={16} /> 检测 Codex
        </button>
      </div>

      <div className="info-card compact">
        <strong>生成时间</strong>
        <span>大型演示、海报和图片类任务会经历资料读取、结构规划、内容生成、文件写入和预览索引，通常需要数分钟。</span>
      </div>
      <div className="capability-strip">
        {(skills.length ? skills.map((skill) => typeName(skill.id)) : ["演示", "海报", "网页", "学术文稿"]).map((name) => (
          <span key={name}>{name}</span>
        ))}
      </div>

      <div className="settings-title"><KeyRound size={18} /> API 模型配置（推荐）</div>
      <label>配置名称<input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} placeholder="例如：学校代理 / 本地网关 / 公司接口" /></label>
      <label>Base URL<input value={form.base_url} onChange={(event) => setForm({ ...form, base_url: event.target.value })} placeholder="https://api.example.com/v1" /></label>
      <label>模型<input value={form.model} onChange={(event) => setForm({ ...form, model: event.target.value })} placeholder="gpt-5.5" /></label>
      <label>
        接口类型
        <select value={form.wire_api} onChange={(event) => setForm({ ...form, wire_api: event.target.value as ProviderPayload["wire_api"] })}>
          <option value="responses">Responses</option>
          <option value="chat_completions">Chat Completions</option>
        </select>
      </label>
      <label>API Key<input type="password" value={form.api_key} onChange={(event) => setForm({ ...form, api_key: event.target.value })} placeholder="只保存在本机" /></label>
      {notice && <p className={`notice ${notice.kind}`}>{notice.text}</p>}
      <div className="button-row">
        <button className="secondary-button" disabled={busy} onClick={testCurrent} type="button">
          <PlugZap size={16} /> 测试连接
        </button>
        <button className="primary-button" disabled={busy} onClick={save} type="button">
          <KeyRound size={18} /> 保存配置
        </button>
      </div>

      <div className="provider-list" aria-label="已保存配置">
        {providers.length === 0 && <p className="muted provider-empty">还没有 API 配置。普通用户建议先保存一个 OpenAI-compatible API 配置。</p>}
        {providers.map((provider) => (
          <div className="provider-row" key={provider.id}>
            <div>
              <span>{provider.name}</span>
              <small>{provider.model} · {displayBaseUrl(provider.base_url)}</small>
            </div>
            <span className={`key-state ${provider.has_api_key ? "ready" : "missing"}`}>Key {provider.has_api_key ? "已配置" : "缺失"}</span>
            <div className="provider-actions">
              <button className="secondary-button" disabled={busy} onClick={() => testSaved(provider)} type="button">
                <PlugZap size={16} /> 测试
              </button>
              <button className="delete-button" disabled={busy} onClick={() => remove(provider.id)} type="button">
                <Trash2 size={16} /> 删除
              </button>
            </div>
          </div>
        ))}
      </div>
      <div className="network-note"><Wifi size={16} /> 局域网访问只开放这个工作台，模型密钥仍保存在运行服务的电脑上。</div>
    </section>
  );
}

function JobDetail({
  job,
  artifacts,
  events,
  onCancel,
  onDelete
}: {
  job: Job;
  artifacts: Artifact[];
  events: JobEvent[];
  onCancel: () => void;
  onDelete: () => void;
}) {
  const canDelete = !["pending", "running"].includes(job.status);
  return (
    <section className="detail">
      <div className="detail-header">
        <div>
          <span className={`pill ${job.status}`}>{statusLabels[job.status]}</span>
          <h3>{typeName(job.skill_type)}</h3>
          <p>{job.prompt}</p>
          <div className="detail-meta">
            <span><Clock3 size={14} /> {formatDate(job.created_at)}</span>
            <span><FileArchive size={14} /> {job.file_ids.length} 个资料</span>
            <span><Globe2 size={14} /> {languageLabels[String(job.options.language ?? "auto")] ?? "自动判断"}</span>
            <span><Layers3 size={14} /> {String(job.options.format ?? "按需求自动匹配")}</span>
          </div>
          {job.error && <p className="error-text">未完成原因：{job.error}</p>}
        </div>
        <div className="detail-actions">
          {job.status === "running" && <button className="danger-button" type="button" onClick={onCancel}><CircleStop size={18} /> 取消</button>}
          {canDelete && <button className="ghost-button" type="button" onClick={onDelete}><Trash2 size={17} /> 删除任务</button>}
        </div>
      </div>
      <div className="detail-grid">
        <section className="log-panel">
          <h4><Activity size={17} /> 运行记录</h4>
          <div className="log-lines">
            {(events.length ? events : [{ type: "idle", message: "暂无实时事件。", job_id: job.id }]).map((event, index) => (
              <div key={`${event.type}-${index}`}><b>{formatEventType(event.type)}</b><span>{event.message}</span></div>
            ))}
          </div>
        </section>
        <section className="artifact-panel">
          <h4><FileArchive size={17} /> 产物</h4>
          <div className="artifact-list">
            {artifacts.length === 0 ? (
              <p className="muted artifact-empty">还没有可用产物。任务完成后会自动出现在这里。</p>
            ) : (
              artifacts.map((artifact) => <ArtifactCard artifact={artifact} key={artifact.id} />)
            )}
          </div>
        </section>
      </div>
    </section>
  );
}

function ArtifactCard({ artifact }: { artifact: Artifact }) {
  const url = api.downloadUrl(artifact.id);
  const [showAnnotation, setShowAnnotation] = React.useState(false);
  const [annotation, setAnnotation] = React.useState("");
  const [processingAnnotation, setProcessingAnnotation] = React.useState(false);

  const handleAnnotationSubmit = async () => {
    if (!annotation.trim()) return;
    setProcessingAnnotation(true);
    try {
      const result = await api.annotateArtifact(artifact.id, annotation.trim());
      alert(`✅ ${result.message}\n新任务 ID: ${result.new_job_id}`);
      setAnnotation("");
      setShowAnnotation(false);
    } catch (error) {
      alert(`处理失败：${error instanceof Error ? error.message : "未知错误"}`);
    } finally {
      setProcessingAnnotation(false);
    }
  };

  return (
    <article className="artifact-card-compact">
      <div className="artifact-header">
        <div className="artifact-info">
          {artifactIcon(artifact.kind)}
          <div>
            <strong>{artifact.name}</strong>
            <small>{artifactKindLabels[artifact.kind] ?? artifact.kind} · {formatBytes(artifact.size)}</small>
            <small className="artifact-path">路径：{artifact.path}</small>
          </div>
        </div>
        <div className="artifact-actions-vertical">
          <a
            className="download-button-primary"
            href={url}
            download={artifact.name}
            title="下载文件"
          >
            <Download size={16} /> 下载
          </a>
          {["image", "html", "pdf"].includes(artifact.kind) && (
            <button
              className="secondary-button-small"
              onClick={() => setShowAnnotation(!showAnnotation)}
              type="button"
            >
              <FileText size={16} /> {showAnnotation ? "取消注释" : "添加注释"}
            </button>
          )}
        </div>
      </div>

      {showAnnotation && (
        <div className="annotation-box">
          <label>
            AI 二次处理指令
            <textarea
              value={annotation}
              onChange={(e) => setAnnotation(e.target.value)}
              placeholder="例如：请将这个海报的配色改为蓝色系，或者：请基于这个PPT生成演讲稿"
              rows={3}
            />
          </label>
          <button
            className="primary-button"
            onClick={handleAnnotationSubmit}
            disabled={processingAnnotation || !annotation.trim()}
            type="button"
          >
            <WandSparkles size={16} /> {processingAnnotation ? "处理中..." : "提交处理"}
          </button>
        </div>
      )}
    </article>
  );
}

function templateIcon(id: string) {
  if (id === "paper-talk") return <BookOpenText size={18} />;
  if (id === "web-deck") return <MonitorCheck size={18} />;
  if (id === "paper-poster") return <FileUp size={18} />;
  if (id === "visual-poster") return <Brush size={18} />;
  return <ClipboardCheck size={18} />;
}

function artifactIcon(kind: Artifact["kind"]) {
  if (kind === "image") return <ImageIcon size={18} />;
  if (kind === "presentation") return <MonitorCheck size={18} />;
  if (kind === "pdf") return <FileArchive size={18} />;
  return <FileText size={18} />;
}

function validateProviderForm(form: ProviderPayload) {
  if (!form.name.trim()) return "请先给配置命名。";
  if (!form.base_url.trim()) return "请填写 Base URL。";
  if (form.base_url.trim().startsWith("sk-")) return "Base URL 填成了 API Key，请把 sk- 开头的内容放到 API Key。";
  if (!/^https?:\/\//i.test(form.base_url.trim())) return "Base URL 必须以 http:// 或 https:// 开头。";
  if (!form.model.trim()) return "请填写模型名称。";
  if (!form.api_key.trim()) return "请填写 API Key。";
  if (/^https?:\/\//i.test(form.api_key.trim())) return "API Key 看起来像 URL，请把接口地址放到 Base URL。";
  return "";
}

function displayBaseUrl(baseUrl: string) {
  return baseUrl.startsWith("sk-") ? "疑似 API Key（已隐藏）" : baseUrl;
}

function typeName(id: string) {
  return productTypes[id] ?? "生成任务";
}

function formatEventType(type: string) {
  if (type === "idle") return "等待中";
  if (type === "stream.end") return "同步完成";
  if (type.includes("error") || type.includes("failed")) return "错误";
  if (type.startsWith("job.")) return "任务状态";
  if (type.includes("message")) return "生成消息";
  if (type.includes("delta") || type.includes("output")) return "实时输出";
  return "运行消息";
}

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  }).format(date);
}

function formatBytes(size: number) {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
}

createRoot(document.getElementById("root")!).render(<App />);
