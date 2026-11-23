"""Fetch the CC0 files the unit tests load, and check each sha256 before use.

The full ambientCG catalog and the full Poly Haven texture, HDRI, and model
libraries are multiple gigabytes. The unit tests only name three ambientCG
materials (Metal001, Fabric004, Wood039) and one Poly Haven texture
(terrain_red_01). No test loads an HDRI, so none is fetched. Pins live in
test_assets.lock.json next to this script.
"""

import argparse
import hashlib
import json
import shutil
import urllib.request
import zipfile
from pathlib import Path

LOCK_PATH = Path(__file__).resolve().parent / "test_assets.lock.json"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO_ROOT / "resources"
DEFAULT_CACHE = DEFAULT_OUTPUT / ".test-asset-cache"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_suffix(dest.suffix + ".partial")
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=180) as response, partial.open("wb") as handle:
        shutil.copyfileobj(response, handle)
    partial.replace(dest)


def cached_blob(url: str, expected: str, cache: Path) -> Path:
    if len(expected) != 64 or any(char not in "0123456789abcdef" for char in expected):
        raise SystemExit(f"Invalid sha256 pin for {url}")
    blob = cache / expected
    if blob.exists():
        actual = sha256_file(blob)
        if actual != expected:
            blob.unlink()
        else:
            return blob
    print(f"download {url}")
    download(url, blob)
    actual = sha256_file(blob)
    if actual != expected:
        blob.unlink()
        raise SystemExit(f"sha256 mismatch for {url}: got {actual}, pin is {expected}. Refusing to use it.")
    return blob


def safe_extract(blob: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    root = dest.resolve()
    with zipfile.ZipFile(blob) as archive:
        for info in archive.infolist():
            name = info.filename
            if name.endswith("/"):
                continue
            target = (dest / name).resolve()
            if target != root and root not in target.parents:
                raise SystemExit(f"Refusing to extract {name}")
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as src, target.open("wb") as out:
                shutil.copyfileobj(src, out)


def install_entry(entry: dict, cache: Path, output: Path) -> int:
    url = entry["url"]
    expected = entry["sha256"]
    blob = cached_blob(url, expected, cache)
    size = blob.stat().st_size
    if "unpack_to" in entry:
        dest = output / entry["unpack_to"]
        safe_extract(blob, dest)
        for name in entry.get("require", []):
            if not (dest / name).is_file():
                raise SystemExit(f"Unpacked {url} is missing {name}. Not using it.")
        print(f"verified {size} bytes -> {entry['unpack_to']}")
    elif "path" in entry:
        dest = output / entry["path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(blob, dest)
        if sha256_file(dest) != expected:
            dest.unlink()
            raise SystemExit(f"Copy of {url} failed the sha256 check. Not using it.")
        print(f"verified {size} bytes -> {entry['path']}")
    else:
        raise SystemExit(f"Lock entry for {url} needs unpack_to or path.")
    return size


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch pinned CC0 files for the unit tests.")
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE, help="Directory of hash-named downloads.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="resources directory (cctextures/ and haven/ are created here).")
    args = parser.parse_args()
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    args.cache.mkdir(parents=True, exist_ok=True)
    total = 0
    for entry in lock["files"]:
        total += install_entry(entry, args.cache, args.output)
    print(f"fetched {len(lock['files'])} files, {total} bytes")


if __name__ == "__main__":
    main()
