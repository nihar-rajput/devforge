import React, { useState } from "react";
import { api } from "../../api/client";

interface ToolOption {
  id: string;
  name: string;
  category: string;
  icon: string;
}

const ALL_TOOLS: ToolOption[] = [
  { id: "python", name: "Python 3.12", category: "Language", icon: "🐍" },
  { id: "git", name: "Git", category: "Version Control", icon: "🐙" },
  { id: "vscode", name: "VS Code", category: "Editor", icon: "💙" },
  { id: "nodejs", name: "Node.js 20", category: "Runtime", icon: "🟢" },
  { id: "docker", name: "Docker Desktop", category: "DevOps", icon: "🐳" },
  { id: "cuda", name: "CUDA Toolkit", category: "AI", icon: "💚" },
  { id: "ollama", name: "Ollama LLM", category: "AI", icon: "🦙" },
  { id: "rust", name: "Rust", category: "Language", icon: "🦀" },
  { id: "go", name: "Go Language", category: "Language", icon: "🐹" },
  { id: "postgresql", name: "PostgreSQL", category: "Database", icon: "🐘" },
  { id: "redis", name: "Redis Cache", category: "Database", icon: "🔴" },
  { id: "terraform", name: "Terraform", category: "DevOps", icon: "🟣" },
];

export const StackWizardSection: React.FC = () => {
  const [selectedTools, setSelectedTools] = useState<string[]>(["python", "git", "vscode"]);
  const [bundleName, setBundleName] = useState<string>("MyCustomStack");
  const [isExporting, setIsExporting] = useState(false);

  const toggleTool = (id: string) => {
    setSelectedTools((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const handleExportBundle = async () => {
    if (selectedTools.length === 0) return;
    setIsExporting(true);
    try {
      await api.exportOfflineBundle(selectedTools, bundleName);
    } catch (err) {
      console.error("Bundle export failed:", err);
    } finally {
      setIsExporting(false);
    }
  };

  const generatedCliCmd = `devforge export --packages ${selectedTools.join(",")} --output ${bundleName}`;

  return (
    <section className="wizard-section">
      <div className="section-header">
        <h2 className="section-title">
          Interactive <span className="gradient-text">1-Click Environment Wizard</span>
        </h2>
        <p className="section-subtitle">
          Select your tools to generate a custom air-gapped offline `.zip` bundle or terminal CLI command.
        </p>
      </div>

      {/* Preset Stack Buttons */}
      <div className="preset-row">
        <button
          className="preset-btn"
          onClick={() => setSelectedTools(["python", "git", "vscode", "uv"])}
        >
          🐍 Python Stack
        </button>
        <button
          className="preset-btn"
          onClick={() => setSelectedTools(["nodejs", "git", "vscode", "pnpm"])}
        >
          🌐 Web React Stack
        </button>
        <button
          className="preset-btn"
          onClick={() => setSelectedTools(["python", "cuda", "ollama", "docker"])}
        >
          🤖 AI / ML Stack
        </button>
        <button
          className="preset-btn"
          onClick={() => setSelectedTools(["rust", "git", "neovim"])}
        >
          🦀 Rust CLI Stack
        </button>
      </div>

      {/* Tool Selector Grid */}
      <div className="wizard-tool-grid">
        {ALL_TOOLS.map((tool) => {
          const isSelected = selectedTools.includes(tool.id);
          return (
            <div
              key={tool.id}
              className={`wizard-tool-card ${isSelected ? "selected" : ""}`}
              onClick={() => toggleTool(tool.id)}
            >
              <span className="tool-icon">{tool.icon}</span>
              <div className="tool-info">
                <span className="tool-name">{tool.name}</span>
                <span className="tool-cat">{tool.category}</span>
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

      {/* Output Actions Box */}
      <div className="wizard-output-box">
        <div className="output-field-group">
          <label className="output-label">Custom Bundle Name:</label>
          <input
            type="text"
            className="output-name-input"
            value={bundleName}
            onChange={(e) => setBundleName(e.target.value)}
          />
        </div>

        <div className="output-cmd-box">
          <code>{generatedCliCmd}</code>
        </div>

        <div className="output-actions">
          <button
            className="export-zip-btn"
            onClick={handleExportBundle}
            disabled={isExporting || selectedTools.length === 0}
          >
            {isExporting ? "⏳ Building Bundle Zip..." : "📦 Download Custom Offline Zip Bundle"}
          </button>
        </div>
      </div>
    </section>
  );
};
