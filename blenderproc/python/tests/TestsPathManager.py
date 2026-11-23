""" TestsPathManager keeps track of all used paths in the tests and allows setting them via environment variables """

import os
from os.path import abspath, join, exists
from blenderproc.python.utility.Utility import resolve_path, Utility

_FETCH_SCRIPT = "blenderproc/scripts/fetch_test_assets.py"


class TestsPathManager:
    """
    The TestsPathManager keeps track of all used paths in the tests and allows setting them via environment variables.
    To allow testing in environments, where the paths are not the default ones.

    Optional asset directories are resolved when a test reads them. Importing this module does not require the
    assets to be present. A missing directory raises FileNotFoundError naming the fetch script.
    """

    def __init__(self):
        self._main_folder = Utility.blenderproc_root

        # for the default resource folder, this one should always be available
        self.example_resources = abspath(join(self._main_folder, "examples/resources"))

    @property
    def cc_materials(self) -> str:
        """ Directory of ambientCG materials. Fetched by blenderproc/scripts/fetch_test_assets.py. """
        return self._require("cc_materials", "resources/cctextures", "BP_CC_MATERIALS_PATH")

    @property
    def haven(self) -> str:
        """ Directory of Poly Haven assets. Fetched by blenderproc/scripts/fetch_test_assets.py. """
        return self._require("haven", "resources/haven", "BP_HAVEN_PATH")

    def _require(self, param_name: str, default_path: str, environment_key: str) -> str:
        """
        Returns the default path when it exists, otherwise the path in environment_key.
        Raises FileNotFoundError naming the fetch script when neither exists.

        :param param_name: Name of the asset directory
        :param default_path: Default path used for this parameter
        :param environment_key: Environment key which has to be set if the default path does not exist
        """
        candidate = abspath(join(self._main_folder, default_path))
        if not exists(candidate) and environment_key in os.environ:
            candidate = resolve_path(os.environ[environment_key])
        if not exists(candidate):
            raise FileNotFoundError(
                f"Missing {param_name} at '{candidate}'. "
                f"{environment_key} is unset or does not point at an existing directory, "
                f"and the default path does not exist: {default_path}. "
                f"Fetch the pinned CC0 test assets with: python {_FETCH_SCRIPT}"
            )
        return candidate


test_path_manager = TestsPathManager()
