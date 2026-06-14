"use client";

import { useMemo, useState } from "react";
import { PlatformShell } from "@/components/PlatformShell";
import { StatusBadge } from "@/components/StatusBadge";

type Tone = "cyan" | "green" | "amber" | "violet" | "slate";
type NodeCategory = "signal" | "evidence" | "reasoning" | "policy" | "action" | "record";
type Lens = "all" | "signal" | "evidence" | "reasoning" | "policy" | "action" | "record";

type GraphNode = {
  id: string;
  label: string;
  category: NodeCategory;
  owner: string;
  summary: string;
  evidence: string[];
  impact: string;
};

type NodePosition = {
  x: number;
  y: number;
};

const nodes: GraphNode[] = [
  {
    id: "alert",
    label: "Alert",
    category: "signal",
    owner: "triage_agent",
    summary: "Checkout API latency anomaly enters the incident workflow.",
    evidence: ["p95 latency crossed critical threshold", "Production checkout path affected"],
    impact: "Starts the incident lifecycle and creates the triage context.",
  },
  {
    id: "metric",
    label: "Metric",
    category: "evidence",
    owner: "observability_agent",
    summary: "Telemetry shows latency degradation and cache health collapse.",
    evidence: ["p95 latency: 2.8s", "Cache hit ratio: 41%", "DB latency elevated by 63%"],
    impact: "Provides quantitative proof for the root-cause hypothesis.",
  },
  {
    id: "logs",
    label: "Logs",
    category: "evidence",
    owner: "observability_agent",
    summary: "Application logs show fallback and retry warnings.",
    evidence: ["Repeated cache miss fallback", "Checkout worker retry pattern", "No security error signature"],
    impact: "Supports cache-path degradation rather than auth or security failure.",
  },
  {
    id: "deployment",
    label: "Deployment",
    category: "evidence",
    owner: "runbook_retrieval_agent",
    summary: "Recent cache configuration change is identified as relevant context.",
    evidence: ["cache-config-v18 detected", "No code deploy in the last 30 minutes", "Rollback candidate available"],
    impact: "Connects observed symptoms to a reversible configuration change.",
  },
  {
    id: "hypothesis",
    label: "Hypothesis",
    category: "reasoning",
    owner: "hypothesis_agent",
    summary: "Cache configuration regression is ranked as the leading explanation.",
    evidence: ["Metric anomaly aligns with config timing", "Logs support fallback path", "Rollback exists"],
    impact: "Transforms raw evidence into a decision-ready operational theory.",
  },
  {
    id: "policy",
    label: "Risk Policy",
    category: "policy",
    owner: "risk_safety_agent",
    summary: "Production rollback requires human approval before execution.",
    evidence: ["Customer-facing production system", "Rollback changes live config", "Alternative DB restart is blocked"],
    impact: "Prevents unsafe autonomous action and keeps the operator in control.",
  },
  {
    id: "approval",
    label: "Approval",
    category: "policy",
    owner: "approval_agent",
    summary: "Operator reviews evidence, policy reason, risk, and rollback plan.",
    evidence: ["Recommended action", "Evidence lineage", "Policy reason", "Rollback plan"],
    impact: "This is the human-in-the-loop checkpoint before production remediation.",
  },
  {
    id: "remediation",
    label: "Remediation",
    category: "action",
    owner: "remediation_executor",
    summary: "Approved rollback restores previous known-good cache configuration.",
    evidence: ["Reversible config rollback", "No database restart", "Controlled execution path"],
    impact: "Executes only the approved, low-risk remediation path.",
  },
  {
    id: "recovery",
    label: "Recovery",
    category: "action",
    owner: "execution_review_agent",
    summary: "Post-action telemetry confirms service recovery.",
    evidence: ["p95 latency: 2.8s → 480ms", "Cache hit ratio: 41% → 89%", "Error rate normalized"],
    impact: "Validates that remediation fixed the customer-facing incident.",
  },
  {
    id: "postmortem",
    label: "Postmortem",
    category: "record",
    owner: "postmortem_agent",
    summary: "Final incident record captures evidence, decisions, actions, and learning.",
    evidence: ["Root cause summary", "Approval record", "Execution review", "Recovery proof"],
    impact: "Turns the incident into an auditable organizational memory.",
  },
];

