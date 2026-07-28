import React from "react";
import { Sparkles, Grid, CheckCircle, Activity, Save, Terminal, Globe } from "lucide-react";

export type NavTab = "welcome" | "catalog" | "installed" | "health" | "profiles";

interface SidebarProps {
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
  installedCount?: number;
  onBackToLanding?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange, installedCount = 0, onBackToLanding }) => {
  const navItems = [
    { id: "welcome", label: "Stacks", icon: Sparkles },
    { id: "catalog", label: "Catalog", icon: Grid },
    { id: "installed", label: "Installed", icon: CheckCircle, count: installedCount },
    { id: "health", label: "Health", icon: Activity },
    { id: "profiles", label: "Profiles", icon: Save },
  ];

  return (
    <aside className="sidebar-container">
      <div className="brand" onClick={onBackToLanding} style={{ cursor: onBackToLanding ? "pointer" : "default" }}>
        <img src="/logo.png" alt="DevForge Logo" style={{ width: "38px", height: "38px", borderRadius: "8px", objectFit: "cover" }} />
        <div className="brand-text">
          <h2>DevForge</h2>
          <span className="version">v1.0.0</span>
        </div>
      </div>

      <nav className="nav-list">
        {onBackToLanding && (
          <button className="nav-item landing-item" onClick={onBackToLanding}>
            <Globe size={18} color="var(--accent-cyan)" />
            <span style={{ color: "var(--accent-cyan)", fontWeight: "700" }}>← Main Landing</span>
          </button>
        )}

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? "active" : ""}`}
              onClick={() => onTabChange(item.id as NavTab)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
              {item.count !== undefined && item.count > 0 && (
                <span className="count-pill">{item.count}</span>
              )}
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="system-status">
          <span className="dot online"></span>
          <span>Engine Online</span>
        </div>
      </div>

      <style>{`
        .sidebar-container {
          width: 240px;
          background: var(--bg-surface);
          backdrop-filter: var(--glass-backdrop);
          border-right: 1px solid var(--border-glass);
          display: flex;
          flex-direction: column;
          padding: 1.5rem 1rem;
        }
        .brand {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.5rem;
          margin-bottom: 2rem;
        }
        .brand-icon {
          width: 38px;
          height: 38px;
          border-radius: var(--radius-sm);
          background: var(--gradient-brand);
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: var(--shadow-glow);
        }
        .brand-text h2 {
          font-size: 1.25rem;
          font-weight: 700;
          color: var(--text-primary);
        }
        .brand-text .version {
          font-size: 0.75rem;
          color: var(--text-muted);
        }
        .nav-list {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          flex: 1;
        }
        .nav-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem 1rem;
          border-radius: var(--radius-sm);
          background: transparent;
          border: none;
          color: var(--text-secondary);
          font-size: 0.95rem;
          font-weight: 500;
          cursor: pointer;
          transition: var(--transition-fast);
          text-align: left;
        }
        .nav-item:hover {
          color: var(--text-primary);
          background: hsla(220, 20%, 20%, 0.4);
        }
        .nav-item.active {
          color: #fff;
          background: var(--gradient-brand);
          box-shadow: var(--shadow-glow);
        }
        .landing-item {
          border: 1px solid hsla(190, 90%, 50%, 0.3);
          background: hsla(190, 90%, 50%, 0.08);
          margin-bottom: 0.5rem;
        }
        .count-pill {
          margin-left: auto;
          background: hsla(220, 20%, 30%, 0.6);
          padding: 0.15rem 0.5rem;
          border-radius: var(--radius-full);
          font-size: 0.75rem;
        }
        .sidebar-footer {
          padding-top: 1rem;
          border-top: 1px solid var(--border-glass);
        }
        .system-status {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.8rem;
          color: var(--text-muted);
        }
        .dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }
        .dot.online {
          background: var(--accent-emerald);
          box-shadow: 0 0 8px var(--accent-emerald);
        }
      `}</style>
    </aside>
  );
};
