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
