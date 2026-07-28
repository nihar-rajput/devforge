import React from "react";
import { HealthDashboard } from "../components/health/HealthDashboard";
import { useSystemHealth } from "../hooks/useSystemHealth";

export const HealthPage: React.FC = () => {
  const { health, systemInfo, loading, repairPackage } = useSystemHealth();

  if (loading) return <div className="page-container">Loading system health diagnostic...</div>;

  return (
    <div className="page-container">
      <div className="page-header mb-4">
        <h2>Environment Health & System Diagnostics</h2>
        <p>Continuous integrity monitoring, health scoring, and 1-click automated repair.</p>
      </div>

      <HealthDashboard health={health} systemInfo={systemInfo} onRepair={repairPackage} />

      <style>{`
        .mb-4 { margin-bottom: 1.5rem; }
        .page-header h2 { font-size: 1.5rem; margin-bottom: 0.25rem; }
        .page-header p { color: var(--text-secondary); font-size: 0.95rem; }
      `}</style>
    </div>
  );
};
