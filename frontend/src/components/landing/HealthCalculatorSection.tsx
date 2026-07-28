import React, { useState } from "react";

interface CheckableTool {
  id: string;
  name: string;
  weight: number;
}

const CHECKABLE_TOOLS: CheckableTool[] = [
  { id: "python", name: "Python 3.12", weight: 20 },
  { id: "git", name: "Git CLI", weight: 20 },
  { id: "vscode", name: "VS Code", weight: 15 },
  { id: "docker", name: "Docker Desktop", weight: 15 },
  { id: "nodejs", name: "Node.js 20", weight: 15 },
  { id: "uv", name: "uv Package Manager", weight: 15 },
];

export const HealthCalculatorSection: React.FC = () => {
  const [checkedIds, setCheckedIds] = useState<string[]>(["python", "git"]);

  const toggleTool = (id: string) => {
    setCheckedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const currentScore = CHECKABLE_TOOLS.reduce((score, tool) => {
    return checkedIds.includes(tool.id) ? score + tool.weight : score;
  }, 0);

  let healthStatus = "UNHEALTHY";
  let statusBadgeClass = "badge-unhealthy";
  if (currentScore >= 80) {
    healthStatus = "HEALTHY";
    statusBadgeClass = "badge-healthy";
  } else if (currentScore >= 40) {
    healthStatus = "DEGRADED";
    statusBadgeClass = "badge-degraded";
  }

  return (
    <section className="health-calculator-section" style={{ maxWidth: "900px", margin: "4rem auto", padding: "0 1.5rem" }}>
      <div className="section-header" style={{ textAlign: "center", marginBottom: "2.5rem" }}>
        <h2 className="section-title">
          Live Environment <span className="gradient-text">Health Audit Calculator</span>
        </h2>
        <p className="section-subtitle">
          Check the developer tools currently installed on your computer to calculate your environment health score live.
        </p>
      </div>

      <div className="glass-card" style={{ padding: "2rem", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
        {/* Score Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <div style={{ fontSize: "0.85rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: "700" }}>
              ENVIRONMENT HEALTH SCORE
            </div>
            <div style={{ fontSize: "2.8rem", fontWeight: "800", color: "var(--accent-cyan)" }}>
              {currentScore} <span style={{ fontSize: "1.2rem", color: "var(--text-secondary)" }}>/ 100</span>
            </div>
          </div>
          <span className={`badge ${statusBadgeClass}`} style={{ fontSize: "0.9rem", padding: "0.4rem 1rem" }}>
            {healthStatus}
          </span>
        </div>

        {/* Progress Bar */}
        <div style={{ background: "hsla(220, 20%, 15%, 0.8)", height: "12px", borderRadius: "6px", overflow: "hidden" }}>
          <div
            style={{
              width: `${currentScore}%`,
              height: "100%",
              background: "var(--gradient-brand)",
              transition: "width 0.4s ease-in-out",
            }}
          />
        </div>

        {/* Checkbox Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: "1rem" }}>
          {CHECKABLE_TOOLS.map((tool) => {
            const isChecked = checkedIds.includes(tool.id);
            return (
              <div
                key={tool.id}
                onClick={() => toggleTool(tool.id)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "0.8rem 1rem",
                  background: isChecked ? "hsla(265, 85%, 65%, 0.12)" : "var(--bg-card)",
                  border: `1px solid ${isChecked ? "var(--accent-purple)" : "var(--border-glass)"}`,
                  borderRadius: "var(--radius-sm)",
                  cursor: "pointer",
                }}
              >
                <span style={{ fontWeight: "600" }}>{tool.name}</span>
                <input type="checkbox" checked={isChecked} onChange={() => {}} />
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
