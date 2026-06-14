from pathlib import Path
import shutil

ROOT = Path("frontend")
SRC = ROOT / "src"

def write(path, content):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + "\n")

# 1. Move current dashboard from / to /dashboard without losing it.
dashboard_dir = SRC / "app" / "dashboard"
dashboard_dir.mkdir(parents=True, exist_ok=True)

current_home = SRC / "app" / "page.tsx"
dashboard_page = dashboard_dir / "page.tsx"

if current_home.exists():
    original = current_home.read_text()
    if not dashboard_page.exists():
        dashboard_page.write_text(original)

# 2. Components
write(SRC / "components" / "OpsPilotLogo.tsx", r'''
export function OpsPilotLogo() {
  return (
    <div className="flex items-center gap-3">
      <div className="relative flex h-10 w-10 items-center justify-center rounded-2xl border border-cyan-400/40 bg-cyan-400/10 shadow-[0_0_35px_rgba(34,211,238,0.22)]">
        <div className="h-3 w-3 rounded-full bg-cyan-300 shadow-[0_0_20px_rgba(34,211,238,0.95)]" />
        <div className="absolute h-7 w-7 rounded-full border border-violet-400/50" />
      </div>
      <div>
        <div className="text-xl font-black tracking-tight text-white">
          Ops<span className="text-cyan-300">Pilot</span>
        </div>
        <div className="text-[10px] font-semibold uppercase tracking-[0.28em] text-slate-400">
          AI Incident Command
        </div>
      </div>
    </div>
  );
}
''')

write(SRC / "components" / "StatusBadge.tsx", r'''
type StatusBadgeProps = {
  label: string;
  tone?: "cyan" | "green" | "amber" | "violet" | "slate";
};

const styles: Record<NonNullable<StatusBadgeProps["tone"]>, string> = {
  cyan: "border-cyan-400/30 bg-cyan-400/10 text-cyan-200",
  green: "border-emerald-400/30 bg-emerald-400/10 text-emerald-200",
  amber: "border-amber-400/30 bg-amber-400/10 text-amber-200",
  violet: "border-violet-400/30 bg-violet-400/10 text-violet-200",
  slate: "border-slate-500/40 bg-slate-800/70 text-slate-200",
};

export function StatusBadge({ label, tone = "slate" }: StatusBadgeProps) {
  return (
    <span className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold ${styles[tone]}`}>
      {label}
    </span>
  );
}
''')

write(SRC / "components" / "PlatformShell.tsx", r'''
import Link from "next/link";
import { OpsPilotLogo } from "./OpsPilotLogo";

type PlatformShellProps = {
  children: React.ReactNode;
};

export function PlatformShell({ children }: PlatformShellProps) {
  return (
    <main className="min-h-screen overflow-hidden bg-[#030712] text-slate-100">
      <div className="pointer-events-none fixed inset-0">
        <div className="absolute left-[-10%] top-[-20%] h-[420px] w-[420px] rounded-full bg-cyan-500/20 blur-3xl" />
        <div className="absolute right-[-10%] top-[10%] h-[420px] w-[420px] rounded-full bg-violet-500/20 blur-3xl" />
        <div className="absolute bottom-[-20%] left-[30%] h-[420px] w-[420px] rounded-full bg-blue-500/10 blur-3xl" />
        <div className="absolute inset-0 bg-[linear-gradient(rgba(148,163,184,0.04)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.04)_1px,transparent_1px)] bg-[size:42px_42px]" />
      </div>

      <div className="relative z-10">
        <header className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6">
          <Link href="/" aria-label="OpsPilot home">
            <OpsPilotLogo />
          </Link>

          <nav className="hidden items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] p-1 text-sm text-slate-300 backdrop-blur md:flex">
            <Link className="rounded-full px-4 py-2 hover:bg-white/10 hover:text-white" href="/">
              Home
            </Link>
            <Link className="rounded-full px-4 py-2 hover:bg-white/10 hover:text-white" href="/dashboard">
              Dashboard
            </Link>
            <Link className="rounded-full px-4 py-2 hover:bg-white/10 hover:text-white" href="/admin">
              Admin
            </Link>
          </nav>

          <Link
            href="/dashboard"
            className="rounded-full border border-cyan-400/30 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 shadow-[0_0_30px_rgba(34,211,238,0.12)] hover:bg-cyan-400/20"
          >
            Launch Console
          </Link>
        </header>

        {children}
      </div>
    </main>
  );
}
''')

