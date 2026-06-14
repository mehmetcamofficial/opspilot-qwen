from pathlib import Path
import subprocess
import shutil
import sys

ROOT = Path(".")
FRONTEND = ROOT / "frontend"
ADMIN = FRONTEND / "src" / "app" / "admin" / "page.tsx"
BACKUP_DIR = ROOT / "scripts" / "_backups_sprint25_hydration"
BACKUP = BACKUP_DIR / "admin.page.tsx"

def run_build():
    return subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

if not ADMIN.exists():
    print("ERROR: admin/page.tsx not found")
    sys.exit(1)

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copyfile(ADMIN, BACKUP)

text = ADMIN.read_text()

old = '''    auditLog: [
      createLog("Governance console initialized"),
      createLog("Mock Qwen mode selected to avoid pay-as-you-go usage"),
    ],'''

new = '''    auditLog: [
      {
        id: "audit-initialized",
        actor: "system",
        message: "Governance console initialized",
        timestamp: "initial state",
      },
      {
        id: "audit-mock-mode",
        actor: "system",
        message: "Mock Qwen mode selected to avoid pay-as-you-go usage",
        timestamp: "initial state",
      },
    ],'''

if old not in text:
    print("ERROR: Could not find initial auditLog block. No changes applied.")
    sys.exit(1)

text = text.replace(old, new, 1)
ADMIN.write_text(text)

print("Hydration fix applied. Running build check...")
result = run_build()
print(result.stdout)

if result.returncode != 0:
    shutil.copyfile(BACKUP, ADMIN)
    print("BUILD FAILED. Admin page restored.")
    sys.exit(result.returncode)

print("BUILD PASSED. Hydration fix kept.")
print(f"Backup stored at {BACKUP}")
