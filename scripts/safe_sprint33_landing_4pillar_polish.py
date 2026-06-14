from pathlib import Path
import subprocess
import shutil
import sys

ROOT = Path(".")
FRONTEND = ROOT / "frontend"
LANDING = FRONTEND / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "scripts" / "_backups_sprint33_landing_4pillar"
BACKUP = BACKUP_DIR / "page.tsx"

def run_build():
    return subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

if not LANDING.exists():
    print("ERROR: frontend/src/app/page.tsx not found")
    sys.exit(1)

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copyfile(LANDING, BACKUP)

LANDING.write_text(r'''
"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { PlatformShell } from "@/components/PlatformShell";
import { StatusBadge } from "@/components/StatusBadge";

const commandSteps = [
  {
    title: "Alert intake",
    detail: "Checkout API latency anomaly enters the incident command flow.",
    metric: "p95 latency",
    value: "2.8s",
    tone: "amber",
  },
  {
    title: "Evidence correlation",
    detail: "Metrics, logs, deployment context, and runbooks are linked.",
    metric: "cache hit ratio",
    value: "41%",
    tone: "cyan",
  },
  {
    title: "Safety gate",
    detail: "Production rollback is paused until human approval.",
    metric: "policy",
    value: "approval",
    tone: "violet",
  },
  {
    title: "Recovery verified",
    detail: "Rollback completes and telemetry confirms recovery.",
    metric: "p95 latency",
    value: "480ms",
    tone: "green",
  },
];

const pillars = [
  {
    title: "Investigation",
    subtitle: "Agents reduce alert noise into evidence-backed incident context.",
    bullets: ["Triage", "Observability signals", "Runbook retrieval"],
  },
  {
    title: "Safety",
    subtitle: "Risk policy blocks unsafe automation before production impact grows.",
    bullets: ["Policy evaluation", "Risk separation", "Rollback guardrails"],
  },
  {
    title: "Approval",
    subtitle: "Operators stay in control with a clear decision package.",
    bullets: ["Approval drawer", "Evidence lineage", "Human-in-the-loop"],
  },
  {
    title: "Postmortem",
    subtitle: "Every action becomes an auditable learning record.",
    bullets: ["Execution review", "Recovery proof", "Incident summary"],
  },
];

const proofItems = [
  ["Track fit", "Autopilot Agent"],
  ["Core loop", "Investigate → approve → recover"],
  ["Model layer", "Qwen-ready / mock-safe"],
  ["Deployment", "Vercel + FastAPI + Alibaba plan"],
];

export default function Home() {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setActiveStep((current) => (current + 1) % commandSteps.length);
    }, 1700);

    return () => window.clearInterval(timer);
  }, []);

  const current = commandSteps[activeStep];

  return (
    <PlatformShell>
      <section className="mx-auto max-w-7xl px-6 pb-16 pt-10">
        <div className="grid min-h-[620px] items-center gap-10 lg:grid-cols-[1.02fr_0.98fr]">
          <div>
            <div className="mb-5 flex flex-wrap gap-3">
              <StatusBadge label="Qwen-powered" tone="cyan" />
              <StatusBadge label="Autopilot Agent Track" tone="violet" />
              <StatusBadge label="Human-in-the-loop" tone="green" />
            </div>

            <h1 className="max-w-5xl text-5xl font-black leading-[0.95] tracking-[-0.06em] text-white md:text-7xl">
              AI incident operations,
              <span className="block bg-gradient-to-r from-cyan-300 via-sky-300 to-violet-300 bg-clip-text text-transparent">
                controlled by agents.
              </span>
            </h1>

            <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-300">
              OpsPilot investigates incidents, proposes safe remediation, keeps operators in control, and documents everything.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                href="/dashboard"
                className="rounded-2xl bg-cyan-300 px-6 py-4 text-sm font-black text-slate-950 shadow-[0_0_40px_rgba(34,211,238,0.18)] hover:bg-cyan-200"
              >
                Open Command Center
              </Link>

              <Link
                href="/simulation"
                className="rounded-2xl border border-white/10 bg-white/[0.04] px-6 py-4 text-sm font-black text-white hover:bg-white/[0.08]"
              >
                Run Simulation
              </Link>

              <Link
                href="/architecture"
                className="rounded-2xl border border-violet-400/20 bg-violet-400/10 px-6 py-4 text-sm font-black text-violet-100 hover:bg-violet-400/20"
              >
                View Architecture
              </Link>
            </div>

            <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:max-w-3xl">
              {proofItems.map(([label, value]) => (
                <div key={label} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                  <div className="text-xs uppercase tracking-wider text-slate-500">{label}</div>
                  <div className="mt-2 font-black text-white">{value}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[2rem] border border-cyan-400/20 bg-slate-950/75 p-6 shadow-[0_0_80px_rgba(34,211,238,0.12)]">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-2xl font-black text-white">Live command flow</h2>
                <p className="mt-1 text-sm text-slate-400">Checkout API latency incident</p>
              </div>
              <StatusBadge label="autoplay" tone="green" />
            </div>

            <div className="mt-6 grid gap-3 md:grid-cols-2">
              <MetricCard title="p95 latency" value={activeStep >= 3 ? "480ms" : "2.8s"} detail={activeStep >= 3 ? "recovered" : "critical"} />
              <MetricCard title="cache hit ratio" value={activeStep >= 3 ? "89%" : "41%"} detail={activeStep >= 3 ? "healthy" : "degraded"} />
              <MetricCard title="risk gate" value={activeStep >= 2 ? "approval" : "watching"} detail={activeStep >= 2 ? "active" : "standby"} />
              <MetricCard title="postmortem" value={activeStep >= 3 ? "ready" : "draft"} detail={activeStep >= 3 ? "generated" : "pending"} />
            </div>

            <div className="mt-6 rounded-3xl border border-white/10 bg-white/[0.035] p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="text-xs font-black uppercase tracking-[0.24em] text-cyan-300">
                    Step {activeStep + 1}
                  </div>
                  <h3 className="mt-2 text-2xl font-black text-white">{current.title}</h3>
                  <p className="mt-3 text-sm leading-6 text-slate-300">{current.detail}</p>
                </div>
                <StatusBadge label={current.tone} tone={current.tone as any} />
              </div>

              <div className="mt-5 rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                <div className="text-xs uppercase tracking-wider text-slate-500">{current.metric}</div>
                <div className="mt-2 text-3xl font-black text-white">{current.value}</div>
              </div>
            </div>

            <div className="mt-6 space-y-3">
              {commandSteps.map((step, index) => (
                <button
                  key={step.title}
                  onClick={() => setActiveStep(index)}
                  className={`flex w-full items-center justify-between rounded-2xl border p-4 text-left transition ${
                    index === activeStep
                      ? "border-cyan-300 bg-cyan-300 text-slate-950"
                      : index < activeStep
                      ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-100"
                      : "border-white/10 bg-white/[0.035] text-slate-300 hover:bg-white/[0.07]"
                  }`}
                >
                  <span className="font-black">{step.title}</span>
                  <span className="rounded-full border border-current/20 px-3 py-1 text-xs font-black">
                    {index + 1}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>

        <section className="mt-10 rounded-[2rem] border border-white/10 bg-slate-950/65 p-6">
          <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div>
              <StatusBadge label="Core platform pillars" tone="cyan" />
              <h2 className="mt-4 text-3xl font-black text-white md:text-5xl">
                One lifecycle. Four controlled stages.
              </h2>
              <p className="mt-4 max-w-3xl text-slate-400">
                The landing page now focuses on the product’s core path instead of scattering attention across secondary modules.
              </p>
            </div>

            <Link
              href="/dashboard"
              className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-5 py-3 text-sm font-black text-cyan-100 hover:bg-cyan-400/20"
            >
              Inspect Command Center
            </Link>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {pillars.map((pillar, index) => (
              <div key={pillar.title} className="rounded-3xl border border-white/10 bg-white/[0.035] p-5">
                <div className="flex items-center justify-between gap-3">
                  <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-3 py-2 text-xs font-black text-cyan-100">
                    0{index + 1}
                  </div>
                  <StatusBadge label={pillar.title.toLowerCase()} tone={index === 0 ? "cyan" : index === 1 ? "amber" : index === 2 ? "violet" : "green"} />
                </div>

                <h3 className="mt-5 text-2xl font-black text-white">{pillar.title}</h3>
                <p className="mt-3 min-h-[72px] text-sm leading-6 text-slate-400">{pillar.subtitle}</p>

                <div className="mt-5 space-y-2">
                  {pillar.bullets.map((bullet) => (
                    <div key={bullet} className="rounded-2xl border border-white/10 bg-slate-950/50 px-4 py-3 text-sm font-bold text-slate-200">
                      {bullet}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="mt-10 grid gap-5 lg:grid-cols-[1fr_1fr_1fr]">
          <InfoPanel
            title="For judges"
            label="demo path"
            body="Start at the landing page, open the Command Center, run an incident, approve remediation, then show the generated postmortem."
          />
          <InfoPanel
            title="For operators"
            label="control"
            body="OpsPilot does not blindly execute production actions. It separates confidence, risk, policy, and human approval."
          />
          <InfoPanel
            title="For cloud proof"
            label="architecture"
            body="The backend is Qwen-ready and can move from local mock mode to Alibaba Cloud deployment once credits are active."
          />
        </section>
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

function InfoPanel({ title, label, body }: { title: string; label: string; body: string }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-slate-950/65 p-6">
      <StatusBadge label={label} tone="violet" />
      <h3 className="mt-4 text-2xl font-black text-white">{title}</h3>
      <p className="mt-3 text-sm leading-7 text-slate-400">{body}</p>
    </div>
  );
}
'''.strip() + "\n")

print("Sprint 3.3 landing 4-pillar polish applied. Running build check...")
result = run_build()
print(result.stdout)

if result.returncode != 0:
    shutil.copyfile(BACKUP, LANDING)
    print("BUILD FAILED. Landing page restored.")
    sys.exit(result.returncode)

print("BUILD PASSED. Landing polish kept.")
print(f"Backup stored at {BACKUP}")
