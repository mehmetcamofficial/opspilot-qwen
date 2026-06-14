from pathlib import Path
import subprocess
import shutil
import sys
import re

ROOT = Path(".")
FRONTEND = ROOT / "frontend"
PAGE = FRONTEND / "src" / "app" / "page.tsx"
VIDEO = FRONTEND / "public" / "opspilot-ambient-bg.webm"
BACKUP_DIR = ROOT / "scripts" / "_backups_sprint54_landing_video"
BACKUP = BACKUP_DIR / "landing.page.tsx"

def run_build():
    return subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

if not PAGE.exists():
    print("ERROR: landing page not found")
    sys.exit(1)

if not VIDEO.exists():
    print("ERROR: frontend/public/opspilot-ambient-bg.webm not found")
    sys.exit(1)

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copyfile(PAGE, BACKUP)

text = PAGE.read_text()

text = re.sub(
    r'\s*\{/\* landing-ambient-motion-layer \*/\}.*?<style jsx>\{`.*?`\}</style>',
    '',
    text,
    count=1,
    flags=re.S,
)

if "landing-video-background-layer" in text:
    print("Video background layer already exists. No change needed.")
    sys.exit(0)

video_layer = '''
      {/* landing-video-background-layer */}
      <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
        <video
          className="absolute inset-0 h-full w-full object-cover opacity-[0.24]"
          src="/opspilot-ambient-bg.webm"
          autoPlay
          muted
          loop
          playsInline
          preload="metadata"
          aria-hidden="true"
        />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_28%,rgba(34,211,238,0.18),transparent_34%),radial-gradient(circle_at_86%_18%,rgba(167,139,250,0.18),transparent_36%)]" />
        <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(2,6,23,0.42),rgba(2,6,23,0.66)_48%,rgba(2,6,23,0.78))]" />
        <div className="absolute inset-0 bg-[linear-gradient(to_bottom,rgba(2,6,23,0.10),rgba(2,6,23,0.72)_72%,rgba(2,6,23,0.92))]" />
      </div>
'''

return_idx = text.find("return (")
if return_idx == -1:
    print("ERROR: Could not find return (. Restoring.")
    shutil.copyfile(BACKUP, PAGE)
    sys.exit(1)

class_match = re.search(r'className="([^"]*)"', text[return_idx:])
if not class_match:
    print("ERROR: Could not find root className after return. Restoring.")
    shutil.copyfile(BACKUP, PAGE)
    sys.exit(1)

start = return_idx + class_match.start(1)
end = return_idx + class_match.end(1)
classes = text[start:end]

for needed in ["relative", "overflow-hidden"]:
    if needed not in classes.split():
        classes += " " + needed

text = text[:start] + classes + text[end:]

after_open = text.find(">", end)
if after_open == -1:
    print("ERROR: Could not find root opening tag close. Restoring.")
    shutil.copyfile(BACKUP, PAGE)
    sys.exit(1)

text = text[:after_open + 1] + video_layer + text[after_open + 1:]

PAGE.write_text(text)

print("Sprint 5.4 landing video background applied. Running build check...")
result = run_build()
print(result.stdout)

if result.returncode != 0:
    shutil.copyfile(BACKUP, PAGE)
    print("BUILD FAILED. Landing restored.")
    sys.exit(result.returncode)

print("BUILD PASSED. Landing video background kept.")
print(f"Backup stored at {BACKUP}")
