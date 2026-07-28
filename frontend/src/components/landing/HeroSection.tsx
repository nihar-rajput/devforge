import React, { useState } from "react";

export const HeroSection: React.FC = () => {
  const [selectedOS, setSelectedOS] = useState<"windows" | "macos" | "linux">("windows");
  const [copied, setCopied] = useState(false);

  const cliCommands = {
    windows: "devforge export --packages python,git,vscode --output DevStack",
    macos: "curl -fsSL https://raw.githubusercontent.com/nihar-rajput/devforge/main/install.sh | bash",
    linux: "curl -fsSL https://raw.githubusercontent.com/nihar-rajput/devforge/main/install.sh | bash",
  };

  const downloadUrls = {
    windows: "https://github.com/nihar-rajput/devforge/releases/download/v1.0.0/DevForge.exe",
    macos: "https://github.com/nihar-rajput/devforge/archive/refs/tags/v1.0.0.tar.gz",
    linux: "https://github.com/nihar-rajput/devforge/archive/refs/tags/v1.0.0.tar.gz",
  };

  const currentCommand = cliCommands[selectedOS];

  const copyToClipboard = () => {
    navigator.clipboard.writeText(currentCommand);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="hero-landing">
      <div className="hero-glow-bg"></div>

      {/* Pill Badge */}
      <div className="hero-pill">
        <span className="pill-dot"></span>
        <span className="pill-text">v1.0.0 Production Release • 36 Packages • 100% Cross-Platform</span>
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
            🪟 Windows (DevForge.exe)
          </button>
          <button
            className={`os-tab ${selectedOS === "macos" ? "active" : ""}`}
            onClick={() => setSelectedOS("macos")}
          >
            🍏 macOS (.tar.gz / Curl)
          </button>
          <button
            className={`os-tab ${selectedOS === "linux" ? "active" : ""}`}
            onClick={() => setSelectedOS("linux")}
          >
            🐧 Linux (.tar.gz / Curl)
          </button>
        </div>

        <div className="download-action-row" style={{ display: "flex", gap: "1rem", justifyContent: "center", flexWrap: "wrap" }}>
          <a
            href={downloadUrls[selectedOS]}
            download
            className="primary-download-btn"
          >
            <span className="dl-icon">⬇</span>
            Download {selectedOS.toUpperCase()} Bundle (v1.0.0)
          </a>
          <a
            href="https://github.com/nihar-rajput/devforge/releases/tag/v1.0.0"
            target="_blank"
            rel="noopener noreferrer"
            className="primary-download-btn"
            style={{ background: "hsla(220, 20%, 20%, 0.8)", border: "1px solid var(--border-glass)" }}
          >
            ⭐ View Release Assets
          </a>
        </div>
      </div>

      {/* Dynamic CLI Snippet Box */}
      <div className="cli-terminal-card">
        <div className="terminal-header">
          <div className="terminal-dots">
            <span className="dot red"></span>
            <span className="dot yellow"></span>
            <span className="dot green"></span>
          </div>
          <span className="terminal-title">1-Line Terminal Install ({selectedOS.toUpperCase()})</span>
        </div>
        <div className="terminal-body">
          <span className="prompt">$</span>
          <span className="command-text">{currentCommand}</span>
          <button className="copy-btn" onClick={copyToClipboard}>
            {copied ? "✓ Copied!" : "📋 Copy"}
          </button>
        </div>
      </div>
    </section>
  );
};
