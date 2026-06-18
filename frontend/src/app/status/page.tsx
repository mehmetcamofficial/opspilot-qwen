"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { PlatformShell } from "@/components/PlatformShell";
import { StatusBadge } from "@/components/StatusBadge";
import { EmptyState } from "@/components/ui/EmptyState";
import { InlineError } from "@/components/ui/InlineError";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { BodyText, PageTitle, SectionTitle } from "@/components/ui/Typography";
import { getPublicStatus } from "@/lib/api";
import { useLanguage, type Language } from "@/lib/language";
import { toneForSeverity } from "@/lib/severity";

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

const statusCopy = {
  EN: {
    badge: "Public status",
    title: {
      operational: "All systems operational",
      degraded: "Degraded performance",
      major_outage: "Major outage",
    },
    description: "Read-only service health for stakeholders outside the operations console.",
    lastUpdated: "Last updated",
    waitingBackend: "waiting for backend",
    activeIncidents: "Active incidents",
    backendError: "Status backend is not reachable yet:",
    serviceHealth: "Service health",
    serviceHealthDescription: "Services impacted by active incidents appear here.",
    clear: "clear",
    owner: "Owner",
    noIncidentsTitle: "No active customer-impacting incidents",
    noIncidentsBody: "OpsPilot has no unresolved incidents in the public status feed.",
    policyTitle: "Status policy",
    p0Policy: "P0 incidents publish as major outage.",
    p1Policy: "P1/P2 incidents publish as degraded performance.",
    resolvedPolicy: "Resolved incidents are hidden from public impact.",
    openCommandCenter: "Open Command Center →",
    unableToLoad: "Unable to load public status.",
    retry: "Retry status check",
    loadingServices: "Loading service health",
  },
  TR: {
    badge: "Genel durum",
    title: {
      operational: "Tüm sistemler çalışıyor",
      degraded: "Performans düşüşü var",
      major_outage: "Büyük kesinti",
    },
    description: "Operasyon konsolu dışındaki paydaşlar için salt okunur servis sağlığı.",
    lastUpdated: "Son güncelleme",
    waitingBackend: "backend bekleniyor",
    activeIncidents: "Aktif olaylar",
    backendError: "Durum backend'i henüz erişilebilir değil:",
    serviceHealth: "Servis sağlığı",
    serviceHealthDescription: "Aktif olaylardan etkilenen servisler burada görünür.",
    clear: "temiz",
    owner: "Sahip",
    noIncidentsTitle: "Müşteri etkili aktif olay yok",
    noIncidentsBody: "OpsPilot genel durum akışında çözülmemiş olay bulunmuyor.",
    policyTitle: "Durum politikası",
    p0Policy: "P0 olayları büyük kesinti olarak yayınlanır.",
    p1Policy: "P1/P2 olayları performans düşüşü olarak yayınlanır.",
    resolvedPolicy: "Çözülen olaylar genel etkiden gizlenir.",
    openCommandCenter: "Komuta Merkezini Aç →",
    unableToLoad: "Genel durum yüklenemedi.",
    retry: "Durumu tekrar kontrol et",
    loadingServices: "Servis sağlığı yükleniyor",
  },
} satisfies Record<Language, unknown>;

function statusLabel(status: PublicStatus["status"], copy: (typeof statusCopy)["EN"]) {
  return copy.title[status];
}

