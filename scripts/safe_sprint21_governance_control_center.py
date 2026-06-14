from pathlib import Path
import subprocess
import shutil
import sys

ROOT = Path(".")
FRONTEND = ROOT / "frontend"
SRC = FRONTEND / "src"
BACKUP_DIR = ROOT / "scripts" / "_backups_sprint21_governance"

FILES = [
    SRC / "app" / "admin" / "page.tsx",
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

type Agent = {
  id: string;
  description: string;
  enabled: boolean;
  critical: boolean;
};

type PolicyAction = "approval_required" | "block" | "allow";

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
  status: "published" | "draft" | "archived";
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

type GovernanceState = {
  modelMode: "mock" | "qwen_live";
  approvalFreeze: boolean;
  auditExportEnabled: boolean;
  agents: Agent[];
  policies: Policy[];
  posts: BlogPost[];
  deployment: DeploymentItem[];
  auditLog: AuditEvent[];
};

const STORAGE_KEY = "opspilot-governance-control-v1";

function createId(prefix: string) {
  return `${prefix}-${Math.random().toString(16).slice(2, 8)}`;
}

function createLog(message: string): AuditEvent {
  return {
    id: createId("audit"),
    actor: "operator",
    message,
    timestamp: new Date().toLocaleString(),
  };
}

function freshState(): GovernanceState {
  return {
    modelMode: "mock",
    approvalFreeze: false,
    auditExportEnabled: true,
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
      {
        id: "policy-prod-rollback",
        rule: "Production configuration rollback",
        action: "approval_required",
        enabled: true,
        archived: false,
      },
      {
        id: "policy-db-restart",
        rule: "Database restart without evidence",
        action: "block",
        enabled: true,
        archived: false,
      },
      {
        id: "policy-low-risk-cache",
        rule: "Low-risk cache validation",
        action: "allow",
        enabled: true,
        archived: false,
      },
    ],
    posts: [
      {
        id: "post-multi-agent",
        title: "Why incident response needs multi-agent systems",
        category: "AI Operations",
        language: "EN",
        status: "published",
      },
      {
        id: "post-human-approval",
        title: "Human-in-the-loop remediation for safer automation",
        category: "Safety",
        language: "EN",
        status: "published",
      },
      {
        id: "post-qwen",
        title: "Qwen Cloud as the reasoning layer for OpsPilot",
        category: "Qwen Cloud",
        language: "EN",
        status: "draft",
      },
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

function actionTone(action: PolicyAction): Tone {
  if (action === "allow") return "green";
  if (action === "block") return "amber";
  return "violet";
}

function statusTone(status: string): Tone {
  if (status === "published" || status === "ready" || status === "enabled") return "green";
  if (status === "draft" || status === "pending") return "amber";
  if (status === "archived" || status === "disabled") return "slate";
  return "cyan";
}

export default function AdminPage() {
  const [loaded, setLoaded] = useState(false);
  const [state, setState] = useState<GovernanceState>(() => freshState());

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

  const stats = useMemo(() => {
    const enabledAgents = state.agents.filter((agent) => agent.enabled).length;
    const activePolicies = state.policies.filter((policy) => policy.enabled && !policy.archived).length;
    const readyDeployment = state.deployment.filter((item) => item.ready).length;
    const publishedPosts = state.posts.filter((post) => post.status === "published").length;

    return {
      enabledAgents,
      activePolicies,
      readyDeployment,
      publishedPosts,
    };
  }, [state]);

  function commit(updater: (previous: GovernanceState) => GovernanceState, message: string) {
    setState((previous) => {
      const next = updater(previous);
      return {
        ...next,
        auditLog: [createLog(message), ...next.auditLog].slice(0, 18),
      };
    });
  }

  function addAgent() {
    const id = newAgentId.trim().toLowerCase().replaceAll(" ", "_");
    const description = newAgentDescription.trim();

    if (!id || !description) {
      alert("Agent name and description are required.");
      return;
    }

    if (state.agents.some((agent) => agent.id === id)) {
      alert("Agent already exists.");
      return;
    }

    commit(
      (previous) => ({
        ...previous,
        agents: [
          ...previous.agents,
          {
            id,
            description,
            enabled: true,
            critical: false,
          },
        ],
      }),
      `Agent added: ${id}`
    );

    setNewAgentId("");
    setNewAgentDescription("");
  }

  function addPolicy() {
    const rule = newPolicyRule.trim();

    if (!rule) {
      alert("Policy rule is required.");
      return;
    }

    const id = createId("policy");

    commit(
      (previous) => ({
        ...previous,
        policies: [
          {
            id,
            rule,
            action: newPolicyAction,
            enabled: true,
            archived: false,
          },
          ...previous.policies,
        ],
      }),
      `Safety policy added: ${rule}`
    );

    setNewPolicyRule("");
    setNewPolicyAction("approval_required");
  }

  function addPost() {
    const title = newPostTitle.trim();

    if (!title) {
      alert("Post title is required.");
      return;
    }

    commit(
      (previous) => ({
        ...previous,
        posts: [
          {
            id: createId("post"),
            title,
            category: newPostCategory,
            language: newPostLanguage,
            status: "draft",
          },
          ...previous.posts,
        ],
      }),
      `Blog draft created: ${title}`
    );

    setNewPostTitle("");
    setNewPostCategory("AI Operations");
    setNewPostLanguage("EN");
  }

  function simulateDeploymentCheck() {
    commit(
      (previous) => ({
        ...previous,
        deployment: previous.deployment.map((item) =>
          ["frontend-vercel", "backend-local", "dockerfile", "ecs-plan"].includes(item.id)
            ? { ...item, ready: true }
            : item
        ),
      }),
      "Deployment readiness check simulated"
    );
  }

  function resetGovernance() {
    setState({
      ...freshState(),
      auditLog: [createLog("Governance state reset by operator")],
    });
  }

  return (
    <PlatformShell>
      <section className="mx-auto max-w-7xl px-6 pb-20 pt-10">
        <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="mb-4 flex flex-wrap gap-3">
              <StatusBadge label="Governance Console" tone="violet" />
              <StatusBadge label={state.modelMode === "mock" ? "Mock LLM safe mode" : "Qwen live selected"} tone={state.modelMode === "mock" ? "amber" : "cyan"} />
              <StatusBadge label={state.approvalFreeze ? "Approvals frozen" : "Approvals active"} tone={state.approvalFreeze ? "amber" : "green"} />
            </div>
            <h1 className="text-4xl font-black text-white md:text-6xl">Governance control center</h1>
            <p className="mt-4 max-w-3xl text-slate-400">
              Control agents, safety policies, deployment readiness, blog content, model mode, and audit actions from one operator console.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              onClick={simulateDeploymentCheck}
              className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-5 py-3 text-sm font-black text-cyan-100 hover:bg-cyan-400/20"
            >
              Run readiness check
            </button>
            <button
              onClick={resetGovernance}
              className="rounded-2xl border border-amber-400/20 bg-amber-400/10 px-5 py-3 text-sm font-black text-amber-100 hover:bg-amber-400/20"
            >
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

        <div className="mt-6 grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <h2 className="text-2xl font-black text-white">Platform switches</h2>
            <p className="mt-2 text-sm text-slate-400">
              These controls affect the demo governance state and persist locally in the browser.
            </p>

            <div className="mt-6 grid gap-4 md:grid-cols-2">
              <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-5">
                <div className="text-sm font-black text-white">Model mode</div>
                <div className="mt-1 text-sm text-slate-400">Choose safe mock mode or prepare Qwen live mode.</div>

                <div className="mt-4 grid grid-cols-2 gap-2">
                  <button
                    onClick={() =>
                      commit((previous) => ({ ...previous, modelMode: "mock" }), "Model mode changed to mock fallback")
                    }
                    className={`rounded-2xl px-4 py-3 text-sm font-black ${
                      state.modelMode === "mock"
                        ? "bg-cyan-300 text-slate-950"
                        : "border border-white/10 bg-white/[0.04] text-slate-200"
                    }`}
                  >
                    Mock
                  </button>
                  <button
                    onClick={() =>
                      commit((previous) => ({ ...previous, modelMode: "qwen_live" }), "Qwen live mode selected as pending")
                    }
                    className={`rounded-2xl px-4 py-3 text-sm font-black ${
                      state.modelMode === "qwen_live"
                        ? "bg-violet-300 text-slate-950"
                        : "border border-white/10 bg-white/[0.04] text-slate-200"
                    }`}
                  >
                    Qwen Live
                  </button>
                </div>

                {state.modelMode === "qwen_live" && (
                  <div className="mt-4 rounded-2xl border border-amber-400/20 bg-amber-400/10 p-4 text-sm leading-6 text-amber-100">
                    Qwen live mode is selected in the console, but real API usage should wait until credits are activated.
                  </div>
                )}
              </div>

              <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-5">
                <div className="text-sm font-black text-white">Approval freeze</div>
                <div className="mt-1 text-sm text-slate-400">Temporarily block remediation approvals.</div>

                <button
                  onClick={() =>
                    commit(
                      (previous) => ({ ...previous, approvalFreeze: !previous.approvalFreeze }),
                      state.approvalFreeze ? "Approval freeze disabled" : "Approval freeze enabled"
                    )
                  }
                  className={`mt-4 w-full rounded-2xl px-4 py-3 text-sm font-black ${
                    state.approvalFreeze
                      ? "bg-amber-300 text-slate-950"
                      : "border border-emerald-400/20 bg-emerald-400/10 text-emerald-100"
                  }`}
                >
                  {state.approvalFreeze ? "Unfreeze approvals" : "Freeze approvals"}
                </button>

                <button
                  onClick={() =>
                    commit(
                      (previous) => ({ ...previous, auditExportEnabled: !previous.auditExportEnabled }),
                      state.auditExportEnabled ? "Audit export disabled" : "Audit export enabled"
                    )
                  }
                  className="mt-3 w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-bold text-white hover:bg-white/[0.08]"
                >
                  {state.auditExportEnabled ? "Disable audit export" : "Enable audit export"}
                </button>
              </div>
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
                            deployment: previous.deployment.map((entry) =>
                              entry.id === item.id ? { ...entry, ready: !entry.ready } : entry
                            ),
                          }),
                          `${item.label} set to ${item.ready ? "pending" : "ready"}`
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

        <div className="mt-6 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
              <div>
                <h2 className="text-2xl font-black text-white">Agent registry control</h2>
                <p className="mt-2 text-sm text-slate-400">Enable, disable, add, or remove agents from the demo registry.</p>
              </div>
            </div>

            <div className="mt-6 grid gap-3 md:grid-cols-[0.75fr_1fr_auto]">
              <input
                value={newAgentId}
                onChange={(event) => setNewAgentId(event.target.value)}
                placeholder="agent_id"
                className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-300"
              />
              <input
                value={newAgentDescription}
                onChange={(event) => setNewAgentDescription(event.target.value)}
                placeholder="Agent description"
                className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-300"
              />
              <button
                onClick={addAgent}
                className="rounded-2xl bg-cyan-300 px-5 py-3 text-sm font-black text-slate-950 hover:bg-cyan-200"
              >
                Add agent
              </button>
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
                            agents: previous.agents.map((entry) =>
                              entry.id === agent.id ? { ...entry, enabled: !entry.enabled } : entry
                            ),
                          }),
                          `${agent.id} ${agent.enabled ? "disabled" : "enabled"}`
                        )
                      }
                      className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-xs font-bold text-white hover:bg-white/[0.08]"
                    >
                      {agent.enabled ? "Disable" : "Enable"}
                    </button>

                    <button
                      onClick={() =>
                        commit(
                          (previous) => ({
                            ...previous,
                            agents: previous.agents.filter((entry) => entry.id !== agent.id),
                          }),
                          `${agent.id} removed from registry`
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
              <input
                value={newPolicyRule}
                onChange={(event) => setNewPolicyRule(event.target.value)}
                placeholder="Policy rule"
                className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-300"
              />
              <select
                value={newPolicyAction}
                onChange={(event) => setNewPolicyAction(event.target.value as PolicyAction)}
                className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none focus:border-cyan-300"
              >
                <option value="approval_required">approval required</option>
                <option value="block">block</option>
                <option value="allow">allow</option>
              </select>
              <button
                onClick={addPolicy}
                className="rounded-2xl bg-violet-300 px-5 py-3 text-sm font-black text-slate-950 hover:bg-violet-200"
              >
                Add policy
              </button>
            </div>

            <div className="mt-6 space-y-3">
              {state.policies.map((policy) => (
                <div key={policy.id} className={`rounded-2xl border p-4 ${policy.archived ? "border-white/5 bg-white/[0.02] opacity-60" : "border-white/10 bg-white/[0.035]"}`}>
                  <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                    <div>
                      <div className="font-bold text-white">{policy.rule}</div>
                      <div className="mt-1 font-mono text-xs text-slate-500">{policy.id}</div>
                      <div className="mt-3 flex flex-wrap gap-2">
                        <StatusBadge label={policy.action} tone={actionTone(policy.action)} />
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
                              policies: previous.policies.map((entry) =>
                                entry.id === policy.id ? { ...entry, enabled: !entry.enabled } : entry
                              ),
                            }),
                            `${policy.rule} ${policy.enabled ? "disabled" : "enabled"}`
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
                              policies: previous.policies.map((entry) =>
                                entry.id === policy.id ? { ...entry, archived: !entry.archived } : entry
                              ),
                            }),
                            `${policy.rule} ${policy.archived ? "unarchived" : "archived"}`
                          )
                        }
                        className="rounded-full border border-amber-400/20 bg-amber-400/10 px-3 py-2 text-xs font-bold text-amber-100 hover:bg-amber-400/20"
                      >
                        {policy.archived ? "Unarchive" : "Archive"}
                      </button>

                      <button
                        onClick={() =>
                          commit(
                            (previous) => ({
                              ...previous,
                              policies: previous.policies.filter((entry) => entry.id !== policy.id),
                            }),
                            `${policy.rule} deleted`
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

        <div className="mt-6 grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <h2 className="text-2xl font-black text-white">Blog CMS control</h2>
            <p className="mt-2 text-sm text-slate-400">Create, publish, draft, archive, and delete content items.</p>

            <div className="mt-6 grid gap-3 md:grid-cols-[1fr_0.55fr_0.35fr_auto]">
              <input
                value={newPostTitle}
                onChange={(event) => setNewPostTitle(event.target.value)}
                placeholder="Post title"
                className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-300"
              />
              <input
                value={newPostCategory}
                onChange={(event) => setNewPostCategory(event.target.value)}
                placeholder="Category"
                className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-300"
              />
              <select
                value={newPostLanguage}
                onChange={(event) => setNewPostLanguage(event.target.value as "EN" | "TR")}
                className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none focus:border-cyan-300"
              >
                <option value="EN">EN</option>
                <option value="TR">TR</option>
              </select>
              <button
                onClick={addPost}
                className="rounded-2xl bg-cyan-300 px-5 py-3 text-sm font-black text-slate-950 hover:bg-cyan-200"
              >
                Add post
              </button>
            </div>

            <div className="mt-6 space-y-3">
              {state.posts.map((post) => (
                <div key={post.id} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                  <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                    <div>
                      <div className="font-bold text-white">{post.title}</div>
                      <div className="mt-1 text-sm text-slate-400">{post.category} · {post.language}</div>
                      <div className="mt-3">
                        <StatusBadge label={post.status} tone={statusTone(post.status)} />
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      {(["published", "draft", "archived"] as BlogPost["status"][]).map((status) => (
                        <button
                          key={status}
                          onClick={() =>
                            commit(
                              (previous) => ({
                                ...previous,
                                posts: previous.posts.map((entry) =>
                                  entry.id === post.id ? { ...entry, status } : entry
                                ),
                              }),
                              `${post.title} set to ${status}`
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
                            (previous) => ({
                              ...previous,
                              posts: previous.posts.filter((entry) => entry.id !== post.id),
                            }),
                            `${post.title} deleted`
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
                  (previous) => ({
                    ...previous,
                    auditLog: [],
                  }),
                  "Audit log cleared"
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
      <div className="mt-4">
        <StatusBadge label={tone} tone={tone} />
      </div>
    </div>
  );
}
''')

print("Sprint 2.1 Governance Control Center patch applied. Running build check...")
result = run_build()
print(result.stdout)

if result.returncode != 0:
    restore()
    print("BUILD FAILED. Sprint 2.1 changes were rolled back.")
    sys.exit(result.returncode)

print("BUILD PASSED. Sprint 2.1 changes kept.")
print(f"Backups stored in {BACKUP_DIR}")
