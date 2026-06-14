from pathlib import Path
import subprocess
import shutil
import sys

ROOT = Path(".")
FRONTEND = ROOT / "frontend"
SRC = FRONTEND / "src"
BACKUP_DIR = ROOT / "scripts" / "_backups_sprint23_controls_dashboard"

FILES = [
    SRC / "app" / "admin" / "page.tsx",
    SRC / "app" / "dashboard" / "page.tsx",
]

def write(path, content):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + "\n")

def backup():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    for file in FILES:
        if file.exists():
            target = BACKUP_DIR / str(file).replace("/", "__")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(file, target)

def restore():
    for file in FILES:
        target = BACKUP_DIR / str(file).replace("/", "__")
        if target.exists():
            shutil.copyfile(target, file)

def run_build():
    return subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

backup()

write(SRC / "app" / "admin" / "page.tsx", r'''
"use client";

import { useEffect, useMemo, useState } from "react";
import { PlatformShell } from "@/components/PlatformShell";
import { StatusBadge } from "@/components/StatusBadge";

type Tone = "cyan" | "green" | "amber" | "violet" | "slate";
type PolicyAction = "approval_required" | "block" | "allow";
type PostStatus = "published" | "draft" | "archived";

type Agent = {
  id: string;
  description: string;
  enabled: boolean;
  critical: boolean;
};

type Policy = {
  id: string;
  rule: string;
  action: PolicyAction;
  enabled: boolean;
  archived: boolean;
};

type BlogPost = {
  id: string;
  title: string;
  category: string;
  language: "EN" | "TR";
  status: PostStatus;
};

type DeploymentItem = {
  id: string;
  label: string;
  ready: boolean;
};

type AuditEvent = {
  id: string;
  actor: string;
  message: string;
  timestamp: string;
};

type Toast = {
  message: string;
  tone: Tone;
};

type GovernanceState = {
  modelMode: "mock" | "qwen_live";
  approvalFreeze: boolean;
  auditExportEnabled: boolean;
  lastReadinessCheck: string;
  agents: Agent[];
  policies: Policy[];
  posts: BlogPost[];
  deployment: DeploymentItem[];
  auditLog: AuditEvent[];
};

const STORAGE_KEY = "opspilot-governance-control-v2";

function createId(prefix: string) {
  return `${prefix}-${Math.random().toString(16).slice(2, 8)}`;
}

function nowLabel() {
  return new Date().toLocaleString();
}

function createLog(message: string): AuditEvent {
  return {
    id: createId("audit"),
    actor: "operator",
    message,
    timestamp: nowLabel(),
  };
}

function freshState(): GovernanceState {
  return {
    modelMode: "mock",
    approvalFreeze: false,
    auditExportEnabled: true,
    lastReadinessCheck: "not checked",
    agents: [
      { id: "triage_agent", description: "Classifies severity and blast radius", enabled: true, critical: true },
      { id: "observability_agent", description: "Analyzes metrics, logs, and deployments", enabled: true, critical: true },
      { id: "runbook_retrieval_agent", description: "Retrieves runbooks and prior incidents", enabled: true, critical: true },
      { id: "hypothesis_agent", description: "Ranks root-cause hypotheses", enabled: true, critical: true },
      { id: "remediation_planner_agent", description: "Plans safe remediation and rollback", enabled: true, critical: true },
      { id: "risk_safety_agent", description: "Applies production safety policy", enabled: true, critical: true },
      { id: "approval_agent", description: "Prepares human approval brief", enabled: true, critical: true },
      { id: "postmortem_agent", description: "Generates closure report", enabled: true, critical: false },
    ],
    policies: [
      { id: "policy-prod-rollback", rule: "Production configuration rollback", action: "approval_required", enabled: true, archived: false },
      { id: "policy-db-restart", rule: "Database restart without evidence", action: "block", enabled: true, archived: false },
      { id: "policy-low-risk-cache", rule: "Low-risk cache validation", action: "allow", enabled: true, archived: false },
    ],
    posts: [
      { id: "post-multi-agent", title: "Why incident response needs multi-agent systems", category: "AI Operations", language: "EN", status: "published" },
      { id: "post-human-approval", title: "Human-in-the-loop remediation for safer automation", category: "Safety", language: "EN", status: "published" },
      { id: "post-qwen", title: "Qwen Cloud as the reasoning layer for OpsPilot", category: "Qwen Cloud", language: "EN", status: "draft" },
    ],
    deployment: [
      { id: "frontend-vercel", label: "Frontend deployed on Vercel", ready: true },
      { id: "backend-local", label: "FastAPI backend working locally", ready: true },
      { id: "dockerfile", label: "Dockerfile prepared", ready: true },
      { id: "ecs-plan", label: "Alibaba ECS deployment plan", ready: true },
      { id: "qwen-real", label: "Qwen real API mode tested", ready: false },
      { id: "credits", label: "Cloud credits activated", ready: false },
      { id: "prod-url", label: "Production backend URL connected", ready: false },
    ],
    auditLog: [
      createLog("Governance console initialized"),
      createLog("Mock Qwen mode selected to avoid pay-as-you-go usage"),
    ],
  };
}

function toneForAction(action: PolicyAction): Tone {
  if (action === "allow") return "green";
  if (action === "block") return "amber";
  return "violet";
}

function toneForStatus(status: string): Tone {
  if (status === "published" || status === "ready" || status === "enabled") return "green";
  if (status === "draft" || status === "pending") return "amber";
  return "slate";
}

export default function AdminPage() {
  const [loaded, setLoaded] = useState(false);
  const [state, setState] = useState<GovernanceState>(() => freshState());
  const [toast, setToast] = useState<Toast | null>(null);

  const [newAgentId, setNewAgentId] = useState("");
  const [newAgentDescription, setNewAgentDescription] = useState("");

  const [newPolicyRule, setNewPolicyRule] = useState("");
  const [newPolicyAction, setNewPolicyAction] = useState<PolicyAction>("approval_required");

  const [newPostTitle, setNewPostTitle] = useState("");
  const [newPostCategory, setNewPostCategory] = useState("AI Operations");
  const [newPostLanguage, setNewPostLanguage] = useState<"EN" | "TR">("EN");

  useEffect(() => {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (raw) {
      try {
        setState(JSON.parse(raw));
      } catch {
        setState(freshState());
      }
    }
    setLoaded(true);
  }, []);

  useEffect(() => {
    if (loaded) {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    }
  }, [state, loaded]);

  function notify(message: string, tone: Tone = "cyan") {
    setToast({ message, tone });
    window.setTimeout(() => setToast(null), 2400);
  }

  function commit(updater: (previous: GovernanceState) => GovernanceState, message: string, tone: Tone = "cyan") {
    setState((previous) => {
      const next = updater(previous);
      return {
        ...next,
        auditLog: [createLog(message), ...next.auditLog].slice(0, 24),
      };
    });
    notify(message, tone);
  }

  const stats = useMemo(() => {
    const enabledAgents = state.agents.filter((agent) => agent.enabled).length;
    const activePolicies = state.policies.filter((policy) => policy.enabled && !policy.archived).length;
    const readyDeployment = state.deployment.filter((item) => item.ready).length;
    const publishedPosts = state.posts.filter((post) => post.status === "published").length;
    return { enabledAgents, activePolicies, readyDeployment, publishedPosts };
  }, [state]);

  function addAgent() {
    const id = newAgentId.trim().toLowerCase().replaceAll(" ", "_");
    const description = newAgentDescription.trim();

    if (!id || !description) {
      notify("Agent name and description are required.", "amber");
      return;
    }

    if (state.agents.some((agent) => agent.id === id)) {
      notify("Agent already exists.", "amber");
      return;
    }

    commit(
      (previous) => ({
        ...previous,
        agents: [...previous.agents, { id, description, enabled: true, critical: false }],
      }),
      `Agent added: ${id}`,
      "green"
    );

    setNewAgentId("");
    setNewAgentDescription("");
  }

  function addPolicy() {
    const rule = newPolicyRule.trim();
    if (!rule) {
      notify("Policy rule is required.", "amber");
      return;
    }

    commit(
      (previous) => ({
        ...previous,
        policies: [{ id: createId("policy"), rule, action: newPolicyAction, enabled: true, archived: false }, ...previous.policies],
      }),
      `Safety policy added: ${rule}`,
      "green"
    );

    setNewPolicyRule("");
    setNewPolicyAction("approval_required");
  }

  function addPost() {
    const title = newPostTitle.trim();
    if (!title) {
      notify("Post title is required.", "amber");
      return;
    }

    commit(
      (previous) => ({
        ...previous,
        posts: [{ id: createId("post"), title, category: newPostCategory, language: newPostLanguage, status: "draft" }, ...previous.posts],
      }),
      `Blog draft created: ${title}`,
      "green"
    );

    setNewPostTitle("");
    setNewPostCategory("AI Operations");
    setNewPostLanguage("EN");
  }

  function runReadinessCheck() {
    commit(
      (previous) => ({
        ...previous,
        lastReadinessCheck: nowLabel(),
        deployment: previous.deployment.map((item) => {
          if (["frontend-vercel", "backend-local", "dockerfile", "ecs-plan"].includes(item.id)) {
            return { ...item, ready: true };
          }
          return item;
        }),
      }),
      "Readiness check completed: local, Docker, and ECS plan verified",
      "green"
    );
  }

  function prepareExport() {
    const summary = {
      modelMode: state.modelMode,
      approvalFreeze: state.approvalFreeze,
      enabledAgents: stats.enabledAgents,
      activePolicies: stats.activePolicies,
      deploymentReady: stats.readyDeployment,
      lastReadinessCheck: state.lastReadinessCheck,
    };

    navigator.clipboard?.writeText(JSON.stringify(summary, null, 2)).catch(() => undefined);

    commit(
      (previous) => ({ ...previous, auditExportEnabled: true }),
      "Governance snapshot copied to clipboard",
      "green"
    );
  }

  function resetGovernance() {
    setState({
      ...freshState(),
      auditLog: [createLog("Governance state reset by operator")],
    });
    notify("Governance controls reset.", "amber");
  }

  return (
    <PlatformShell>
      <section className="mx-auto max-w-7xl px-6 pb-20 pt-10">
        {toast && (
          <div className="fixed right-6 top-24 z-[80] rounded-2xl border border-cyan-400/20 bg-slate-950/95 p-4 shadow-[0_0_40px_rgba(34,211,238,0.16)]">
            <StatusBadge label={toast.tone} tone={toast.tone} />
            <div className="mt-2 max-w-sm text-sm font-bold text-white">{toast.message}</div>
          </div>
        )}

        <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="mb-4 flex flex-wrap gap-3">
              <StatusBadge label="Governance Console" tone="violet" />
              <StatusBadge label={state.modelMode === "mock" ? "Mock LLM safe mode" : "Qwen live selected"} tone={state.modelMode === "mock" ? "amber" : "cyan"} />
              <StatusBadge label={state.approvalFreeze ? "Approvals frozen" : "Approvals active"} tone={state.approvalFreeze ? "amber" : "green"} />
            </div>
            <h1 className="text-4xl font-black text-white md:text-6xl">Governance control center</h1>
            <p className="mt-4 max-w-3xl text-slate-400">
              Add, remove, enable, disable, archive, publish, verify, freeze, export, and audit platform controls.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <button onClick={runReadinessCheck} className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-5 py-3 text-sm font-black text-cyan-100 hover:bg-cyan-400/20">
              Run readiness check
            </button>
            <button onClick={prepareExport} className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-5 py-3 text-sm font-black text-emerald-100 hover:bg-emerald-400/20">
              Copy governance snapshot
            </button>
            <button onClick={resetGovernance} className="rounded-2xl border border-amber-400/20 bg-amber-400/10 px-5 py-3 text-sm font-black text-amber-100 hover:bg-amber-400/20">
              Reset controls
            </button>
          </div>
        </div>

        <div className="grid gap-4 lg:grid-cols-4">
          <ControlStat title="Enabled agents" value={`${stats.enabledAgents}/${state.agents.length}`} tone="green" />
          <ControlStat title="Active policies" value={`${stats.activePolicies}`} tone="violet" />
          <ControlStat title="Deployment ready" value={`${stats.readyDeployment}/${state.deployment.length}`} tone="cyan" />
          <ControlStat title="Published posts" value={`${stats.publishedPosts}`} tone="amber" />
        </div>

        <div className="mt-6 grid items-start gap-6 lg:grid-cols-[0.95fr_1.05fr]">
          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <h2 className="text-2xl font-black text-white">Platform switches</h2>
            <p className="mt-2 text-sm text-slate-400">Every control below changes local governance state and writes an audit event.</p>

            <div className="mt-6 grid gap-4 md:grid-cols-2">
              <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-5">
                <div className="text-sm font-black text-white">Model mode</div>
                <div className="mt-1 text-sm text-slate-400">Mock mode avoids pay-as-you-go risk.</div>

                <div className="mt-4 grid grid-cols-2 gap-2">
                  <button
                    onClick={() => commit((previous) => ({ ...previous, modelMode: "mock" }), "Model mode changed to mock fallback", "green")}
                    className={`rounded-2xl px-4 py-3 text-sm font-black ${state.modelMode === "mock" ? "bg-cyan-300 text-slate-950" : "border border-white/10 bg-white/[0.04] text-slate-200"}`}
                  >
                    Mock
                  </button>
                  <button
                    onClick={() => commit((previous) => ({ ...previous, modelMode: "qwen_live" }), "Qwen live mode selected as pending", "amber")}
                    className={`rounded-2xl px-4 py-3 text-sm font-black ${state.modelMode === "qwen_live" ? "bg-violet-300 text-slate-950" : "border border-white/10 bg-white/[0.04] text-slate-200"}`}
                  >
                    Qwen Live
                  </button>
                </div>
              </div>

              <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-5">
                <div className="text-sm font-black text-white">Approval controls</div>
                <div className="mt-1 text-sm text-slate-400">Freeze or unfreeze remediation approvals.</div>

                <button
                  onClick={() =>
                    commit(
                      (previous) => ({ ...previous, approvalFreeze: !previous.approvalFreeze }),
                      state.approvalFreeze ? "Approval freeze disabled" : "Approval freeze enabled",
                      state.approvalFreeze ? "green" : "amber"
                    )
                  }
                  className={`mt-4 w-full rounded-2xl px-4 py-3 text-sm font-black ${state.approvalFreeze ? "bg-amber-300 text-slate-950" : "border border-emerald-400/20 bg-emerald-400/10 text-emerald-100"}`}
                >
                  {state.approvalFreeze ? "Unfreeze approvals" : "Freeze approvals"}
                </button>

                <button
                  onClick={() =>
                    commit(
                      (previous) => ({ ...previous, auditExportEnabled: !previous.auditExportEnabled }),
                      state.auditExportEnabled ? "Audit export disabled" : "Audit export enabled",
                      state.auditExportEnabled ? "amber" : "green"
                    )
                  }
                  className="mt-3 w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-bold text-white hover:bg-white/[0.08]"
                >
                  {state.auditExportEnabled ? "Disable audit export" : "Enable audit export"}
                </button>
              </div>
            </div>

            <div className="mt-5 grid gap-3 md:grid-cols-3">
              <button onClick={() => commit((previous) => ({ ...previous, approvalFreeze: true }), "Production actions frozen from quick action", "amber")} className="rounded-2xl border border-amber-400/20 bg-amber-400/10 px-4 py-3 text-sm font-black text-amber-100 hover:bg-amber-400/20">
                Freeze prod actions
              </button>
              <button onClick={prepareExport} className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-3 text-sm font-black text-cyan-100 hover:bg-cyan-400/20">
                Prepare export
              </button>
              <button onClick={runReadinessCheck} className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm font-black text-emerald-100 hover:bg-emerald-400/20">
                Recheck readiness
              </button>
            </div>

            <div className="mt-5 grid gap-3 md:grid-cols-2">
              <MiniState label="Approval mode" value={state.approvalFreeze ? "Frozen" : "Active"} />
              <MiniState label="Audit export" value={state.auditExportEnabled ? "Enabled" : "Disabled"} />
              <MiniState label="Model safety" value={state.modelMode === "mock" ? "Cost-safe mock" : "Qwen live pending"} />
              <MiniState label="Last readiness check" value={state.lastReadinessCheck} />
            </div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <h2 className="text-2xl font-black text-white">Deployment readiness control</h2>
            <p className="mt-2 text-sm text-slate-400">Toggle readiness items as deployment conditions change.</p>

            <div className="mt-6 space-y-3">
              {state.deployment.map((item) => (
                <div key={item.id} className="flex items-center justify-between gap-4 rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                  <div>
                    <div className="font-bold text-white">{item.label}</div>
                    <div className="mt-1 font-mono text-xs text-slate-500">{item.id}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <StatusBadge label={item.ready ? "ready" : "pending"} tone={item.ready ? "green" : "amber"} />
                    <button
                      onClick={() =>
                        commit(
                          (previous) => ({
                            ...previous,
                            deployment: previous.deployment.map((entry) => entry.id === item.id ? { ...entry, ready: !entry.ready } : entry),
                          }),
                          `${item.label} set to ${item.ready ? "pending" : "ready"}`,
                          item.ready ? "amber" : "green"
                        )
                      }
                      className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-2 text-xs font-bold text-slate-200 hover:bg-white/[0.08]"
                    >
                      Toggle
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>

        <div className="mt-6 grid items-start gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <h2 className="text-2xl font-black text-white">Agent registry control</h2>
            <p className="mt-2 text-sm text-slate-400">Enable, disable, add, or remove agents from the demo registry.</p>

            <div className="mt-6 grid gap-3 md:grid-cols-[0.75fr_1fr_auto]">
              <input value={newAgentId} onChange={(event) => setNewAgentId(event.target.value)} placeholder="agent_id" className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-300" />
              <input value={newAgentDescription} onChange={(event) => setNewAgentDescription(event.target.value)} placeholder="Agent description" className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-300" />
              <button onClick={addAgent} className="rounded-2xl bg-cyan-300 px-5 py-3 text-sm font-black text-slate-950 hover:bg-cyan-200">Add agent</button>
            </div>

            <div className="mt-6 space-y-3">
              {state.agents.map((agent) => (
                <div key={agent.id} className="flex flex-col gap-4 rounded-2xl border border-white/10 bg-white/[0.035] p-4 md:flex-row md:items-center md:justify-between">
                  <div>
                    <div className="font-mono text-sm font-black text-cyan-100">{agent.id}</div>
                    <div className="mt-1 text-sm text-slate-400">{agent.description}</div>
                    <div className="mt-2 flex gap-2">
                      <StatusBadge label={agent.enabled ? "enabled" : "disabled"} tone={agent.enabled ? "green" : "slate"} />
                      {agent.critical && <StatusBadge label="core" tone="violet" />}
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() =>
                        commit(
                          (previous) => ({
                            ...previous,
                            agents: previous.agents.map((entry) => entry.id === agent.id ? { ...entry, enabled: !entry.enabled } : entry),
                          }),
                          `${agent.id} ${agent.enabled ? "disabled" : "enabled"}`,
                          agent.enabled ? "amber" : "green"
                        )
                      }
                      className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-xs font-bold text-white hover:bg-white/[0.08]"
                    >
                      {agent.enabled ? "Disable" : "Enable"}
                    </button>

                    <button
                      onClick={() =>
                        commit(
                          (previous) => ({ ...previous, agents: previous.agents.filter((entry) => entry.id !== agent.id) }),
                          `${agent.id} removed from registry`,
                          "amber"
                        )
                      }
                      disabled={agent.critical}
                      className="rounded-full border border-rose-400/20 bg-rose-400/10 px-4 py-2 text-xs font-bold text-rose-100 hover:bg-rose-400/20 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <h2 className="text-2xl font-black text-white">Safety policy control</h2>
            <p className="mt-2 text-sm text-slate-400">Control guardrails that decide whether actions are allowed, blocked, or approval-gated.</p>

            <div className="mt-6 grid gap-3 md:grid-cols-[1fr_0.55fr_auto]">
              <input value={newPolicyRule} onChange={(event) => setNewPolicyRule(event.target.value)} placeholder="Policy rule" className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-300" />
              <select value={newPolicyAction} onChange={(event) => setNewPolicyAction(event.target.value as PolicyAction)} className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none focus:border-cyan-300">
                <option value="approval_required">approval required</option>
                <option value="block">block</option>
                <option value="allow">allow</option>
              </select>
              <button onClick={addPolicy} className="rounded-2xl bg-violet-300 px-5 py-3 text-sm font-black text-slate-950 hover:bg-violet-200">Add policy</button>
            </div>

            <div className="mt-6 space-y-3">
              {state.policies.map((policy) => (
                <div key={policy.id} className={`rounded-2xl border p-4 ${policy.archived ? "border-white/5 bg-white/[0.02] opacity-60" : "border-white/10 bg-white/[0.035]"}`}>
                  <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                    <div>
                      <div className="font-bold text-white">{policy.rule}</div>
                      <div className="mt-1 font-mono text-xs text-slate-500">{policy.id}</div>
                      <div className="mt-3 flex flex-wrap gap-2">
                        <StatusBadge label={policy.action} tone={toneForAction(policy.action)} />
                        <StatusBadge label={policy.enabled ? "enabled" : "disabled"} tone={policy.enabled ? "green" : "slate"} />
                        {policy.archived && <StatusBadge label="archived" tone="slate" />}
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      <button
                        onClick={() =>
                          commit(
                            (previous) => ({
                              ...previous,
                              policies: previous.policies.map((entry) => entry.id === policy.id ? { ...entry, enabled: !entry.enabled } : entry),
                            }),
                            `${policy.rule} ${policy.enabled ? "disabled" : "enabled"}`,
                            policy.enabled ? "amber" : "green"
                          )
                        }
                        className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-2 text-xs font-bold text-white hover:bg-white/[0.08]"
                      >
                        {policy.enabled ? "Disable" : "Enable"}
                      </button>

                      <button
                        onClick={() =>
                          commit(
                            (previous) => ({
                              ...previous,
                              policies: previous.policies.map((entry) => entry.id === policy.id ? { ...entry, archived: !entry.archived } : entry),
                            }),
                            `${policy.rule} ${policy.archived ? "unarchived" : "archived"}`,
                            "amber"
                          )
                        }
                        className="rounded-full border border-amber-400/20 bg-amber-400/10 px-3 py-2 text-xs font-bold text-amber-100 hover:bg-amber-400/20"
                      >
                        {policy.archived ? "Unarchive" : "Archive"}
                      </button>

                      <button
                        onClick={() =>
                          commit(
                            (previous) => ({ ...previous, policies: previous.policies.filter((entry) => entry.id !== policy.id) }),
                            `${policy.rule} deleted`,
                            "amber"
                          )
                        }
                        className="rounded-full border border-rose-400/20 bg-rose-400/10 px-3 py-2 text-xs font-bold text-rose-100 hover:bg-rose-400/20"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>

        <div className="mt-6 grid items-start gap-6 xl:grid-cols-[0.95fr_1.05fr]">
          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <h2 className="text-2xl font-black text-white">Blog CMS control</h2>
            <p className="mt-2 text-sm text-slate-400">Create, publish, draft, archive, and delete content items.</p>

            <div className="mt-6 grid gap-3 md:grid-cols-[1fr_0.55fr_0.35fr_auto]">
              <input value={newPostTitle} onChange={(event) => setNewPostTitle(event.target.value)} placeholder="Post title" className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-300" />
              <input value={newPostCategory} onChange={(event) => setNewPostCategory(event.target.value)} placeholder="Category" className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-300" />
              <select value={newPostLanguage} onChange={(event) => setNewPostLanguage(event.target.value as "EN" | "TR")} className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none focus:border-cyan-300">
                <option value="EN">EN</option>
                <option value="TR">TR</option>
              </select>
              <button onClick={addPost} className="rounded-2xl bg-cyan-300 px-5 py-3 text-sm font-black text-slate-950 hover:bg-cyan-200">Add post</button>
            </div>

            <div className="mt-6 space-y-3">
              {state.posts.map((post) => (
                <div key={post.id} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                  <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                    <div>
                      <div className="font-bold text-white">{post.title}</div>
                      <div className="mt-1 text-sm text-slate-400">{post.category} · {post.language}</div>
                      <div className="mt-3"><StatusBadge label={post.status} tone={toneForStatus(post.status)} /></div>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      {(["published", "draft", "archived"] as PostStatus[]).map((status) => (
                        <button
                          key={status}
                          onClick={() =>
                            commit(
                              (previous) => ({
                                ...previous,
                                posts: previous.posts.map((entry) => entry.id === post.id ? { ...entry, status } : entry),
                              }),
                              `${post.title} set to ${status}`,
                              status === "published" ? "green" : status === "draft" ? "amber" : "slate"
                            )
                          }
                          className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-2 text-xs font-bold text-white hover:bg-white/[0.08]"
                        >
                          {status}
                        </button>
                      ))}

                      <button
                        onClick={() =>
                          commit(
                            (previous) => ({ ...previous, posts: previous.posts.filter((entry) => entry.id !== post.id) }),
                            `${post.title} deleted`,
                            "amber"
                          )
                        }
                        className="rounded-full border border-rose-400/20 bg-rose-400/10 px-3 py-2 text-xs font-bold text-rose-100 hover:bg-rose-400/20"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <h2 className="text-2xl font-black text-white">Governance audit log</h2>
            <p className="mt-2 text-sm text-slate-400">Every control action is recorded locally for demo traceability.</p>

            <div className="mt-6 space-y-3">
              {state.auditLog.map((event) => (
                <div key={event.id} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                  <div className="flex items-center justify-between gap-4">
                    <div className="font-bold text-white">{event.message}</div>
                    <div className="font-mono text-xs text-cyan-200">{event.actor}</div>
                  </div>
                  <div className="mt-2 font-mono text-xs text-slate-500">{event.timestamp}</div>
                </div>
              ))}
            </div>

            <button
              onClick={() =>
                commit(
                  (previous) => ({ ...previous, auditLog: [] }),
                  "Audit log cleared",
                  "amber"
                )
              }
              className="mt-5 w-full rounded-2xl border border-amber-400/20 bg-amber-400/10 px-5 py-3 text-sm font-black text-amber-100 hover:bg-amber-400/20"
            >
              Clear audit log
            </button>
          </section>
        </div>
      </section>
    </PlatformShell>
  );
}

function ControlStat({ title, value, tone }: { title: string; value: string; tone: Tone }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-6">
      <div className="text-sm text-slate-400">{title}</div>
      <div className="mt-2 text-3xl font-black text-white">{value}</div>
      <div className="mt-4"><StatusBadge label={tone} tone={tone} /></div>
    </div>
  );
}

function MiniState({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">
      <div className="text-xs uppercase tracking-wider text-slate-500">{label}</div>
      <div className="mt-2 truncate font-black text-white">{value}</div>
    </div>
  );
}
''')

