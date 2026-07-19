"""Verify the run script exists and the app serves end-to-end over HTTP."""

import os, sys, time, threading, urllib.request, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TAURI_DIR = os.path.abspath(os.path.join(REPO, "..", "src-tauri"))


def test_run_script_exists_and_executable():
    for s in ("run.sh",):
        p = os.path.join(REPO, s)
        assert os.path.isfile(p), f"{s} missing"
        assert os.access(p, os.X_OK), f"{s} not executable"


def test_tauri_shell_present():
    assert os.path.isfile(os.path.join(TAURI_DIR, "src", "main.rs"))
    assert os.path.isfile(os.path.join(TAURI_DIR, "tauri.conf.json"))


def test_app_serves_end_to_end():
    import uvicorn
    from app.main import app
    port = 8137
    proc = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    t = threading.Thread(target=proc.run, daemon=True)
    t.start()
    base = f"http://127.0.0.1:{port}"
    for _ in range(40):
        try:
            urllib.request.urlopen(base + "/api/info", timeout=1)
            break
        except Exception:
            time.sleep(0.1)
    try:
        with urllib.request.urlopen(base + "/", timeout=3) as r:
            html = r.read().decode()
            assert "Investor" in html
        with urllib.request.urlopen(base + "/api/info", timeout=3) as r:
            info = json.load(r)
            assert "/api/top-picks" in info["endpoints"]
    finally:
        proc.should_exit = True
        t.join(timeout=5)
