import React from "react";
import { Download, CheckCircle, AlertTriangle, ExternalLink } from "lucide-react";
import { Package } from "../../api/client";

interface PackageCardProps {
  pkg: Package;
  onInstall: (pkgId: string) => void;
  onUninstall?: (pkgId: string) => void;
}

export const PackageCard: React.FC<PackageCardProps> = ({ pkg, onInstall, onUninstall }) => {
  return (
    <div className="glass-card package-card">
      <div className="card-top">
        <div className="pkg-badge">{pkg.category}</div>
        {pkg.is_installed && (
          <span className="installed-tag">
            <CheckCircle size={12} /> Installed {pkg.installed_version || ""}
          </span>
        )}
      </div>

      <div className="pkg-header">
        <div className="pkg-icon">{pkg.name.charAt(0)}</div>
        <div className="pkg-title">
          <h4>{pkg.name}</h4>
          {pkg.available_versions && pkg.available_versions.length > 1 ? (
            <select className="version-select" defaultValue={pkg.latest_version || pkg.available_versions[0]}>
              {pkg.available_versions.map((ver) => (
                <option key={ver} value={ver}>
                  v{ver}
                </option>
              ))}
            </select>
          ) : (
            <span className="version">{pkg.latest_version ? `v${pkg.latest_version}` : "Latest"}</span>
          )}
        </div>
      </div>

      <p className="pkg-desc">{pkg.description}</p>

      <div className="card-footer">
        {pkg.is_installed ? (
          <button
            className="btn btn-secondary uninstall-btn"
            onClick={() => onUninstall && onUninstall(pkg.id)}
          >
            Uninstall
          </button>
        ) : (
          <button className="btn btn-primary" onClick={() => onInstall(pkg.id)}>
            <Download size={15} /> Install
          </button>
        )}

        {pkg.website && (
          <a
            href={pkg.website}
            target="_blank"
            rel="noreferrer"
            className="ext-link"
            title="Official Website"
          >
            <ExternalLink size={14} />
          </a>
        )}
      </div>

      <style>{`
        .package-card {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        .card-top {
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        .pkg-badge {
          background: var(--bg-dark);
          color: var(--accent-purple);
          border: 1px solid hsla(265, 85%, 65%, 0.3);
          font-size: 0.7rem;
          font-weight: 600;
          text-transform: uppercase;
          padding: 0.15rem 0.5rem;
          border-radius: var(--radius-full);
        }
        .installed-tag {
          font-size: 0.75rem;
          color: var(--accent-emerald);
          display: flex;
          align-items: center;
          gap: 0.25rem;
        }
        .pkg-header {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }
        .pkg-icon {
          width: 38px;
          height: 38px;
          border-radius: var(--radius-sm);
          background: var(--bg-surface);
          border: 1px solid var(--border-glass);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          font-size: 1.1rem;
          color: var(--accent-cyan);
        }
        .pkg-title h4 {
          font-size: 1.05rem;
          color: var(--text-primary);
        }
        .pkg-title .version {
          font-size: 0.75rem;
          color: var(--text-muted);
        }
        .version-select {
          background: var(--bg-dark);
          color: var(--accent-cyan);
          border: 1px solid var(--border-glass);
          border-radius: var(--radius-sm);
          font-size: 0.75rem;
          padding: 0.1rem 0.4rem;
          outline: none;
          cursor: pointer;
        }
        .pkg-desc {
          font-size: 0.85rem;
          color: var(--text-secondary);
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
          flex: 1;
        }
        .card-footer {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding-top: 0.5rem;
          border-top: 1px solid var(--border-glass);
        }
        .ext-link {
          color: var(--text-muted);
          transition: var(--transition-fast);
        }
        .ext-link:hover {
          color: var(--accent-cyan);
        }
      `}</style>
    </div>
  );
};
