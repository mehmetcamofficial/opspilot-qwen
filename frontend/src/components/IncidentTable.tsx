"use client";

import { useMemo, useState } from "react";
import { StatusBadge } from "@/components/StatusBadge";
import { Icon } from "@/components/ui/Icon";
import { toneForSeverity } from "@/lib/severity";

type IncidentRow = {
  incident_id?: string;
  status?: string;
  severity?: string;
  service?: string;
  assignee?: string;
  triage_result?: {
    affected_service?: string;
    severity?: string;
  };
};

type IncidentTableProps = {
  incidents: IncidentRow[];
  copy: {
    all: string;
    assignee: string;
    actions: string;
    copyId: string;
    filter: string;
    incident: string;
    next: string;
    open: string;
    page: string;
    previous: string;
    service: string;
    severity: string;
    sort: string;
    status: string;
  };
};

const pageSize = 6;

export function IncidentTable({ incidents, copy }: IncidentTableProps) {
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortKey, setSortKey] = useState<"incident" | "severity" | "status">("incident");
  const [page, setPage] = useState(1);

  const statuses = useMemo(() => {
    return Array.from(new Set(incidents.map((incident) => incident.status || "unknown"))).sort();
  }, [incidents]);

  const filtered = useMemo(() => {
    return incidents
      .filter((incident) => statusFilter === "all" || (incident.status || "unknown") === statusFilter)
      .sort((first, second) => {
        if (sortKey === "severity") {
          return (first.triage_result?.severity || first.severity || "").localeCompare(second.triage_result?.severity || second.severity || "");
        }
        if (sortKey === "status") {
          return (first.status || "").localeCompare(second.status || "");
        }
        return (first.incident_id || "").localeCompare(second.incident_id || "");
      });
  }, [incidents, sortKey, statusFilter]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const currentPage = Math.min(page, totalPages);
  const visibleRows = filtered.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div className="flex flex-wrap gap-2">
          <label className="inline-flex items-center gap-2 rounded-2xl border border-white/10 bg-white/[0.04] px-3 py-2 text-xs font-bold text-slate-300">
            <Icon name="filter" className="h-4 w-4 text-cyan-200" />
            {copy.filter}
            <select
              value={statusFilter}
              onChange={(event) => {
                setStatusFilter(event.target.value);
                setPage(1);
              }}
              className="bg-transparent text-cyan-100 outline-none"
            >
              <option value="all">{copy.all}</option>
              {statuses.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </label>

          <label className="inline-flex items-center gap-2 rounded-2xl border border-white/10 bg-white/[0.04] px-3 py-2 text-xs font-bold text-slate-300">
            <Icon name="table" className="h-4 w-4 text-cyan-200" />
            {copy.sort}
            <select
              value={sortKey}
              onChange={(event) => setSortKey(event.target.value as "incident" | "severity" | "status")}
              className="bg-transparent text-cyan-100 outline-none"
            >
              <option value="incident">{copy.incident}</option>
              <option value="severity">{copy.severity}</option>
              <option value="status">{copy.status}</option>
            </select>
          </label>
        </div>

        <div className="text-xs font-bold text-slate-500">
          {copy.page} {currentPage}/{totalPages}
        </div>
      </div>

      <div className="overflow-hidden rounded-3xl border border-white/10">
        <div className="grid grid-cols-[1.2fr_0.8fr_0.8fr] gap-3 bg-white/[0.05] px-4 py-3 text-xs font-black uppercase tracking-wider text-slate-500 md:grid-cols-[1.3fr_1fr_0.8fr_0.9fr_0.9fr_0.9fr]">
          <div>{copy.incident}</div>
          <div className="hidden md:block">{copy.service}</div>
          <div>{copy.severity}</div>
          <div>{copy.status}</div>
          <div className="hidden md:block">{copy.assignee}</div>
          <div className="hidden md:block">{copy.actions}</div>
        </div>

        {visibleRows.map((incident) => {
          const severity = incident.triage_result?.severity || incident.severity || "P3";
          return (
            <div
              key={incident.incident_id}
              className="group grid grid-cols-[1.2fr_0.8fr_0.8fr] gap-3 border-t border-white/10 px-4 py-3 text-sm text-slate-300 transition hover:bg-white/[0.035] md:grid-cols-[1.3fr_1fr_0.8fr_0.9fr_0.9fr_0.9fr]"
            >
              <div className="truncate font-mono font-black text-cyan-100">{incident.incident_id}</div>
              <div className="hidden truncate md:block">{incident.triage_result?.affected_service || incident.service || "unknown"}</div>
              <div><StatusBadge label={severity} tone={toneForSeverity(severity)} /></div>
              <div className="truncate">{incident.status || "unknown"}</div>
              <div className="hidden truncate md:block">{incident.assignee || "unassigned"}</div>
              <div className="hidden items-center gap-2 opacity-0 transition group-hover:opacity-100 md:flex">
                <a href={`/dashboard#${incident.incident_id || "incident"}`} className="rounded-xl border border-cyan-300/20 bg-cyan-300/10 px-2 py-1 text-[11px] font-black text-cyan-50 hover:bg-cyan-300/20">
                  {copy.open}
                </a>
                <button
                  type="button"
                  onClick={() => navigator.clipboard?.writeText(incident.incident_id || "").catch(() => undefined)}
                  className="rounded-xl border border-white/10 bg-white/[0.04] px-2 py-1 text-[11px] font-black text-slate-200 hover:bg-white/[0.08]"
                >
                  {copy.copyId}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      <div className="flex justify-end gap-2">
        <button
          type="button"
          disabled={currentPage === 1}
          onClick={() => setPage((value) => Math.max(1, value - 1))}
          className="rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-2 text-xs font-black text-white transition hover:bg-white/[0.08] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-40"
        >
          {copy.previous}
        </button>
        <button
          type="button"
          disabled={currentPage === totalPages}
          onClick={() => setPage((value) => Math.min(totalPages, value + 1))}
          className="rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-2 text-xs font-black text-white transition hover:bg-white/[0.08] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-40"
        >
          {copy.next}
        </button>
      </div>
    </div>
  );
}
