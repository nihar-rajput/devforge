import React, { useState, useEffect } from "react";
import { api, Package } from "../../api/client";

export const PackageCatalogSection: React.FC = () => {
  const [packages, setPackages] = useState<Package[]>([]);
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] = useState<string>("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCatalog = async () => {
      try {
        const catFilter = activeCategory === "all" ? undefined : activeCategory;
        const data = await api.getPackages(catFilter, search);
        setPackages(data);
      } catch (err) {
        console.error("Failed to load catalog:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchCatalog();
  }, [search, activeCategory]);

  const categories = [
    { id: "all", label: "All (36)" },
    { id: "language", label: "Languages" },
    { id: "editor", label: "Editors" },
    { id: "database", label: "Databases" },
    { id: "devops", label: "DevOps" },
    { id: "ai", label: "AI & ML" },
    { id: "runtime", label: "Runtimes" },
    { id: "utility", label: "Utilities" },
  ];

  return (
    <section className="catalog-landing-section">
      <div className="section-header">
        <h2 className="section-title">
          Supported <span className="gradient-text">36 Package Catalog</span>
        </h2>
        <p className="section-subtitle">
          Every tool is audited for SemVer resolution, URL integrity, silent install, and verification checks.
        </p>
      </div>

      {/* Filter Chips & Search Bar */}
      <div className="catalog-filter-bar">
        <input
          type="text"
          placeholder="🔍 Search 36 tools (e.g. Python, Docker, CUDA)..."
          className="catalog-search-input"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <div className="category-chips">
          {categories.map((cat) => (
            <button
              key={cat.id}
              className={`chip-btn ${activeCategory === cat.id ? "active" : ""}`}
              onClick={() => setActiveCategory(cat.id)}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Catalog Grid */}
      {loading ? (
        <div className="catalog-loading">Loading 36 verified plugins...</div>
      ) : (
        <div className="catalog-grid">
          {packages.map((pkg) => (
            <div key={pkg.id} className="catalog-card">
              <div className="card-top">
                <span className="pkg-name">{pkg.name}</span>
                <span className="pkg-version">v{pkg.latest_version}</span>
              </div>
              <span className="pkg-category">{pkg.category.toUpperCase()}</span>
              <p className="pkg-desc">{pkg.description}</p>
              {pkg.website && (
                <a
                  href={pkg.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="pkg-link"
                >
                  Official Site ↗
                </a>
              )}
            </div>
          ))}
        </div>
      )}
    </section>
  );
};
