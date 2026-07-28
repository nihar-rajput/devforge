import React from "react";
import { PackageGrid } from "../components/catalog/PackageGrid";
import { usePackages } from "../hooks/usePackages";

interface CatalogPageProps {
  onInstall: (pkgId: string) => void;
  onUninstall?: (pkgId: string) => void;
}

export const CatalogPage: React.FC<CatalogPageProps> = ({ onInstall, onUninstall }) => {
  const { packages, loading, error, selectedCategory, setSelectedCategory } = usePackages();

  if (loading) return <div className="page-container">Loading package catalog...</div>;
  if (error) return <div className="page-container">Error: {error}</div>;

  return (
    <div className="page-container">
      <PackageGrid
        packages={packages}
        selectedCategory={selectedCategory}
        onSelectCategory={setSelectedCategory}
        onInstall={onInstall}
        onUninstall={onUninstall}
      />
    </div>
  );
};
