import * as React from "react";
import { Search, FileDown, Loader2, History, Briefcase, RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

import { TopNav } from "@/components/TopNav";
import { RiskAssessmentCard } from "@/components/RiskAssessmentCard";
import { HostingGeoPanel } from "@/components/HostingGeoPanel";
import { DomainIntelligenceCard } from "@/components/DomainIntelligenceCard";
import { SecurityConfigurationCard } from "@/components/SecurityConfigurationCard";
import { CaseReportsExports, type ReportItem } from "@/components/CaseReportsExports";
import { ReportDownloads } from "@/components/ReportDownloads";

// Import the real API client
import {
  analyzeDomain,
  generateReport,
  getScanHistory,
  getUserDetails,
  type AnalysisResponse,
  type ScanHistoryItem
} from "@/lib/api";

// Active case type (session-based)
interface ActiveCase {
  id: string;
  domain: string;
  risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  analyst_name: string;
  case_id: string;
  analyzed_at: string;
}

// Risk level badge component
function RiskLevelBadge({ level }: { level: "LOW" | "MEDIUM" | "HIGH" }) {
  const styles = {
    LOW: "bg-success/20 text-success border-success/30",
    MEDIUM: "bg-warning/20 text-warning border-warning/30",
    HIGH: "bg-destructive/20 text-destructive border-destructive/30",
  };

  return (
    <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-semibold uppercase tracking-[0.16em] ${styles[level]}`}>
      {level}
    </span>
  );
}

export function CyberInvestigationDashboard() {
  const [activeTab, setActiveTab] = React.useState<"Dashboard" | "Active Cases" | "History">("Dashboard");
  const [domain, setDomain] = React.useState("");
  const [user, setUser] = React.useState({ name: "Agent", org: "Cyber Cell" });
  const [analystName, setAnalystName] = React.useState("");
  const [caseId, setCaseId] = React.useState("");

  // Load user details on mount
  React.useEffect(() => {
    const userDetails = getUserDetails();
    setUser(userDetails);
    setAnalystName(userDetails.name);
  }, []);

  // Analysis state
  const [error, setError] = React.useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = React.useState(false);
  const [result, setResult] = React.useState<AnalysisResponse | null>(null);
  const [shouldFlyTo, setShouldFlyTo] = React.useState(false);

  // PDF generation state
  const [isGeneratingPdf, setIsGeneratingPdf] = React.useState(false);

  // Reports (PDF downloads this session)
  const [reports, setReports] = React.useState<ReportItem[]>([]);

  // Session-based active cases (analyses done in this session)
  const [activeCases, setActiveCases] = React.useState<ActiveCase[]>([]);

  // Persistent history from backend DB
  const [history, setHistory] = React.useState<ScanHistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = React.useState(false);
  const [historyError, setHistoryError] = React.useState<string | null>(null);

  // Cleanup blob URLs on unmount
  React.useEffect(() => {
    return () => {
      for (const r of reports) {
        if (r.url.startsWith("blob:")) URL.revokeObjectURL(r.url);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Load history when History tab is selected
  React.useEffect(() => {
    if (activeTab !== "History") return;
    loadHistory();
  }, [activeTab]);

  const loadHistory = async () => {
    setHistoryLoading(true);
    setHistoryError(null);

    try {
      const data = await getScanHistory(50);
      setHistory(data);
    } catch (err: unknown) {
      console.error("Failed to load history:", err);
      const message = err instanceof Error ? err.message : "Unknown error";
      setHistoryError(message);
    } finally {
      setHistoryLoading(false);
    }
  };

  // =========================================================================
  // REAL API CALL - Domain Analysis
  // =========================================================================
  const runAnalysis = async () => {
    const cleaned = domain.trim();
    if (!cleaned) {
      setError("Enter a domain or URL to analyze.");
      setResult(null);
      return;
    }

    const currentCaseId = caseId || `CASE-${Date.now()}`;
    const currentAnalyst = analystName || "Demo User";

    setError(null);
    setIsAnalyzing(true);
    setShouldFlyTo(false);
    setResult(null);

    try {
      // Call the FastAPI backend
      const data = await analyzeDomain({
        domain: cleaned,
        analyst_name: currentAnalyst,
        case_id: currentCaseId,
      });

      setResult(data);
      setShouldFlyTo(true);

      // Add to session-based active cases
      const newCase: ActiveCase = {
        id: crypto.randomUUID(),
        domain: cleaned,
        risk_score: data.risk_assessment.risk_score,
        risk_level: data.risk_assessment.risk_level,
        analyst_name: currentAnalyst,
        case_id: currentCaseId,
        analyzed_at: new Date().toISOString(),
      };
      setActiveCases(prev => [newCase, ...prev]);

    } catch (err: unknown) {
      console.error("❌ Analysis failed:", err);
      const message = err instanceof Error ? err.message : "Unknown error";
      setError(message || "Failed to analyze domain. Make sure the backend is running on http://localhost:8000");
    } finally {
      setIsAnalyzing(false);
    }
  };

  // =========================================================================
  // REAL API CALL - PDF Report Generation
  // =========================================================================
  const handleDownloadReport = async () => {
    if (!result) return;

    setIsGeneratingPdf(true);
    try {
      const url = await generateReport({
        domain: domain.trim(),
        analyst_name: analystName || "Demo User",
        case_id: caseId || `CASE-${Date.now()}`,
      });

      // Open the PDF in a new tab for download
      window.open(url, "_blank");

      // Also add to the reports list
      const ts = new Date();
      setReports((prev) => [
        {
          id: crypto.randomUUID(),
          fileName: `${domain.replace(/\./g, "_")}_report.pdf`,
          createdAtISO: ts.toISOString(),
          url,
          target: domain.trim(),
          status: "Ready",
          type: "PDF",
        },
        ...prev,
      ]);
    } catch (err: unknown) {
      console.error("❌ PDF generation failed:", err);
      const message = err instanceof Error ? err.message : "Unknown error";
      alert("Failed to generate report: " + message);
    } finally {
      setIsGeneratingPdf(false);
    }
  };

  return (
    <div className="min-h-screen bg-investigation-grid">
      <TopNav
        active={activeTab}
        onChangeActive={setActiveTab}
        userLabel={user.name}
        unitLabel={user.org}
      />

      {/* ================================================================= */}
      {/* HISTORY TAB - Persistent scan history from backend SQLite DB     */}
      {/* ================================================================= */}
      {activeTab === "History" ? (
        <main className="mx-auto w-full max-w-6xl space-y-6 px-4 py-6 sm:px-6">
          <Card className="surface-elevated">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <History className="h-4 w-4" />
                  <div className="text-sm font-semibold">Scan History</div>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={loadHistory}
                  disabled={historyLoading}
                >
                  {historyLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <RefreshCw className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <div className="mt-2 text-xs text-muted-foreground">
                Previous domain scans stored in the backend database.
              </div>
            </CardContent>
          </Card>

          <Card className="surface-elevated">
            <CardContent className="p-0">
              <div className="overflow-hidden rounded-xl border bg-background">
                {/* Table Header */}
                <div className="hidden grid-cols-12 gap-3 border-b bg-panel px-4 py-3 text-[11px] font-semibold text-muted-foreground sm:grid">
                  <div className="col-span-4">DOMAIN</div>
                  <div className="col-span-2">SCORE</div>
                  <div className="col-span-2">RISK</div>
                  <div className="col-span-2">ANALYST</div>
                  <div className="col-span-2">DATE</div>
                </div>

                {historyLoading ? (
                  <div className="p-6 text-center text-sm text-muted-foreground">
                    <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
                    Loading scan history...
                  </div>
                ) : historyError ? (
                  <div className="p-6 text-left text-sm">
                    <div className="font-medium text-destructive">Failed to load history</div>
                    <div className="mt-1 text-xs text-muted-foreground">{historyError}</div>
                    <div className="mt-2 text-xs text-muted-foreground">
                      Make sure the backend is running on http://localhost:8000
                    </div>
                  </div>
                ) : history.length === 0 ? (
                  <div className="p-6 text-left text-sm">
                    <div className="font-medium">No scan history</div>
                    <div className="mt-1 text-xs text-muted-foreground">
                      Analyzed domains will appear here after you run scans.
                    </div>
                  </div>
                ) : (
                  <ul className="divide-y">
                    {history.map((scan) => (
                      <li key={scan.id} className="p-4 hover:bg-panel/50 transition-colors">
                        <div className="grid grid-cols-1 gap-2 sm:grid-cols-12 sm:items-center sm:gap-3">
                          <div className="sm:col-span-4">
                            <div className="truncate text-xs font-semibold">{scan.domain}</div>
                            {scan.case_id && (
                              <div className="truncate text-[11px] text-muted-foreground">{scan.case_id}</div>
                            )}
                          </div>
                          <div className="sm:col-span-2">
                            <div className="text-sm font-bold">{scan.risk_score.toFixed(1)}/10</div>
                          </div>
                          <div className="sm:col-span-2">
                            <RiskLevelBadge level={scan.risk_level} />
                          </div>
                          <div className="sm:col-span-2">
                            <div className="truncate text-xs">{scan.analyst_name || "—"}</div>
                          </div>
                          <div className="sm:col-span-2">
                            <div className="text-xs text-muted-foreground">
                              {new Date(scan.scan_date).toLocaleDateString()}
                            </div>
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </CardContent>
          </Card>

          <div className="text-left text-xs text-muted-foreground">
            {history.length > 0
              ? `✅ Showing ${history.length} scans from backend database`
              : "History is fetched from the FastAPI backend SQLite database."
            }
          </div>
        </main>

        /* ================================================================= */
        /* ACTIVE CASES TAB - Session-based (domains analyzed this session) */
        /* ================================================================= */
      ) : activeTab === "Active Cases" ? (
        <main className="mx-auto w-full max-w-6xl space-y-6 px-4 py-6 sm:px-6">
          <Card className="surface-elevated">
            <CardContent className="p-6">
              <div className="flex items-center gap-2">
                <Briefcase className="h-4 w-4" />
                <div className="text-sm font-semibold">Active Cases (This Session)</div>
              </div>
              <div className="mt-2 text-xs text-muted-foreground">
                Domains you have analyzed during this browser session. {activeCases.length > 0 && `(${activeCases.length} case${activeCases.length !== 1 ? 's' : ''})`}
              </div>
            </CardContent>
          </Card>

          <Card className="surface-elevated">
            <CardContent className="p-0">
              <div className="overflow-hidden rounded-xl border bg-background">
                {/* Table Header */}
                <div className="hidden grid-cols-12 gap-3 border-b bg-panel px-4 py-3 text-[11px] font-semibold text-muted-foreground sm:grid">
                  <div className="col-span-3">CASE ID</div>
                  <div className="col-span-3">DOMAIN</div>
                  <div className="col-span-2">SCORE</div>
                  <div className="col-span-2">RISK</div>
                  <div className="col-span-2">ANALYZED</div>
                </div>

                {activeCases.length === 0 ? (
                  <div className="p-6 text-left text-sm">
                    <div className="font-medium">No active cases</div>
                    <div className="mt-1 text-xs text-muted-foreground">
                      Go to the Dashboard and analyze a domain to add it to your active cases.
                    </div>
                  </div>
                ) : (
                  <ul className="divide-y">
                    {activeCases.map((c) => (
                      <li key={c.id} className="p-4 hover:bg-panel/50 transition-colors">
                        <div className="grid grid-cols-1 gap-2 sm:grid-cols-12 sm:items-center sm:gap-3">
                          <div className="sm:col-span-3">
                            <div className="truncate text-xs font-semibold">{c.case_id}</div>
                            <div className="truncate text-[11px] text-muted-foreground">{c.analyst_name}</div>
                          </div>
                          <div className="sm:col-span-3">
                            <div className="truncate text-xs font-medium">{c.domain}</div>
                          </div>
                          <div className="sm:col-span-2">
                            <div className="text-sm font-bold">{c.risk_score.toFixed(1)}/10</div>
                          </div>
                          <div className="sm:col-span-2">
                            <RiskLevelBadge level={c.risk_level} />
                          </div>
                          <div className="sm:col-span-2">
                            <div className="text-xs text-muted-foreground">
                              {new Date(c.analyzed_at).toLocaleTimeString()}
                            </div>
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </CardContent>
          </Card>

          <CaseReportsExports items={reports} onGenerate={handleDownloadReport} />

          <div className="text-left text-xs text-muted-foreground">
            Active cases are stored in browser memory and will be cleared when you close the tab.
          </div>
        </main>

        /* ================================================================= */
        /* DASHBOARD TAB - Main analysis view                               */
        /* ================================================================= */
      ) : (
        <main className="mx-auto w-full max-w-6xl space-y-6 px-4 py-6 sm:px-6">
          {/* Search Card */}
          <Card className="surface-elevated">
            <CardContent className="p-6">
              <div className="flex items-center gap-2">
                <Search className="h-4 w-4" />
                <div className="text-sm font-semibold">New Investigation Query</div>
              </div>

              <div className="mt-4 grid gap-4 lg:grid-cols-12">
                <div className="lg:col-span-3">
                  <label
                    className="mb-1.5 block text-[11px] font-semibold tracking-[0.14em] text-muted-foreground"
                    htmlFor="analyst"
                  >
                    ANALYST NAME
                  </label>
                  <Input
                    id="analyst"
                    value={analystName}
                    onChange={(e) => setAnalystName(e.target.value)}
                    placeholder="Det. J. Doe"
                    className="bg-background"
                    autoComplete="off"
                  />
                </div>

                <div className="lg:col-span-3">
                  <label
                    className="mb-1.5 block text-[11px] font-semibold tracking-[0.14em] text-muted-foreground"
                    htmlFor="caseId"
                  >
                    CASE REFERENCE ID
                  </label>
                  <Input
                    id="caseId"
                    value={caseId}
                    onChange={(e) => setCaseId(e.target.value)}
                    placeholder="e.g., CASE-24-001"
                    className="bg-background"
                    autoComplete="off"
                  />
                </div>

                <div className="lg:col-span-4">
                  <label
                    className="mb-1.5 block text-[11px] font-semibold tracking-[0.14em] text-muted-foreground"
                    htmlFor="domain"
                  >
                    TARGET DOMAIN / URL
                  </label>
                  <Input
                    id="domain"
                    value={domain}
                    onChange={(e) => setDomain(e.target.value)}
                    placeholder="Enter domain (e.g., suspicious-site.net)"
                    className="bg-background"
                    autoComplete="off"
                    onKeyDown={(e) => e.key === "Enter" && runAnalysis()}
                  />
                </div>

                <div className="lg:col-span-2 lg:flex lg:items-end lg:gap-2">
                  <Button onClick={runAnalysis} disabled={isAnalyzing} className="h-10 flex-1">
                    {isAnalyzing ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <span className="text-[11px] font-semibold tracking-[0.14em]">ANALYZE</span>
                    )}
                  </Button>
                </div>
              </div>

              {/* Error Display */}
              {error && (
                <div className="mt-4 rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-left text-sm">
                  <span className="font-medium text-destructive">Error:</span>{" "}
                  <span className="text-muted-foreground">{error}</span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Results Section */}
          <section className="grid gap-6 lg:grid-cols-12">
            {/* Risk Assessment Card */}
            <Card className="surface-elevated lg:col-span-4">
              <CardContent className="p-6">
                {result ? (
                  <>
                    <RiskAssessmentCard
                      score={result.risk_assessment.risk_score}
                      level={result.risk_assessment.risk_level}
                      explanation={result.risk_assessment.explanation}
                      reasons={result.risk_assessment.reasons}
                    />
                    {/* Download Report Button */}
                    <Button
                      onClick={handleDownloadReport}
                      disabled={isGeneratingPdf}
                      className="mt-4 w-full"
                      variant="outline"
                    >
                      {isGeneratingPdf ? (
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      ) : (
                        <FileDown className="h-4 w-4 mr-2" />
                      )}
                      <span className="text-[11px] font-semibold tracking-[0.14em]">
                        {isGeneratingPdf ? "GENERATING..." : "DOWNLOAD PDF"}
                      </span>
                    </Button>
                  </>
                ) : (
                  <div className="space-y-3">
                    <div className="text-sm font-semibold">Safety Assessment</div>
                    <div className="rounded-xl border bg-panel p-6 text-left">
                      <div className="text-sm font-medium">Awaiting analysis</div>
                      <div className="mt-1 text-xs text-muted-foreground">
                        Enter a domain and click "ANALYZE" to compute safety score and populate infrastructure details.
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Hosting & Geo Panel */}
            <Card className="surface-elevated lg:col-span-8">
              <CardContent className="p-6">
                <HostingGeoPanel
                  targetUrl={domain}
                  flyTo={shouldFlyTo}
                  hostingInfo={result?.hosting_info}
                />
              </CardContent>
            </Card>
          </section>

          {/* Domain & Security Info Section */}
          <section className="grid gap-6 lg:grid-cols-12">
            <Card className="surface-elevated lg:col-span-4">
              <CardContent className="p-6">
                <DomainIntelligenceCard domainInfo={result?.domain_info} />
              </CardContent>
            </Card>

            <Card className="surface-elevated lg:col-span-8">
              <CardContent className="p-6">
                <SecurityConfigurationCard securityInfo={result?.security_info} />
              </CardContent>
            </Card>
          </section>

          <ReportDownloads items={reports} />

          <div className="text-left text-xs text-muted-foreground">
            {result
              ? `✅ Live data from FastAPI backend (${result.domain})`
              : "Data will be fetched from the FastAPI backend when you run an analysis."
            }
          </div>
        </main>
      )}
    </div>
  );
}
