"use client";

import { useMemo, useState } from "react";
import { PlatformShell } from "@/components/PlatformShell";
import { StatusBadge } from "@/components/StatusBadge";

const nodes = [
  { id: "Incident", x: 48, y: 48, type: "core", description: "Checkout API latency spike after cache configuration regression." },
  { id: "Service", x: 25, y: 22, type: "entity", description: "checkout-api in production environment." },
  { id: "Alert", x: 72, y: 22, type: "signal", description: "p95 latency exceeds threshold." },
  { id: "Metric", x: 84, y: 48, type: "signal", description: "Cache hit ratio collapse and DB latency increase." },
  { id: "Log", x: 70, y: 74, type: "signal", description: "Repeated cache-miss fallback warnings." },
  { id: "Deployment", x: 28, y: 74, type: "change", description: "Recent cache configuration change." },
  { id: "Runbook", x: 15, y: 48, type: "knowledge", description: "Rollback cache configuration and verify latency recovery." },
  { id: "Hypothesis", x: 48, y: 22, type: "reasoning", description: "Cache config regression is the leading root cause." },
  { id: "Risk Policy", x: 48, y: 82, type: "safety", description: "Production rollback requires human approval." },
  { id: "Remediation", x: 48, y: 62, type: "action", description: "Controlled rollback simulation." },
  { id: "Postmortem", x: 84, y: 84, type: "closure", description: "Document root cause, action, gaps, and follow-up tasks." },
];

const edges = [
  ["Incident", "Service"],
  ["Incident", "Alert"],
  ["Alert", "Metric"],
  ["Alert", "Log"],
  ["Metric", "Hypothesis"],
  ["Log", "Hypothesis"],
  ["Deployment", "Hypothesis"],
  ["Runbook", "Remediation"],
  ["Hypothesis", "Remediation"],
  ["Risk Policy", "Remediation"],
  ["Remediation", "Postmortem"],
];

const filters = ["all", "signal", "reasoning", "safety", "action", "knowledge", "closure"];

const typeTone: Record<string, "cyan" | "green" | "amber" | "violet" | "slate"> = {
  core: "cyan",
  entity: "slate",
  signal: "cyan",
  change: "amber",
  knowledge: "violet",
  reasoning: "violet",
  safety: "green",
  action: "amber",
  closure: "green",
};

