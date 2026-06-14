from pathlib import Path
import subprocess
import shutil
import sys
import re

ROOT = Path(".")
FRONTEND = ROOT / "frontend"
PAGE = FRONTEND / "src" / "app" / "dashboard" / "page.tsx"
BACKUP_DIR = ROOT / "scripts" / "_backups_sprint50c_dashboard_demo_compact"
BACKUP = BACKUP_DIR / "dashboard.page.tsx"

def run_build():
    return subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

if not PAGE.exists():
    print("ERROR: dashboard/page.tsx not found")
    sys.exit(1)

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copyfile(PAGE, BACKUP)

text = PAGE.read_text()

compact_banner = '''      {/* demo-hardening-banner */}
      <section className="mx-auto mb-8 max-w-7xl rounded-[1.5rem] border border-cyan-400/15 bg-slate-950/70 p-4 shadow-[0_0_32px_rgba(34,211,238,0.06)]">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-full border border-cyan-300/30 bg-cyan-300/10 px-3 py-1 text-[11px] font-black uppercase tracking-[0.2em] text-cyan-100">
                Demo Mode
              </span>
              <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] font-bold text-slate-300">
                Frontend: Vercel
              </span>
              <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] font-bold text-slate-300">
                Backend: Local FastAPI
              </span>
              <span className="rounded-full border border-violet-300/20 bg-violet-300/10 px-3 py-1 text-[11px] font-bold text-violet-100">
                Qwen-ready / mock-safe
              </span>
            </div>
            <p className="mt-2 max-w-5xl text-xs leading-5 text-slate-400">
              Live preview is deployed on Vercel. The interactive Command Center uses a local backend for the demo; Qwen-compatible orchestration is prepared with mock fallback until cloud credits are activated.
            </p>
          </div>

          <a
            href="/simulation"
            className="inline-flex shrink-0 items-center justify-center rounded-xl border border-cyan-300/25 bg-cyan-300/10 px-3 py-2 text-xs font-black text-cyan-50 transition hover:bg-cyan-300/20"
          >
            Run safe simulation →
          </a>
        </div>
      </section>
'''

pattern = r'\s*\{/\* demo-hardening-banner \*/\}\s*<section className="mb-6.*?</section>'

new_text, count = re.subn(pattern, "\n" + compact_banner, text, count=1, flags=re.S)

if count == 0:
    print("ERROR: Existing demo-hardening-banner block not found. Restoring.")
    shutil.copyfile(BACKUP, PAGE)
    sys.exit(1)

PAGE.write_text(new_text)

print("Sprint 5.1c compact dashboard demo banner applied. Running build check...")
result = run_build()
print(result.stdout)

if result.returncode != 0:
    shutil.copyfile(BACKUP, PAGE)
    print("BUILD FAILED. Dashboard restored.")
    sys.exit(result.returncode)

print("BUILD PASSED. Compact demo banner kept.")
print(f"Backup stored at {BACKUP}")
