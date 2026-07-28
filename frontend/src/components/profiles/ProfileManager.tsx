import React, { useState } from "react";
import { Camera, Download, Upload, FileText } from "lucide-react";
import { api } from "../../api/client";

export const ProfileManager: React.FC = () => {
  const [snapshotName, setSnapshotName] = useState("");
  const [description, setDescription] = useState("");
  const [createdSnapshot, setCreatedSnapshot] = useState<any | null>(null);
  const [exportJson, setExportJson] = useState<string>("");
  const [importJson, setImportJson] = useState<string>("");
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  const handleCreateSnapshot = async () => {
    if (!snapshotName.trim()) return;
    try {
      const res = await api.createSnapshot(snapshotName, description);
      setCreatedSnapshot(res);
      setStatusMsg(`Snapshot "${snapshotName}" created successfully!`);
      setSnapshotName("");
      setDescription("");
    } catch (e: any) {
      setStatusMsg(`Error creating snapshot: ${e.message}`);
    }
  };

  const handleExport = async () => {
    if (!createdSnapshot) return;
    try {
      const res = await api.exportProfile(createdSnapshot.id);
      setExportJson(res.manifest || JSON.stringify(createdSnapshot, null, 2));
    } catch (e: any) {
      setStatusMsg(`Export failed: ${e.message}`);
    }
  };

  return (
    <div className="profiles-container">
      <div className="glass-card profile-card">
        <h3>
          <Camera size={20} className="icon" /> Create Environment Snapshot
        </h3>
        <p className="desc">
          Capture the exact state and versions of all currently installed packages into a shareable profile.
        </p>

        <div className="form-group">
          <input
            type="text"
            placeholder="Profile Name (e.g. AI Workstation 2026)"
            value={snapshotName}
            onChange={(e) => setSnapshotName(e.target.value)}
          />
          <textarea
            placeholder="Optional description..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={2}
          />
          <button className="btn btn-primary" onClick={handleCreateSnapshot}>
            <Camera size={16} /> Take Snapshot
          </button>
        </div>

        {statusMsg && <div className="status-banner">{statusMsg}</div>}
      </div>

      {createdSnapshot && (
        <div className="glass-card profile-card">
          <h3>
            <FileText size={20} className="icon" /> Active Snapshot: {createdSnapshot.name}
          </h3>
          <p className="desc">Package Count: {createdSnapshot.packages?.length ?? 0}</p>

          <button className="btn btn-secondary" onClick={handleExport}>
            <Download size={16} /> Export Profile JSON Manifest
          </button>

          {exportJson && (
            <textarea
              className="json-viewer"
              value={exportJson}
              readOnly
              rows={8}
            />
          )}
        </div>
      )}

      <style>{`
        .profiles-container {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }
        .profile-card {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        .profile-card h3 {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 1.15rem;
        }
        .profile-card h3 .icon {
          color: var(--accent-cyan);
        }
        .desc {
          font-size: 0.9rem;
          color: var(--text-secondary);
        }
        .form-group {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }
        .form-group input, .form-group textarea {
          background: var(--bg-dark);
          border: 1px solid var(--border-glass);
          border-radius: var(--radius-sm);
          padding: 0.7rem 0.9rem;
          color: var(--text-primary);
          font-size: 0.9rem;
          outline: none;
        }
        .status-banner {
          background: hsla(155, 85%, 45%, 0.15);
          color: var(--accent-emerald);
          padding: 0.6rem 0.9rem;
          border-radius: var(--radius-sm);
          font-size: 0.85rem;
          border: 1px solid hsla(155, 85%, 45%, 0.3);
        }
        .json-viewer {
          font-family: var(--font-mono);
          background: var(--bg-terminal);
          color: var(--accent-cyan);
          border: 1px solid var(--border-glass);
          border-radius: var(--radius-sm);
          padding: 0.8rem;
          font-size: 0.8rem;
        }
      `}</style>
    </div>
  );
};
