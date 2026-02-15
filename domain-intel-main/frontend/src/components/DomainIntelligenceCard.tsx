import { Shield, Calendar, Building, Globe, Server } from "lucide-react";
import type { DomainInfo } from "@/lib/api";

interface DomainIntelligenceCardProps {
  domainInfo?: DomainInfo;
}

// Helper to format dates nicely
function formatDate(dateStr?: string): string {
  if (!dateStr) return "—";
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return dateStr; // Return original if invalid
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return dateStr;
  }
}

// Calculate domain age in human-readable format
function getDomainAge(creationDate?: string): string {
  if (!creationDate) return "—";
  try {
    const created = new Date(creationDate);
    if (isNaN(created.getTime())) return "—";

    const now = new Date();
    const diffMs = now.getTime() - created.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays < 7) return `${diffDays} days (Very New!)`;
    if (diffDays < 30) return `${diffDays} days (Recent)`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months`;
    return `${Math.floor(diffDays / 365)} years`;
  } catch {
    return "—";
  }
}

export function DomainIntelligenceCard({ domainInfo }: DomainIntelligenceCardProps) {
  const hasData = Boolean(domainInfo);

  const rows: Array<{
    label: string;
    value: string;
    icon: React.ReactNode;
    highlight?: boolean;
  }> = [
      {
        label: "Registrar",
        value: domainInfo?.registrar || "—",
        icon: <Building className="h-3.5 w-3.5" />,
      },
      {
        label: "Creation Date",
        value: formatDate(domainInfo?.creation_date),
        icon: <Calendar className="h-3.5 w-3.5" />,
      },
      {
        label: "Expiry Date",
        value: formatDate(domainInfo?.expiry_date),
        icon: <Calendar className="h-3.5 w-3.5" />,
      },
      {
        label: "Domain Age",
        value: getDomainAge(domainInfo?.creation_date),
        icon: <Globe className="h-3.5 w-3.5" />,
        highlight: domainInfo?.domain_age_days !== undefined && domainInfo.domain_age_days < 30,
      },
    ];

  // Add nameservers if available
  const nameservers = domainInfo?.nameservers || [];

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Shield className="h-4 w-4" />
        <div className="text-sm font-semibold">Domain Intelligence</div>
      </div>

      {hasData ? (
        <>
          <div className="rounded-xl border bg-background">
            <dl className="divide-y">
              {rows.map((r) => (
                <div key={r.label} className="flex items-center justify-between gap-4 p-4">
                  <dt className="flex items-center gap-2 text-xs text-muted-foreground">
                    {r.icon}
                    {r.label}
                  </dt>
                  <dd className={`text-xs font-medium ${r.highlight ? "text-warning" : "text-foreground"}`}>
                    {r.value}
                  </dd>
                </div>
              ))}
            </dl>
          </div>

          {/* Nameservers */}
          {nameservers.length > 0 && (
            <div className="rounded-xl border bg-background p-4">
              <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
                <Server className="h-3.5 w-3.5" />
                Nameservers
              </div>
              <div className="flex flex-wrap gap-2">
                {nameservers.slice(0, 4).map((ns, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center rounded-md border bg-panel px-2 py-1 text-[11px] font-medium"
                  >
                    {ns}
                  </span>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="rounded-xl border bg-panel p-6 text-center">
          <div className="text-sm font-medium text-muted-foreground">Awaiting data</div>
          <div className="mt-1 text-xs text-muted-foreground">
            WHOIS information will appear after analysis
          </div>
        </div>
      )}
    </div>
  );
}
