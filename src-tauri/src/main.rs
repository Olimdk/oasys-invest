// Prevents an extra console window on Windows in release.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::{Command, Child, Stdio};
use std::sync::{Arc, Mutex};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::{PathBuf};
use tauri::Manager;

struct Engine(Arc<Mutex<Option<Child>>>);

#[tauri::command]
fn engine_status(state: tauri::State<Engine>) -> String {
    let mut guard = state.0.lock().unwrap();
    let status = match guard.as_mut() {
        Some(child) => match child.try_wait() {
            Ok(Some(_)) => "exited",
            _ => "running",
        },
        None => "not_started",
    };
    status.to_string()
}

fn log(msg: &str) {
    if let Ok(mut f) = OpenOptions::new().create(true).append(true).open("/tmp/tauri_engine.log") {
        let _ = writeln!(f, "{}", msg);
    }
}

fn find_backend_dir(app: &tauri::AppHandle) -> Option<PathBuf> {
    let exe = std::env::current_exe().ok()?;
    let exe_dir = exe.parent()?.to_path_buf();

    let mut candidates: Vec<PathBuf> = Vec::new();
    // 1. Bundled next to the executable (release / AppImage / deb resources).
    candidates.push(exe_dir.join("backend"));
    // 2. Repo source tree: <repo>/backend when running from src-tauri/target/(debug|release).
    candidates.push(exe_dir.join("../../../backend"));
    // 3. Tauri resource directory.
    if let Some(res) = app.path().resource_dir().ok() {
        candidates.push(res.join("backend"));
    }

    for c in &candidates {
        if c.join(".venv").join("bin").join("python").exists() {
            return Some(c.clone());
        }
    }
    candidates.into_iter().next()
}

fn spawn_engine(app: &tauri::AppHandle) -> Option<Child> {
    let backend_dir = find_backend_dir(app)?;
    let python = backend_dir.join(".venv").join("bin").join("python");

    log(&format!("spawning: {} -m app.main in {}", python.display(), backend_dir.display()));

    match Command::new(&python)
        .arg("-m").arg("app.main")
        .arg("--host").arg("127.0.0.1")
        .arg("--port").arg("8000")
        .current_dir(&backend_dir)
        .stdout(Stdio::null())
        .stderr(Stdio::piped())
        .spawn()
    {
        Ok(mut child) => {
            if let Some(mut stderr) = child.stderr.take() {
                std::thread::spawn(move || {
                    use std::io::Read;
                    let mut buf = String::new();
                    let _ = stderr.read_to_string(&mut buf);
                    if !buf.is_empty() {
                        log(&format!("ENGINE STDERR: {}", buf));
                    }
                });
            }
            Some(child)
        }
        Err(e) => {
            log(&format!("SPAWN ERROR: {}", e));
            None
        }
    }
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            let child = spawn_engine(app.handle());
            app.manage(Engine(Arc::new(Mutex::new(child))));
            std::thread::sleep(std::time::Duration::from_millis(1500));
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![engine_status])
        .run(tauri::generate_context!())
        .expect("error while running OASYS Invest");
}