const edges: [string, string][] = [
  ["alert", "metric"],
  ["alert", "logs"],
  ["alert", "deployment"],
  ["metric", "hypothesis"],
  ["logs", "hypothesis"],
  ["deployment", "hypothesis"],
  ["hypothesis", "policy"],
  ["policy", "approval"],
  ["approval", "remediation"],
  ["remediation", "recovery"],
  ["recovery", "postmortem"],
];

const nodePositions: Record<string, NodePosition> = {
  alert: { x: 10, y: 52 },
  metric: { x: 28, y: 24 },
  logs: { x: 28, y: 52 },
  deployment: { x: 28, y: 80 },
  hypothesis: { x: 48, y: 52 },
  policy: { x: 65, y: 34 },
  approval: { x: 65, y: 70 },
  remediation: { x: 81, y: 49 },
  recovery: { x: 90, y: 66 },
  postmortem: { x: 87, y: 86 },
};

const lensOptions: { label: string; value: Lens; focus: string; active: string[] }[] = [
  {
    label: "All",
    value: "all",
    focus: "hypothesis",
    active: [],
  },
  {
    label: "Signals",
    value: "signal",
    focus: "alert",
    active: ["alert", "metric", "logs", "deployment", "hypothesis"],
  },
  {
    label: "Evidence",
    value: "evidence",
    focus: "metric",
    active: ["alert", "metric", "logs", "deployment", "hypothesis", "policy"],
  },
  {
    label: "Reasoning",
    value: "reasoning",
    focus: "hypothesis",
    active: ["metric", "logs", "deployment", "hypothesis", "policy", "approval"],
  },
  {
    label: "Policy",
    value: "policy",
    focus: "policy",
    active: ["hypothesis", "policy", "approval", "remediation", "recovery", "postmortem"],
  },
  {
    label: "Actions",
    value: "action",
    focus: "remediation",
    active: ["policy", "approval", "remediation", "recovery", "postmortem"],
  },
  {
    label: "Records",
    value: "record",
    focus: "postmortem",
    active: ["hypothesis", "policy", "approval", "remediation", "recovery", "postmortem"],
  },
];

function categoryTone(category: NodeCategory): Tone {
  if (category === "signal") return "cyan";
  if (category === "evidence") return "green";
  if (category === "reasoning") return "violet";
  if (category === "policy") return "amber";
  if (category === "action") return "cyan";
  return "slate";
}

function categoryDotClass(category: NodeCategory) {
  if (category === "signal") return "bg-cyan-300";
  if (category === "evidence") return "bg-emerald-300";
  if (category === "reasoning") return "bg-violet-300";
  if (category === "policy") return "bg-amber-300";
  if (category === "action") return "bg-sky-300";
  return "bg-slate-300";
}

function shortNodeLabel(label: string) {
  if (label === "Risk Policy") return "Policy";
  if (label === "Remediation") return "Fix";
  if (label === "Postmortem") return "Report";
  return label;
}

function connectedNodes(startId: string, depth: number) {
  const connected = new Set<string>([startId]);
  let frontier = new Set<string>([startId]);

  for (let level = 0; level < depth; level += 1) {
    const next = new Set<string>();

    edges.forEach(([from, to]) => {
      if (frontier.has(from) && !connected.has(to)) next.add(to);
      if (frontier.has(to) && !connected.has(from)) next.add(from);
    });

    next.forEach((id) => connected.add(id));
    frontier = next;
  }

  return connected;
}

function edgeHasNode(edge: [string, string], nodeId: string) {
  return edge[0] === nodeId || edge[1] === nodeId;
}

function edgePath(from: NodePosition, to: NodePosition) {
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const length = Math.sqrt(dx * dx + dy * dy) || 1;

  const radius = 8.6;
  const x1 = from.x + (dx / length) * radius;
  const y1 = from.y + (dy / length) * radius;
  const x2 = to.x - (dx / length) * radius;
  const y2 = to.y - (dy / length) * radius;

  const midX = (x1 + x2) / 2;
  return `M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`;
}

