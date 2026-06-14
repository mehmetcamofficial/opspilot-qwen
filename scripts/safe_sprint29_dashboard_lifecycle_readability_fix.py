from pathlib import Path
import subprocess
import shutil
import sys

ROOT = Path(".")
FRONTEND = ROOT / "frontend"
DASHBOARD = FRONTEND / "src" / "app" / "dashboard" / "page.tsx"
BACKUP_DIR = ROOT / "scripts" / "_backups_sprint29_dashboard_lifecycle_readability"
BACKUP = BACKUP_DIR / "dashboard.page.tsx"

def run_build():
    return subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

if not DASHBOARD.exists():
    print("ERROR: dashboard/page.tsx not found")
    sys.exit(1)

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copyfile(DASHBOARD, BACKUP)

text = DASHBOARD.read_text()

# 1. Make agent display names readable, not over-truncated.
old_agent_display = '''function agentDisplayName(agent?: string) {
  const labels: Record<string, string> = {
    triage_agent: "triage",
    observability_agent: "observability",
    runbook_agent: "runbook",
    runbook_retrieval_agent: "runbook",
    hypothesis_agent: "hypothesis",
    remediation_planner_agent: "remediation",
    risk_safety_agent: "safety",
    approval_agent: "approval",
    remediation_executor: "executor",
    execution_review_agent: "review",
    postmortem_agent: "postmortem",
  };

  if (!agent) return "agent";
  return labels[agent] || agent.replaceAll("_agent", "").replaceAll("_", " ");
}'''

new_agent_display = '''function agentDisplayName(agent?: string) {
  const labels: Record<string, string> = {
    triage_agent: "Triage",
    observability_agent: "Observability",
    runbook_agent: "Runbook",
    runbook_retrieval_agent: "Runbook",
    hypothesis_agent: "Hypothesis",
    remediation_planner_agent: "Planner",
    risk_safety_agent: "Safety",
    approval_agent: "Approval Gate",
    remediation_executor: "Executor",
    execution_review_agent: "Execution Review",
    postmortem_agent: "Postmortem",
  };

  if (!agent) return "Agent";
  return labels[agent] || agent.replaceAll("_agent", "").replaceAll("_", " ");
}

function displayTimelineStatus(agent: string | undefined, status: string | undefined, isResolved: boolean) {
  if (agent === "approval_agent" && isResolved) return "approved";
  if (status === "approval_required") return "awaiting approval";
  if (status === "completed") return "completed";
  if (status === "executed") return "executed";
  return status || "completed";
}'''

if old_agent_display not in text:
    print("ERROR: agentDisplayName block not found. Restoring.")
    shutil.copyfile(BACKUP, DASHBOARD)
    sys.exit(1)

text = text.replace(old_agent_display, new_agent_display, 1)

# 2. Start Incident should visibly walk 1->2->3->4, not jump directly to 4.
old_start = '''  async function startIncident() {
    setLoading(true);
    setVisualStep(0);
    try {
      const data = await createIncident();
      setIncident(data.state ?? data);
      setVisualStep(3);
      notify("Demo incident started. Safety gate is waiting for approval.");
    } catch (error: any) {
      alert(error.message);
      setVisualStep(null);
    } finally {
      setLoading(false);
    }
  }'''

new_start = '''  async function startIncident() {
    setLoading(true);
    setVisualStep(0);
    try {
      await sleep(300);
      setVisualStep(1);

      await sleep(300);
      setVisualStep(2);

      const data = await createIncident();
      setIncident(data.state ?? data);

      await sleep(300);
      setVisualStep(3);

      notify("Investigation completed. Safety gate is waiting for human approval.");
    } catch (error: any) {
      alert(error.message);
      setVisualStep(null);
    } finally {
      setLoading(false);
    }
  }'''

if old_start not in text:
    print("ERROR: startIncident block not found. Restoring.")
    shutil.copyfile(BACKUP, DASHBOARD)
    sys.exit(1)

text = text.replace(old_start, new_start, 1)

# 3. State machine: use clearer labels while keeping same state keys.
old_machine_card = '''                  <div className="text-xs font-black uppercase tracking-wider">Step {index + 1}</div>
                  <div className="mt-1 text-sm font-black">{state}</div>'''

