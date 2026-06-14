from pathlib import Path
import subprocess
import shutil
import sys
import re

ROOT = Path(".")
FRONTEND = ROOT / "frontend"
PAGE = FRONTEND / "src" / "app" / "knowledge-graph" / "page.tsx"
BACKUP_DIR = ROOT / "scripts" / "_backups_sprint52_reasoning_graph_context"
BACKUP = BACKUP_DIR / "knowledge_graph.page.tsx"

def run_build():
    return subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

if not PAGE.exists():
    print("ERROR: knowledge-graph/page.tsx not found")
    sys.exit(1)

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copyfile(PAGE, BACKUP)

text = PAGE.read_text()

new_sentence = (
    "Investigating: checkout API latency after a cache configuration change. "
    "Active path: deployment context → metric anomaly → hypothesis → approval gate."
)

old_sentences = [
    "Relation depth expands context; connection lines preserve the approval-to-recovery path.",
    "Relation depth expands context; clean connection lines preserve the full approval-to-recovery path.",
    "Relation depth expands context; the human gate preserves downstream remediation, recovery, and postmortem.",
    "Arrows stop before node labels. The approval gate highlights where automation pauses for a human decision.",
]

changed = False

for old in old_sentences:
    if old in text:
        text = text.replace(old, new_sentence, 1)
        changed = True
        print(f"Patched existing sentence: {old}")
        break

if not changed:
    pattern = r'(<h1[^>]*>\s*Human-controlled neural canvas\s*</h1>\s*)<p[^>]*>.*?</p>'
    replacement = (
        r'\1'
        '<p className="mt-1 text-sm text-slate-400">'
        + new_sentence +
        '</p>'
    )
    text, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count == 0:
        print("ERROR: Could not find graph header paragraph. Restoring.")
        shutil.copyfile(BACKUP, PAGE)
        sys.exit(1)
    changed = True
    print("Patched graph header paragraph via fallback.")

PAGE.write_text(text)

print("Sprint 5.2 reasoning graph context header applied. Running build check...")
result = run_build()
print(result.stdout)

if result.returncode != 0:
    shutil.copyfile(BACKUP, PAGE)
    print("BUILD FAILED. Reasoning Graph restored.")
    sys.exit(result.returncode)

print("BUILD PASSED. Reasoning Graph context header kept.")
print(f"Backup stored at {BACKUP}")