export default function KnowledgeGraphPage() {
  const [selectedId, setSelectedId] = useState("Incident");
  const [filter, setFilter] = useState("all");
  const [depth, setDepth] = useState<1 | 2>(1);

  const selected = nodes.find((node) => node.id === selectedId) || nodes[0];

  const connectedIds = useMemo(() => {
    const direct = new Set<string>([selectedId]);
    edges.forEach(([from, to]) => {
      if (from === selectedId) direct.add(to);
      if (to === selectedId) direct.add(from);
    });

    if (depth === 1) return direct;

    const second = new Set<string>(direct);
    edges.forEach(([from, to]) => {
      if (direct.has(from)) second.add(to);
      if (direct.has(to)) second.add(from);
    });
    return second;
  }, [selectedId, depth]);

  const visibleNodes = nodes.filter((node) => filter === "all" || node.type === filter || node.id === selectedId);

  return (
    <PlatformShell>
      <section className="mx-auto max-w-7xl px-6 pb-20 pt-10">
        <div className="mb-8">
          <div className="mb-4 flex flex-wrap gap-3">
            <StatusBadge label="Knowledge graph" tone="cyan" />
            <StatusBadge label="Interactive incident map" tone="violet" />
            <StatusBadge label={selected.type} tone={typeTone[selected.type]} />
          </div>
          <h1 className="text-4xl font-black text-white md:text-6xl">Incident knowledge graph</h1>
          <p className="mt-4 max-w-3xl text-slate-400">
            Filter nodes, inspect relationship depth, and click entities to understand how OpsPilot reasons over incident evidence.
          </p>
        </div>

        <div className="mb-6 flex flex-wrap items-center gap-3">
          {filters.map((item) => (
            <button
              key={item}
              onClick={() => setFilter(item)}
              className={`rounded-full border px-4 py-2 text-sm font-bold ${
                filter === item
                  ? "border-cyan-300 bg-cyan-300 text-slate-950"
                  : "border-white/10 bg-white/[0.04] text-slate-300 hover:bg-white/[0.08]"
              }`}
            >
              {item}
            </button>
          ))}

          <button
            onClick={() => setDepth(depth === 1 ? 2 : 1)}
            className="rounded-full border border-violet-400/20 bg-violet-400/10 px-4 py-2 text-sm font-bold text-violet-100 hover:bg-violet-400/20"
          >
            relation depth: {depth}
          </button>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1.25fr_0.75fr]">
          <div className="relative min-h-[620px] overflow-hidden rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(34,211,238,0.10),transparent_35%)]" />

            <svg className="absolute inset-0 h-full w-full" viewBox="0 0 100 100" preserveAspectRatio="none">
              {edges.map(([from, to]) => {
                const a = nodes.find((node) => node.id === from);
                const b = nodes.find((node) => node.id === to);
                if (!a || !b) return null;
                const active = connectedIds.has(from) && connectedIds.has(to);
                return (
                  <line
                    key={`${from}-${to}`}
                    x1={a.x}
                    y1={a.y}
                    x2={b.x}
                    y2={b.y}
                    stroke={active ? "rgba(34,211,238,0.88)" : "rgba(148,163,184,0.14)"}
                    strokeWidth={active ? 0.38 : 0.16}
                    strokeDasharray={active ? "1 0.6" : "0.7 1.2"}
                  />
                );
              })}
            </svg>

            {visibleNodes.map((node) => {
              const active = selected.id === node.id;
              const connected = connectedIds.has(node.id);
              return (
                <button
                  key={node.id}
                  onClick={() => setSelectedId(node.id)}
                  className={`absolute -translate-x-1/2 -translate-y-1/2 rounded-2xl border px-4 py-3 text-left shadow-2xl transition hover:scale-105 ${
                    active
                      ? "border-cyan-300 bg-cyan-300 text-slate-950 shadow-[0_0_45px_rgba(34,211,238,0.35)]"
                      : connected
                      ? "border-cyan-400/40 bg-cyan-400/10 text-white"
                      : "border-white/10 bg-[#07111f]/95 text-white opacity-55 hover:opacity-100"
                  }`}
                  style={{ left: `${node.x}%`, top: `${node.y}%` }}
                >
                  <div className="text-xs font-black uppercase tracking-wider opacity-70">{node.type}</div>
                  <div className="mt-1 text-sm font-black">{node.id}</div>
                </button>
              );
            })}
          </div>

          <aside className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <StatusBadge label="Selected node" tone="green" />
            <h2 className="mt-5 text-3xl font-black text-white">{selected.id}</h2>
            <p className="mt-4 leading-7 text-slate-300">{selected.description}</p>

            <div className="mt-8 rounded-3xl border border-white/10 bg-white/[0.04] p-5">
              <h3 className="font-black text-white">Connected relationships</h3>
              <div className="mt-4 space-y-2">
                {edges
                  .filter(([from, to]) => from === selected.id || to === selected.id)
                  .map(([from, to]) => (
                    <div key={`${from}-${to}`} className="rounded-2xl border border-white/10 bg-slate-950/50 p-3 text-sm text-slate-300">
                      <span className="font-bold text-cyan-200">{from}</span>
                      <span className="px-2 text-slate-500">→</span>
                      <span className="font-bold text-violet-200">{to}</span>
                    </div>
                  ))}
              </div>
            </div>

            <div className="mt-6 rounded-3xl border border-cyan-400/20 bg-cyan-400/10 p-5">
              <h3 className="font-black text-white">Why this matters</h3>
              <p className="mt-3 text-sm leading-6 text-slate-300">
                OpsPilot keeps evidence, hypotheses, risk, remediation, and audit history connected instead of scattered across tools.
              </p>
            </div>
          </aside>
        </div>
      </section>
    </PlatformShell>
  );
}
