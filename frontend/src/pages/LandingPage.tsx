import React from "react";
import { HeroSection } from "../components/landing/HeroSection";
import { StackWizardSection } from "../components/landing/StackWizardSection";
import { PackageCatalogSection } from "../components/landing/PackageCatalogSection";
import { AdBanner } from "../components/landing/AdBanner";

interface LandingPageProps {
  onOpenApp?: () => void;
  onOpenCustomBuilder?: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onOpenApp, onOpenCustomBuilder }) => {
  return (
    <div className="landing-page-container">
      {/* Top Header Navigation */}
      <header className="landing-nav">
        <div className="nav-logo">
          <span className="logo-icon">⚡</span>
          <span className="logo-text">DevForge</span>
          <span className="logo-badge">v1.0.0</span>
        </div>
        <div className="nav-links">
          {onOpenCustomBuilder && (
            <button className="chip-btn" onClick={onOpenCustomBuilder} style={{ borderColor: "var(--accent-purple)", color: "#fff" }}>
              🛠️ Custom 36-Tool Builder
            </button>
          )}
          <a href="#wizard" className="nav-link">Stack Wizard</a>
          <a href="#catalog" className="nav-link">36 Tools Catalog</a>
          <a href="https://github.com/nihar-rajput/devforge" target="_blank" rel="noopener noreferrer" className="nav-link">GitHub</a>
          {onOpenApp && (
            <button className="nav-app-btn" onClick={onOpenApp}>
              Launch Web Dashboard 🚀
            </button>
          )}
        </div>
      </header>

      {/* Top Sponsored Ad Banner */}
      <div className="landing-ad-wrapper">
        <AdBanner type="sponsor" />
      </div>

      {/* Hero Section */}
      <HeroSection />

      {/* Interactive Stack Wizard Section */}
      <div id="wizard">
        <StackWizardSection />
      </div>

      {/* Middle Sponsored Ad Banner */}
      <div className="landing-ad-wrapper">
        <AdBanner type="sponsor" />
      </div>

      {/* Package Catalog Grid Section */}
      <div id="catalog">
        <PackageCatalogSection />
      </div>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-left">
            <span className="logo-text">DevForge Platform</span>
            <p className="footer-copy">
              Universal cross-platform developer environment manager. Open-source MIT License.
            </p>
          </div>
          <div className="footer-right">
            <a href="https://github.com/nihar-rajput/devforge" target="_blank" rel="noopener noreferrer">GitHub Releases</a>
            <a href="https://github.com/nihar-rajput/devforge/blob/main/docs/installation_and_usage_guide.md" target="_blank" rel="noopener noreferrer">Documentation</a>
          </div>
        </div>
      </footer>
    </div>
  );
};
