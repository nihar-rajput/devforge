import React from "react";
import { StackDefinition } from "../../api/client";
import { StackCard } from "./StackCard";

interface StackSelectorProps {
  stacks: StackDefinition[];
  onSelectStack: (stack: StackDefinition) => void;
  isInstalling?: boolean;
}

export const StackSelector: React.FC<StackSelectorProps> = ({
  stacks,
  onSelectStack,
  isInstalling = false,
}) => {
  return (
    <div className="stacks-section">
      <div className="section-header">
        <h2>Choose Your Development Stack</h2>
        <p>Select a pre-configured environment stack to install all tools in one click.</p>
      </div>

      <div className="stacks-grid">
        {stacks.map((stack) => (
          <StackCard
            key={stack.id}
            stack={stack}
            onInstall={onSelectStack}
            isInstalling={isInstalling}
          />
        ))}
      </div>

      <style>{`
        .stacks-section {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }
        .section-header h2 {
          font-size: 1.5rem;
          margin-bottom: 0.25rem;
        }
        .section-header p {
          color: var(--text-secondary);
          font-size: 0.95rem;
        }
        .stacks-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
          gap: 1.5rem;
        }
      `}</style>
    </div>
  );
};