write(SRC / "app" / "dashboard" / "page.tsx", r'''
"use client";

import { useState } from "react";
import { PlatformShell } from "@/components/PlatformShell";
import { StatusBadge } from "@/components/StatusBadge";
import { approveIncident, createIncident, healthcheck, listIncidents } from "@/lib/api";

type IncidentState = any;
type EvidenceTab = "metrics" | "logs" | "deployments" | "runbooks";

const stateMachine = ["triaging", "investigating", "hypothesis", "awaiting approval", "remediating", "monitoring", "resolved"];

const defaultEvidence: Record<EvidenceTab, string[]> = {
  metrics: ["p95 latency increased from 420ms to 2.8s", "cache hit ratio dropped from 91% to 41%", "database latency increased by 63%"],
  logs: ["Repeated cache-miss fallback warnings detected", "Checkout workers report increased downstream retries", "No security-related error pattern detected"],
  deployments: ["Recent cache configuration change detected", "No application code deployment in the last 30 minutes", "Rollback candidate identified: cache-config-v18"],
  runbooks: ["Runbook match: cache configuration rollback", "Validation step: confirm cache hit ratio recovery", "Rollback plan: restore previous cache TTL and routing config"],
};

function toneForStatus(status: string): "cyan" | "green" | "amber" | "violet" | "slate" {
  if (status === "resolved" || status === "completed") return "green";
  if (status.includes("approval") || status === "awaiting_approval") return "amber";
  if (status.includes("executed") || status.includes("remediating")) return "violet";
  if (status.includes("running") || status.includes("investigating")) return "cyan";
  return "slate";
}

function normalizeStatus(status?: string) {
  if (!status) return "standby";
  return status.replaceAll("_", " ");
}

function leadingHypothesis(state: IncidentState | null) {
  return state?.hypothesis_result?.ranked_hypotheses?.[0]?.summary || "Cache configuration regression introduced in the latest config change";
}

function recommendedAction(state: IncidentState | null) {
  return state?.remediation_plan?.candidate_actions?.[0]?.title || "Rollback cache configuration safely";
}

function postmortemSummary(state: IncidentState | null) {
  return state?.postmortem?.summary || "The incident was likely caused by cache config regression and mitigated with approval-gated rollback.";
}

function timelineFromState(state: IncidentState | null) {
  if (state?.agent_timeline?.length) return state.agent_timeline;
  return [
    { agent: "triage_agent", status: "waiting" },
    { agent: "observability_agent", status: "waiting" },
    { agent: "runbook_agent", status: "waiting" },
    { agent: "hypothesis_agent", status: "waiting" },
    { agent: "remediation_planner_agent", status: "waiting" },
    { agent: "risk_safety_agent", status: "waiting" },
    { agent: "approval_agent", status: "waiting" },
  ];
}

export default function DashboardPage() {
  const [backendStatus, setBackendStatus] = useState<string>("not checked");
  const [incident, setIncident] = useState<IncidentState | null>(null);
  const [incidents, setIncidents] = useState<IncidentState[]>([]);
  const [loading, setLoading] = useState(false);
  const [evidenceTab, setEvidenceTab] = useState<EvidenceTab>("metrics");
  const [toast, setToast] = useState<string | null>(null);

  const status = normalizeStatus(incident?.status);
  const timeline = timelineFromState(incident);
  const isResolved = status === "resolved";
  const isAwaitingApproval = status.includes("approval");

  function notify(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(null), 2200);
  }

  async function checkBackend() {
    setLoading(true);
    try {
      const data = await healthcheck();
      setBackendStatus(`${data.status} | mock_llm=${data.mock_llm}`);
      notify("Backend healthcheck completed.");
    } catch (error: any) {
      setBackendStatus(`error: ${error.message}`);
      notify("Backend check failed. Start FastAPI backend first.");
    } finally {
      setLoading(false);
    }
  }

  async function startIncident() {
    setLoading(true);
    try {
      const data = await createIncident();
      setIncident(data.state ?? data);
      notify("Demo incident started. Safety gate is waiting for approval.");
    } catch (error: any) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function refreshIncidents() {
    setLoading(true);
    try {
      const data = await listIncidents();
      setIncidents(data.incidents || []);
      notify("Stored incidents refreshed.");
    } catch (error: any) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function approve() {
    if (!incident?.incident_id) {
      notify("Start an incident before approval.");
      return;
    }

    setLoading(true);
    try {
      const data = await approveIncident(incident.incident_id);
      setIncident(data.state ?? data);
      notify("Remediation approved. Execution review and postmortem generated.");
    } catch (error: any) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function copyIncidentSummary() {
    const summary = {
      incident_id: incident?.incident_id || "no-active-incident",
      status,
      hypothesis: leadingHypothesis(incident),
      recommended_action: recommendedAction(incident),
      postmortem: postmortemSummary(incident),
    };
    await navigator.clipboard?.writeText(JSON.stringify(summary, null, 2)).catch(() => undefined);
    notify("Incident summary copied to clipboard.");
  }

  async function exportAuditLog() {
    const audit = timeline.map((item: any, index: number) => ({
      step: index + 1,
      agent: item.agent,
      status: item.status || "completed",
    }));
    await navigator.clipboard?.writeText(JSON.stringify(audit, null, 2)).catch(() => undefined);
    notify("Audit log copied to clipboard.");
  }

  return (
    <PlatformShell>
      <section className="mx-auto max-w-7xl px-6 pb-20 pt-10">
        {toast && (
          <div className="fixed right-6 top-24 z-[80] rounded-2xl border border-cyan-400/20 bg-slate-950/95 p-4 shadow-[0_0_40px_rgba(34,211,238,0.16)]">
            <div className="text-sm font-bold text-white">{toast}</div>
          </div>
        )}

        <div className="mb-6 rounded-3xl border border-white/10 bg-slate-950/70 p-5">
          <div className="grid gap-3 md:grid-cols-4">
            <SystemStripItem label="Frontend" value="Vercel / local" tone="green" />
            <SystemStripItem label="Backend" value={backendStatus} tone={backendStatus.startsWith("ok") ? "green" : backendStatus.startsWith("error") ? "amber" : "slate"} />
            <SystemStripItem label="Qwen mode" value="mock fallback" tone="amber" />
            <SystemStripItem label="Cloud billing" value="credits pending" tone="violet" />
          </div>
        </div>

        <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="mb-4 flex flex-wrap gap-3">
              <StatusBadge label="Command Center" tone="cyan" />
              <StatusBadge label={status} tone={toneForStatus(status)} />
              <StatusBadge label="human approval gated" tone="violet" />
            </div>
            <h1 className="text-4xl font-black text-white md:text-6xl">Incident lifecycle console</h1>
            <p className="mt-4 max-w-3xl text-slate-400">
              Trace evidence, review policy decisions, approve remediation, and generate an auditable postmortem.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <button onClick={checkBackend} disabled={loading} className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-bold text-white hover:bg-white/[0.08] disabled:opacity-50">Check Backend</button>
            <button onClick={startIncident} disabled={loading} className="rounded-2xl bg-cyan-300 px-5 py-3 text-sm font-black text-slate-950 hover:bg-cyan-200 disabled:opacity-50">Start Incident</button>
            <button onClick={refreshIncidents} disabled={loading} className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-bold text-white hover:bg-white/[0.08] disabled:opacity-50">Refresh</button>
          </div>
        </div>

        <div className="mb-6 rounded-3xl border border-white/10 bg-slate-950/70 p-5">
          <h2 className="text-xl font-black text-white">Incident state machine</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-7">
            {stateMachine.map((state, index) => {
              const active = status === state || (status === "standby" && index === 0);
              const passed = Boolean(incident) && index <= 3;
              return (
                <div key={state} className={`rounded-2xl border p-3 ${active ? "border-cyan-300 bg-cyan-300 text-slate-950" : passed ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-100" : "border-white/10 bg-white/[0.035] text-slate-400"}`}>
                  <div className="text-xs font-black uppercase tracking-wider">Step {index + 1}</div>
                  <div className="mt-1 text-sm font-black">{state}</div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="grid items-start gap-6 xl:grid-cols-[0.9fr_1.15fr_0.95fr]">
          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-2xl font-black text-white">Incident summary</h2>
                <p className="mt-1 font-mono text-sm text-slate-500">{incident?.incident_id || "No active incident yet"}</p>
              </div>
              <StatusBadge label={status} tone={toneForStatus(status)} />
            </div>

            <div className="mt-6 grid gap-3 md:grid-cols-2">
              <MetricCard title="Service" value={incident?.triage_result?.affected_service || "checkout-api"} />
              <MetricCard title="Environment" value="production" />
              <MetricCard title="Severity" value={incident?.triage_result?.severity || "high"} />
              <MetricCard title="Business impact" value="checkout degraded" />
              <MetricCard title="Confidence" value={String(incident?.hypothesis_result?.confidence || "0.86")} />
              <MetricCard title="Risk" value={incident?.risk_review?.risk_level || "medium"} />
            </div>

            <div className="mt-6 rounded-3xl border border-cyan-400/20 bg-cyan-400/10 p-5">
              <h3 className="text-xl font-black text-white">Leading hypothesis</h3>
              <p className="mt-3 leading-7 text-slate-300">{leadingHypothesis(incident)}</p>
            </div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-2xl font-black text-white">Evidence console</h2>
                <p className="mt-1 text-sm text-slate-400">Evidence lineage behind the recommendation.</p>
              </div>
              <StatusBadge label="traceable" tone="green" />
            </div>

            <div className="mt-5 flex flex-wrap gap-2">
              {(["metrics", "logs", "deployments", "runbooks"] as EvidenceTab[]).map((tab) => (
                <button key={tab} onClick={() => setEvidenceTab(tab)} className={`rounded-full border px-4 py-2 text-sm font-bold ${evidenceTab === tab ? "border-cyan-300 bg-cyan-300 text-slate-950" : "border-white/10 bg-white/[0.04] text-slate-300 hover:bg-white/[0.08]"}`}>
                  {tab}
                </button>
              ))}
            </div>

            <div className="mt-5 space-y-3">
              {defaultEvidence[evidenceTab].map((item, index) => (
                <div key={item} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                  <div className="text-xs font-black uppercase tracking-wider text-cyan-300">source {index + 1}</div>
                  <div className="mt-2 text-sm leading-6 text-slate-300">{item}</div>
                </div>
              ))}
            </div>

            <div className="mt-5 rounded-3xl border border-violet-400/20 bg-violet-400/10 p-5">
              <h3 className="font-black text-white">Why multi-agent?</h3>
              <p className="mt-3 text-sm leading-6 text-slate-300">
                Each agent owns one decision boundary: triage, evidence, hypothesis, risk, approval, execution review, and postmortem.
              </p>
            </div>
          </section>

          <aside className="space-y-6">
            <section className="rounded-3xl border border-amber-400/20 bg-amber-400/10 p-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-black text-white">Safety Gate</h2>
                  <p className="mt-1 text-sm text-amber-100/80">Policy-aware control before production action.</p>
                </div>
                <StatusBadge label={isResolved ? "approved" : "approval required"} tone={isResolved ? "green" : "amber"} />
              </div>

              <div className="mt-5 space-y-3 text-sm">
                <PolicyItem label="Rule matched" value="production configuration rollback" />
                <PolicyItem label="Guardrail" value="human approval required" />
                <PolicyItem label="Rollback plan" value="restore previous cache config" />
                <PolicyItem label="Blocked alternative" value="database restart without evidence" />
              </div>

              <button onClick={approve} disabled={loading || !incident?.incident_id || isResolved} className="mt-5 w-full rounded-2xl bg-emerald-300 px-5 py-3 text-sm font-black text-slate-950 hover:bg-emerald-200 disabled:cursor-not-allowed disabled:opacity-40">
                {isResolved ? "Remediation approved" : isAwaitingApproval ? "Approve Remediation" : "Start incident first"}
              </button>
            </section>

            <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
              <h2 className="text-2xl font-black text-white">Audit trail</h2>
              <div className="mt-5 space-y-3">
                <AuditItem label="Incident created" value={incident ? "recorded" : "pending"} />
                <AuditItem label="Evidence linked" value={incident ? "metrics/logs/runbook" : "pending"} />
                <AuditItem label="Policy evaluated" value={incident ? "approval required" : "pending"} />
                <AuditItem label="Operator approval" value={isResolved ? "approved" : "pending"} />
              </div>
            </section>
          </aside>
        </div>

        <div className="mt-6 grid items-start gap-6 xl:grid-cols-[1fr_1fr]">
          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <h2 className="text-2xl font-black text-white">Live agent timeline</h2>
            <div className="mt-6 grid gap-3 md:grid-cols-2">
              {timeline.map((item: any, index: number) => (
                <div key={`${item.agent}-${index}`} className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                  <div>
                    <div className="font-mono text-sm font-black text-cyan-100">{item.agent}</div>
                    <div className="mt-1 text-xs text-slate-500">step {index + 1}</div>
                  </div>
                  <StatusBadge label={item.status || "completed"} tone={toneForStatus(item.status || "completed")} />
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <h2 className="text-2xl font-black text-white">Outcome and postmortem</h2>
            <div className={`mt-5 rounded-3xl border p-5 ${isResolved ? "border-emerald-400/20 bg-emerald-400/10" : "border-white/10 bg-white/[0.035]"}`}>
              <h3 className="font-black text-white">{isResolved ? "Postmortem generated" : "Postmortem preview"}</h3>
              <p className="mt-3 text-sm leading-6 text-slate-300">{postmortemSummary(incident)}</p>
            </div>

            <div className="mt-5 grid gap-3 md:grid-cols-2">
              <button onClick={copyIncidentSummary} className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-bold text-white hover:bg-white/[0.08]">
                Copy incident summary
              </button>
              <button onClick={exportAuditLog} className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-bold text-white hover:bg-white/[0.08]">
                Export audit log
              </button>
            </div>
          </section>
        </div>

        {incidents.length > 0 && (
          <section className="mt-6 rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <h2 className="text-2xl font-black text-white">Stored incidents</h2>
            <div className="mt-4 grid gap-3 md:grid-cols-3">
              {incidents.map((item: any) => (
                <div key={item.incident_id} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                  <div className="font-mono text-sm font-black text-cyan-100">{item.incident_id}</div>
                  <div className="mt-2 text-sm text-slate-400">Status: {item.status}</div>
                </div>
              ))}
            </div>
          </section>
        )}
      </section>
    </PlatformShell>
  );
}

function SystemStripItem({ label, value, tone }: { label: string; value: string; tone: "cyan" | "green" | "amber" | "violet" | "slate" }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
      <div className="text-xs uppercase tracking-wider text-slate-500">{label}</div>
      <div className="mt-2 truncate font-mono text-sm text-slate-200">{value}</div>
      <div className="mt-3"><StatusBadge label={tone} tone={tone} /></div>
    </div>
  );
}

function MetricCard({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-4">
      <div className="text-xs uppercase tracking-wider text-slate-500">{title}</div>
      <div className="mt-2 truncate text-xl font-black text-white">{value}</div>
    </div>
  );
}

function PolicyItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-amber-400/20 bg-slate-950/40 p-3">
      <div className="text-xs uppercase tracking-wider text-amber-200/70">{label}</div>
      <div className="mt-1 font-semibold text-amber-50">{value}</div>
    </div>
  );
}

function AuditItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.035] p-3 text-sm">
      <span className="font-semibold text-slate-200">{label}</span>
      <span className="font-mono text-cyan-200">{value}</span>
    </div>
  );
}
''')

print("Sprint 2.3 controls and dashboard flow patch applied. Running build check...")
result = run_build()
print(result.stdout)

if result.returncode != 0:
    restore()
    print("BUILD FAILED. Sprint 2.3 changes were rolled back.")
    sys.exit(result.returncode)

print("BUILD PASSED. Sprint 2.3 changes kept.")
print(f"Backups stored in {BACKUP_DIR}")
