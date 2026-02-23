import { Lock, ShieldCheck, ShieldX, ShieldAlert, Network, CheckCircle2, XCircle } from "lucide-react";
import type { SecurityInfo } from "@/lib/api";

interface SecurityConfigurationCardProps {
  securityInfo?: SecurityInfo;
}

function Chip({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center gap-2 rounded-md border bg-panel px-2 py-1 text-[11px] text-muted-foreground">
      {children}
    </span>
  );
}

function StatusBadge({ isSecure }: { isSecure: boolean }) {
  if (isSecure) {
    return (
      <div className="flex items-center gap-2 rounded-lg border border-success/30 bg-success/10 px-3 py-2">
        <ShieldCheck className="h-5 w-5 text-success" />
        <div>
          <div className="text-sm font-semibold text-success">Secure</div>
          <div className="text-[11px] text-muted-foreground">HTTPS enabled with valid SSL</div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2">
      <ShieldX className="h-5 w-5 text-destructive" />
      <div>
        <div className="text-sm font-semibold text-destructive">Insecure</div>
        <div className="text-[11px] text-muted-foreground">HTTPS missing or SSL invalid</div>
      </div>
    </div>
  );
}

// Format SSL expiry date and show days remaining
function formatSslExpiry(expiryStr?: string): { display: string; isWarning: boolean } {
  if (!expiryStr) return { display: "—", isWarning: false };

  try {
    const expiry = new Date(expiryStr);
    if (isNaN(expiry.getTime())) return { display: expiryStr, isWarning: false };

    const now = new Date();
    const diffMs = expiry.getTime() - now.getTime();
    const daysLeft = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    const dateStr = expiry.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });

    if (daysLeft < 0) {
      return { display: `EXPIRED (${dateStr})`, isWarning: true };
    } else if (daysLeft < 30) {
      return { display: `${dateStr} (${daysLeft} days left!)`, isWarning: true };
    } else {
      return { display: `${dateStr} (${daysLeft} days left)`, isWarning: false };
    }
  } catch {
    return { display: expiryStr, isWarning: false };
  }
}

export function SecurityConfigurationCard({ securityInfo }: SecurityConfigurationCardProps) {
  const hasData = Boolean(securityInfo);
  const isSecure = securityInfo?.https_enabled && securityInfo?.ssl_valid;
  const sslExpiry = formatSslExpiry(securityInfo?.ssl_expiry);

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <ShieldCheck className="h-4 w-4" />
        <div className="text-sm font-semibold">Security &amp; Configuration</div>
      </div>

      {hasData ? (
        <div className="rounded-xl border bg-background p-4">
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Left Column - SSL Status */}
            <div className="space-y-4">
              {/* Security Badge */}
              <StatusBadge isSecure={isSecure ?? false} />

              {/* SSL Details */}
              <div className="space-y-3">
                <div className="text-[11px] font-semibold tracking-[0.14em] text-muted-foreground">
                  SSL CERTIFICATE
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">HTTPS Enabled</span>
                    <span className="flex items-center gap-1 font-medium">
                      {securityInfo?.https_enabled ? (
                        <><CheckCircle2 className="h-3.5 w-3.5 text-success" /> Yes</>
                      ) : (
                        <><XCircle className="h-3.5 w-3.5 text-destructive" /> No</>
                      )}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">SSL Valid</span>
                    <span className="flex items-center gap-1 font-medium">
                      {securityInfo?.ssl_valid ? (
                        <><CheckCircle2 className="h-3.5 w-3.5 text-success" /> Yes</>
                      ) : (
                        <><XCircle className="h-3.5 w-3.5 text-destructive" /> No</>
                      )}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">Issuer</span>
                    <span className="font-medium">{securityInfo?.ssl_issuer || "—"}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">Expiry</span>
                    <span className={`font-medium ${sslExpiry.isWarning ? "text-warning" : ""}`}>
                      {sslExpiry.display}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column - Blacklist Status */}
            <div className="space-y-4">
              <div className="text-[11px] font-semibold tracking-[0.14em] text-muted-foreground">
                THREAT INTELLIGENCE
              </div>

              {securityInfo?.blacklisted ? (
                <div className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2">
                  <ShieldAlert className="h-5 w-5 text-destructive" />
                  <div>
                    <div className="text-sm font-semibold text-destructive">Blacklisted</div>
                    <div className="text-[11px] text-muted-foreground">
                      Found in threat databases
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-2 rounded-lg border border-success/30 bg-success/10 px-3 py-2">
                  <ShieldCheck className="h-5 w-5 text-success" />
                  <div>
                    <div className="text-sm font-semibold text-success">Clean</div>
                    <div className="text-[11px] text-muted-foreground">
                      Not found in blacklists
                    </div>
                  </div>
                </div>
              )}

              {/* Blacklist Sources */}
              {securityInfo?.blacklisted && securityInfo.blacklist_sources && securityInfo.blacklist_sources.length > 0 && (
                <div className="space-y-2">
                  <div className="text-xs text-muted-foreground">Found in:</div>
                  <div className="flex flex-wrap gap-2">
                    {securityInfo.blacklist_sources.map((source, idx) => (
                      <Chip key={idx}>
                        <span className="text-destructive">{source}</span>
                      </Chip>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="rounded-xl border bg-panel p-6 text-center">
          <Lock className="h-8 w-8 mx-auto mb-2 text-muted-foreground opacity-50" />
          <div className="text-sm font-medium text-muted-foreground">Awaiting data</div>
          <div className="mt-1 text-xs text-muted-foreground">
            Security configuration will appear after analysis
          </div>
        </div>
      )}
    </div>
  );
}
