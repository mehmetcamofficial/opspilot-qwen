from pathlib import Path
import subprocess
import shutil
import sys

ROOT = Path(".")
FRONTEND = ROOT / "frontend"
SRC = FRONTEND / "src"
ADMIN = SRC / "app" / "admin" / "page.tsx"
NEXT_CONFIG = FRONTEND / "next.config.ts"
BACKUP_DIR = ROOT / "scripts" / "_backups_sprint22_governance_layout"

FILES = [ADMIN, NEXT_CONFIG]

def backup():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    for file in FILES:
        if file.exists():
            target = BACKUP_DIR / str(file).replace("/", "__")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(file, target)

def restore():
    for file in FILES:
        target = BACKUP_DIR / str(file).replace("/", "__")
        if target.exists():
            shutil.copyfile(target, file)

def run_build():
    return subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

if not ADMIN.exists():
    print("ERROR: admin page not found")
    sys.exit(1)

backup()

text = ADMIN.read_text()

# Stop grid cards from stretching to the height of the tallest column.
text = text.replace(
    '        <div className="mt-6 grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">',
    '        <div className="mt-6 grid items-start gap-6 lg:grid-cols-[0.95fr_1.05fr]">',
)
text = text.replace(
    '        <div className="mt-6 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">',
    '        <div className="mt-6 grid items-start gap-6 xl:grid-cols-[1.1fr_0.9fr]">',
)
text = text.replace(
    '        <div className="mt-6 grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">',
    '        <div className="mt-6 grid items-start gap-6 xl:grid-cols-[0.95fr_1.05fr]">',
)

# Add more meaningful controls into Platform switches so it feels like a real control center.
platform_title = '<h2 className="text-2xl font-black text-white">Platform switches</h2>'
deployment_title = '<h2 className="text-2xl font-black text-white">Deployment readiness control</h2>'

if "Quick governance actions" not in text:
    try:
        start = text.index(platform_title)
        end = text.index('\n          </section>\n\n          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">\n            ' + deployment_title, start)
        insert = r'''

            <div className="mt-5 grid gap-3 md:grid-cols-3">
              <button
                onClick={() =>
                  commit(
                    (previous) => ({ ...previous, approvalFreeze: true }),
                    "Production remediation approvals frozen from quick action"
                  )
                }
                className="rounded-2xl border border-amber-400/20 bg-amber-400/10 px-4 py-3 text-sm font-black text-amber-100 hover:bg-amber-400/20"
              >
                Freeze prod actions
              </button>

              <button
                onClick={() =>
                  commit(
                    (previous) => ({ ...previous, auditExportEnabled: true }),
                    "Governance snapshot prepared for export"
                  )
                }
                className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-3 text-sm font-black text-cyan-100 hover:bg-cyan-400/20"
              >
                Prepare export
              </button>

              <button
                onClick={simulateDeploymentCheck}
                className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm font-black text-emerald-100 hover:bg-emerald-400/20"
              >
                Recheck readiness
              </button>
            </div>

            <div className="mt-5 rounded-3xl border border-white/10 bg-white/[0.035] p-5">
              <div className="mb-4 flex items-center justify-between gap-3">
                <div>
                  <div className="text-sm font-black text-white">Quick governance actions</div>
                  <div className="mt-1 text-sm text-slate-400">
                    Operator controls for demo safety, auditability, and deployment preparation.
                  </div>
                </div>
                <StatusBadge label="local controls" tone="cyan" />
              </div>

              <div className="grid gap-3 md:grid-cols-2">
                <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">
                  <div className="text-xs uppercase tracking-wider text-slate-500">Approval mode</div>
                  <div className="mt-2 font-black text-white">
                    {state.approvalFreeze ? "Frozen" : "Active"}
                  </div>
                </div>

                <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">
                  <div className="text-xs uppercase tracking-wider text-slate-500">Audit export</div>
                  <div className="mt-2 font-black text-white">
                    {state.auditExportEnabled ? "Enabled" : "Disabled"}
                  </div>
                </div>

                <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">
                  <div className="text-xs uppercase tracking-wider text-slate-500">Model safety</div>
                  <div className="mt-2 font-black text-white">
                    {state.modelMode === "mock" ? "Cost-safe mock" : "Qwen live pending"}
                  </div>
                </div>

                <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">
                  <div className="text-xs uppercase tracking-wider text-slate-500">Governance storage</div>
                  <div className="mt-2 font-black text-white">localStorage</div>
                </div>
              </div>
            </div>
'''
        text = text[:end] + insert + text[end:]
    except ValueError:
        print("WARNING: Could not insert Quick governance actions. Continuing with layout fixes.")

ADMIN.write_text(text)

# Disable Next.js dev indicator bubble for cleaner screenshots.
NEXT_CONFIG.write_text(r'''
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  devIndicators: false,
};

export default nextConfig;
'''.strip() + "\n")

print("Sprint 2.2 governance layout patch applied. Running build check...")
result = run_build()
print(result.stdout)

if result.returncode != 0:
    restore()
    print("BUILD FAILED. Sprint 2.2 changes were rolled back.")
    sys.exit(result.returncode)

print("BUILD PASSED. Sprint 2.2 changes kept.")
print(f"Backups stored in {BACKUP_DIR}")
