from pathlib import Path
import subprocess
import shutil
import sys

ROOT = Path(".")
FRONTEND = ROOT / "frontend"
SIMULATION = FRONTEND / "src" / "app" / "simulation" / "page.tsx"
BACKUP_DIR = ROOT / "scripts" / "_backups_sprint32_simulation_density"
BACKUP = BACKUP_DIR / "simulation.page.tsx"

def run_build():
    return subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

if not SIMULATION.exists():
    print("ERROR: simulation/page.tsx not found")
    sys.exit(1)

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copyfile(SIMULATION, BACKUP)

text = SIMULATION.read_text()

# 1. Slightly tighten page spacing.
text = text.replace(
    'className="mx-auto max-w-7xl px-6 pb-16 pt-8"',
    'className="mx-auto max-w-7xl px-6 pb-12 pt-6"',
    1,
)

text = text.replace(
    'className="mb-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between"',
    'className="mb-5 flex flex-col gap-4 md:flex-row md:items-end md:justify-between"',
    1,
)

# 2. Slightly rebalance columns.
text = text.replace(
    'className="grid items-start gap-5 xl:grid-cols-[0.9fr_1.1fr_0.85fr]"',
    'className="grid items-start gap-5 xl:grid-cols-[0.86fr_1.16fr_0.88fr]"',
    1,
)

# 3. Fill the middle-column empty space with mission artifacts.
old_block = '''              <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-5">
                <h3 className="font-black text-white">Event log</h3>
                <div className="mt-4 space-y-3">
                  {eventStream.map((event) => (
                    <div
                      key={event}
                      className="rounded-2xl border border-white/10 bg-slate-950/60 p-3 font-mono text-xs text-slate-300"
                    >
                      {event}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </section>'''

new_block = '''              <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-5">
                <h3 className="font-black text-white">Event log</h3>
                <div className="mt-4 space-y-3">
                  {eventStream.map((event) => (
                    <div
                      key={event}
                      className="rounded-2xl border border-white/10 bg-slate-950/60 p-3 font-mono text-xs text-slate-300"
                    >
                      {event}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-5 grid gap-5 lg:grid-cols-[1fr_1fr]">
              <div className="rounded-3xl border border-violet-400/20 bg-violet-400/10 p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3 className="font-black text-white">Mission outcome package</h3>
                    <p className="mt-2 text-sm leading-6 text-slate-300">
                      Final artefacts produced by the incident command workflow.
                    </p>
                  </div>
                  <StatusBadge label={completed ? "ready" : "draft"} tone={completed ? "green" : "slate"} />
                </div>

                <div className="mt-4 space-y-3">
                  <DecisionLine label="Root cause" value="cache configuration drift" />
                  <DecisionLine label="Decision" value="approval-gated rollback" />
                  <DecisionLine label="Recovery proof" value={completed ? "telemetry verified" : "waiting for approval"} />
                  <DecisionLine label="Audit output" value={completed ? "postmortem generated" : "draft prepared"} />
                </div>
              </div>

              <div className="rounded-3xl border border-emerald-400/20 bg-emerald-400/10 p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3 className="font-black text-white">Judge demo checkpoints</h3>
                    <p className="mt-2 text-sm leading-6 text-slate-300">
                      What the reviewer should notice during the simulation.
                    </p>
                  </div>
                  <StatusBadge label="demo ready" tone="cyan" />
                </div>

                <div className="mt-4 space-y-3">
                  <DecisionLine label="Autopilot" value="agents advance the workflow" />
                  <DecisionLine label="Control" value="automation pauses at safety gate" />
                  <DecisionLine label="Evidence" value="each decision has linked signals" />
                  <DecisionLine label="Outcome" value="recovery and postmortem are visible" />
                </div>
              </div>
            </div>
          </section>'''

if old_block not in text:
    print("ERROR: event log block not found. Restoring.")
    shutil.copyfile(BACKUP, SIMULATION)
    sys.exit(1)

text = text.replace(old_block, new_block, 1)

SIMULATION.write_text(text)

print("Sprint 3.2 simulation density patch applied. Running build check...")
result = run_build()
print(result.stdout)

if result.returncode != 0:
    shutil.copyfile(BACKUP, SIMULATION)
    print("BUILD FAILED. Simulation restored.")
    sys.exit(result.returncode)

print("BUILD PASSED. Simulation density patch kept.")
print(f"Backup stored at {BACKUP}")
