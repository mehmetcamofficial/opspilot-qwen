"use client";

import { useEffect, useMemo, useRef, useState } from "react";
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
      {
        id: "audit-initialized",
        actor: "system",
        message: "Governance console initialized",
        timestamp: "initial state",
      },
      {
        id: "audit-mock-mode",
        actor: "system",
        message: "Mock Qwen mode selected to avoid pay-as-you-go usage",
        timestamp: "initial state",
      },
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
  const hasMounted = useRef(false);
  const [state, setState] = useState<GovernanceState>(() => {
    if (typeof window === "undefined") {
      return freshState();
    }

    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return freshState();
    }

    try {
      return JSON.parse(raw);
    } catch {
      return freshState();
    }
  });
  const [toast, setToast] = useState<Toast | null>(null);

  const [newAgentId, setNewAgentId] = useState("");
  const [newAgentDescription, setNewAgentDescription] = useState("");

  const [newPolicyRule, setNewPolicyRule] = useState("");
  const [newPolicyAction, setNewPolicyAction] = useState<PolicyAction>("approval_required");

  const [newPostTitle, setNewPostTitle] = useState("");
  const [newPostCategory, setNewPostCategory] = useState("AI Operations");
  const [newPostLanguage, setNewPostLanguage] = useState<"EN" | "TR">("EN");

  useEffect(() => {
    if (!hasMounted.current) {
      hasMounted.current = true;
      return;
    }

    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [state]);

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
      <section className="mx-auto max-w-7xl px-6 pb-16 pt-8">
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
            <p className="mt-2 text-sm text-slate-400">Enable, disable, add, or remove agents from the agent registry.</p>

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

            <div className="mt-6 rounded-3xl border border-violet-400/20 bg-violet-400/10 p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="font-black text-white">Policy enforcement preview</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-300">
                    Shows how the current policy set would handle common production actions before they reach the Command Center.
                  </p>
                </div>
                <StatusBadge label="live local state" tone="cyan" />
              </div>

              <div className="mt-5 grid gap-3 md:grid-cols-2">
                <MiniState
                  label="Approval-gated rules"
                  value={String(state.policies.filter((policy) => policy.action === "approval_required" && policy.enabled && !policy.archived).length)}
                />
                <MiniState
                  label="Blocked rules"
                  value={String(state.policies.filter((policy) => policy.action === "block" && policy.enabled && !policy.archived).length)}
                />
                <MiniState
                  label="Allowed rules"
                  value={String(state.policies.filter((policy) => policy.action === "allow" && policy.enabled && !policy.archived).length)}
                />
                <MiniState
                  label="Archived policies"
                  value={String(state.policies.filter((policy) => policy.archived).length)}
                />
              </div>

              <div className="mt-5 space-y-3">
                <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">
                  <div className="text-xs uppercase tracking-wider text-slate-500">Production rollback</div>
                  <div className="mt-2 font-black text-white">Requires human approval before execution</div>
                </div>
                <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">
                  <div className="text-xs uppercase tracking-wider text-slate-500">Database restart without evidence</div>
                  <div className="mt-2 font-black text-white">Blocked by safety policy</div>
                </div>
                <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">
                  <div className="text-xs uppercase tracking-wider text-slate-500">Low-risk validation</div>
                  <div className="mt-2 font-black text-white">Allowed with audit logging</div>
                </div>
              </div>
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
            <p className="mt-2 text-sm text-slate-400">Every control action is recorded locally for traceability.</p>

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
