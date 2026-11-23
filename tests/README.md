# Unit tests

The loader tests need a few CC0 files. The full ambientCG catalog and the full Poly Haven texture, HDRI, and model libraries are multiple gigabytes, and no test loads an HDRI. Fetch the pinned subset (each file's sha256 is checked before use), then run:

```
python3 blenderproc/scripts/fetch_test_assets.py
python3 cli.py run tests/run_all.py
```

`BP_CC_MATERIALS_PATH` and `BP_HAVEN_PATH` still override those directories when the default `resources/` paths are absent. A missing directory raises `FileNotFoundError` naming `blenderproc/scripts/fetch_test_assets.py` when a test reads it, rather than while the test module is imported.
