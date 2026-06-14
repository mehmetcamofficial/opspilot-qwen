"use client";

import { useState } from "react";
import { approveIncident, createIncident, healthcheck, listIncidents } from "@/lib/api";

type IncidentState = any;

export default function Home() {
  const [backendStatus, setBackendStatus] = useState<string>("not checked");
  const [incident, setIncident] = useState<IncidentState | null>(null);
  const [incidents, setIncidents] = useState<IncidentState[]>([]);
  const [loading, setLoading] = useState(false);

  async function checkBackend() {
    setLoading(true);
    try {
      const data = await healthcheck();
      setBackendStatus(`${data.status} | mock_llm=${data.mock_llm}`);
    } catch (error: any) {
      setBackendStatus(`error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function startIncident() {
    setLoading(true);
    try {
      const data = await createIncident();
      setIncident(data.state);
    } catch (error: any) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function refreshIncidents() {
    setLoading(true);
    try {
      const data = await listIncidents();
      setIncidents(data);
    } catch (error: any) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function approveCurrentIncident() {
    if (!incident?.incident_id) return;
    setLoading(true);
    try {
      const data = await approveIncident(incident.incident_id);
      setIncident(data);
    } catch (error: any) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  }

  const state = incident;

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto max-w-7xl px-6 py-8">
        <div className="mb-8 rounded-3xl border border-slate-800 bg-slate-900/70 p-8 shadow-2xl">
          <p className="mb-2 text-sm uppercase tracking-[0.3em] text-cyan-300">
            Qwen-Powered Multi-Agent Incident Commander
          </p>
          <h1 className="text-4xl font-bold tracking-tight md:text-6xl">
            OpsPilot
          </h1>
          <p className="mt-4 max-w-3xl text-lg text-slate-300">
            A production-oriented incident response system that triages alerts,
            analyzes observability evidence, retrieves runbooks, plans safe remediation,
            requests human approval, executes controlled actions, and generates postmortems.
          </p>

          <div className="mt-6 flex flex-wrap gap-3">
            <button
              onClick={checkBackend}
              className="rounded-xl border border-slate-700 px-4 py-2 text-sm hover:bg-slate-800"
            >
              Check Backend
            </button>
            <button
              onClick={startIncident}
              className="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-cyan-300"
            >
              Start Demo Incident
            </button>
            <button
              onClick={refreshIncidents}
              className="rounded-xl border border-slate-700 px-4 py-2 text-sm hover:bg-slate-800"
            >
              Refresh Incidents
            </button>
          </div>

          <div className="mt-4 text-sm text-slate-400">
            Backend status: <span className="text-cyan-300">{backendStatus}</span>
          </div>
        </div>

        {loading && (
          <div className="mb-6 rounded-xl border border-cyan-800 bg-cyan-950/40 p-4 text-cyan-200">
            Running workflow...
          </div>
        )}

        {state && (
          <div className="grid gap-6 lg:grid-cols-3">
            <section className="lg:col-span-2 rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-semibold">Incident Command Center</h2>
                  <p className="text-slate-400">{state.incident_id}</p>
                </div>
                <div className="rounded-full border border-slate-700 px-4 py-2 text-sm">
                  Status: <span className="font-semibold text-cyan-300">{state.status}</span>
                </div>
              </div>

              <div className="mt-6 grid gap-4 md:grid-cols-4">
                <MetricCard title="Service" value={state.alert?.service || "-"} />
                <MetricCard title="Severity" value={state.triage_result?.severity || "-"} />
                <MetricCard title="Risk" value={state.risk_review?.action_reviews?.[0]?.risk_level || "-"} />
                <MetricCard title="Confidence" value={String(state.hypothesis_result?.leading_hypothesis?.confidence ?? "-")} />
              </div>

              <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950 p-5">
                <h3 className="mb-3 text-lg font-semibold">Leading Hypothesis</h3>
                <p className="text-slate-300">
                  {state.hypothesis_result?.leading_hypothesis?.title || "No hypothesis yet"}
                </p>
                <p className="mt-2 text-sm text-slate-500">
                  {state.hypothesis_result?.leading_hypothesis?.reason}
                </p>
              </div>

              <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950 p-5">
                <h3 className="mb-3 text-lg font-semibold">Evidence Board</h3>
                <ul className="space-y-2 text-sm text-slate-300">
                  {state.hypothesis_result?.hypotheses?.[0]?.supporting_evidence?.map((item: string, index: number) => (
                    <li key={index} className="rounded-lg bg-slate-900 p-3">
                      {item}
                    </li>
                  ))}
                </ul>
              </div>

              {state.status === "awaiting_approval" && (
                <div className="mt-6 rounded-2xl border border-amber-700 bg-amber-950/30 p-5">
                  <h3 className="text-lg font-semibold text-amber-200">
                    Human Approval Required
                  </h3>
                  <p className="mt-2 text-slate-300">
                    {state.approval_brief?.approval_title}
                  </p>
                  <p className="mt-2 text-sm text-slate-400">
                    {state.approval_brief?.risk_statement}
                  </p>
                  <button
                    onClick={approveCurrentIncident}
                    className="mt-4 rounded-xl bg-amber-300 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-amber-200"
                  >
                    Approve Remediation
                  </button>
                </div>
              )}

              {state.postmortem && (
                <div className="mt-6 rounded-2xl border border-emerald-800 bg-emerald-950/30 p-5">
                  <h3 className="text-lg font-semibold text-emerald-200">
                    Postmortem Generated
                  </h3>
                  <p className="mt-2 text-slate-300">
                    {state.postmortem.root_cause_summary}
                  </p>
                  <div className="mt-4">
                    <h4 className="font-semibold">Follow-up Items</h4>
                    <ul className="mt-2 space-y-2 text-sm text-slate-300">
                      {state.postmortem.follow_up_items?.map((item: any, index: number) => (
                        <li key={index} className="rounded-lg bg-slate-900 p-3">
                          <span className="font-semibold">{item.priority}</span> — {item.title}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </section>

            <aside className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h3 className="text-xl font-semibold">Agent Timeline</h3>
              <div className="mt-4 space-y-3">
                {state.agent_timeline?.map((item: any, index: number) => (
                  <div key={index} className="flex items-center justify-between rounded-xl bg-slate-950 p-3">
                    <span className="text-sm">{item.agent}</span>
                    <span className="rounded-full bg-slate-800 px-2 py-1 text-xs text-cyan-300">
                      {item.status}
                    </span>
                  </div>
                ))}
              </div>

              <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950 p-4">
                <h4 className="font-semibold">Recommended Action</h4>
                <p className="mt-2 text-sm text-slate-300">
                  {state.remediation_plan?.candidate_actions?.[0]?.title || "-"}
                </p>
              </div>
            </aside>
          </div>
        )}

        {incidents.length > 0 && (
          <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="text-xl font-semibold">Stored Incidents</h2>
            <div className="mt-4 space-y-3">
              {incidents.map((item: any) => (
                <div key={item.incident_id} className="rounded-xl bg-slate-950 p-4 text-sm">
                  <div className="font-semibold">{item.incident_id}</div>
                  <div className="text-slate-400">Status: {item.status}</div>
                </div>
              ))}
            </div>
          </section>
        )}
      </section>
    </main>
  );
}

function MetricCard({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
      <div className="text-xs uppercase tracking-wider text-slate-500">{title}</div>
      <div className="mt-2 truncate text-lg font-semibold text-slate-100">{value}</div>
    </div>
  );
}
