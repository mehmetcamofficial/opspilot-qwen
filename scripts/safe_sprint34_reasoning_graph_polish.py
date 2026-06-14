from pathlib import Path
import subprocess
import shutil
import sys

ROOT = Path(".")
FRONTEND = ROOT / "frontend"
PAGE = FRONTEND / "src" / "app" / "knowledge-graph" / "page.tsx"
BACKUP_DIR = ROOT / "scripts" / "_backups_sprint34_reasoning_graph"
BACKUP = BACKUP_DIR / "knowledge_graph.page.tsx"

def run_build():
    return subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

if not PAGE.exists():
    print("ERROR: knowledge-graph/page.tsx not found")
    sys.exit(1)

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copyfile(PAGE, BACKUP)

PAGE.write_text(r'''
"use client";

import { useMemo, useState } from "react";
import { PlatformShell } from "@/components/PlatformShell";
import { StatusBadge } from "@/components/StatusBadge";

type Tone = "cyan" | "green" | "amber" | "violet" | "slate";
type NodeCategory = "signal" | "evidence" | "reasoning" | "policy" | "action" | "record";

type GraphNode = {
  id: string;
  label: string;
  category: NodeCategory;
  owner: string;
  summary: string;
  evidence: string[];
  impact: string;
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
    summary: "Operator receives a compact approval package with evidence and rollback safety.",
    evidence: ["Recommended action", "Evidence lineage", "Policy reason", "Rollback plan"],
    impact: "Creates a human-in-the-loop checkpoint before remediation.",
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
  ["metric", "hypothesis"],
  ["logs", "hypothesis"],
  ["deployment", "hypothesis"],
  ["hypothesis", "policy"],
  ["policy", "approval"],
  ["approval", "remediation"],
  ["remediation", "recovery"],
  ["recovery", "postmortem"],
];

const filterOptions: { label: string; value: NodeCategory | "all" }[] = [
  { label: "All", value: "all" },
  { label: "Signals", value: "signal" },
  { label: "Evidence", value: "evidence" },
  { label: "Reasoning", value: "reasoning" },
  { label: "Policy", value: "policy" },
  { label: "Actions", value: "action" },
  { label: "Records", value: "record" },
];

function categoryTone(category: NodeCategory): Tone {
  if (category === "signal") return "cyan";
  if (category === "evidence") return "green";
  if (category === "reasoning") return "violet";
  if (category === "policy") return "amber";
  if (category === "action") return "cyan";
  return "slate";
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

export default function KnowledgeGraphPage() {
  const [selectedId, setSelectedId] = useState("hypothesis");
  const [filter, setFilter] = useState<NodeCategory | "all">("all");
  const [depth, setDepth] = useState(2);

  const selectedNode = nodes.find((node) => node.id === selectedId) || nodes[0];

  const connected = useMemo(
    () => connectedNodes(selectedId, depth),
    [selectedId, depth]
  );

  const visibleNodes = useMemo(() => {
    return nodes.filter((node) => filter === "all" || node.category === filter);
  }, [filter]);

  const downstream = edges
    .filter(([from]) => from === selectedId)
    .map(([, to]) => nodes.find((node) => node.id === to))
    .filter(Boolean) as GraphNode[];

  const upstream = edges
    .filter(([, to]) => to === selectedId)
    .map(([from]) => nodes.find((node) => node.id === from))
    .filter(Boolean) as GraphNode[];

  return (
    <PlatformShell>
      <section className="mx-auto max-w-7xl px-6 pb-16 pt-8">
        <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="mb-4 flex flex-wrap gap-3">
              <StatusBadge label="Incident Reasoning Graph" tone="cyan" />
              <StatusBadge label="Evidence lineage" tone="green" />
              <StatusBadge label="Explainable decisions" tone="violet" />
            </div>

            <h1 className="text-4xl font-black text-white md:text-6xl">
              Incident Reasoning Graph
            </h1>

            <p className="mt-4 max-w-3xl text-slate-400">
              Trace how OpsPilot connects alert signals, telemetry, deployment context, root-cause reasoning, safety policy, human approval, remediation, recovery, and postmortem output.
            </p>
          </div>

          <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-4">
            <div className="text-xs uppercase tracking-wider text-slate-500">Selected node</div>
            <div className="mt-2 text-2xl font-black text-white">{selectedNode.label}</div>
            <div className="mt-3">
              <StatusBadge label={selectedNode.category} tone={categoryTone(selectedNode.category)} />
            </div>
          </div>
        </div>

        <div className="mb-5 rounded-3xl border border-white/10 bg-slate-950/70 p-5">
          <div className="grid gap-4 lg:grid-cols-[1fr_auto] lg:items-center">
            <div>
              <h2 className="text-xl font-black text-white">Graph controls</h2>
              <p className="mt-1 text-sm text-slate-400">
                Filter the reasoning map and change relation depth to highlight nearby evidence.
              </p>
            </div>

            <div className="flex flex-wrap gap-2">
              {filterOptions.map((option) => (
                <button
                  key={option.value}
                  onClick={() => setFilter(option.value)}
                  className={`rounded-full border px-4 py-2 text-sm font-black ${
                    filter === option.value
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
          </div>
        </div>

        <div className="grid items-start gap-5 xl:grid-cols-[1fr_390px]">
          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-2xl font-black text-white">Reasoning path</h2>
                <p className="mt-1 text-sm text-slate-400">
                  Alert → Metric → Deployment → Hypothesis → Policy → Approval → Remediation → Recovery → Postmortem.
                </p>
              </div>
              <StatusBadge label={`${visibleNodes.length} nodes`} tone="cyan" />
            </div>

            <div className="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {visibleNodes.map((node, index) => {
                const isSelected = node.id === selectedId;
                const isConnected = connected.has(node.id);

                return (
                  <button
                    key={node.id}
                    onClick={() => setSelectedId(node.id)}
                    className={`rounded-3xl border p-5 text-left transition ${
                      isSelected
                        ? "border-cyan-300 bg-cyan-300 text-slate-950 shadow-[0_0_30px_rgba(34,211,238,0.22)]"
                        : isConnected
                        ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-50"
                        : "border-white/10 bg-white/[0.035] text-slate-300 hover:bg-white/[0.07]"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <div className="rounded-full border border-current/20 px-3 py-1 text-xs font-black">
                        {String(index + 1).padStart(2, "0")}
                      </div>
                      <StatusBadge label={node.category} tone={categoryTone(node.category)} />
                    </div>

                    <h3 className="mt-5 text-2xl font-black">{node.label}</h3>
                    <p className={`mt-3 text-sm leading-6 ${isSelected ? "text-slate-900" : "text-slate-400"}`}>
                      {node.summary}
                    </p>

                    <div className={`mt-4 font-mono text-xs ${isSelected ? "text-slate-800" : "text-cyan-200"}`}>
                      owner: {node.owner}
                    </div>
                  </button>
                );
              })}
            </div>

            <div className="mt-6 rounded-3xl border border-violet-400/20 bg-violet-400/10 p-5">
              <h3 className="font-black text-white">Connected path highlight</h3>
              <p className="mt-3 text-sm leading-7 text-slate-300">
                Selecting a node highlights upstream and downstream reasoning dependencies. This shows judges that OpsPilot decisions are not isolated LLM outputs; they are linked to evidence, policy, and operational consequences.
              </p>
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
            title="Why this matters"
            body="The graph makes every recommendation inspectable: what signal triggered the workflow, what evidence supported the hypothesis, and which policy controlled the action."
          />
          <InfoPanel
            label="safety"
            title="Policy-aware automation"
            body="Production actions are not treated as simple LLM suggestions. The graph shows exactly where safety policy pauses execution."
          />
          <InfoPanel
            label="postmortem"
            title="Audit-ready memory"
            body="The final postmortem is not a generic summary. It is produced from the same linked reasoning path used during the incident."
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
'''.strip() + "\n")

print("Sprint 3.4 Incident Reasoning Graph polish applied. Running build check...")
result = run_build()
print(result.stdout)

if result.returncode != 0:
    shutil.copyfile(BACKUP, PAGE)
    print("BUILD FAILED. Reasoning Graph page restored.")
    sys.exit(result.returncode)

print("BUILD PASSED. Reasoning Graph polish kept.")
print(f"Backup stored at {BACKUP}")
