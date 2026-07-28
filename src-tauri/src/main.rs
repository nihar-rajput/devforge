// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::{Child, Command};
use std::sync::Mutex;
use tauri::{Manager, RunEvent};

struct SidecarState {
    child: Mutex<Option<Child>>,
}

fn spawn_fastapi_backend() -> Option<Child> {
    println!("[DevForge Tauri] Spawning FastAPI backend sidecar...");

    #[cfg(target_os = "windows")]
    let child = Command::new("python")
        .args(["-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8000"])
        .current_dir("../backend")
        .spawn();

    #[cfg(not(target_os = "windows"))]
    let child = Command::new("python3")
        .args(["-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8000"])
        .current_dir("../backend")
        .spawn();

    match child {
        Ok(c) => {
            println!("[DevForge Tauri] FastAPI backend spawned with PID {}", c.id());
            Some(c)
        }
        Err(e) => {
            eprintln!("[DevForge Tauri] Failed to spawn FastAPI sidecar: {}", e);
            None
        }
    }
}

fn main() {
    let sidecar_child = spawn_fastapi_backend();

    tauri::Builder::default()
        .manage(SidecarState {
            child: Mutex::new(sidecar_child),
        })
        .setup(|app| {
            println!("[DevForge Tauri] Application setup complete.");
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building tauri application")
        .run(|app_handle, event| match event {
            RunEvent::ExitRequested { .. } => {
                println!("[DevForge Tauri] App exit requested, shutting down sidecar...");
                let state = app_handle.state::<SidecarState>();
                if let Ok(mut lock) = state.child.lock() {
                    if let Some(mut child) = lock.take() {
                        let _ = child.kill();
                        println!("[DevForge Tauri] FastAPI sidecar process terminated.");
                    }
                }
            }
            _ => {}
        });
}
