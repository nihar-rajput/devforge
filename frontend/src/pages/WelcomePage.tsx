import React, { useEffect, useState } from "react";
import { api, StackDefinition } from "../api/client";
import { StackSelector } from "../components/welcome/StackSelector";

interface WelcomePageProps {
  onInstallStack: (packageIds: string[]) => void;
  isInstalling?: boolean;
}

export const WelcomePage: React.FC<WelcomePageProps> = ({ onInstallStack, isInstalling }) => {
  const [stacks, setStacks] = useState<StackDefinition[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getStacks()
      .then((data) => setStacks(data))
      .catch((e) => console.error("Error loading stacks:", e))
      .finally(() => setLoading(false));
  }, []);

  const handleSelectStack = (stack: StackDefinition) => {
    onInstallStack(stack.packages);
  };

  if (loading) {
    return <div className="page-container">Loading development stacks...</div>;
  }

  return (
    <div className="page-container">
      <div className="hero-banner glass-card mb-6">
        <h1 className="gradient-text">One-Click Developer Environment Manager</h1>
        <p>
          DevForge automatically downloads, installs, configures PATH, verifies, and repairs complete developer toolchains.
        </p>
      </div>

      <StackSelector stacks={stacks} onSelectStack={handleSelectStack} isInstalling={isInstalling} />

      <style>{`
        .mb-6 { margin-bottom: 2rem; }
        .hero-banner {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          padding: 2.5rem 2rem;
          background: linear-gradient(135deg, hsla(265, 85%, 65%, 0.15), hsla(190, 90%, 50%, 0.1));
          border-color: var(--border-glass-strong);
        }
        .hero-banner h1 {
          font-size: 2rem;
          font-weight: 800;
        }
        .hero-banner p {
          font-size: 1.05rem;
          color: var(--text-secondary);
          max-width: 680px;
        }
      `}</style>
    </div>
  );
};
