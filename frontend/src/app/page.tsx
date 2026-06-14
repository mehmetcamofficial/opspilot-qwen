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
