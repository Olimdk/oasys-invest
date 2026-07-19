"""Verify the desktop-app packaging (Tauri shell + install script) is present."""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TAURI = os.path.join(REPO, "..", "src-tauri")


def test_install_script_exists_and_executable():
    p = os.path.join(REPO, "..", "install.sh")
    assert os.path.isfile(p), "install.sh missing at repo root"
    assert os.access(p, os.X_OK), "install.sh not executable"


def test_tauri_config_exists():
    p = os.path.join(TAURI, "tauri.conf.json")
    assert os.path.isfile(p), "tauri.conf.json missing"
    txt = open(p).read()
    assert "com.oasys.invest" in txt
    assert "backend" in txt or "resources" in txt


def test_tauri_main_spawns_engine():
    p = os.path.join(TAURI, "src", "main.rs")
    assert os.path.isfile(p)
    txt = open(p).read()
    assert "app.main" in txt
    assert "spawn_engine" in txt
