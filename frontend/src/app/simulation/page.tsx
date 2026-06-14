"use client";

import { useEffect, useMemo, useState } from "react";
import { PlatformShell } from "@/components/PlatformShell";
import { StatusBadge } from "@/components/StatusBadge";

const steps = [
  ["Alert created", "Monitoring detects checkout API latency and creates an incident.", "alert.event.created"],
  ["Orchestrator launches agents", "The incident orchestrator selects the required agents.", "orchestrator.dispatch"],
  ["Agents gather evidence", "Metrics, logs, deployment history, and runbooks are collected.", "agents.evidence.collect"],
  ["Qwen analyzes and plans", "Reasoning agents generate hypotheses and remediation options.", "qwen.reasoning.plan"],
  ["Risk review and approval", "Safety agents require human approval for production actions.", "safety.approval.required"],
  ["Controlled remediation", "A rollback action is simulated in a controlled workflow.", "remediation.execute.controlled"],
  ["Verification and postmortem", "Results are checked and a postmortem is generated.", "postmortem.generated"],
];

const missionStats = [
  ["Incident status", "active simulation"],
  ["Agent network", "7 stages"],
  ["Risk gate", "approval required"],
  ["Cloud mode", "cost-safe mock"],
];

export default function SimulationPage() {
  const [activeStep, setActiveStep] = useState(0);
  const [running, setRunning] = useState(false);
  const active = useMemo(() => steps[activeStep], [activeStep]);

  useEffect(() => {
    if (!running) return;

    const timer = window.setInterval(() => {
      setActiveStep((current) => {
        if (current >= steps.length - 1) {
          setRunning(false);
          return current;
        }
        return current + 1;
      });
    }, 1200);

    return () => window.clearInterval(timer);
  }, [running]);

  function nextStep() {
    setRunning(false);
    setActiveStep((current) => Math.min(current + 1, steps.length - 1));
  }

  function reset() {
    setRunning(false);
    setActiveStep(0);
  }

  return (
    <PlatformShell>
      <section className="mx-auto max-w-7xl px-6 pb-20 pt-10">
        <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="mb-4 flex flex-wrap gap-3">
              <StatusBadge label="Mission-control simulation" tone="cyan" />
              <StatusBadge label="No cloud cost" tone="green" />
              <StatusBadge label={running ? "running" : "manual"} tone={running ? "green" : "amber"} />
            </div>
            <h1 className="text-4xl font-black text-white md:text-6xl">How OpsPilot works</h1>
            <p className="mt-4 max-w-3xl text-slate-400">
              Step through the multi-agent incident response workflow without calling paid cloud resources.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <button onClick={reset} className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-bold text-white hover:bg-white/[0.08]">
              Reset
            </button>
            <button onClick={() => setRunning(true)} className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-5 py-3 text-sm font-black text-emerald-100 hover:bg-emerald-400/20">
              Run full simulation
            </button>
            <button onClick={nextStep} className="rounded-2xl bg-cyan-300 px-5 py-3 text-sm font-black text-slate-950 hover:bg-cyan-200">
              Next step
            </button>
          </div>
        </div>

        <div className="mb-6 grid gap-3 md:grid-cols-4">
          {missionStats.map(([label, value]) => (
            <div key={label} className="rounded-3xl border border-white/10 bg-white/[0.04] p-4">
              <div className="text-xs uppercase tracking-wider text-slate-500">{label}</div>
              <div className="mt-2 text-xl font-black text-white">{value}</div>
            </div>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <h2 className="text-2xl font-black text-white">Current operation</h2>
            <div className="mt-6 rounded-3xl border border-cyan-400/20 bg-cyan-400/10 p-6">
              <div className="text-sm font-black text-cyan-200">Step {activeStep + 1} of {steps.length}</div>
              <div className="mt-3 text-3xl font-black text-white">{active[0]}</div>
              <p className="mt-4 leading-7 text-slate-300">{active[1]}</p>
              <div className="mt-6 rounded-2xl border border-white/10 bg-slate-950/50 p-4 font-mono text-sm text-cyan-200">
                event: {active[2]}
              </div>
            </div>

            <div className="mt-6 rounded-3xl border border-white/10 bg-white/[0.035] p-5">
              <h3 className="font-black text-white">Mission event stream</h3>
              <div className="mt-4 space-y-2 font-mono text-xs text-slate-300">
                {steps.slice(0, activeStep + 1).map((step, index) => (
                  <div key={step[2]} className="rounded-xl border border-white/10 bg-slate-950/50 p-3">
                    [{String(index + 1).padStart(2, "0")}] {step[2]} — completed
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <h2 className="text-2xl font-black text-white">Workflow timeline</h2>
            <div className="mt-6 space-y-3">
              {steps.map(([title, description], index) => {
                const isActive = index === activeStep;
                const isDone = index < activeStep;
                return (
                  <button
                    key={title}
                    onClick={() => {
                      setRunning(false);
                      setActiveStep(index);
                    }}
                    className={`w-full rounded-2xl border p-4 text-left transition ${
                      isActive
                        ? "border-cyan-400/40 bg-cyan-400/10"
                        : isDone
                        ? "border-emerald-400/20 bg-emerald-400/5"
                        : "border-white/10 bg-white/[0.035] hover:bg-white/[0.06]"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex h-9 w-9 items-center justify-center rounded-full border border-cyan-400/30 bg-cyan-400/10 text-sm font-black text-cyan-200">
                        {index + 1}
                      </div>
                      <div>
                        <div className="font-black text-white">{title}</div>
                        <div className="mt-1 text-sm text-slate-400">{description}</div>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </section>
    </PlatformShell>
  );
}
