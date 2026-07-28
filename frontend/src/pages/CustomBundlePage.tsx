import React, { useState } from "react";
import { STATIC_36_CATALOG } from "../data/staticCatalog";
import { AdBanner } from "../components/landing/AdBanner";

interface CustomBundlePageProps {
  onBackToLanding?: () => void;
}

export const CustomBundlePage: React.FC<CustomBundlePageProps> = ({ onBackToLanding }) => {
  const [selectedPackageIds, setSelectedPackageIds] = useState<string[]>(["python", "git", "vscode"]);
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] = useState("all");
  const [bundleName, setBundleName] = useState("MyCustomStack");
  const [copied, setCopied] = useState(false);

  const togglePackage = (id: string) => {
    setSelectedPackageIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const selectAll = () => {
    setSelectedPackageIds(STATIC_36_CATALOG.map((p) => p.id));
  };

  const clearAll = () => {
    setSelectedPackageIds([]);
  };

  // Filter 36 tools
  let filtered = STATIC_36_CATALOG;
  if (activeCategory !== "all") {
    filtered = filtered.filter((p) => p.category.toLowerCase() === activeCategory.toLowerCase());
  }
  if (search.trim()) {
    const q = search.toLowerCase();
    filtered = filtered.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q) ||
        p.id.toLowerCase().includes(q)
    );
  }

  const generatedCliCmd = `devforge export --packages ${selectedPackageIds.join(",")} --output ${bundleName}`;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(generatedCliCmd);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadManifestZip = () => {
    const selectedPlugins = STATIC_36_CATALOG.filter((p) => selectedPackageIds.includes(p.id));
    const manifest = {
      bundle_name: bundleName,
      created_at: new Date().toISOString(),
      total_packages: selectedPlugins.length,
      packages: selectedPlugins.map((p) => ({
        id: p.id,
        name: p.name,
        version: p.latest_version,
        category: p.category,
        download_url: p.website,
      })),
      launcher_script: `@echo off\necho Installing ${bundleName}...\nfor %%i in (*.exe *.msi) do %%i /VERYSILENT\necho Done!`,
    };

    const blob = new Blob([JSON.stringify(manifest, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${bundleName}_manifest.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

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
    <div className="custom-builder-page">
      {/* Navigation Header */}
      <header className="landing-nav">
        <div className="nav-logo" onClick={onBackToLanding} style={{ cursor: "pointer" }}>
          <span className="logo-icon">⚡</span>
          <span className="logo-text">DevForge</span>
          <span className="logo-badge">Custom Stack Builder</span>
        </div>
        <div className="nav-links">
          {onBackToLanding && (
            <button className="chip-btn" onClick={onBackToLanding}>
              ← Back to Main Landing Page
            </button>
          )}
        </div>
      </header>

      <div className="landing-ad-wrapper">
        <AdBanner type="sponsor" />
      </div>

      <div className="custom-builder-container">
        <div className="builder-header">
          <h1 className="hero-title">
            Custom <span className="gradient-text">Air-Gapped Stack Builder</span>
          </h1>
          <p className="hero-subtitle">
            Search and select any combination from all 36 package plugins below to construct your custom offline installer bundle and CLI deployment command.
          </p>
        </div>

        {/* Controls Bar */}
        <div className="catalog-filter-bar">
          <div className="search-row">
            <input
              type="text"
              placeholder="🔍 Search all 36 packages (e.g. Python, Docker, CUDA, Ollama, Rust)..."
              className="catalog-search-input"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <div className="select-action-btns">
              <button className="chip-btn" onClick={selectAll}>Select All (36)</button>
              <button className="chip-btn" onClick={clearAll}>Clear Selection</button>
            </div>
          </div>

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

        {/* 36 Package Checkbox Selection Grid */}
        <div className="wizard-tool-grid">
          {filtered.map((pkg) => {
            const isSelected = selectedPackageIds.includes(pkg.id);
            return (
              <div
                key={pkg.id}
                className={`wizard-tool-card ${isSelected ? "selected" : ""}`}
                onClick={() => togglePackage(pkg.id)}
              >
                <span className="tool-icon">{pkg.icon || "📦"}</span>
                <div className="tool-info">
                  <span className="tool-name">{pkg.name}</span>
                  <span className="tool-cat">{pkg.category.toUpperCase()} • v{pkg.latest_version}</span>
                </div>
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => {}}
                  className="tool-checkbox"
                />
              </div>
            );
          })}
        </div>

        {/* Dynamic Output Box */}
        <div className="wizard-output-box">
          <div className="output-field-row">
            <div>
              <label className="output-label">Custom Stack Bundle Name:</label>
              <input
                type="text"
                className="output-name-input"
                value={bundleName}
                onChange={(e) => setBundleName(e.target.value)}
              />
            </div>
            <div className="selected-count-badge">
              Selected: <strong>{selectedPackageIds.length}</strong> / 36 Tools
            </div>
          </div>

          <div className="terminal-body" style={{ background: "#0d1117", borderRadius: "6px", padding: "1rem" }}>
            <span className="prompt">$</span>
            <span className="command-text">{generatedCliCmd}</span>
            <button className="copy-btn" onClick={copyToClipboard}>
              {copied ? "✓ Copied!" : "📋 Copy Command"}
            </button>
          </div>

          <div className="output-actions">
            <button
              className="export-zip-btn"
              onClick={downloadManifestZip}
              disabled={selectedPackageIds.length === 0}
            >
              📦 Download Custom Offline Manifest (.json)
            </button>
          </div>
        </div>
      </div>

      <div className="landing-ad-wrapper" style={{ marginTop: "3rem" }}>
        <AdBanner type="sponsor" />
      </div>
    </div>
  );
};
