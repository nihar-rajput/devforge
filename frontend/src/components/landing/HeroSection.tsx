import React, { useState } from "react";

export const HeroSection: React.FC = () => {
  const [selectedOS, setSelectedOS] = useState<"windows" | "macos" | "linux">("windows");
  const [copied, setCopied] = useState(false);

  const cliCommand = "devforge export --packages python,git,vscode --output DevStack";

  const downloadUrls = {
    windows: "https://github.com/nihar-rajput/devforge/releases/tag/v1.0.0",
    macos: "https://github.com/nihar-rajput/devforge/releases/tag/v1.0.0",
    linux: "https://github.com/nihar-rajput/devforge/releases/tag/v1.0.0",
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(cliCommand);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="hero-landing">
      <div className="hero-glow-bg"></div>

      {/* Pill Badge */}
      <div className="hero-pill">
        <span className="pill-dot"></span>
        <span className="pill-text">v1.0.0 Release Live • 36 Packages • 100% Air-Gapped Ready</span>
      </div>

      {/* Hero Headline */}
      <h1 className="hero-title">
        The Universal <span className="gradient-text">Developer Environment</span> Platform
      </h1>

      <p className="hero-subtitle">
        One click installs, configures, and verifies complete dev stacks across Windows, macOS, and Linux. No broken PATHs, no manual configuration.
      </p>

      {/* OS Selector & Download CTA */}
      <div className="download-box-card">
        <div className="os-selector-tabs">
          <button
            className={`os-tab ${selectedOS === "windows" ? "active" : ""}`}
            onClick={() => setSelectedOS("windows")}
          >
            🪟 Windows (.exe / .zip)
          </button>
          <button
            className={`os-tab ${selectedOS === "macos" ? "active" : ""}`}
            onClick={() => setSelectedOS("macos")}
          >
            🍏 macOS (.dmg)
          </button>
          <button
            className={`os-tab ${selectedOS === "linux" ? "active" : ""}`}
            onClick={() => setSelectedOS("linux")}
          >
            🐧 Linux (.AppImage)
          </button>
        </div>

        <div className="download-action-row" style={{ display: "flex", gap: "1rem", justifyContent: "center", flexWrap: "wrap" }}>
          <a
            href={downloadUrls[selectedOS]}
            target="_blank"
            rel="noopener noreferrer"
            className="primary-download-btn"
          >
            <span className="dl-icon">⬇</span>
            Download {selectedOS.toUpperCase()} Setup (v1.0.0)
          </a>
          <a
            href="https://github.com/nihar-rajput/devforge/archive/refs/tags/v1.0.0.zip"
            target="_blank"
            rel="noopener noreferrer"
            className="primary-download-btn"
            style={{ background: "hsla(220, 20%, 20%, 0.8)", border: "1px solid var(--border-glass)" }}
          >
            📦 Download Release .zip
          </a>
        </div>
      </div>

      {/* CLI Snippet Box */}
      <div className="cli-terminal-card">
        <div className="terminal-header">
          <div className="terminal-dots">
            <span className="dot red"></span>
            <span className="dot yellow"></span>
            <span className="dot green"></span>
          </div>
          <span className="terminal-title">Terminal CLI Mode</span>
        </div>
        <div className="terminal-body">
          <span className="prompt">$</span>
          <span className="command-text">{cliCommand}</span>
          <button className="copy-btn" onClick={copyToClipboard}>
            {copied ? "✓ Copied!" : "📋 Copy"}
          </button>
        </div>
      </div>
    </section>
  );
};
