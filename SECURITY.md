# Dependency installs

Development, CI, and local use of this repository install Python dependencies from `requirements.lock` only.

- The lock pins direct and transitive dependencies and includes hashes.
- `uv.toml` sets `exclude-newer = "7 days"`. Keep that cooldown on every re-lock so a package published in the last 7 days cannot be selected.
- `setup.py` stays the packaging manifest. Install this checkout without resolving those unpinned requirements:

```bash
python blenderproc/scripts/install_from_lock.py
python -m pip install -e . --no-deps --no-build-isolation
```

`progressbar` is sdist-only. `--no-build-isolation` keeps the install from fetching unpinned build tools, and pip builds that sdist before it installs the rest of the lock. `install_from_lock.py` first installs the setuptools wheel already hash-pinned in `requirements.lock` (`--require-hashes --only-binary=:all:`), then installs the lock with `--require-hashes --no-build-isolation`. Do not `pip install --upgrade pip` unless that pip version is hash-pinned.

To update the lock, review the diff, then recompile:

```bash
uv pip compile requirements.in --universal --generate-hashes --config-file uv.toml -o requirements.lock
```

CI fails when that command does not reproduce `requirements.lock`.
