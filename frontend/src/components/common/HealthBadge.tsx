import React from "react";
import { ShieldCheck, ShieldAlert, ShieldX } from "lucide-react";

interface HealthBadgeProps {
  score: number;
  status: string;
}

export const HealthBadge: React.FC<HealthBadgeProps> = ({ score, status }) => {
  let badgeClass = "badge-healthy";
  let Icon = ShieldCheck;

  if (score < 40 || status === "unhealthy") {
    badgeClass = "badge-unhealthy";
    Icon = ShieldX;
  } else if (score < 80 || status === "degraded") {
    badgeClass = "badge-degraded";
    Icon = ShieldAlert;
  }

  return (
    <div className={`badge ${badgeClass}`}>
      <Icon size={14} />
      <span>{score}% Health</span>
    </div>
  );
};
