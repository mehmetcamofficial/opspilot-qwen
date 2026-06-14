from pathlib import Path
import subprocess
import shutil
import sys

ROOT = Path(".")
FRONTEND = ROOT / "frontend"
SIMULATION = FRONTEND / "src" / "app" / "simulation" / "page.tsx"
BACKUP_DIR = ROOT / "scripts" / "_backups_sprint31_simulation_mission_control"
BACKUP = BACKUP_DIR / "simulation.page.tsx"

def run_build():
    return subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

if not SIMULATION.exists():
    print("ERROR: simulation/page.tsx not found")
    sys.exit(1)

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copyfile(SIMULATION, BACKUP)

SIMULATION.write_text(r'''
"use client";

import { useMemo, useState } from "react";
import { PlatformShell } from "@/components/PlatformShell";
import { StatusBadge } from "@/components/StatusBadge";

type Tone = "cyan" | "green" | "amber" | "violet" | "slate";

type MissionStep = {
  id: string;
  title: string;
  agent: string;
  description: string;
};

type EvidenceItem = {
  step: number;
  source: string;
  title: string;
  detail: string;
};

const missionSteps: MissionStep[] = [
  {
    id: "alert",
    title: "Alert intake",
    agent: "triage_agent",
    description: "Production checkout latency anomaly is received and normalized.",
  },
  {
    id: "triage",
    title: "Triage",
    agent: "triage_agent",
    description: "Severity, affected service, environment, and blast radius are classified.",
  },
  {
    id: "evidence",
    title: "Evidence analysis",
    agent: "observability_agent",
    description: "Metrics, logs, deployment records, and runbook signals are correlated.",
  },
  {
    id: "hypothesis",
    title: "Root-cause hypothesis",
    agent: "hypothesis_agent",
    description: "Likely cause is ranked against evidence lineage and confidence.",
  },
  {
    id: "safety",
    title: "Safety gate",
    agent: "risk_safety_agent",
    description: "Production remediation policy is evaluated before any action is allowed.",
  },
  {
    id: "approval",
    title: "Human approval",
    agent: "approval_agent",
    description: "Operator reviews recommendation, risk, rollback plan, and policy reason.",
  },
  {
    id: "remediation",
    title: "Remediation",
    agent: "remediation_executor",
    description: "Approved rollback is executed with reversible production controls.",
  },
  {
    id: "monitoring",
    title: "Recovery monitoring",
    agent: "execution_review_agent",
    description: "Post-action telemetry confirms latency and cache health recovery.",
  },
  {
    id: "postmortem",
    title: "Postmortem",
    agent: "postmortem_agent",
    description: "Final incident record, evidence chain, and learning summary are generated.",
  },
];

const evidenceItems: EvidenceItem[] = [
  {
    step: 0,
    source: "alert",
    title: "Checkout API latency alert",
    detail: "p95 latency crossed the critical threshold at 2.8s.",
  },
  {
    step: 1,
    source: "triage",
    title: "Severity classified",
    detail: "Production checkout path is degraded with customer-facing impact.",
  },
  {
    step: 2,
    source: "metrics",
    title: "Cache hit ratio drop",
    detail: "Cache hit ratio dropped from 91% to 41% after configuration drift.",
  },
  {
    step: 2,
    source: "logs",
    title: "Fallback retry pattern",
    detail: "Checkout workers emit repeated fallback and retry warnings.",
  },
  {
    step: 3,
    source: "deployment",
    title: "Recent cache configuration",
    detail: "No code deploy detected; latest relevant change is cache-config-v18.",
  },
  {
    step: 4,
    source: "policy",
    title: "Approval required",
    detail: "Production rollback is allowed only after human approval.",
  },
  {
    step: 6,
    source: "remediation",
    title: "Rollback executed",
    detail: "Cache configuration restored to previous known-good version.",
  },
  {
    step: 7,
    source: "monitoring",
    title: "Recovery verified",
    detail: "Latency and cache hit ratio return to healthy operating range.",
  },
  {
    step: 8,
    source: "postmortem",
    title: "Postmortem generated",
    detail: "Evidence, decision, remediation, and recovery are recorded.",
  },
];

function sleep(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function stepTone(index: number, activeStep: number): Tone {
  if (index === activeStep) return "cyan";
  if (index < activeStep) return "green";
  return "slate";
}

function agentStatus(index: number, activeStep: number, approved: boolean) {
  if (index < activeStep) return "completed";
  if (index === activeStep) {
    if (index === 4 && !approved) return "paused";
    return "active";
  }
  return "waiting";
}

function statusTone(status: string): Tone {
  if (status === "completed" || status === "approved" || status === "verified") return "green";
  if (status === "active") return "cyan";
  if (status === "paused" || status === "approval required") return "amber";
  if (status === "waiting") return "slate";
  return "violet";
}

function agentLabel(agent: string) {
  const labels: Record<string, string> = {
    triage_agent: "Triage",
    observability_agent: "Observability",
    hypothesis_agent: "Hypothesis",
    risk_safety_agent: "Safety",
    approval_agent: "Approval",
    remediation_executor: "Executor",
    execution_review_agent: "Execution Review",
    postmortem_agent: "Postmortem",
  };

  return labels[agent] || agent;
}

export default function SimulationPage() {
  const [activeStep, setActiveStep] = useState(0);
  const [running, setRunning] = useState(false);
  const [approvalRequired, setApprovalRequired] = useState(false);
  const [approved, setApproved] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [eventStream, setEventStream] = useState<string[]>([
    "T+00:00 Mission console initialized",
    "T+00:00 Awaiting simulation command",
  ]);

  const visibleEvidence = useMemo(
    () => evidenceItems.filter((item) => item.step <= activeStep),
    [activeStep]
  );

  const metricState = useMemo(() => {
    const recovered = activeStep >= 7;

    return {
      latency: recovered ? "480ms" : "2.8s",
      cache: recovered ? "89%" : "41%",
      errorRate: recovered ? "0.4%" : "6.4%",
      risk: completed ? "resolved" : approvalRequired ? "approval required" : "investigating",
      latencyDetail: recovered ? "recovered" : "critical",
      cacheDetail: recovered ? "healthy" : "degraded",
      errorDetail: recovered ? "normal" : "elevated",
    };
  }, [activeStep, approvalRequired, completed]);

  function pushEvent(message: string) {
    setEventStream((previous) => [message, ...previous].slice(0, 12));
  }

  async function runFullSimulation() {
    setRunning(true);
    setApproved(false);
    setCompleted(false);
    setApprovalRequired(false);
    setEventStream(["T+00:00 Mission started"]);

    for (let index = 0; index <= 4; index += 1) {
      setActiveStep(index);
      pushEvent(`T+00:0${index + 1} ${missionSteps[index].title}`);
      await sleep(520);
    }

    setApprovalRequired(true);
    pushEvent("T+00:06 Safety gate paused automation — human approval required");
    setRunning(false);
  }

  async function approveAndContinue() {
    if (!approvalRequired || running) return;

    setRunning(true);
    setApproved(true);
    setApprovalRequired(false);
    pushEvent("T+00:07 Operator approved safe rollback");

    for (let index = 5; index <= 8; index += 1) {
      setActiveStep(index);
      pushEvent(`T+00:${index + 3} ${missionSteps[index].title}`);
      await sleep(520);
    }

    setCompleted(true);
    pushEvent("T+00:12 Postmortem generated and mission completed");
    setRunning(false);
  }

  function resetSimulation() {
    setActiveStep(0);
    setRunning(false);
    setApprovalRequired(false);
    setApproved(false);
    setCompleted(false);
    setEventStream([
      "T+00:00 Mission console initialized",
      "T+00:00 Awaiting simulation command",
    ]);
  }

  return (
    <PlatformShell>
      <section className="mx-auto max-w-7xl px-6 pb-16 pt-8">
        <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="mb-4 flex flex-wrap gap-3">
              <StatusBadge label="Simulation Lab" tone="cyan" />
              <StatusBadge label={running ? "running" : approvalRequired ? "approval pause" : completed ? "completed" : "standby"} tone={running ? "cyan" : approvalRequired ? "amber" : completed ? "green" : "slate"} />
              <StatusBadge label="no cloud cost" tone="violet" />
            </div>

            <h1 className="text-4xl font-black text-white md:text-6xl">
              Mission-control incident simulation
            </h1>

            <p className="mt-4 max-w-3xl text-slate-400">
              Demonstrate the full OpsPilot lifecycle: alert intake, agent reasoning, evidence accumulation, safety gate pause, human approval, recovery monitoring, and postmortem generation.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              onClick={runFullSimulation}
              disabled={running}
              className="rounded-2xl bg-cyan-300 px-5 py-3 text-sm font-black text-slate-950 hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Run Full Simulation
            </button>

            <button
              onClick={approveAndContinue}
              disabled={!approvalRequired || running}
              className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-5 py-3 text-sm font-black text-emerald-100 hover:bg-emerald-400/20 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Approve & Continue
            </button>

            <button
              onClick={resetSimulation}
              disabled={running}
              className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-bold text-white hover:bg-white/[0.08] disabled:opacity-50"
            >
              Reset
            </button>
          </div>
        </div>

        <div className="mb-5 rounded-3xl border border-white/10 bg-slate-950/70 p-5">
          <h2 className="text-xl font-black text-white">Mission lifecycle</h2>

          <div className="mt-5 grid gap-3 md:grid-cols-3 xl:grid-cols-9">
            {missionSteps.map((step, index) => {
              const tone = stepTone(index, activeStep);

              return (
                <div
                  key={step.id}
                  className={`rounded-2xl border p-4 transition-all duration-300 ${
                    index === activeStep
                      ? "border-cyan-300 bg-cyan-300 text-slate-950 shadow-[0_0_28px_rgba(34,211,238,0.22)]"
                      : index < activeStep
                      ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-100"
                      : "border-white/10 bg-white/[0.035] text-slate-400"
                  }`}
                >
                  <div className="text-xs font-black uppercase tracking-wider">
                    Step {index + 1}
                  </div>
                  <div className="mt-2 text-sm font-black leading-5">
                    {step.title}
                  </div>
                  <div className="mt-3">
                    <StatusBadge label={tone} tone={tone} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="grid items-start gap-5 xl:grid-cols-[0.9fr_1.1fr_0.85fr]">
          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-2xl font-black text-white">Agent activation board</h2>
                <p className="mt-1 text-sm text-slate-400">
                  Agent states activate as the mission progresses.
                </p>
              </div>
              <StatusBadge label="agent society" tone="violet" />
            </div>

            <div className="mt-5 space-y-3">
              {missionSteps.map((step, index) => {
                const status = agentStatus(index, activeStep, approved);

                return (
                  <div
                    key={step.id}
                    className="rounded-2xl border border-white/10 bg-white/[0.035] p-4"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="font-black text-cyan-100">{agentLabel(step.agent)}</div>
                        <div className="mt-1 font-mono text-xs text-slate-500">{step.agent}</div>
                      </div>
                      <StatusBadge label={status} tone={statusTone(status)} />
                    </div>
                    <p className="mt-3 text-sm leading-6 text-slate-400">
                      {step.description}
                    </p>
                  </div>
                );
              })}
            </div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-2xl font-black text-white">Mission event stream</h2>
                <p className="mt-1 text-sm text-slate-400">
                  A judge-friendly incident story with step-by-step operational evidence.
                </p>
              </div>
              <StatusBadge label={running ? "streaming" : "ready"} tone={running ? "cyan" : "green"} />
            </div>

            <div className="mt-5 grid gap-3 md:grid-cols-4">
              <MetricCard title="p95 latency" value={metricState.latency} detail={metricState.latencyDetail} />
              <MetricCard title="cache hit ratio" value={metricState.cache} detail={metricState.cacheDetail} />
              <MetricCard title="error rate" value={metricState.errorRate} detail={metricState.errorDetail} />
              <MetricCard title="risk gate" value={metricState.risk} detail={completed ? "closed" : "active"} />
            </div>

            <div className="mt-5 grid gap-5 lg:grid-cols-[0.95fr_1.05fr]">
              <div className="rounded-3xl border border-cyan-400/20 bg-cyan-400/10 p-5">
                <h3 className="font-black text-white">Evidence appearing now</h3>
                <div className="mt-4 space-y-3">
                  {visibleEvidence.map((item) => (
                    <div
                      key={`${item.step}-${item.title}`}
                      className="rounded-2xl border border-white/10 bg-slate-950/50 p-4"
                    >
                      <div className="text-xs font-black uppercase tracking-wider text-cyan-300">
                        {item.source}
                      </div>
                      <div className="mt-1 font-black text-white">{item.title}</div>
                      <p className="mt-2 text-sm leading-6 text-slate-400">{item.detail}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-5">
                <h3 className="font-black text-white">Event log</h3>
                <div className="mt-4 space-y-3">
                  {eventStream.map((event) => (
                    <div
                      key={event}
                      className="rounded-2xl border border-white/10 bg-slate-950/60 p-3 font-mono text-xs text-slate-300"
                    >
                      {event}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </section>

          <aside className="space-y-5 xl:sticky xl:top-24">
            <section className="rounded-3xl border border-amber-400/20 bg-amber-400/10 p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-black text-white">Safety gate</h2>
                  <p className="mt-1 text-sm text-amber-100/80">
                    Automation pauses before production remediation.
                  </p>
                </div>
                <StatusBadge label={approvalRequired ? "approval required" : approved ? "approved" : "watching"} tone={approvalRequired ? "amber" : approved ? "green" : "slate"} />
              </div>

              <div className="mt-5 space-y-3">
                <DecisionLine label="Policy" value="production rollback requires approval" />
                <DecisionLine label="Reason" value="customer-facing production impact" />
                <DecisionLine label="Rollback" value="restore known-good cache configuration" />
                <DecisionLine label="Operator state" value={approved ? "approved" : approvalRequired ? "waiting" : "not requested"} />
              </div>
            </section>

            <section className="rounded-3xl border border-emerald-400/20 bg-emerald-400/10 p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-black text-white">Recovery</h2>
                  <p className="mt-1 text-sm text-emerald-100/80">
                    Recovery metrics appear after approved remediation.
                  </p>
                </div>
                <StatusBadge label={completed ? "verified" : "pending"} tone={completed ? "green" : "amber"} />
              </div>

              <div className="mt-5 grid gap-3">
                <DecisionLine label="Latency" value={completed ? "2.8s → 480ms" : "waiting for remediation"} />
                <DecisionLine label="Cache" value={completed ? "41% → 89%" : "waiting for remediation"} />
                <DecisionLine label="Error rate" value={completed ? "6.4% → 0.4%" : "waiting for remediation"} />
              </div>
            </section>

            <section className="rounded-3xl border border-violet-400/20 bg-violet-400/10 p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-black text-white">Postmortem preview</h2>
                  <p className="mt-1 text-sm text-violet-100/80">
                    Final incident record for audit and learning.
                  </p>
                </div>
                <StatusBadge label={completed ? "generated" : "draft"} tone={completed ? "green" : "slate"} />
              </div>

              <p className="mt-5 text-sm leading-7 text-slate-300">
                OpsPilot identified cache configuration drift as the likely cause, paused automation at the safety gate, required human approval, executed a reversible rollback, verified telemetry recovery, and generated a postmortem-ready incident summary.
              </p>
            </section>
          </aside>
        </div>
      </section>
    </PlatformShell>
  );
}

function MetricCard({ title, value, detail }: { title: string; value: string; detail: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
      <div className="text-xs uppercase tracking-wider text-slate-500">{title}</div>
      <div className="mt-2 text-2xl font-black text-white">{value}</div>
      <div className="mt-2 text-xs font-bold text-cyan-200">{detail}</div>
    </div>
  );
}

function DecisionLine({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">
      <div className="text-xs uppercase tracking-wider text-slate-500">{label}</div>
      <div className="mt-2 text-sm font-black leading-6 text-white">{value}</div>
    </div>
  );
}
'''.strip() + "\n")

print("Sprint 3.1 simulation mission-control polish applied. Running build check...")
result = run_build()
print(result.stdout)

if result.returncode != 0:
    shutil.copyfile(BACKUP, SIMULATION)
    print("BUILD FAILED. Simulation page restored.")
    sys.exit(result.returncode)

print("BUILD PASSED. Simulation polish kept.")
print(f"Backup stored at {BACKUP}")
