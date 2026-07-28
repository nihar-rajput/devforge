import React from "react";
import { Download, Check } from "lucide-react";
import { StackDefinition } from "../../api/client";

interface StackCardProps {
  stack: StackDefinition;
  onInstall: (stack: StackDefinition) => void;
  isInstalling?: boolean;
}

export const StackCard: React.FC<StackCardProps> = ({ stack, onInstall, isInstalling = false }) => {
  return (
    <div className="glass-card stack-card">
      <div className="stack-header">
        <div className="stack-icon">{stack.name.charAt(0)}</div>
        <div className="stack-title">
          <h3>{stack.name}</h3>
          <p>{stack.description}</p>
        </div>
      </div>

      <div className="stack-packages">
        <span className="label">Included Tools:</span>
        <div className="pills">
          {stack.packages.map((pkg) => (
            <span key={pkg} className="pkg-pill">
              {pkg}
            </span>
          ))}
        </div>
      </div>

      <button
        className="btn btn-primary stack-action"
        onClick={() => onInstall(stack)}
        disabled={isInstalling}
      >
        <Download size={16} />
        <span>1-Click Install Environment</span>
      </button>

      <style>{`
        .stack-card {
          display: flex;
          flex-direction: column;
          gap: 1.25rem;
        }
        .stack-header {
          display: flex;
          align-items: flex-start;
          gap: 1rem;
        }
        .stack-icon {
          width: 48px;
          height: 48px;
          border-radius: var(--radius-md);
          background: var(--gradient-brand);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.5rem;
          font-weight: 700;
          color: #fff;
          box-shadow: var(--shadow-glow);
        }
        .stack-title h3 {
          font-size: 1.15rem;
          font-weight: 600;
          color: var(--text-primary);
          margin-bottom: 0.25rem;
        }
        .stack-title p {
          font-size: 0.85rem;
          color: var(--text-secondary);
        }
        .stack-packages .label {
          font-size: 0.75rem;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.05em;
          display: block;
          margin-bottom: 0.5rem;
        }
        .pills {
          display: flex;
          flex-wrap: wrap;
          gap: 0.4rem;
        }
        .pkg-pill {
          background: var(--bg-dark);
          border: 1px solid var(--border-glass);
          padding: 0.2rem 0.6rem;
          border-radius: var(--radius-sm);
          font-size: 0.8rem;
          color: var(--accent-cyan);
          font-family: var(--font-mono);
        }
        .stack-action {
          width: 100%;
          justify-content: center;
          margin-top: 0.5rem;
        }
      `}</style>
    </div>
  );
};