new_machine_card = '''                  <div className="text-xs font-black uppercase tracking-wider">Step {index + 1}</div>
                  <div className="mt-1 text-sm font-black">
                    {state === "awaiting approval" ? "approval gate" : state}
                  </div>'''

if old_machine_card not in text:
    print("ERROR: state machine label block not found. Restoring.")
    shutil.copyfile(BACKUP, DASHBOARD)
    sys.exit(1)

text = text.replace(old_machine_card, new_machine_card, 1)

# 4. Timeline card layout: no overlap, status below name, enough room for readable names.
old_timeline_card = '''                    <div key={`${item.agent}-${index}`} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                      <div className="flex min-w-0 items-start justify-between gap-3">
                        <div className="min-w-0">
                          <div title={item.agent} className="truncate font-mono text-sm font-black text-cyan-100">
                            {agentDisplayName(item.agent)}
                          </div>
                          <div className="mt-1 text-xs text-slate-500">step {index + 1}</div>
                        </div>
                        <div className="shrink-0">
                          <StatusBadge label={item.status || "completed"} tone={toneForStatus(item.status || "completed")} />
                        </div>
                      </div>
                    </div>'''

new_timeline_card = '''                    <div key={`${item.agent}-${index}`} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                          <div title={item.agent} className="text-sm font-black leading-5 text-cyan-100">
                            {agentDisplayName(item.agent)}
                          </div>
                          <div className="mt-1 text-xs text-slate-500">Agent step {index + 1}</div>
                        </div>
                        <div className="shrink-0 rounded-full border border-white/10 bg-slate-950/50 px-2.5 py-1 text-xs font-black text-slate-400">
                          {index + 1}
                        </div>
                      </div>

                      <div className="mt-3">
                        <StatusBadge
                          label={displayTimelineStatus(item.agent, item.status, isResolved)}
                          tone={toneForStatus(displayTimelineStatus(item.agent, item.status, isResolved))}
                        />
                      </div>
                    </div>'''

if old_timeline_card not in text:
    print("ERROR: timeline card block not found. Restoring.")
    shutil.copyfile(BACKUP, DASHBOARD)
    sys.exit(1)

text = text.replace(old_timeline_card, new_timeline_card, 1)

# 5. Reduce blank visual feel by adding compact recovery checks inside Execution Review.
old_execution_review_cards = '''                <div className="mt-5 grid gap-3 md:grid-cols-3">
                  <MiniReview label="Action" value={isResolved ? "Rollback executed" : "Waiting approval"} />
                  <MiniReview label="Validation" value={isResolved ? "Latency recovered" : "Not started"} />
                  <MiniReview label="Risk" value={isResolved ? "Reduced" : "Medium"} />
                </div>'''

new_execution_review_cards = '''                <div className="mt-5 grid gap-3 md:grid-cols-3">
                  <MiniReview label="Action" value={isResolved ? "Rollback executed" : "Waiting approval"} />
                  <MiniReview label="Validation" value={isResolved ? "Latency recovered" : "Not started"} />
                  <MiniReview label="Risk" value={isResolved ? "Reduced" : "Medium"} />
                </div>

                <div className="mt-5 grid gap-3 md:grid-cols-2">
                  <MiniReview label="p95 latency" value={isResolved ? "2.8s → 480ms" : "2.8s"} />
                  <MiniReview label="Cache hit ratio" value={isResolved ? "41% → 89%" : "41%"} />
                </div>'''

if old_execution_review_cards not in text:
    print("ERROR: execution review cards block not found. Restoring.")
    shutil.copyfile(BACKUP, DASHBOARD)
    sys.exit(1)

text = text.replace(old_execution_review_cards, new_execution_review_cards, 1)

DASHBOARD.write_text(text)

print("Sprint 2.9 lifecycle readability fix applied. Running build check...")
result = run_build()
print(result.stdout)

if result.returncode != 0:
    shutil.copyfile(BACKUP, DASHBOARD)
    print("BUILD FAILED. Dashboard restored.")
    sys.exit(result.returncode)

print("BUILD PASSED. Sprint 2.9 kept.")
print(f"Backup stored at {BACKUP}")
