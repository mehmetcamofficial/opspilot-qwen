from pathlib import Path
import subprocess
import shutil
import sys

ROOT = Path(".")
FRONTEND = ROOT / "frontend"
DASHBOARD = FRONTEND / "src" / "app" / "dashboard" / "page.tsx"
BACKUP_DIR = ROOT / "scripts" / "_backups_sprint26_dashboard_polish"
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

# Tighten dashboard vertical rhythm only on dashboard page.
text = text.replace(
    'className="mx-auto max-w-7xl px-6 pb-20 pt-10"',
    'className="mx-auto max-w-7xl px-6 pb-16 pt-8"',
    1,
)

# Add an Approval Drawer card after the Safety Gate block, without changing approval logic.
old_safety_end = '''              <button onClick={approve} disabled={loading || !incident?.incident_id || isResolved} className="mt-5 w-full rounded-2xl bg-emerald-300 px-5 py-3 text-sm font-black text-slate-950 hover:bg-emerald-200 disabled:cursor-not-allowed disabled:opacity-40">
                {isResolved ? "Remediation approved" : isAwaitingApproval ? "Approve Remediation" : "Start incident first"}
              </button>
            </section>

            <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
              <h2 className="text-2xl font-black text-white">Audit trail</h2>'''

new_safety_end = '''              <button onClick={approve} disabled={loading || !incident?.incident_id || isResolved} className="mt-5 w-full rounded-2xl bg-emerald-300 px-5 py-3 text-sm font-black text-slate-950 hover:bg-emerald-200 disabled:cursor-not-allowed disabled:opacity-40">
                {isResolved ? "Remediation approved" : isAwaitingApproval ? "Approve Remediation" : "Start incident first"}
              </button>
            </section>

            <section className="rounded-3xl border border-violet-400/20 bg-violet-400/10 p-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-black text-white">Approval Drawer</h2>
                  <p className="mt-1 text-sm text-violet-100/80">Operator decision package before remediation.</p>
                </div>
                <StatusBadge label={isResolved ? "closed" : "review"} tone={isResolved ? "green" : "violet"} />
              </div>

              <div className="mt-5 space-y-3">
                <ApprovalLine label="Recommended action" value={recommendedAction(incident)} />
                <ApprovalLine label="Evidence used" value="metrics + logs + deployment + runbook" />
                <ApprovalLine label="Policy triggered" value="production rollback requires approval" />
                <ApprovalLine label="Rollback safety" value="reversible config change" />
              </div>
            </section>

            <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
              <h2 className="text-2xl font-black text-white">Audit trail</h2>'''

if old_safety_end not in text:
    print("ERROR: Could not find Safety Gate insertion point. Restoring.")
    shutil.copyfile(BACKUP, DASHBOARD)
    sys.exit(1)

text = text.replace(old_safety_end, new_safety_end, 1)

# Replace outcome/postmortem section internals with a denser execution review + postmortem layout.
old_outcome = '''          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <h2 className="text-2xl font-black text-white">Outcome and postmortem</h2>
            <div className={`mt-5 rounded-3xl border p-5 ${isResolved ? "border-emerald-400/20 bg-emerald-400/10" : "border-white/10 bg-white/[0.035]"}`}>
              <h3 className="font-black text-white">{isResolved ? "Postmortem generated" : "Postmortem preview"}</h3>
              <p className="mt-3 text-sm leading-6 text-slate-300">{postmortemSummary(incident)}</p>
            </div>

            <div className="mt-5 grid gap-3 md:grid-cols-2">
              <button onClick={copyIncidentSummary} className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-bold text-white hover:bg-white/[0.08]">
                Copy incident summary
              </button>
              <button onClick={exportAuditLog} className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-bold text-white hover:bg-white/[0.08]">
                Export audit log
              </button>
            </div>
          </section>'''

new_outcome = '''          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-2xl font-black text-white">Execution Review</h2>
                <p className="mt-1 text-sm text-slate-400">What happened after approval and how the platform verified recovery.</p>
              </div>
              <StatusBadge label={isResolved ? "verified" : "pending"} tone={isResolved ? "green" : "amber"} />
            </div>

            <div className="mt-5 grid gap-3 md:grid-cols-3">
              <MiniReview label="Action" value={isResolved ? "Rollback executed" : "Waiting approval"} />
              <MiniReview label="Validation" value={isResolved ? "Latency recovered" : "Not started"} />
              <MiniReview label="Risk" value={isResolved ? "Reduced" : "Medium"} />
            </div>

            <div className={`mt-5 rounded-3xl border p-5 ${isResolved ? "border-emerald-400/20 bg-emerald-400/10" : "border-white/10 bg-white/[0.035]"}`}>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h3 className="font-black text-white">{isResolved ? "Postmortem generated" : "Postmortem preview"}</h3>
                  <p className="mt-3 text-sm leading-6 text-slate-300">{postmortemSummary(incident)}</p>
                </div>
                <StatusBadge label={isResolved ? "final" : "draft"} tone={isResolved ? "green" : "slate"} />
              </div>
            </div>

            <div className="mt-5 grid gap-3 md:grid-cols-2">
              <button onClick={copyIncidentSummary} className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-bold text-white hover:bg-white/[0.08]">
                Copy incident summary
              </button>
              <button onClick={exportAuditLog} className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-bold text-white hover:bg-white/[0.08]">
                Export audit log
              </button>
            </div>
          </section>'''

if old_outcome not in text:
    print("ERROR: Could not find Outcome section. Restoring.")
    shutil.copyfile(BACKUP, DASHBOARD)
    sys.exit(1)

text = text.replace(old_outcome, new_outcome, 1)

# Add two tiny presentational helper components at end. No business logic changed.
if "function ApprovalLine" not in text:
    text = text.replace(
'''function AuditItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.035] p-3 text-sm">
      <span className="font-semibold text-slate-200">{label}</span>
      <span className="font-mono text-cyan-200">{value}</span>
    </div>
  );
}''',
'''function AuditItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.035] p-3 text-sm">
      <span className="font-semibold text-slate-200">{label}</span>
      <span className="font-mono text-cyan-200">{value}</span>
    </div>
  );
}

function ApprovalLine({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-violet-400/20 bg-slate-950/40 p-3">
      <div className="text-xs uppercase tracking-wider text-violet-200/70">{label}</div>
      <div className="mt-1 text-sm font-semibold leading-6 text-violet-50">{value}</div>
    </div>
  );
}

function MiniReview({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
      <div className="text-xs uppercase tracking-wider text-slate-500">{label}</div>
      <div className="mt-2 font-black text-white">{value}</div>
    </div>
  );
}''',
    )

DASHBOARD.write_text(text)

print("Sprint 2.6 dashboard approval/postmortem polish applied. Running build check...")
result = run_build()
print(result.stdout)

if result.returncode != 0:
    shutil.copyfile(BACKUP, DASHBOARD)
    print("BUILD FAILED. Dashboard restored.")
    sys.exit(result.returncode)

print("BUILD PASSED. Dashboard polish kept.")
print(f"Backup stored at {BACKUP}")
