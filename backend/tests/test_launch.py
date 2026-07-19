"""Verify the one-command launcher exists and the app imports cleanly."""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import main as app_main


def test_run_script_exists_and_executable():
    path = os.path.join(os.path.dirname(__file__), "..", "run.sh")
    assert os.path.isfile(path), "run.sh missing"
    assert os.access(path, os.X_OK), "run.sh not executable"


def test_app_imports_with_fastapi_instance():
    assert hasattr(app_main, "app")
    assert app_main.app is not None