# 3. Landing page
write(SRC / "app" / "page.tsx", r'''
import Link from "next/link";
import { PlatformShell } from "@/components/PlatformShell";
import { StatusBadge } from "@/components/StatusBadge";

const features = [
  {
    title: "Multi-agent incident command",
    description: "Specialized agents triage, investigate, reason, plan, review risk, execute controlled actions, and generate postmortems.",
  },
  {
    title: "Human approval by design",
    description: "Risky production actions require a decision-ready human approval brief before remediation can proceed.",
  },
  {
    title: "Qwen-ready reasoning layer",
    description: "The backend includes a Qwen-compatible client with mock fallback while Qwen Cloud credits are pending.",
  },
  {
    title: "Alibaba Cloud deployment-ready",
    description: "Docker and ECS deployment files are prepared so the backend can be deployed once hackathon credits are active.",
  },
];

const workflow = [
  "Alert intake",
  "Triage",
  "Evidence analysis",
  "Root-cause hypothesis",
  "Remediation plan",
  "Risk review",
  "Human approval",
  "Execution review",
  "Postmortem",
];

export default function Home() {
  return (
    <PlatformShell>
      <section className="mx-auto grid max-w-7xl gap-10 px-6 pb-20 pt-10 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
        <div>
          <div className="mb-6 flex flex-wrap gap-3">
            <StatusBadge label="Qwen-powered" tone="cyan" />
            <StatusBadge label="Autopilot Agent Track" tone="violet" />
            <StatusBadge label="Human-in-the-loop" tone="green" />
          </div>

          <h1 className="max-w-4xl text-5xl font-black tracking-tight text-white md:text-7xl">
            AI incident operations,
            <span className="block bg-gradient-to-r from-cyan-300 via-blue-300 to-violet-300 bg-clip-text text-transparent">
              controlled by agents.
            </span>
          </h1>

          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300">
            OpsPilot is a futuristic incident command platform that turns noisy production alerts into structured investigation,
            safe remediation planning, human approval, execution review, and postmortem generation.
          </p>

          <div className="mt-8 flex flex-wrap gap-4">
            <Link
              href="/dashboard"
              className="rounded-2xl bg-cyan-300 px-6 py-3 text-sm font-black text-slate-950 shadow-[0_0_45px_rgba(34,211,238,0.25)] hover:bg-cyan-200"
            >
              Open Operator Dashboard
            </Link>
            <Link
              href="/admin"
              className="rounded-2xl border border-white/10 bg-white/[0.04] px-6 py-3 text-sm font-bold text-white hover:bg-white/[0.08]"
            >
              View Admin Console
            </Link>
          </div>

          <div className="mt-10 grid max-w-2xl grid-cols-3 gap-3">
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <div className="text-2xl font-black text-white">10</div>
              <div className="text-xs text-slate-400">Specialized agents</div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <div className="text-2xl font-black text-white">7-step</div>
              <div className="text-xs text-slate-400">Incident workflow</div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <div className="text-2xl font-black text-white">ECS</div>
              <div className="text-xs text-slate-400">Deployment-ready</div>
            </div>
          </div>
        </div>

        <div className="rounded-[2rem] border border-cyan-400/20 bg-slate-950/70 p-5 shadow-[0_0_80px_rgba(34,211,238,0.12)] backdrop-blur">
          <div className="rounded-[1.5rem] border border-white/10 bg-[#050b18] p-5">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <div className="text-sm font-bold text-white">Live command flow</div>
                <div className="text-xs text-slate-400">Checkout API latency incident</div>
              </div>
              <StatusBadge label="awaiting approval" tone="amber" />
            </div>

            <div className="space-y-3">
              {workflow.map((item, index) => (
                <div key={item} className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/[0.035] p-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-cyan-400/30 bg-cyan-400/10 text-xs font-black text-cyan-200">
                    {index + 1}
                  </div>
                  <div className="flex-1 text-sm font-semibold text-slate-200">{item}</div>
                  <div className="h-2 w-2 rounded-full bg-cyan-300 shadow-[0_0_12px_rgba(34,211,238,0.8)]" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 pb-20">
        <div className="mb-8">
          <h2 className="text-3xl font-black text-white">Platform modules</h2>
          <p className="mt-2 max-w-2xl text-slate-400">
            Designed to look and behave like an enterprise incident operations console, not a one-screen prototype.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {features.map((feature) => (
            <div key={feature.title} className="rounded-3xl border border-white/10 bg-white/[0.04] p-6 backdrop-blur">
              <div className="mb-4 h-10 w-10 rounded-2xl border border-violet-400/30 bg-violet-400/10" />
              <h3 className="text-lg font-black text-white">{feature.title}</h3>
              <p className="mt-3 text-sm leading-6 text-slate-400">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>
    </PlatformShell>
  );
}
''')

