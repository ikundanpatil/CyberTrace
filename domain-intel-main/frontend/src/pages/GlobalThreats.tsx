import * as React from "react";
import { useState, useMemo } from "react";
import { Globe, MapPin, AlertTriangle, Loader2, Shield, Flag, Search, X } from "lucide-react";
import { DEMO_MAP_DATA, type ThreatPoint } from "@/lib/api";
import { ThreatMap } from "@/components/ThreatMap";
import { ThreatStatsCharts } from "@/components/ThreatStatsCharts";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function GlobalThreats() {
    // Search state
    const [searchTerm, setSearchTerm] = useState("");
    const [isRefreshing, setIsRefreshing] = useState(false);

    // Filter threats by search term (city or type)
    const filteredData = useMemo(() => {
        if (!searchTerm.trim()) return DEMO_MAP_DATA;

        return DEMO_MAP_DATA.filter((item) =>
            item.city.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.type.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }, [searchTerm]);

    // Calculate dynamic stats from filtered data
    const stats = useMemo(() => {
        // Total count
        const total = filteredData.length;

        // High Alert Zone - most frequent city in filtered data
        const cityCount = filteredData.reduce((acc: Record<string, number>, curr) => {
            acc[curr.city] = (acc[curr.city] || 0) + 1;
            return acc;
        }, {});

        const topCity = Object.entries(cityCount)
            .sort(([, a], [, b]) => b - a)[0];

        const highAlertZone = searchTerm
            ? (topCity ? topCity[0] : "N/A")
            : "Jamtara, JH";

        const highAlertCount = topCity ? topCity[1] : 0;

        // Top Threat Category - most frequent type in filtered data
        const typeCount = filteredData.reduce((acc: Record<string, number>, curr) => {
            acc[curr.type] = (acc[curr.type] || 0) + 1;
            return acc;
        }, {});

        const topType = Object.entries(typeCount)
            .sort(([, a], [, b]) => b - a)[0];

        const topThreatCategory = topType ? topType[0] : "N/A";
        const topThreatCount = topType ? topType[1] : 0;

        // Critical threats count
        const criticalCount = filteredData.filter(
            (item) => item.severity === "Critical"
        ).length;

        return {
            total,
            highAlertZone,
            highAlertCount,
            topThreatCategory,
            topThreatCount,
            criticalCount,
        };
    }, [filteredData, searchTerm]);

    const handleRefresh = () => {
        setIsRefreshing(true);
        setTimeout(() => setIsRefreshing(false), 1000);
    };

    const clearSearch = () => {
        setSearchTerm("");
    };

    return (
        <div className="min-h-screen bg-background">
            {/* Header */}
            <header className="border-b bg-background/80 backdrop-blur sticky top-0 z-10">
                <div className="mx-auto flex w-full max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-orange-500/10 rounded-lg">
                            <Flag className="h-6 w-6 text-orange-500" />
                        </div>
                        <div>
                            <h1 className="text-lg font-bold text-foreground flex items-center gap-2">
                                🇮🇳 National Cybercrime Surveillance
                                <span className="text-xs bg-orange-500/20 text-orange-400 px-2 py-0.5 rounded-full font-medium">
                                    INDIA
                                </span>
                            </h1>
                            <p className="text-xs text-muted-foreground">
                                Real-time threat monitoring • I4C Integration
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        {/* Search Input */}
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                            <Input
                                type="text"
                                placeholder="Filter by city or threat..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="pl-9 pr-8 w-[240px] h-9 bg-panel border-border/50 text-sm"
                            />
                            {searchTerm && (
                                <button
                                    onClick={clearSearch}
                                    className="absolute right-2 top-1/2 -translate-y-1/2 p-1 hover:bg-muted rounded"
                                >
                                    <X className="h-3 w-3 text-muted-foreground" />
                                </button>
                            )}
                        </div>

                        {/* Live Feed Indicator */}
                        <div className="hidden sm:flex items-center gap-2 px-3 py-1 bg-green-900/30 border border-green-500/50 rounded-full">
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                            </span>
                            <span className="text-xs font-medium text-green-400">LIVE</span>
                        </div>

                        <Button
                            variant="outline"
                            size="sm"
                            onClick={handleRefresh}
                            disabled={isRefreshing}
                        >
                            {isRefreshing ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                                <Shield className="h-4 w-4" />
                            )}
                            <span className="ml-2 hidden sm:inline">Refresh</span>
                        </Button>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => (window.location.href = "/")}
                        >
                            ← Dashboard
                        </Button>
                    </div>
                </div>
            </header>

            <main className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 space-y-6">
                {/* Search Results Banner */}
                {searchTerm && (
                    <div className="flex items-center justify-between bg-primary/10 border border-primary/30 rounded-lg px-4 py-2">
                        <div className="flex items-center gap-2 text-sm">
                            <Search className="h-4 w-4 text-primary" />
                            <span className="text-muted-foreground">Filtering:</span>
                            <span className="bg-primary/20 text-primary px-2 py-0.5 rounded font-medium">
                                "{searchTerm}"
                            </span>
                            <span className="text-muted-foreground">
                                → {filteredData.length} of {DEMO_MAP_DATA.length} threats
                            </span>
                        </div>
                        <button
                            onClick={clearSearch}
                            className="text-xs text-destructive hover:underline flex items-center gap-1"
                        >
                            <X className="h-3 w-3" /> Clear Filter
                        </button>
                    </div>
                )}

                {/* Stats Cards Row */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Total Threats */}
                    <Card className="surface-elevated border-orange-500/20">
                        <CardContent className="p-5">
                            <div className="flex items-center gap-4">
                                <div className="p-3 bg-destructive/10 rounded-xl">
                                    <AlertTriangle className="h-6 w-6 text-destructive" />
                                </div>
                                <div>
                                    <p className="text-xs text-muted-foreground uppercase tracking-wider font-medium">
                                        {searchTerm ? "Filtered Threats" : "Total Threats"}
                                    </p>
                                    <p className="text-3xl font-bold text-foreground">
                                        {stats.total}
                                    </p>
                                    {stats.criticalCount > 0 && (
                                        <p className="text-xs text-destructive">
                                            {stats.criticalCount} critical
                                        </p>
                                    )}
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* High Alert Zone */}
                    <Card className="surface-elevated border-warning/30 bg-warning/5">
                        <CardContent className="p-5">
                            <div className="flex items-center gap-4">
                                <div className="p-3 bg-warning/20 rounded-xl">
                                    <MapPin className="h-6 w-6 text-warning" />
                                </div>
                                <div>
                                    <p className="text-xs text-warning uppercase tracking-wider font-bold flex items-center gap-1">
                                        🚨 High Alert Zone
                                    </p>
                                    <p className="text-2xl font-bold text-foreground">
                                        {stats.highAlertZone}
                                    </p>
                                    <p className="text-xs text-muted-foreground">
                                        {stats.highAlertCount} active threats
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Top Threat Category */}
                    <Card className="surface-elevated">
                        <CardContent className="p-5">
                            <div className="flex items-center gap-4">
                                <div className="p-3 bg-primary/10 rounded-xl">
                                    <Globe className="h-6 w-6 text-primary" />
                                </div>
                                <div>
                                    <p className="text-xs text-muted-foreground uppercase tracking-wider font-medium">
                                        Top Threat Type
                                    </p>
                                    <p className="text-xl font-bold text-foreground">
                                        {stats.topThreatCategory}
                                    </p>
                                    <p className="text-xs text-muted-foreground">
                                        {stats.topThreatCount} incidents
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Threat Map */}
                <Card className="surface-elevated overflow-hidden">
                    <CardContent className="p-0">
                        <div className="p-4 border-b border-border/50 flex items-center justify-between">
                            <div>
                                <h2 className="text-sm font-semibold text-foreground uppercase tracking-wider flex items-center gap-2">
                                    🗺️ Cybercrime Hotspot Map
                                </h2>
                                <p className="text-xs text-muted-foreground mt-1">
                                    {filteredData.length} threat zones displayed
                                </p>
                            </div>
                            <div className="text-xs text-muted-foreground bg-panel px-3 py-1 rounded-full">
                                Source: NCRP • I4C • State Cyber Cells
                            </div>
                        </div>
                        <ThreatMap data={filteredData} height="520px" />
                    </CardContent>
                </Card>

                {/* Dynamic Stats Charts */}
                <div>
                    <h2 className="text-sm font-semibold text-foreground uppercase tracking-wider mb-4 flex items-center gap-2">
                        📊 Threat Analysis {searchTerm && `(${filteredData.length} results)`}
                    </h2>
                    <ThreatStatsCharts data={filteredData} />
                </div>
            </main>
        </div>
    );
}
