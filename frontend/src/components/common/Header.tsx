import React from "react";
import { Search, RefreshCw, Cpu } from "lucide-react";
import { HealthBadge } from "./HealthBadge";

interface HeaderProps {
  healthScore?: number;
  healthStatus?: string;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onRefresh?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  healthScore = 100,
  healthStatus = "healthy",
  searchQuery,
  onSearchChange,
  onRefresh,
}) => {
  return (
    <header className="header-container">
      <div className="search-bar">
        <Search size={18} className="search-icon" />
        <input
          type="text"
          placeholder="Search software packages (Python, Git, Docker, CUDA...)"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>

      <div className="header-actions">
        {onRefresh && (
          <button className="icon-btn" onClick={onRefresh} title="Refresh catalog">
            <RefreshCw size={18} />
          </button>
        )}
        <HealthBadge score={healthScore} status={healthStatus} />
      </div>

      <style>{`
        .header-container {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 1.25rem 2rem;
          background: var(--bg-surface);
          backdrop-filter: var(--glass-backdrop);
          border-bottom: 1px solid var(--border-glass);
        }
        .search-bar {
          position: relative;
          width: 380px;
        }
        .search-icon {
          position: absolute;
          left: 12px;
          top: 50%;
          transform: translateY(-50%);
          color: var(--text-muted);
        }
        .search-bar input {
          width: 100%;
          padding: 0.6rem 0.8rem 0.6rem 2.4rem;
          background: var(--bg-dark);
          border: 1px solid var(--border-glass);
          border-radius: var(--radius-sm);
          color: var(--text-primary);
          font-size: 0.9rem;
          outline: none;
          transition: var(--transition-fast);
        }
        .search-bar input:focus {
          border-color: var(--accent-cyan);
          box-shadow: 0 0 10px hsla(190, 90%, 50%, 0.2);
        }
        .header-actions {
          display: flex;
          align-items: center;
          gap: 1rem;
        }
        .icon-btn {
          background: var(--bg-dark);
          border: 1px solid var(--border-glass);
          color: var(--text-secondary);
          padding: 0.5rem;
          border-radius: var(--radius-sm);
          cursor: pointer;
          transition: var(--transition-fast);
        }
        .icon-btn:hover {
          color: var(--text-primary);
          border-color: var(--border-glass-strong);
        }
      `}</style>
    </header>
  );
};
