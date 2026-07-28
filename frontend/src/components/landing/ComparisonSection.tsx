import React from "react";

export const ComparisonSection: React.FC = () => {
  const features = [
    { name: "1-Click Curated Dev Stacks", devforge: true, winget: false, homebrew: false, manual: false },
    { name: "Air-Gapped Offline Zip Exporter", devforge: true, winget: false, homebrew: false, manual: false },
    { name: "LIFO Transaction Rollback Engine", devforge: true, winget: false, homebrew: false, manual: false },
    { name: "1-Click Project Workspace Scaffolder", devforge: true, winget: false, homebrew: false, manual: false },
    { name: "System Tray Background Health Worker", devforge: true, winget: false, homebrew: false, manual: false },
    { name: "Multi-OS Native Support (Win/Mac/Linux)", devforge: true, winget: false, homebrew: true, manual: true },
    { name: "Privacy Log Sanitizer & Consent", devforge: true, winget: false, homebrew: false, manual: false },
    { name: "Terminal CLI & Interactive Web Dashboard", devforge: true, winget: false, homebrew: false, manual: false },
  ];

  return (
    <section className="comparison-section" style={{ maxWidth: "1100px", margin: "4rem auto", padding: "0 1.5rem" }}>
      <div className="section-header" style={{ textAlign: "center", marginBottom: "2.5rem" }}>
        <h2 className="section-title">
          Why Choose <span className="gradient-text">DevForge</span>?
        </h2>
        <p className="section-subtitle">
          See how DevForge compares to traditional package managers and manual setups.
        </p>
      </div>

      <div className="glass-card" style={{ padding: "0.5rem", overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--border-glass)", background: "hsla(220, 20%, 12%, 0.8)" }}>
              <th style={{ padding: "1rem 1.2rem", color: "#fff" }}>Feature / Capability</th>
              <th style={{ padding: "1rem 1.2rem", color: "var(--accent-cyan)", fontWeight: "800" }}>⚡ DevForge</th>
              <th style={{ padding: "1rem 1.2rem", color: "var(--text-muted)" }}>Winget / Choco</th>
              <th style={{ padding: "1rem 1.2rem", color: "var(--text-muted)" }}>Homebrew</th>
              <th style={{ padding: "1rem 1.2rem", color: "var(--text-muted)" }}>Manual Setup</th>
            </tr>
          </thead>
          <tbody>
            {features.map((item, idx) => (
              <tr key={idx} style={{ borderBottom: "1px solid var(--border-glass)" }}>
                <td style={{ padding: "1rem 1.2rem", fontWeight: "600" }}>{item.name}</td>
                <td style={{ padding: "1rem 1.2rem", color: "var(--accent-emerald)", fontWeight: "800" }}>
                  {item.devforge ? "✓ Yes" : "—"}
                </td>
                <td style={{ padding: "1rem 1.2rem", color: "var(--text-muted)" }}>
                  {item.winget ? "✓ Yes" : "✗ No"}
                </td>
                <td style={{ padding: "1rem 1.2rem", color: "var(--text-muted)" }}>
                  {item.homebrew ? "✓ Yes" : "✗ No"}
                </td>
                <td style={{ padding: "1rem 1.2rem", color: "var(--text-muted)" }}>
                  {item.manual ? "✓ Yes" : "✗ No"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
};
