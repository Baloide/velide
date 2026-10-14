"""Build and verify the bundled service, Electron app, installer and portable ZIP."""

import hashlib
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if sys.platform != "win32":
    raise SystemExit("Build the Windows package on Windows.")
subprocess.run([sys.executable, str(ROOT / "scripts/set_version.py"), "--check"], check=True)
subprocess.run([sys.executable, str(ROOT / "scripts/create_icon.py")], check=True)
subprocess.run(
    [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--console",
        "--name",
        "VelideService",
        "--distpath",
        str(ROOT / "build/service"),
        "--workpath",
        str(ROOT / "build/service-work"),
        "--specpath",
        str(ROOT / "build"),
        "--paths",
        str(ROOT / "backend"),
        "--add-data",
        f"{ROOT / 'backend/app/static'}:app/static",
        "--collect-data",
        "docx",
        "--hidden-import",
        "uvicorn.logging",
        "--hidden-import",
        "uvicorn.loops.asyncio",
        "--hidden-import",
        "uvicorn.protocols.http.h11_impl",
        "--hidden-import",
        "uvicorn.lifespan.on",
        str(ROOT / "desktop/service.py"),
    ],
    check=True,
    cwd=ROOT,
)
electron = ROOT / "desktop/electron"
subprocess.run(["npm.cmd", "ci", "--no-audit", "--no-fund"], cwd=electron, check=True)
subprocess.run(["npm.cmd", "run", "package"], cwd=electron, check=True)
app_folder = ROOT / "dist/electron/win-unpacked"
exe = app_folder / "Velide.exe"
result = ROOT / "build/electron-smoke.txt"
result.unlink(missing_ok=True)
environment = os.environ.copy()
environment.pop("ELECTRON_RUN_AS_NODE", None)
subprocess.run(
    [str(exe), "--smoke-test", "--smoke-result", str(result)],
    check=True,
    timeout=120,
    env=environment,
)
if not result.is_file() or not result.read_text().startswith("OK:"):
    raise SystemExit("Electron smoke test failed; no portable ZIP created.")
archive = ROOT / "dist/Velide-Windows.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
    for file in app_folder.rglob("*"):
        if file.is_file():
            output.write(file, file.relative_to(app_folder))
    for file in [
        ROOT / "desktop/Install.cmd",
        ROOT / "desktop/Install.ps1",
        ROOT / "desktop/assets/velide.ico",
        ROOT / "README.md",
        ROOT / "ARCHITECTURE.md",
        ROOT / "RELEASING.md",
        ROOT / "CHANGELOG.md",
    ]:
        output.write(file, file.name)
    for file in (ROOT / "branding").iterdir():
        if file.is_file():
            output.write(file, f"branding/{file.name}")
setup = ROOT / "dist/Velide-Setup.exe"
shutil.copy2(ROOT / "dist/electron/Velide-Setup.exe", setup)
for file in [archive, setup]:
    with file.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    file.with_name(file.name + ".sha256").write_text(f"{digest}  {file.name}\n", encoding="utf-8")
verification = ROOT / "build/electron-install-verification"
package, installed, desktop = [verification / name for name in ("package", "app", "desktop")]
with zipfile.ZipFile(archive) as output:
    output.extractall(package)
subprocess.run(
    [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(package / "Install.ps1"),
        "-InstallDirectory",
        str(installed),
        "-DesktopDirectory",
        str(desktop),
    ],
    check=True,
    timeout=60,
)
if (
    not (installed / "resources/backend/VelideService.exe").is_file()
    or not (desktop / "Velide.lnk").is_file()
):
    raise SystemExit("Portable desktop installation verification failed.")
print(f"Built and verified: {setup} and {archive}")
