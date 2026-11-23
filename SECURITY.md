# Dependency installs

Development, CI, and local use of this repository install Python dependencies from `requirements.lock` only.

- The lock pins direct and transitive dependencies and includes hashes.
- `uv.toml` sets `exclude-newer = "7 days"`. Keep that cooldown on every re-lock so a package published in the last 7 days cannot be selected.
- `setup.py` stays the packaging manifest. Install this checkout without resolving those unpinned requirements:

```bash
python -m pip install --require-hashes --no-build-isolation -r requirements.lock
python -m pip install -e . --no-deps --no-build-isolation
```

`--no-build-isolation` keeps the install from fetching unpinned build tools. Do not `pip install --upgrade pip` unless that pip version is hash-pinned.

To update the lock, review the diff, then recompile:

```bash
uv pip compile requirements.in --universal --generate-hashes --config-file uv.toml -o requirements.lock
```

CI fails when that command does not reproduce `requirements.lock`.
