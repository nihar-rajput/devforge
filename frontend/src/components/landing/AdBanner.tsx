import React, { useEffect } from "react";

export interface AdBannerProps {
  type?: "adsense" | "carbon" | "sponsor";
  adClient?: string; // e.g. "ca-pub-1234567890"
  adSlot?: string;   // e.g. "1234567890"
  className?: string;
}

export const AdBanner: React.FC<AdBannerProps> = ({
  type = "sponsor",
  adClient,
  adSlot,
  className = "",
}) => {

  useEffect(() => {
    if (type === "adsense" && adClient && adSlot) {
      try {
        // @ts-ignore
        (window.adsbygoogle = window.adsbygoogle || []).push({});
      } catch (err) {
        console.error("AdSense error:", err);
      }
    }
  }, [type, adClient, adSlot]);

  if (type === "adsense" && adClient && adSlot) {
    return (
      <div className={`ad-container ${className}`}>
        <span className="ad-badge">SPONSORED</span>
        <ins
          className="adsbygoogle"
          style={{ display: "block", minHeight: "90px" }}
          data-ad-client={adClient}
          data-ad-slot={adSlot}
          data-ad-format="auto"
          data-full-width-responsive="true"
        />
      </div>
    );
  }

  // Default Developer Sponsor / Affiliate Banner Fallback
  return (
    <div className={`ad-sponsor-banner ${className}`}>
      <div className="ad-sponsor-content">
        <span className="ad-badge">DEVELOPER SPONSOR</span>
        <div className="ad-sponsor-text">
          ⚡ <strong>DevForge Air-Gapped Mode</strong>: Deploy pre-configured offline bundles to air-gapped workstations in minutes.
        </div>
      </div>
      <a
        href="https://github.com/nihar-rajput/devforge"
        target="_blank"
        rel="noopener noreferrer"
        className="ad-sponsor-btn"
      >
        ⭐ Sponsor on GitHub
      </a>
    </div>
  );
};
