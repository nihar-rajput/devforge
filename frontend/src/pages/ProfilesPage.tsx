import React from "react";
import { ProfileManager } from "../components/profiles/ProfileManager";

export const ProfilesPage: React.FC = () => {
  return (
    <div className="page-container">
      <div className="page-header mb-4">
        <h2>Snapshot & Restore Profiles</h2>
        <p>Export your development setup into JSON manifests to restore or share across machines.</p>
      </div>

      <ProfileManager />

      <style>{`
        .mb-4 { margin-bottom: 1.5rem; }
        .page-header h2 { font-size: 1.5rem; margin-bottom: 0.25rem; }
        .page-header p { color: var(--text-secondary); font-size: 0.95rem; }
      `}</style>
    </div>
  );
};
