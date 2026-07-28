import React, { useState } from "react";
import { FolderPlus, Code, Terminal, Layers, X, CheckCircle } from "lucide-react";
import { api } from "../../api/client";

interface ProjectScaffolderModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ProjectScaffolderModal: React.FC<ProjectScaffolderModalProps> = ({ isOpen, onClose }) => {
  const [template, setTemplate] = useState("python-app");
  const [projectName, setProjectName] = useState("my-new-app");
  const [targetDir, setTargetDir] = useState("");
  const [initGit, setInitGit] = useState(true);
  const [creating, setCreating] = useState(false);
  const [resultMessage, setResultMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleCreate = async () => {
    if (!projectName.trim()) return;
    setCreating(true);
    setResultMessage(null);
    try {
      const res = await api.scaffoldProject({
        template,
        project_name: projectName,
        target_directory: targetDir.trim() || undefined,
        initialize_git: initGit,
      });
      if (res.success) {
        setResultMessage(`Workspace created at ${res.project_path} (${res.files_created.length} files)`);
      }
    } catch (e: any) {
      setResultMessage(`Error: ${e.message}`);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="glass-card modal-content">
        <div className="modal-header">
          <div className="title-box">
            <FolderPlus size={22} color="var(--accent-cyan)" />
            <h3>1-Click Project Workspace Scaffolder</h3>
          </div>
          <button className="close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="form-group">
          <label>Select Project Template:</label>
          <div className="template-grid">
            <button
              className={`template-btn ${template === "python-app" ? "active" : ""}`}
              onClick={() => setTemplate("python-app")}
            >
              <Code size={18} />
              <div className="text">
                <strong>Python App</strong>
                <span>.venv + pyproject.toml + pytest</span>
              </div>
            </button>

            <button
              className={`template-btn ${template === "web-react" ? "active" : ""}`}
              onClick={() => setTemplate("web-react")}
            >
              <Layers size={18} />
              <div className="text">
                <strong>React + Vite</strong>
                <span>React 18 + TypeScript + Vite</span>
              </div>
            </button>

            <button
              className={`template-btn ${template === "rust-cli" ? "active" : ""}`}
              onClick={() => setTemplate("rust-cli")}
            >
              <Terminal size={18} />
              <div className="text">
                <strong>Rust CLI</strong>
                <span>Cargo binary + src/main.rs</span>
              </div>
            </button>

            <button
              className={`template-btn ${template === "go-service" ? "active" : ""}`}
              onClick={() => setTemplate("go-service")}
            >
              <Code size={18} />
              <div className="text">
                <strong>Go Service</strong>
                <span>go.mod + main.go + Makefile</span>
              </div>
            </button>
          </div>
        </div>

        <div className="form-group">
          <label>Project Name:</label>
          <input
            type="text"
            className="text-input"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            placeholder="e.g. my-awesome-app"
          />
        </div>

        <div className="form-group">
          <label>Destination Directory (Optional):</label>
          <input
            type="text"
            className="text-input"
            value={targetDir}
            onChange={(e) => setTargetDir(e.target.value)}
            placeholder="Leave empty for default directory"
          />
        </div>

        <div className="checkbox-group">
          <label>
            <input type="checkbox" checked={initGit} onChange={(e) => setInitGit(e.target.checked)} />
            <span>Automatically run `git init`</span>
          </label>
        </div>

        {resultMessage && (
          <div className="result-banner">
            <CheckCircle size={16} /> {resultMessage}
          </div>
        )}

        <div className="modal-actions">
          <button className="btn btn-secondary" onClick={onClose} disabled={creating}>
            Cancel
          </button>
          <button className="btn btn-primary" onClick={handleCreate} disabled={creating}>
            {creating ? "Scaffolding Workspace..." : "Create Project Workspace"}
          </button>
        </div>
      </div>

      <style>{`
        .modal-overlay {
          position: fixed;
          top: 0; left: 0; right: 0; bottom: 0;
          background: rgba(0, 0, 0, 0.7);
          backdrop-filter: blur(8px);
          display: flex; align-items: center; justify-content: center;
          z-index: 200;
        }
        .modal-content {
          width: 580px; max-width: 90vw;
          display: flex; flex-direction: column; gap: 1.25rem;
          box-shadow: var(--shadow-glow);
        }
        .modal-header {
          display: flex; align-items: center; justify-content: space-between;
        }
        .title-box {
          display: flex; align-items: center; gap: 0.6rem;
        }
        .close-btn {
          background: transparent; border: none; color: var(--text-muted); cursor: pointer;
        }
        .form-group {
          display: flex; flex-direction: column; gap: 0.4rem;
        }
        .form-group label {
          font-size: 0.82rem; color: var(--text-secondary); font-weight: 600;
        }
        .template-grid {
          display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem;
        }
        .template-btn {
          background: var(--bg-dark);
          border: 1px solid var(--border-glass);
          border-radius: var(--radius-sm);
          padding: 0.75rem;
          display: flex; align-items: center; gap: 0.75rem;
          cursor: pointer; color: var(--text-primary); text-align: left;
          transition: all 0.2s;
        }
        .template-btn.active {
          border-color: var(--accent-cyan);
          background: hsla(185, 85%, 50%, 0.1);
        }
        .template-btn .text {
          display: flex; flex-direction: column;
        }
        .template-btn strong { font-size: 0.85rem; }
        .template-btn span { font-size: 0.72rem; color: var(--text-muted); }
        .text-input {
          background: var(--bg-dark);
          border: 1px solid var(--border-glass);
          border-radius: var(--radius-sm);
          padding: 0.6rem 0.8rem;
          color: var(--text-primary);
          font-size: 0.9rem;
        }
        .checkbox-group label {
          display: flex; align-items: center; gap: 0.5rem;
          font-size: 0.85rem; color: var(--text-secondary); cursor: pointer;
        }
        .result-banner {
          background: hsla(155, 85%, 45%, 0.2);
          color: var(--accent-emerald);
          padding: 0.75rem; border-radius: var(--radius-sm);
          font-size: 0.85rem; display: flex; align-items: center; gap: 0.5rem;
        }
        .modal-actions {
          display: flex; justify-content: flex-end; gap: 0.75rem;
        }
      `}</style>
    </div>
  );
};
