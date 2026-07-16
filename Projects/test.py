import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

TARGET_PYTHON_VERSION = "3.12.7"
DEFAULT_INSTALL_DIR = Path(r"C:\Python312")


def get_python_candidate_paths() -> list[str]:
    candidates = []

    if shutil.which("python"):
        candidates.append("python")
    if shutil.which("py"):
        candidates.append("py")

    if sys.executable:
        candidates.append(sys.executable)

    return list(dict.fromkeys(candidates))


def get_python_version(executable: str) -> tuple[str, tuple[int, int, int]] | None:
    try:
        result = subprocess.run(
            [executable, "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None

    output = (result.stdout or result.stderr).strip()
    if not output.startswith("Python "):
        return None

    version_text = output.split()[1]
    parts = version_text.split(".")
    try:
        version_tuple = tuple(int(part) for part in parts[:3])
    except ValueError:
        return None

    return output, version_tuple


def find_installed_python() -> tuple[str, tuple[int, int, int]] | None:
    for executable in get_python_candidate_paths():
        version_info = get_python_version(executable)
        if version_info is not None:
            return executable, version_info[1]
    return None


def download_installer(version: str) -> Path:
    architecture = platform.machine().upper()
    if architecture in ("AMD64", "X86_64", "X64"):
        filename = f"python-{version}-amd64.exe"
    elif architecture in ("ARM64", "AARCH64"):
        filename = f"python-{version}-arm64.exe"
    else:
        filename = f"python-{version}.exe"

    url = f"https://www.python.org/ftp/python/{version}/{filename}"
    dest = Path(tempfile.gettempdir()) / filename

    if dest.exists():
        print(f"Installer already downloaded: {dest}")
        return dest

    print(f"Downloading Python {version} installer from {url}...")
    urllib.request.urlretrieve(url, dest)
    print(f"Downloaded to {dest}")
    return dest


def install_python(installer_path: Path, target_dir: Path) -> None:
    target_dir = target_dir.resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    install_args = [
        str(installer_path),
        "/quiet",
        "InstallAllUsers=0",
        "PrependPath=1",
        f"TargetDir={target_dir}",
    ]

    print(f"Installing Python to {target_dir}...")
    subprocess.run(install_args, check=True)
    print("Installation complete.")


def main() -> None:
    current_python = find_installed_python()
    if current_python is not None:
        executable, version_tuple = current_python
        print(f"Found Python executable: {executable}")
        print(f"Version: {version_tuple[0]}.{version_tuple[1]}.{version_tuple[2]}")
        return

    print("No usable Python installation was found on PATH.")
    print(f"Downloading Python {TARGET_PYTHON_VERSION} and installing to {DEFAULT_INSTALL_DIR}")

    installer = download_installer(TARGET_PYTHON_VERSION)
    install_python(installer, DEFAULT_INSTALL_DIR)

    print("Python should now be installed. Restart your terminal to pick up the updated PATH.")


if __name__ == "__main__":
    if platform.system() != "Windows":
        print("This installer script is intended only for Windows.")
        sys.exit(1)

    main()
