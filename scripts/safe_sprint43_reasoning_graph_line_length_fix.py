from pathlib import Path
import subprocess
import shutil
import sys
import re

ROOT = Path(".")
FRONTEND = ROOT / "frontend"
PAGE = FRONTEND / "src" / "app" / "knowledge-graph" / "page.tsx"
BACKUP_DIR = ROOT / "scripts" / "_backups_sprint43_reasoning_graph_line_length"
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

text, radius_count = re.subn(
    r"  const radius = [0-9.]+;",
    "  const radius = 8.6;",
    text,
    count=1,
)

if radius_count == 0:
    print("ERROR: edgePath radius not found. Restoring.")
    shutil.copyfile(BACKUP, PAGE)
    sys.exit(1)

# Slightly stronger active lines after removing arrowheads.
text = text.replace(
    'strokeWidth={humanGate ? 0.72 : direct ? 0.58 : active ? 0.52 : 0.26}',
    'strokeWidth={humanGate ? 0.78 : direct ? 0.62 : active ? 0.56 : 0.28}',
)

PAGE.write_text(text)

print("Sprint 4.3 reasoning graph line length fix applied. Running build check...")
result = run_build()
print(result.stdout)

if result.returncode != 0:
    shutil.copyfile(BACKUP, PAGE)
    print("BUILD FAILED. Reasoning Graph restored.")
    sys.exit(result.returncode)

print("BUILD PASSED. Line length fix kept.")
print(f"Backup stored at {BACKUP}")
