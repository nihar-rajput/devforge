import React, { useState } from "react";
import { AlertTriangle, ShieldCheck, Send, X, Check } from "lucide-react";
import { api } from "../../api/client";

interface ErrorReporterModalProps {
  isOpen: boolean;
  packageId?: string | null;
  errorMessage: string;
  logSnippet?: string;
  onClose: () => void;
}

export const ErrorReporterModal: React.FC<ErrorReporterModalProps> = ({
  isOpen,
  packageId,
  errorMessage,
  logSnippet,
  onClose,
}) => {
  const [sending, setSending] = useState(false);
  const [sentReportId, setSentReportId] = useState<string | null>(null);

  if (!isOpen) return null;

  const payloadPreview = {
    app_version: "0.1.0",
    timestamp: new Date().toISOString(),
    error_type: "InstallationError",
    package_id: packageId || "system",
    os_info: "Windows x64",
    error_message: errorMessage,
    log_snippet: logSnippet || "No terminal logs recorded",
    user_consent: true,
  };

  const handleSendReport = async () => {
    setSending(true);
    try {
      const res = await api.sendErrorReport(payloadPreview);
      if (res.success) {
        setSentReportId(res.report_id);
      }
    } catch (e) {
      console.error("Telemetry report error:", e);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="glass-card modal-content">
        <div className="modal-header">
          <div className="title-box">
            <AlertTriangle size={22} color="var(--accent-rose)" />
            <h3>Send Error Diagnostic Report?</h3>
          </div>
          <button className="close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <p className="modal-desc">
          DevForge encountered an error during installation. Would you like to send an anonymized error report to help fix this issue?
        </p>

        <div className="privacy-badge">
          <ShieldCheck size={16} color="var(--accent-emerald)" />
          <span>
            <strong>Privacy Guarantee:</strong> No personal files, usernames, IP addresses, or passwords will ever be collected or sent.
          </span>
        </div>

        <div className="payload-box">
          <span className="box-label">JSON Payload Preview (What will be sent):</span>
          <pre className="json-preview">{JSON.stringify(payloadPreview, null, 2)}</pre>
        </div>

        {sentReportId ? (
          <div className="success-banner">
            <Check size={16} /> Error report <strong>#{sentReportId}</strong> sent successfully! Thank you for helping improve DevForge.
          </div>
        ) : (
          <div className="modal-actions">
            <button className="btn btn-secondary" onClick={onClose} disabled={sending}>
              Don't Send
            </button>
            <button className="btn btn-primary" onClick={handleSendReport} disabled={sending}>
              <Send size={15} /> {sending ? "Sending..." : "Grant Permission & Send Report"}
            </button>
          </div>
        )}
      </div>

      <style>{`
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.7);
          backdrop-filter: blur(8px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 200;
        }
        .modal-content {
          width: 540px;
          max-width: 90vw;
          display: flex;
          flex-direction: column;
          gap: 1.25rem;
          box-shadow: var(--shadow-glow);
          border-color: var(--accent-rose);
        }
        .modal-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        .title-box {
          display: flex;
          align-items: center;
          gap: 0.6rem;
        }
        .title-box h3 {
          font-size: 1.2rem;
          color: var(--text-primary);
        }
        .close-btn {
          background: transparent;
          border: none;
          color: var(--text-muted);
          cursor: pointer;
        }
        .modal-desc {
          font-size: 0.9rem;
          color: var(--text-secondary);
        }
        .privacy-badge {
          display: flex;
          align-items: center;
          gap: 0.6rem;
          background: hsla(155, 85%, 45%, 0.1);
          border: 1px solid hsla(155, 85%, 45%, 0.3);
          padding: 0.6rem 0.9rem;
          border-radius: var(--radius-sm);
          font-size: 0.8rem;
          color: var(--text-primary);
        }
        .payload-box {
          display: flex;
          flex-direction: column;
          gap: 0.4rem;
        }
        .box-label {
          font-size: 0.75rem;
          color: var(--text-muted);
        }
        .json-preview {
          background: var(--bg-terminal);
          color: var(--accent-cyan);
          padding: 0.8rem;
          border-radius: var(--radius-sm);
          font-family: var(--font-mono);
          font-size: 0.78rem;
          max-height: 180px;
          overflow-y: auto;
          border: 1px solid var(--border-glass);
        }
        .modal-actions {
          display: flex;
          justify-content: flex-end;
          gap: 0.75rem;
          padding-top: 0.5rem;
        }
        .success-banner {
          background: hsla(155, 85%, 45%, 0.2);
          color: var(--accent-emerald);
          padding: 0.75rem;
          border-radius: var(--radius-sm);
          font-size: 0.85rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
      `}</style>
    </div>
  );
};
