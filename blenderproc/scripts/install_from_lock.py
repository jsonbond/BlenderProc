"""Install requirements.lock without fetching unpinned build tools.

progressbar publishes an sdist and no wheel. The locked install uses
``--no-build-isolation`` so pip cannot download a build backend on its own.
Pip generates that sdist's metadata before it installs anything else in the
lock, including setuptools. This script therefore installs the setuptools
wheel already pinned in requirements.lock, then installs the full lock.

Both steps pass ``--require-hashes``. The first step also passes
``--only-binary=:all:`` so the build backend itself is not built from an sdist.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LOCK_PATH = REPO_ROOT / "requirements.lock"
# Present in the lock today: setuptools. wheel is included when a future
# re-lock pins it, because some legacy sdists import it while building.
BUILD_BACKENDS = ("setuptools", "wheel")


def requirement_name(line: str) -> str:
    name = line.strip().split("==", 1)[0].split("[", 1)[0]
    return name.rstrip("\\").strip()


def extract_build_backends(lock_text: str) -> str:
    """Return the setuptools and wheel stanzas, hashes included."""
    selected = []
    capture = False
    for line in lock_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith((" ", "\t")):
            capture = requirement_name(line) in BUILD_BACKENDS
        if capture:
            selected.append(line)
    names = {requirement_name(line) for line in selected if "==" in line and not line.startswith((" ", "\t"))}
    missing = [name for name in ("setuptools",) if name not in names]
    if missing:
        raise SystemExit(f"{LOCK_PATH.name} is missing a hash pin for {', '.join(missing)}")
    return "\n".join(selected) + "\n"


def pip_install(arguments: list[str]) -> None:
    subprocess.run([sys.executable, "-m", "pip", "install", *arguments], check=True)


def main() -> None:
    lock_text = LOCK_PATH.read_text()
    with tempfile.TemporaryDirectory() as tmp:
        backend_lock = Path(tmp) / "build-backends.lock"
        backend_lock.write_text(extract_build_backends(lock_text))
        pip_install([
            "--require-hashes",
            "--no-deps",
            "--only-binary=:all:",
            "-r",
            str(backend_lock),
        ])
    pip_install([
        "--require-hashes",
        "--no-build-isolation",
        "-r",
        str(LOCK_PATH),
    ])


if __name__ == "__main__":
    main()
