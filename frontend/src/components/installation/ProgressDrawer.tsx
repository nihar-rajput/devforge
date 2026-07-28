import React from "react";
import { Loader, CheckCircle, XCircle } from "lucide-react";
import { LogLine } from "../../hooks/useInstallation";
import { LiveTerminal } from "./LiveTerminal";

interface ProgressDrawerProps {
  isOpen: boolean;
  packageName?: string | null;
  progressPercent: number;
  stage: string;
  logs: LogLine[];
  onClose?: () => void;
}

export const ProgressDrawer: React.FC<ProgressDrawerProps> = ({
  isOpen,
  packageName,
  progressPercent,
  stage,
  logs,
}) => {
  if (!isOpen) return null;

  return (
    <div className="progress-drawer-overlay">
      <div className="glass-card drawer-content">
        <div className="drawer-header">
          <div className="drawer-title">
            <Loader size={20} className="spinner" />
            <h3>Installing {packageName || "Package Stack"}...</h3>
          </div>
          <span className="stage-tag">{stage}</span>
        </div>

        <div className="progress-bar-container">
          <div
            className="progress-bar-fill"
            style={{ width: `${Math.max(5, progressPercent)}%` }}
          />
        </div>

        <div className="progress-stats">
          <span>Overall Progress</span>
          <span>{Math.round(progressPercent)}%</span>
        </div>

        <LiveTerminal logs={logs} />
      </div>

      <style>{`
        .progress-drawer-overlay {
          position: fixed;
          bottom: 1.5rem;
          right: 1.5rem;
          width: 480px;
          z-index: 100;
        }
        .drawer-content {
          display: flex;
          flex-direction: column;
          gap: 1rem;
          box-shadow: var(--shadow-md);
          border: 1px solid var(--accent-cyan);
        }
        .drawer-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        .drawer-title {
          display: flex;
          align-items: center;
          gap: 0.6rem;
        }
        .spinner {
          animation: spin 1s linear infinite;
          color: var(--accent-cyan);
        }
        @keyframes spin {
          100% { transform: rotate(360deg); }
        }
        .stage-tag {
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
          background: var(--bg-dark);
          color: var(--accent-cyan);
          padding: 0.2rem 0.6rem;
          border-radius: var(--radius-full);
          border: 1px solid var(--border-glass);
        }
        .progress-bar-container {
          height: 8px;
          background: var(--bg-dark);
          border-radius: var(--radius-full);
          overflow: hidden;
        }
        .progress-bar-fill {
          height: 100%;
          background: var(--gradient-brand);
          transition: width 0.3s ease;
        }
        .progress-stats {
          display: flex;
          justify-content: space-between;
          font-size: 0.8rem;
          color: var(--text-secondary);
        }
      `}</style>
    </div>
  );
};