export default function StatusPage() {
  const language = useLanguage();
  const copy = statusCopy[language];
  const [status, setStatus] = useState<PublicStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  function loadStatus() {
    setIsLoading(true);
    getPublicStatus()
      .then((data) => {
        setStatus(data);
        setError(null);
      })
      .catch((error: unknown) => {
        setError(error instanceof Error ? error.message : copy.unableToLoad);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }

  useEffect(() => {
    let mounted = true;

    getPublicStatus()
      .then((data) => {
        if (!mounted) return;
        setStatus(data);
        setError(null);
      })
      .catch((error: unknown) => {
        if (!mounted) return;
        setError(error instanceof Error ? error.message : copy.unableToLoad);
      })
      .finally(() => {
        if (mounted) {
          setIsLoading(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, [copy.unableToLoad]);

  const currentStatus = status?.status || "operational";

  return (
    <PlatformShell>
      <section className="mx-auto max-w-7xl px-4 pb-20 pt-10 sm:px-6">
        <div className="rounded-[2rem] border border-white/10 bg-slate-950/70 p-6 shadow-[0_0_80px_rgba(34,211,238,0.08)]">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <div className="mb-4 flex flex-wrap gap-3">
                <StatusBadge label={copy.badge} tone="cyan" />
                <StatusBadge label={statusLabel(currentStatus, copy)} tone={statusTone(currentStatus)} />
              </div>
              <PageTitle>{statusLabel(currentStatus, copy)}</PageTitle>
              <BodyText className="mt-4 max-w-3xl">
                {copy.description}
              </BodyText>
            </div>

            <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-5">
              <div className="text-xs uppercase tracking-wider text-slate-500">{copy.lastUpdated}</div>
              <div className="mt-2 font-mono text-sm text-slate-200">
                {status?.updated_at ? new Date(status.updated_at).toLocaleString() : copy.waitingBackend}
              </div>
              <div className="mt-4 text-xs uppercase tracking-wider text-slate-500">{copy.activeIncidents}</div>
              <div className="mt-2 text-3xl font-black text-white">{status?.active_incidents ?? 0}</div>
            </div>
          </div>

          {error && (
            <div className="mt-6">
              <InlineError title={copy.backendError} message={error} actionLabel={copy.retry} onAction={loadStatus} />
            </div>
          )}
        </div>

        <div className="mt-6 grid gap-5 lg:grid-cols-[1fr_360px]">
          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <SectionTitle>{copy.serviceHealth}</SectionTitle>
                <BodyText className="mt-1">{copy.serviceHealthDescription}</BodyText>
              </div>
              <StatusBadge label={status?.highest_severity || copy.clear} tone={status?.highest_severity ? toneForSeverity(status.highest_severity) : "green"} />
            </div>

            <div className="mt-5 grid gap-3">
              {isLoading ? (
                <LoadingSkeleton rows={3} />
              ) : status?.services?.length ? (
                status.services.map((service) => (
                  <div key={`${service.incident_id}-${service.service}`} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                    <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                      <div>
                        <div className="font-mono text-xs font-black text-cyan-100">{service.incident_id}</div>
                        <h3 className="mt-2 text-xl font-black text-white">{service.service}</h3>
                        <p className="mt-2 text-sm leading-6 text-slate-300">{service.message}</p>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        <StatusBadge label={service.severity} tone={toneForSeverity(service.severity)} />
                        <StatusBadge label={service.status} tone="amber" />
                      </div>
                    </div>
                    <div className="mt-3 text-xs uppercase tracking-wider text-slate-500">{copy.owner}: {service.assignee}</div>
                  </div>
                ))
              ) : (
                <EmptyState title={copy.noIncidentsTitle} description={copy.noIncidentsBody} action={{ label: copy.openCommandCenter, href: "/dashboard" }} />
              )}
            </div>
          </section>

          <aside className="space-y-5">
            <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-5">
              <SectionTitle>{copy.policyTitle}</SectionTitle>
              <div className="mt-4 space-y-3 text-sm text-slate-300">
                <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-3">{copy.p0Policy}</div>
                <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-3">{copy.p1Policy}</div>
                <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-3">{copy.resolvedPolicy}</div>
              </div>
            </section>

            <Link
              href="/dashboard"
              className="flex rounded-3xl border border-cyan-300/20 bg-cyan-300/10 p-5 text-sm font-black text-cyan-50 transition hover:bg-cyan-300/20 active:scale-[0.98]"
            >
              {copy.openCommandCenter}
            </Link>
          </aside>
        </div>
      </section>
    </PlatformShell>
  );
}