# 4. Admin page
write(SRC / "app" / "admin" / "page.tsx", r'''
import Link from "next/link";
import { PlatformShell } from "@/components/PlatformShell";
import { StatusBadge } from "@/components/StatusBadge";

const agents = [
  ["triage_agent", "enabled", "Classifies severity and blast radius"],
  ["observability_agent", "enabled", "Analyzes metrics, logs, and deployments"],
  ["runbook_retrieval_agent", "enabled", "Retrieves runbooks and prior incidents"],
  ["hypothesis_agent", "enabled", "Ranks root-cause hypotheses"],
  ["remediation_planner_agent", "enabled", "Plans safe remediation and rollback"],
  ["risk_safety_agent", "enabled", "Applies production safety policy"],
  ["approval_agent", "enabled", "Prepares human approval brief"],
  ["postmortem_agent", "enabled", "Generates closure report"],
];

const checklist = [
  ["Frontend deployed on Vercel", true],
  ["FastAPI backend working locally", true],
  ["Dockerfile prepared", true],
  ["Alibaba ECS deployment plan", true],
  ["Qwen real API mode", false],
  ["Cloud credits activated", false],
  ["Production backend URL connected", false],
];

export default function AdminPage() {
  return (
    <PlatformShell>
      <section className="mx-auto max-w-7xl px-6 pb-20 pt-10">
        <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="mb-4 flex flex-wrap gap-3">
              <StatusBadge label="Admin Console" tone="violet" />
              <StatusBadge label="Mock LLM safe mode" tone="amber" />
            </div>
            <h1 className="text-4xl font-black text-white md:text-6xl">Platform control center</h1>
            <p className="mt-4 max-w-3xl text-slate-400">
              Manage agent readiness, deployment status, safety posture, and Qwen Cloud activation state from a single operator console.
            </p>
          </div>

          <Link
            href="/dashboard"
            className="rounded-2xl bg-cyan-300 px-5 py-3 text-sm font-black text-slate-950 hover:bg-cyan-200"
          >
            Open dashboard
          </Link>
        </div>

        <div className="grid gap-4 lg:grid-cols-4">
          <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-6">
            <div className="text-sm text-slate-400">Qwen mode</div>
            <div className="mt-2 text-2xl font-black text-white">Mock fallback</div>
            <div className="mt-4">
              <StatusBadge label="cost-safe" tone="green" />
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-6">
            <div className="text-sm text-slate-400">Frontend</div>
            <div className="mt-2 text-2xl font-black text-white">Vercel live</div>
            <div className="mt-4">
              <StatusBadge label="deployed" tone="cyan" />
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-6">
            <div className="text-sm text-slate-400">Backend</div>
            <div className="mt-2 text-2xl font-black text-white">Docker-ready</div>
            <div className="mt-4">
              <StatusBadge label="ECS pending" tone="amber" />
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-6">
            <div className="text-sm text-slate-400">Safety posture</div>
            <div className="mt-2 text-2xl font-black text-white">Approval gated</div>
            <div className="mt-4">
              <StatusBadge label="human-in-loop" tone="violet" />
            </div>
          </div>
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
          <section className="rounded-3xl border border-white/10 bg-slate-950/60 p-6">
            <h2 className="text-2xl font-black text-white">Agent registry</h2>
            <p className="mt-2 text-sm text-slate-400">Specialized agents available in the incident workflow.</p>

            <div className="mt-6 space-y-3">
              {agents.map(([name, state, description]) => (
                <div key={name} className="flex items-center justify-between gap-4 rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                  <div>
                    <div className="font-mono text-sm font-bold text-cyan-100">{name}</div>
                    <div className="mt-1 text-sm text-slate-400">{description}</div>
                  </div>
                  <StatusBadge label={state} tone="green" />
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-slate-950/60 p-6">
            <h2 className="text-2xl font-black text-white">Deployment readiness</h2>
            <p className="mt-2 text-sm text-slate-400">Pay-as-you-go will not be used before credits are activated.</p>

            <div className="mt-6 space-y-3">
              {checklist.map(([label, done]) => (
                <div key={String(label)} className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                  <span className="text-sm font-semibold text-slate-200">{label}</span>
                  <StatusBadge label={done ? "ready" : "pending"} tone={done ? "green" : "amber"} />
                </div>
              ))}
            </div>

            <div className="mt-6 rounded-2xl border border-amber-400/20 bg-amber-400/10 p-4 text-sm leading-6 text-amber-100">
              Qwen Cloud coupon request is pending. Real Qwen mode and Alibaba Cloud ECS backend deployment will be activated only after credits are available.
            </div>
          </section>
        </div>
      </section>
    </PlatformShell>
  );
}
''')

print("Frontend platform upgrade completed.")
