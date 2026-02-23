import * as React from "react";
import { AlertTriangle, ShieldAlert, ShieldCheck } from "lucide-react";

// Props interface for dynamic Safety Score (1.0 - 10.0)
interface RiskAssessmentCardProps {
  score: number;                            // 1.0 to 10.0 Safety Score
  level: "LOW" | "MEDIUM" | "HIGH";         // Risk level from backend
  explanation?: string;                     // AI-generated explanation
  reasons?: string[];                       // List of penalty reasons
}

// Get visual styling based on risk level
function getStyleConfig(level: "LOW" | "MEDIUM" | "HIGH") {
  switch (level) {
    case "LOW":
      return {
        Icon: ShieldCheck,
        pillClass: "bg-success text-success-foreground border-success/20",
        scoreColor: "text-green-500",
        headline: "SAFE",
        headlineColor: "text-green-600",
      };
    case "MEDIUM":
      return {
        Icon: AlertTriangle,
        pillClass: "bg-warning text-warning-foreground border-warning/20",
        scoreColor: "text-yellow-500",
        headline: "CAUTION",
        headlineColor: "text-yellow-600",
      };
    case "HIGH":
      return {
        Icon: ShieldAlert,
        pillClass: "bg-destructive text-destructive-foreground border-destructive/20",
        scoreColor: "text-red-500",
        headline: "DANGER",
        headlineColor: "text-red-600",
      };
  }
}

export function RiskAssessmentCard({
  score,
  level,
  explanation,
  reasons = []
}: RiskAssessmentCardProps) {
  const style = getStyleConfig(level);
  const Icon = style.Icon;

  return (
    <div className="space-y-4">
      {/* Header with icon and risk pill */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon className="h-4 w-4" />
          <div className="text-sm font-semibold">Safety Assessment</div>
        </div>
        <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-semibold ${style.pillClass}`}>
          {level === "HIGH" ? "CRITICAL" : level}
        </span>
      </div>

      {/* Score Display - 1-10 Scale */}
      <div className="grid place-items-center rounded-lg border bg-background p-6">
        <div className="text-center">
          <div className="flex items-end justify-center gap-2">
            <span className={`text-5xl font-bold ${style.scoreColor}`}>
              {score.toFixed(1)}
            </span>
            <span className="text-xl text-muted-foreground mb-1">/ 10</span>
          </div>
          <div className={`mt-2 text-xs font-semibold tracking-[0.18em] ${style.headlineColor}`}>
            {style.headline}
          </div>
        </div>
      </div>

      {/* Explanation */}
      {explanation && (
        <div className="rounded-lg border bg-panel p-3">
          <div className="text-sm">{explanation}</div>
        </div>
      )}

      {/* Penalty Reasons */}
      {reasons.length > 0 && (
        <div className="space-y-2">
          <div className="text-xs font-semibold text-muted-foreground tracking-wide">
            CONTRIBUTING FACTORS
          </div>
          {reasons.map((reason, idx) => (
            <div key={idx} className="rounded-lg border bg-panel p-3">
              <div className="text-sm text-muted-foreground">{reason}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
