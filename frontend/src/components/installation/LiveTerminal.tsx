import React, { useRef, useEffect } from "react";
import { LogLine } from "../../hooks/useInstallation";

interface LiveTerminalProps {
  logs: LogLine[];
}

export const LiveTerminal: React.FC<LiveTerminalProps> = ({ logs }) => {
  const terminalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="terminal-container" ref={terminalRef}>
      <div className="terminal-header">
        <span className="dot red"></span>
        <span className="dot yellow"></span>
        <span className="dot green"></span>
        <span className="terminal-title">DevForge Installation Stream</span>
      </div>

      <div className="terminal-body">
        {logs.length === 0 ? (
          <div className="empty-logs">Waiting for installation activity...</div>
        ) : (
          logs.map((log) => (
            <div key={log.id} className="log-line">
              <span className="time">[{log.timestamp}]</span>
              <span className={`tag ${log.type.toLowerCase()}`}>{log.type}</span>
              <span className="msg">{log.message}</span>
            </div>
          ))
        )}
      </div>

      <style>{`
        .terminal-container {
          background: var(--bg-terminal);
          border: 1px solid var(--border-glass-strong);
          border-radius: var(--radius-md);
          overflow: hidden;
          font-family: var(--font-mono);
          font-size: 0.82rem;
          max-height: 260px;
          display: flex;
          flex-direction: column;
        }
        .terminal-header {
          background: hsla(224, 30%, 10%, 0.8);
          padding: 0.5rem 0.8rem;
          display: flex;
          align-items: center;
          gap: 0.4rem;
          border-bottom: 1px solid var(--border-glass);
        }
        .dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
        }
        .dot.red { background: #ff5f56; }
        .dot.yellow { background: #ffbd2e; }
        .dot.green { background: #27c93f; }
        .terminal-title {
          margin-left: 0.5rem;
          font-size: 0.75rem;
          color: var(--text-muted);
        }
        .terminal-body {
          padding: 0.8rem;
          overflow-y: auto;
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 0.35rem;
        }
        .empty-logs {
          color: var(--text-muted);
          font-style: italic;
        }
        .log-line {
          display: flex;
          gap: 0.6rem;
        }
        .log-line .time {
          color: var(--text-muted);
        }
        .log-line .tag {
          color: var(--accent-cyan);
          font-weight: 600;
        }
        .log-line .msg {
          color: var(--text-primary);
        }
      `}</style>
    </div>
  );
};
