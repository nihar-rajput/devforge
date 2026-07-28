import React, { useState } from "react";

interface FaqItem {
  question: string;
  answer: string;
}

const FAQS: FaqItem[] = [
  {
    question: "How does the LIFO Transaction Rollback Engine protect my computer?",
    answer: "Every installation step (downloading, extracting, registry edits, PATH appending) is logged as a transaction checkpoint. If an installer fails or an error occurs mid-way, DevForge automatically reverses every step in Last-In, First-Out (LIFO) order, restoring your PC to a clean state.",
  },
  {
    question: "Can I use DevForge on air-gapped computers with no internet access?",
    answer: "Yes! Use the Air-Gapped Offline Bundle Exporter to generate a `.zip` archive containing installer manifests, SHA-256 hashes, and 1-click `install_offline.bat` scripts. Take it on a USB drive to any offline machine.",
  },
  {
    question: "Does DevForge modify my Windows Registry or PATH safely?",
    answer: "Yes. DevForge writes to user-level environment PATH variables and broadcasts the Windows `WM_SETTINGCHANGE` system update event so new binaries are recognized immediately without requiring a PC reboot.",
  },
  {
    question: "How does privacy-preserving telemetry work?",
    answer: "DevForge scrubs all local user paths (e.g. `C:\\Users\\username\\` -> `C:\\Users\\<User>\\`) before submitting error logs. Telemetry is completely optional and strictly requires explicit user consent.",
  },
  {
    question: "Is DevForge 100% free and open-source?",
    answer: "Yes! DevForge is 100% open-source under the MIT License. You can inspect the source code, contribute plugins, or deploy custom internal bundles for enterprise teams.",
  },
];

export const FaqSection: React.FC = () => {
  const [openIdx, setOpenIdx] = useState<number | null>(0);

  const toggleFaq = (idx: number) => {
    setOpenIdx(openIdx === idx ? null : idx);
  };

  return (
    <section className="faq-section" style={{ maxWidth: "900px", margin: "4rem auto", padding: "0 1.5rem" }}>
      <div className="section-header" style={{ textAlign: "center", marginBottom: "2.5rem" }}>
        <h2 className="section-title">
          Frequently Asked <span className="gradient-text">Questions</span>
        </h2>
        <p className="section-subtitle">
          Everything you need to know about DevForge features and security architecture.
        </p>
      </div>

      <div className="faq-list" style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {FAQS.map((faq, idx) => {
          const isOpen = openIdx === idx;
          return (
            <div
              key={idx}
              className="glass-card"
              style={{ cursor: "pointer", transition: "all 0.2s" }}
              onClick={() => toggleFaq(idx)}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontWeight: "700", fontSize: "1.1rem" }}>
                <span>{faq.question}</span>
                <span style={{ color: "var(--accent-cyan)", fontSize: "1.2rem" }}>{isOpen ? "−" : "+"}</span>
              </div>
              {isOpen && (
                <p style={{ marginTop: "0.8rem", color: "var(--text-secondary)", lineHeight: "1.6", fontSize: "0.95rem" }}>
                  {faq.answer}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
};
