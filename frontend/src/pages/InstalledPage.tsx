import React from "react";
import { PackageGrid } from "../components/catalog/PackageGrid";
import { usePackages } from "../hooks/usePackages";

interface InstalledPageProps {
  onInstall: (pkgId: string) => void;
  onUninstall: (pkgId: string) => void;
}

export const InstalledPage: React.FC<InstalledPageProps> = ({ onInstall, onUninstall }) => {
  const { packages, loading, selectedCategory, setSelectedCategory } = usePackages();

  const installedPackages = packages.filter((p) => p.is_installed);

  if (loading) return <div className="page-container">Loading installed packages...</div>;

  return (
    <div className="page-container">
      <div className="page-header mb-4">
        <h2>Installed Packages ({installedPackages.length})</h2>
        <p>Software packages currently installed and verified on your system.</p>
      </div>

      {installedPackages.length === 0 ? (
        <div className="glass-card empty-state">
          <p>No software packages are currently installed.</p>
        </div>
      ) : (
        <PackageGrid
          packages={installedPackages}
          selectedCategory={selectedCategory}
          onSelectCategory={setSelectedCategory}
          onInstall={onInstall}
          onUninstall={onUninstall}
        />
      )}

      <style>{`
        .mb-4 { margin-bottom: 1.5rem; }
        .page-header h2 { font-size: 1.5rem; margin-bottom: 0.25rem; }
        .page-header p { color: var(--text-secondary); font-size: 0.95rem; }
        .empty-state { text-align: center; padding: 3rem; color: var(--text-muted); }
      `}</style>
    </div>
  );
};
