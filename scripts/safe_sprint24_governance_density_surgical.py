from pathlib import Path
import subprocess
import shutil
import sys

ROOT = Path(".")
FRONTEND = ROOT / "frontend"
SRC = FRONTEND / "src"
ADMIN = SRC / "app" / "admin" / "page.tsx"
DOCS_IMAGE = ROOT / "docs" / "architecture_workflow_diagram.png"
PUBLIC_IMAGE = FRONTEND / "public" / "architecture_workflow_diagram.png"
BACKUP_DIR = ROOT / "scripts" / "_backups_sprint24_governance_density"

FILES = [ADMIN, PUBLIC_IMAGE]

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
        elif file.exists() and file == PUBLIC_IMAGE:
            file.unlink()

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

# Restore public architecture image if architecture page uses /architecture_workflow_diagram.png.
if DOCS_IMAGE.exists():
    PUBLIC_IMAGE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(DOCS_IMAGE, PUBLIC_IMAGE)
    print("Architecture public image restored from docs.")
else:
    print("WARNING: docs/architecture_workflow_diagram.png not found; skipped image restore.")

text = ADMIN.read_text()

if "Policy enforcement preview" not in text:
    marker = '''          </section>
        </div>

        <div className="mt-6 grid items-start gap-6 xl:grid-cols-[0.95fr_1.05fr]">'''

    insert = r'''
            <div className="mt-6 rounded-3xl border border-violet-400/20 bg-violet-400/10 p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="font-black text-white">Policy enforcement preview</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-300">
                    Shows how the current policy set would handle common production actions before they reach the Command Center.
                  </p>
                </div>
                <StatusBadge label="live local state" tone="cyan" />
              </div>

              <div className="mt-5 grid gap-3 md:grid-cols-2">
                <MiniState
                  label="Approval-gated rules"
                  value={String(state.policies.filter((policy) => policy.action === "approval_required" && policy.enabled && !policy.archived).length)}
                />
                <MiniState
                  label="Blocked rules"
                  value={String(state.policies.filter((policy) => policy.action === "block" && policy.enabled && !policy.archived).length)}
                />
                <MiniState
                  label="Allowed rules"
                  value={String(state.policies.filter((policy) => policy.action === "allow" && policy.enabled && !policy.archived).length)}
                />
                <MiniState
                  label="Archived policies"
                  value={String(state.policies.filter((policy) => policy.archived).length)}
                />
              </div>

              <div className="mt-5 space-y-3">
                <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">
                  <div className="text-xs uppercase tracking-wider text-slate-500">Production rollback</div>
                  <div className="mt-2 font-black text-white">Requires human approval before execution</div>
                </div>
                <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">
                  <div className="text-xs uppercase tracking-wider text-slate-500">Database restart without evidence</div>
                  <div className="mt-2 font-black text-white">Blocked by safety policy</div>
                </div>
                <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">
                  <div className="text-xs uppercase tracking-wider text-slate-500">Low-risk validation</div>
                  <div className="mt-2 font-black text-white">Allowed with audit logging</div>
                </div>
              </div>
            </div>
'''

    if marker not in text:
        print("ERROR: Could not find safe insertion marker. No changes applied.")
        restore()
        sys.exit(1)

    text = text.replace(
        marker,
        insert + "\n" + marker,
        1,
    )

# Slightly tighten vertical rhythm without changing logic.
text = text.replace(
    'className="mx-auto max-w-7xl px-6 pb-20 pt-10"',
    'className="mx-auto max-w-7xl px-6 pb-16 pt-8"',
    1,
)

ADMIN.write_text(text)

print("Sprint 2.4 surgical governance density patch applied. Running build check...")
result = run_build()
print(result.stdout)

if result.returncode != 0:
    restore()
    print("BUILD FAILED. Sprint 2.4 changes were rolled back.")
    sys.exit(result.returncode)

print("BUILD PASSED. Sprint 2.4 changes kept.")
print(f"Backups stored in {BACKUP_DIR}")
