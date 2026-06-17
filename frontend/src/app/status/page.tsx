"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { PlatformShell } from "@/components/PlatformShell";
import { StatusBadge } from "@/components/StatusBadge";
import { getPublicStatus } from "@/lib/api";

type ServiceStatus = {
  service: string;
  status: string;
  severity: "P0" | "P1" | "P2" | "P3";
  incident_id: string;
  message: string;
  assignee: string;
};

type PublicStatus = {
  status: "operational" | "degraded" | "major_outage";
  active_incidents: number;
  highest_severity: "P0" | "P1" | "P2" | "P3" | null;
  updated_at: string;
  services: ServiceStatus[];
};

function statusTone(status: PublicStatus["status"]): "green" | "amber" | "violet" {
  if (status === "operational") return "green";
  if (status === "degraded") return "amber";
  return "violet";
}

function statusLabel(status: PublicStatus["status"]) {
  if (status === "major_outage") return "Major outage";
  if (status === "degraded") return "Degraded performance";
  return "All systems operational";
}

export default function StatusPage() {
  const [status, setStatus] = useState<PublicStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getPublicStatus()
      .then((data) => {
        setStatus(data);
        setError(null);
      })
      .catch((error: unknown) => {
        setError(error instanceof Error ? error.message : "Unable to load public status.");
      });
  }, []);

  const currentStatus = status?.status || "operational";

  return (
    <PlatformShell>
      <section className="mx-auto max-w-7xl px-6 pb-20 pt-10">
        <div className="rounded-[2rem] border border-white/10 bg-slate-950/70 p-6 shadow-[0_0_80px_rgba(34,211,238,0.08)]">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <div className="mb-4 flex flex-wrap gap-3">
                <StatusBadge label="Public status" tone="cyan" />
                <StatusBadge label={statusLabel(currentStatus)} tone={statusTone(currentStatus)} />
              </div>
              <h1 className="text-4xl font-black text-white md:text-6xl">{statusLabel(currentStatus)}</h1>
              <p className="mt-4 max-w-3xl text-slate-400">
                Read-only service health for stakeholders outside the operations console.
              </p>
            </div>

            <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-5">
              <div className="text-xs uppercase tracking-wider text-slate-500">Last updated</div>
              <div className="mt-2 font-mono text-sm text-slate-200">
                {status?.updated_at ? new Date(status.updated_at).toLocaleString() : "waiting for backend"}
              </div>
              <div className="mt-4 text-xs uppercase tracking-wider text-slate-500">Active incidents</div>
              <div className="mt-2 text-3xl font-black text-white">{status?.active_incidents ?? 0}</div>
            </div>
          </div>

          {error && (
            <div className="mt-6 rounded-3xl border border-amber-400/25 bg-amber-400/10 p-5 text-sm leading-6 text-amber-50">
              Status backend is not reachable yet: {error}
            </div>
          )}
        </div>

        <div className="mt-6 grid gap-5 lg:grid-cols-[1fr_360px]">
          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-2xl font-black text-white">Service health</h2>
                <p className="mt-1 text-sm text-slate-400">Services impacted by active incidents appear here.</p>
              </div>
              <StatusBadge label={status?.highest_severity || "clear"} tone={status?.highest_severity === "P0" ? "amber" : "green"} />
            </div>

            <div className="mt-5 grid gap-3">
              {status?.services?.length ? (
                status.services.map((service) => (
                  <div key={`${service.incident_id}-${service.service}`} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                    <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                      <div>
                        <div className="font-mono text-xs font-black text-cyan-100">{service.incident_id}</div>
                        <h3 className="mt-2 text-xl font-black text-white">{service.service}</h3>
                        <p className="mt-2 text-sm leading-6 text-slate-300">{service.message}</p>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        <StatusBadge label={service.severity} tone={service.severity === "P0" ? "amber" : "violet"} />
                        <StatusBadge label={service.status} tone="amber" />
                      </div>
                    </div>
                    <div className="mt-3 text-xs uppercase tracking-wider text-slate-500">Owner: {service.assignee}</div>
                  </div>
                ))
              ) : (
                <div className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 p-5">
                  <h3 className="font-black text-emerald-50">No active customer-impacting incidents</h3>
                  <p className="mt-2 text-sm text-emerald-100/80">OpsPilot has no unresolved incidents in the public status feed.</p>
                </div>
              )}
            </div>
          </section>

          <aside className="space-y-5">
            <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-5">
              <h2 className="text-2xl font-black text-white">Status policy</h2>
              <div className="mt-4 space-y-3 text-sm text-slate-300">
                <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-3">P0 incidents publish as major outage.</div>
                <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-3">P1/P2 incidents publish as degraded performance.</div>
                <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-3">Resolved incidents are hidden from public impact.</div>
              </div>
            </section>

            <Link
              href="/dashboard"
              className="flex rounded-3xl border border-cyan-300/20 bg-cyan-300/10 p-5 text-sm font-black text-cyan-50 hover:bg-cyan-300/20"
            >
              Open Command Center →
            </Link>
          </aside>
        </div>
      </section>
    </PlatformShell>
  );
}