export default function KnowledgeGraphPage() {
  const [selectedId, setSelectedId] = useState("hypothesis");
  const [lens, setLens] = useState<Lens>("all");
  const [depth, setDepth] = useState(2);

  const selectedNode = nodes.find((node) => node.id === selectedId) || nodes[0];
  const selectedLens = lensOptions.find((item) => item.value === lens) || lensOptions[0];

  const relationConnected = useMemo(
    () => connectedNodes(selectedId, depth),
    [selectedId, depth]
  );

  const activatedNodeIds = useMemo(() => {
    const ids = new Set<string>();

    selectedLens.active.forEach((id) => ids.add(id));
    relationConnected.forEach((id) => ids.add(id));

    const humanTail = ["policy", "approval", "remediation", "recovery", "postmortem"];
    const selectedIsHumanTail = humanTail.includes(selectedId);
    const lensNeedsHumanTail = lens === "policy" || lens === "action" || lens === "record";
    const depthReachedGate = depth >= 3 && (relationConnected.has("policy") || relationConnected.has("approval"));

    if (selectedIsHumanTail || lensNeedsHumanTail || depthReachedGate) {
      humanTail.forEach((id) => ids.add(id));
    }

    if (lens === "record") {
      ["hypothesis", "policy", "approval", "remediation", "recovery", "postmortem"].forEach((id) => ids.add(id));
    }

    return ids;
  }, [selectedLens, relationConnected, selectedId, lens, depth]);

  const neuralEdges = useMemo(() => {
    const humanTail = ["policy", "approval", "remediation", "recovery", "postmortem"];
    const selectedIsHumanTail = humanTail.includes(selectedId);
    const lensNeedsHumanTail = lens === "policy" || lens === "action" || lens === "record";
    const depthReachedGate = depth >= 3 && (relationConnected.has("policy") || relationConnected.has("approval"));

    return edges.map((edge) => {
      const [from, to] = edge;
      const directToSelected = edgeHasNode(edge, selectedId);
      const inLensPath = selectedLens.active.includes(from) && selectedLens.active.includes(to);
      const inRelationPath = relationConnected.has(from) && relationConnected.has(to);
      const humanLoopPath = humanTail.includes(from) && humanTail.includes(to);
      const humanTailActive = humanLoopPath && (selectedIsHumanTail || lensNeedsHumanTail || depthReachedGate);

      return {
        edge,
        active: inLensPath || inRelationPath || humanTailActive,
        direct: directToSelected,
        humanGate: from === "policy" && to === "approval",
      };
    });
  }, [selectedId, selectedLens, relationConnected, lens, depth]);

  const downstream = edges
    .filter(([from]) => from === selectedId)
    .map(([, to]) => nodes.find((node) => node.id === to))
    .filter(Boolean) as GraphNode[];

  const upstream = edges
    .filter(([, to]) => to === selectedId)
    .map(([from]) => nodes.find((node) => node.id === from))
    .filter(Boolean) as GraphNode[];

  function activateLens(value: Lens) {
    const option = lensOptions.find((item) => item.value === value);
    if (!option) return;

    setLens(value);
    setSelectedId(option.focus);
  }

  return (
    <PlatformShell>
      <section className="mx-auto max-w-7xl px-6 pb-16 pt-8">
        <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="mb-4 flex flex-wrap gap-3">
              <StatusBadge label="Incident Reasoning Graph" tone="cyan" />
              <StatusBadge label="Human-in-the-loop gate" tone="amber" />
              <StatusBadge label="Neural activation lens" tone="violet" />
            </div>

            <h1 className="text-4xl font-black text-white md:text-6xl">
              Incident Reasoning Graph
            </h1>

            <p className="mt-4 max-w-3xl text-slate-400">
              The graph always stays visible. Lens buttons activate different circuits while the human approval gate remains connected to remediation, recovery, and postmortem.
            </p>
          </div>

          <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-4">
            <div className="text-xs uppercase tracking-wider text-slate-500">Selected node</div>
            <div className="mt-2 text-2xl font-black text-white">{selectedNode.label}</div>
            <div className="mt-3 flex flex-wrap gap-2">
              <StatusBadge label={selectedNode.category} tone={categoryTone(selectedNode.category)} />
              {lens !== selectedNode.category && (
                <StatusBadge label={`${selectedLens.label} lens`} tone="violet" />
              )}
            </div>
          </div>
        </div>

        <div className="mb-5 rounded-3xl border border-white/10 bg-slate-950/70 p-5">
          <div className="grid gap-4 lg:grid-cols-[1fr_auto] lg:items-center">
            <div>
              <h2 className="text-xl font-black text-white">Activation controls</h2>
              <p className="mt-1 text-sm text-slate-400">
                These controls do not hide nodes. They light up the functional circuit while keeping the full incident brain visible.
              </p>
            </div>

            <div className="flex flex-wrap gap-2">
              {lensOptions.map((option) => (
                <button
                  key={option.value}
                  onClick={() => activateLens(option.value)}
                  className={`rounded-full border px-4 py-2 text-sm font-black ${
                    lens === option.value
                      ? "border-cyan-300 bg-cyan-300 text-slate-950"
                      : "border-white/10 bg-white/[0.04] text-slate-300 hover:bg-white/[0.08]"
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          <div className="mt-4 flex flex-wrap items-center gap-3">
            <span className="text-sm font-bold text-slate-400">Relation depth:</span>
            {[1, 2, 3].map((value) => (
              <button
                key={value}
                onClick={() => setDepth(value)}
                className={`rounded-full border px-4 py-2 text-sm font-black ${
                  depth === value
                    ? "border-violet-300 bg-violet-300 text-slate-950"
                    : "border-white/10 bg-white/[0.04] text-slate-300 hover:bg-white/[0.08]"
                }`}
              >
                {value}
              </button>
            ))}

            <div className="ml-auto rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-black text-cyan-100">
              {activatedNodeIds.size} active nodes / {nodes.length} total
            </div>
          </div>
        </div>

        <div className="grid items-start gap-5 xl:grid-cols-[1fr_390px]">
          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-2xl font-black text-white">Human-controlled neural canvas</h2>
                <p className="mt-1 text-sm text-slate-400">
                  Relation depth expands context; connection lines preserve the approval-to-recovery path.
                </p>
              </div>
              <StatusBadge label={`${nodes.length} nodes`} tone="cyan" />
            </div>

            <div className="relative mt-6 hidden h-[610px] overflow-hidden rounded-[2rem] border border-white/10 bg-[radial-gradient(circle_at_25%_50%,rgba(34,211,238,0.10),transparent_24%),radial-gradient(circle_at_80%_70%,rgba(139,92,246,0.10),transparent_30%)] p-5 md:block">
              <div className="absolute left-[7%] top-5 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs font-black text-cyan-100">
                signal
              </div>
              <div className="absolute left-[21%] top-5 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-black text-emerald-100">
                evidence cluster
              </div>
              <div className="absolute left-[42%] top-5 rounded-full border border-violet-400/20 bg-violet-400/10 px-3 py-1 text-xs font-black text-violet-100">
                reasoning
              </div>
              <div className="absolute left-[57%] top-5 rounded-full border border-amber-400/20 bg-amber-400/10 px-3 py-1 text-xs font-black text-amber-100">
                human approval gate
              </div>
              <div className="absolute right-5 top-5 rounded-full border border-sky-400/20 bg-sky-400/10 px-3 py-1 text-xs font-black text-sky-100">
                action / record
              </div>

              <div className="pointer-events-none absolute left-[59.5%] top-[29%] h-[46%] w-[120px] -translate-x-1/2 rounded-[2rem] border border-amber-300/30 bg-amber-300/5 shadow-[0_0_42px_rgba(251,191,36,0.12)]" />
              <div className="pointer-events-none absolute left-[72%] top-[28%] rounded-2xl border border-amber-300/45 bg-slate-950/90 px-4 py-3 text-xs font-black uppercase tracking-wider text-amber-100 shadow-[0_0_30px_rgba(251,191,36,0.12)]">
                human review checkpoint
              </div>

              <svg className="absolute inset-0 h-full w-full" viewBox="0 0 100 100" preserveAspectRatio="none">
{neuralEdges.map(({ edge, active, direct, humanGate }) => {
                  const [from, to] = edge;
                  const fromPosition = nodePositions[from];
                  const toPosition = nodePositions[to];

                  return (
                    <path
                      key={`${from}-${to}`}
                      d={edgePath(fromPosition, toPosition)}
                      fill="none"
                      stroke={humanGate ? "rgba(251,191,36,0.94)" : active ? "rgba(34,211,238,0.90)" : "rgba(148,163,184,0.20)"}
                      strokeWidth={humanGate ? 0.78 : direct ? 0.62 : active ? 0.56 : 0.28}
                      strokeDasharray={active || humanGate ? "0" : "1.2 1.2"}
                    strokeLinecap="round"
                    />
                  );
                })}
              </svg>

              {nodes.map((node) => {
                const position = nodePositions[node.id];
                const isSelected = node.id === selectedId;
                const isActive = activatedNodeIds.has(node.id);
                const isHumanGate = node.id === "approval";

                return (
                  <button
                    key={node.id}
                    onClick={() => setSelectedId(node.id)}
                    style={{
                      left: `${position.x}%`,
                      top: `${position.y}%`,
                      transform: "translate(-50%, -50%)",
                    }}
                    className={`absolute flex h-[84px] w-[84px] flex-col items-center justify-center rounded-full border text-center transition duration-300 ${
                      isSelected
                        ? "z-30 border-cyan-300 bg-cyan-300 text-slate-950 shadow-[0_0_48px_rgba(34,211,238,0.36)]"
                        : isHumanGate
                        ? "z-20 border-amber-300/80 bg-slate-950 text-amber-50 shadow-[0_0_44px_rgba(251,191,36,0.24)]"
                        : isActive
                        ? "z-20 border-emerald-400/55 bg-slate-950 text-emerald-50 shadow-[0_0_28px_rgba(16,185,129,0.16)]"
                        : "z-10 border-white/10 bg-slate-950 text-slate-400 opacity-65 hover:opacity-100"
                    }`}
                    title={`${node.label} · ${node.owner}`}
                  >
                    {isHumanGate && (
                      <span className="absolute -inset-2 rounded-full border border-amber-300/20 animate-pulse" />
                    )}
                    <span className={`mb-1 h-2.5 w-2.5 rounded-full ${categoryDotClass(node.category)} ${isActive ? "animate-pulse" : ""}`} />
                    <span className="max-w-[70px] truncate text-[13px] font-black leading-4">
                      {shortNodeLabel(node.label)}
                    </span>
                    <span className={`mt-1 text-[9px] font-black uppercase tracking-wider ${
                      isSelected ? "text-slate-700" : isHumanGate ? "text-amber-200" : "text-slate-500"
                    }`}>
                      {node.category}
                    </span>
                  </button>
                );
              })}

              <div className="absolute bottom-5 left-5 rounded-2xl border border-white/10 bg-slate-950/85 p-4 backdrop-blur">
                <div className="text-xs uppercase tracking-wider text-slate-500">selected</div>
                <div className="mt-1 text-lg font-black text-white">{selectedNode.label}</div>
                <div className="mt-1 text-xs text-cyan-200">relation depth expands nearby context</div>
              </div>

              <div className="absolute bottom-5 left-[55%] w-[260px] -translate-x-1/2 rounded-2xl border border-amber-400/25 bg-slate-950/90 p-4 backdrop-blur">
                <div className="text-xs uppercase tracking-wider text-amber-200/80">human control</div>
                <div className="mt-1 text-sm font-black text-white">policy → approval → safe fix</div>
              </div>
            </div>

            <div className="mt-5 rounded-3xl border border-violet-400/20 bg-violet-400/10 p-4">
              <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                <div>
                  <h3 className="font-black text-white">Human-in-the-loop behaviour</h3>
                  <p className="mt-1 text-sm text-slate-300">
                    Relation depth expands nearby context, while the human approval gate always keeps the downstream remediation → recovery → postmortem path visible.
                  </p>
                </div>
                <StatusBadge label={`${selectedLens.label} circuit`} tone="cyan" />
              </div>
            </div>

            <div className="mt-6 grid gap-3 md:hidden">
              {nodes.map((node) => {
                const isSelected = node.id === selectedId;
                const isActive = activatedNodeIds.has(node.id);

                return (
                  <button
                    key={node.id}
                    onClick={() => setSelectedId(node.id)}
                    className={`rounded-3xl border p-5 text-left transition ${
                      isSelected
                        ? "border-cyan-300 bg-cyan-300 text-slate-950"
                        : isActive
                        ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-50"
                        : "border-white/10 bg-white/[0.035] text-slate-400"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <StatusBadge label={node.category} tone={categoryTone(node.category)} />
                      <span className="rounded-full border border-current/20 px-3 py-1 text-xs font-black">
                        {node.id}
                      </span>
                    </div>

                    <h3 className="mt-5 text-2xl font-black">{node.label}</h3>
                    <p className={`mt-3 text-sm leading-6 ${isSelected ? "text-slate-900" : "text-slate-400"}`}>
                      {node.summary}
                    </p>
                  </button>
                );
              })}
            </div>
          </section>

          <aside className="space-y-5 xl:sticky xl:top-24">
            <section className="rounded-3xl border border-cyan-400/20 bg-cyan-400/10 p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-black text-white">{selectedNode.label}</h2>
                  <p className="mt-1 font-mono text-xs text-cyan-100/80">{selectedNode.owner}</p>
                </div>
                <StatusBadge label={selectedNode.category} tone={categoryTone(selectedNode.category)} />
              </div>

              <p className="mt-5 text-sm leading-7 text-slate-300">
                {selectedNode.summary}
              </p>

              <div className="mt-5 space-y-3">
                {selectedNode.evidence.map((item) => (
                  <div key={item} className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">
                    <div className="text-xs uppercase tracking-wider text-slate-500">evidence</div>
                    <div className="mt-2 text-sm font-black leading-6 text-white">{item}</div>
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-3xl border border-amber-400/20 bg-amber-400/10 p-5">
              <h2 className="text-2xl font-black text-white">Downstream impact</h2>
              <p className="mt-4 text-sm leading-7 text-slate-300">
                {selectedNode.impact}
              </p>

              <div className="mt-5 space-y-3">
                {downstream.length > 0 ? (
                  downstream.map((node) => (
                    <button
                      key={node.id}
                      onClick={() => setSelectedId(node.id)}
                      className="w-full rounded-2xl border border-white/10 bg-slate-950/50 p-4 text-left text-sm font-black text-white hover:bg-white/[0.07]"
                    >
                      Next: {node.label}
                    </button>
                  ))
                ) : (
                  <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-4 text-sm font-bold text-slate-300">
                    Final node in this reasoning chain.
                  </div>
                )}
              </div>
            </section>

            <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-5">
              <h2 className="text-2xl font-black text-white">Upstream sources</h2>
              <div className="mt-5 space-y-3">
                {upstream.length > 0 ? (
                  upstream.map((node) => (
                    <button
                      key={node.id}
                      onClick={() => setSelectedId(node.id)}
                      className="w-full rounded-2xl border border-white/10 bg-white/[0.035] p-4 text-left text-sm font-black text-slate-200 hover:bg-white/[0.07]"
                    >
                      From: {node.label}
                    </button>
                  ))
                ) : (
                  <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-4 text-sm font-bold text-slate-400">
                    This is the beginning of the reasoning chain.
                  </div>
                )}
              </div>
            </section>
          </aside>
        </div>

        <section className="mt-5 grid gap-5 lg:grid-cols-3">
          <InfoPanel
            label="evidence lineage"
            title="Whole graph remains visible"
            body="Lens buttons now behave like neural activation circuits, not destructive filters."
          />
          <InfoPanel
            label="human control"
            title="Approval gate is explicit"
            body="The policy-to-approval edge is highlighted as the human-in-the-loop checkpoint before remediation."
          />
          <InfoPanel
            label="postmortem"
            title="Downstream record remains connected"
            body="Remediation, recovery, and postmortem stay visible so the graph shows the full operational consequence."
          />
        </section>
      </section>
    </PlatformShell>
  );
}

function InfoPanel({ label, title, body }: { label: string; title: string; body: string }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-5">
      <StatusBadge label={label} tone="violet" />
      <h3 className="mt-4 text-2xl font-black text-white">{title}</h3>
      <p className="mt-3 text-sm leading-7 text-slate-400">{body}</p>
    </div>
  );
}
