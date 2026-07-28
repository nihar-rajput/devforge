import React from "react";
import { Package } from "../../api/client";
import { PackageCard } from "./PackageCard";

interface PackageGridProps {
  packages: Package[];
  selectedCategory?: string;
  onSelectCategory: (cat?: string) => void;
  onInstall: (pkgId: string) => void;
  onUninstall?: (pkgId: string) => void;
}

const CATEGORIES = [
  { id: undefined, label: "All Packages" },
  { id: "language", label: "Languages" },
  { id: "editor", label: "Editors" },
  { id: "database", label: "Databases" },
  { id: "version_control", label: "Version Control" },
  { id: "runtime", label: "Runtimes" },
  { id: "ai", label: "AI & ML" },
  { id: "utility", label: "Utilities" },
];

export const PackageGrid: React.FC<PackageGridProps> = ({
  packages,
  selectedCategory,
  onSelectCategory,
  onInstall,
  onUninstall,
}) => {
  return (
    <div className="catalog-container">
      <div className="category-tabs">
        {CATEGORIES.map((cat) => (
          <button
            key={cat.id || "all"}
            className={`cat-tab ${selectedCategory === cat.id ? "active" : ""}`}
            onClick={() => onSelectCategory(cat.id)}
          >
            {cat.label}
          </button>
        ))}
      </div>

      <div className="packages-grid">
        {packages.map((pkg) => (
          <PackageCard key={pkg.id} pkg={pkg} onInstall={onInstall} onUninstall={onUninstall} />
        ))}
      </div>

      <style>{`
        .catalog-container {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }
        .category-tabs {
          display: flex;
          gap: 0.5rem;
          overflow-x: auto;
          padding-bottom: 0.5rem;
        }
        .cat-tab {
          background: var(--bg-surface);
          border: 1px solid var(--border-glass);
          color: var(--text-secondary);
          padding: 0.4rem 0.9rem;
          border-radius: var(--radius-full);
          font-size: 0.85rem;
          font-weight: 500;
          cursor: pointer;
          white-space: nowrap;
          transition: var(--transition-fast);
        }
        .cat-tab:hover {
          color: var(--text-primary);
          border-color: var(--border-glass-strong);
        }
        .cat-tab.active {
          background: var(--gradient-brand);
          color: #fff;
          border-color: transparent;
          box-shadow: var(--shadow-glow);
        }
        .packages-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
          gap: 1.25rem;
        }
      `}</style>
    </div>
  );
};
