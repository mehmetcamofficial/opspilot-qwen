from pathlib import Path
import subprocess
import shutil
import sys

ROOT = Path(".")
FRONTEND = ROOT / "frontend"
DASHBOARD = FRONTEND / "src" / "app" / "dashboard" / "page.tsx"
BACKUP_DIR = ROOT / "scripts" / "_backups_sprint30_dashboard_micro_density"
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

# Dashboard-only visual density tuning. No state, API, approval, or timeline logic changes.
replacements = [
    ('className="mx-auto max-w-7xl px-6 pb-16 pt-8"', 'className="mx-auto max-w-7xl px-6 pb-12 pt-6"'),
    ('className="mb-6 rounded-3xl border border-white/10 bg-slate-950/70 p-5"', 'className="mb-5 rounded-3xl border border-white/10 bg-slate-950/70 p-5"'),
    ('className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between"', 'className="mb-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between"'),
    ('className="grid items-start gap-6 xl:grid-cols-[minmax(0,1fr)_390px]"', 'className="grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_390px]"'),
    ('className="space-y-6"', 'className="space-y-5"'),
    ('className="grid items-start gap-6 lg:grid-cols-[0.82fr_1.18fr]"', 'className="grid items-start gap-5 lg:grid-cols-[0.82fr_1.18fr]"'),
    ('className="grid items-start gap-6 lg:grid-cols-[1fr_1fr]"', 'className="grid items-start gap-5 lg:grid-cols-[1fr_1fr]"'),
    ('className="space-y-6 xl:sticky xl:top-28"', 'className="space-y-5 xl:sticky xl:top-24"'),
    ('className="rounded-3xl border border-white/10 bg-slate-950/70 p-6"', 'className="rounded-3xl border border-white/10 bg-slate-950/70 p-5"'),
    ('className="rounded-3xl border border-amber-400/20 bg-amber-400/10 p-6"', 'className="rounded-3xl border border-amber-400/20 bg-amber-400/10 p-5"'),
    ('className="rounded-3xl border border-violet-400/20 bg-violet-400/10 p-6"', 'className="rounded-3xl border border-violet-400/20 bg-violet-400/10 p-5"'),
    ('className="mt-6 grid gap-3 md:grid-cols-2"', 'className="mt-5 grid gap-3 md:grid-cols-2"'),
    ('className="mt-6 grid gap-3 md:grid-cols-7"', 'className="mt-5 grid gap-3 md:grid-cols-7"'),
    ('className="mt-6 grid gap-3 md:grid-cols-2"', 'className="mt-5 grid gap-3 md:grid-cols-2"'),
]

for old, new in replacements:
    text = text.replace(old, new)

DASHBOARD.write_text(text)

print("Sprint 3.0 dashboard micro density patch applied. Running build check...")
result = run_build()
print(result.stdout)

if result.returncode != 0:
    shutil.copyfile(BACKUP, DASHBOARD)
    print("BUILD FAILED. Dashboard restored.")
    sys.exit(result.returncode)

print("BUILD PASSED. Dashboard micro density kept.")
print(f"Backup stored at {BACKUP}")
