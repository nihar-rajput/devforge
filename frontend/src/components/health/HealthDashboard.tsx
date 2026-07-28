import React from "react";
import { Activity, Cpu, HardDrive, Wrench, ShieldCheck } from "lucide-react";
import { HealthSummary, SystemInfo } from "../../api/client";

interface HealthDashboardProps {
  health: HealthSummary | null;
  systemInfo: SystemInfo | null;
  onRepair: (packageId: string) => void;
}

export const HealthDashboard: React.FC<HealthDashboardProps> = ({
  health,
  systemInfo,
  onRepair,
}) => {
  const score = health?.score ?? 100;

  return (
    <div className="health-container">
      <div className="health-overview glass-card">
        <div className="gauge-box">
          <div className="gauge-score">
            <span className="score-num">{score}</span>
            <span className="score-max">/100</span>
          </div>
          <span className="gauge-label">Environment Health Score</span>
        </div>

        <div className="metrics-grid">
          <div className="metric">
            <span className="val healthy">{health?.healthy_count ?? 0}</span>
            <span className="lbl">Healthy Packages</span>
          </div>
          <div className="metric">
            <span className="val degraded">{health?.degraded_count ?? 0}</span>
            <span className="lbl">Degraded</span>
          </div>
          <div className="metric">
            <span className="val unhealthy">{health?.unhealthy_count ?? 0}</span>
            <span className="lbl">Needs Repair</span>
          </div>
        </div>
      </div>

      {systemInfo && (
        <div className="system-specs glass-card">
          <h3>Hardware & Operating System</h3>
          <div className="specs-grid">
            <div className="spec-item">
              <Cpu size={18} className="icon" />
              <div>
                <span className="lbl">CPU Cores</span>
                <span className="val">{systemInfo.cpu_cores} Logical Cores</span>
              </div>
            </div>
            <div className="spec-item">
              <Activity size={18} className="icon" />
              <div>
                <span className="lbl">System RAM</span>
                <span className="val">{Math.round(systemInfo.total_ram_mb / 1024)} GB</span>
              </div>
            </div>
            <div className="spec-item">
              <HardDrive size={18} className="icon" />
              <div>
                <span className="lbl">Available Disk</span>
                <span className="val">{systemInfo.available_disk_gb} GB</span>
              </div>
            </div>
            <div className="spec-item">
              <ShieldCheck size={18} className="icon" />
              <div>
                <span className="lbl">OS & Build</span>
                <span className="val">Windows Build {systemInfo.os_build}</span>
              </div>
            </div>
          </div>

          {systemInfo.gpus.length > 0 && (
            <div className="gpus-list">
              <span className="label">Detected GPU Hardware:</span>
              {systemInfo.gpus.map((gpu, idx) => (
                <div key={idx} className="gpu-card">
                  <span className="gpu-name">{gpu.device_name}</span>
                  <span className="gpu-detail">
                    {gpu.vram_mb ? `${Math.round(gpu.vram_mb / 1024)} GB VRAM` : ""}{" "}
                    {gpu.driver_version ? `| Driver ${gpu.driver_version}` : ""}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <style>{`
        .health-container {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }
        .health-overview {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 2rem;
        }
        .gauge-box {
          display: flex;
          flex-direction: column;
          align-items: center;
        }
        .score-num {
          font-size: 3.5rem;
          font-weight: 800;
          font-family: var(--font-heading);
          background: var(--gradient-brand);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }
        .score-max {
          font-size: 1.2rem;
          color: var(--text-muted);
        }
        .gauge-label {
          font-size: 0.9rem;
          color: var(--text-secondary);
        }
        .metrics-grid {
          display: flex;
          gap: 2rem;
        }
        .metric {
          display: flex;
          flex-direction: column;
          align-items: center;
        }
        .metric .val {
          font-size: 1.8rem;
          font-weight: 700;
        }
        .metric .val.healthy { color: var(--accent-emerald); }
        .metric .val.degraded { color: var(--accent-amber); }
        .metric .val.unhealthy { color: var(--accent-rose); }
        .metric .lbl {
          font-size: 0.8rem;
          color: var(--text-muted);
        }
        .system-specs {
          display: flex;
          flex-direction: column;
          gap: 1.25rem;
        }
        .system-specs h3 {
          font-size: 1.1rem;
        }
        .specs-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
          gap: 1rem;
        }
        .spec-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          background: var(--bg-dark);
          padding: 0.8rem 1rem;
          border-radius: var(--radius-sm);
          border: 1px solid var(--border-glass);
        }
        .spec-item .icon {
          color: var(--accent-cyan);
        }
        .spec-item .lbl {
          display: block;
          font-size: 0.75rem;
          color: var(--text-muted);
        }
        .spec-item .val {
          font-size: 0.9rem;
          font-weight: 600;
          color: var(--text-primary);
        }
        .gpus-list {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }
        .gpu-card {
          background: var(--bg-dark);
          padding: 0.6rem 1rem;
          border-radius: var(--radius-sm);
          border: 1px solid var(--border-glass);
          display: flex;
          justify-content: space-between;
          font-size: 0.85rem;
        }
        .gpu-name {
          font-weight: 600;
          color: var(--accent-cyan);
        }
        .gpu-detail {
          color: var(--text-secondary);
        }
      `}</style>
    </div>
  );
};
