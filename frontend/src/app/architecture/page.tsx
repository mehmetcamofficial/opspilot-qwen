import Image from "next/image";
import { PlatformShell } from "@/components/PlatformShell";
import { StatusBadge } from "@/components/StatusBadge";

const layers = [
  ["Experience layer", "Next.js dashboard, admin console, architecture page, simulation, and knowledge graph."],
  ["API layer", "FastAPI endpoints for incident creation, approval, status, and future admin operations."],
  ["Agent layer", "Triage, observability, runbook, hypothesis, remediation, risk, approval, execution, review, and postmortem agents."],
  ["Reasoning layer", "Qwen Cloud model API for reasoning, planning, risk review, and generation now that credits are active."],
  ["Platform layer", "Vercel frontend, Docker-ready backend, Alibaba Cloud ECS rollout path, state, and audit trail."],
];

export default function ArchitecturePage() {
  return (
    <PlatformShell>
      <section className="mx-auto max-w-7xl px-6 pb-20 pt-10">
        <div className="mb-8">
          <div className="mb-4 flex flex-wrap gap-3">
            <StatusBadge label="Architecture" tone="cyan" />
            <StatusBadge label="Credits active" tone="green" />
            <StatusBadge label="ECS rollout ready" tone="violet" />
          </div>
          <h1 className="text-4xl font-black text-white md:text-6xl">System architecture</h1>
          <p className="mt-4 max-w-3xl text-slate-400">
            OpsPilot is designed as a layered, safety-aware, multi-agent incident operations platform with an active path to Alibaba Cloud and live Qwen reasoning.
          </p>
        </div>

        <div className="rounded-[2rem] border border-cyan-400/20 bg-slate-950/70 p-4 shadow-[0_0_80px_rgba(34,211,238,0.12)]">
          <Image
            src="/architecture_workflow_diagram.png"
            alt="OpsPilot architecture workflow diagram"
            width={1672}
            height={941}
            priority
            className="w-full rounded-[1.5rem] border border-white/10"
          />
        </div>

        <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          {layers.map(([title, description]) => (
            <div key={title} className="rounded-3xl border border-white/10 bg-white/[0.04] p-5">
              <h2 className="text-lg font-black text-white">{title}</h2>
              <p className="mt-3 text-sm leading-6 text-slate-400">{description}</p>
            </div>
          ))}
        </div>

        <div className="mt-8 rounded-3xl border border-white/10 bg-white/[0.04] p-6">
          <h2 className="text-2xl font-black text-white">Technical documentation</h2>
          <div className="mt-4 grid gap-3 text-sm text-slate-300 md:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">docs/architecture.md</div>
            <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">docs/architecture.mmd</div>
            <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">docs/architecture.svg</div>
          </div>
        </div>
      </section>
    </PlatformShell>
  );
}
