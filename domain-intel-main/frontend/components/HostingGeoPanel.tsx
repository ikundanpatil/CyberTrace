import * as React from "react";
import { Crosshair, Globe2, Loader2, MapPin } from "lucide-react";
import { InteractiveGeoMap } from "@/components/InteractiveGeoMap";
import type { HostingInfo } from "@/lib/api";

type HostingGeoPanelProps = {
  targetUrl?: string;
  flyTo?: boolean;
  hostingInfo?: HostingInfo;  // Real data from backend
};

function formatCoords(lat?: number, lon?: number) {
  if (typeof lat !== "number" || typeof lon !== "number") return "—";
  const ns = lat >= 0 ? "N" : "S";
  const ew = lon >= 0 ? "E" : "W";
  return `${Math.abs(lat).toFixed(4)}°${ns}, ${Math.abs(lon).toFixed(4)}°${ew}`;
}

// Approximate coordinates for known countries (fallback when lat/lon not provided)
const COUNTRY_COORDS: Record<string, { lat: number; lon: number }> = {
  US: { lat: 37.0902, lon: -95.7129 },
  IN: { lat: 20.5937, lon: 78.9629 },
  CN: { lat: 35.8617, lon: 104.1954 },
  RU: { lat: 61.5240, lon: 105.3188 },
  DE: { lat: 51.1657, lon: 10.4515 },
  GB: { lat: 55.3781, lon: -3.4360 },
  JP: { lat: 36.2048, lon: 138.2529 },
  FR: { lat: 46.2276, lon: 2.2137 },
  AU: { lat: -25.2744, lon: 133.7751 },
  BR: { lat: -14.2350, lon: -51.9253 },
  NL: { lat: 52.1326, lon: 5.2913 },
  SG: { lat: 1.3521, lon: 103.8198 },
};

export function HostingGeoPanel({ targetUrl, flyTo = false, hostingInfo }: HostingGeoPanelProps) {
  // Extract coordinates from hostingInfo or use country fallback
  const coords = React.useMemo(() => {
    // If we have explicit lat/lon from backend
    if (hostingInfo && typeof (hostingInfo as any).lat === "number") {
      return { lat: (hostingInfo as any).lat, lon: (hostingInfo as any).lon };
    }

    // Fallback to country code lookup
    if (hostingInfo?.country_code) {
      const countryCoords = COUNTRY_COORDS[hostingInfo.country_code.toUpperCase()];
      if (countryCoords) return countryCoords;
    }

    // Default to India
    return { lat: 20.5937, lon: 78.9629 };
  }, [hostingInfo]);

  const hasData = Boolean(hostingInfo?.ip_address);
  const location = hostingInfo?.city && hostingInfo?.country
    ? `${hostingInfo.city}, ${hostingInfo.country}`
    : hostingInfo?.country || "Unknown";

  // Build marker for the map
  const markers = React.useMemo(() => {
    if (!hasData) return [];
    return [{
      id: hostingInfo?.ip_address || "primary",
      latitude: coords.lat,
      longitude: coords.lon,
      title: location,
      subtitle: hostingInfo?.ip_address,
      metaLines: [
        hostingInfo?.asn ? `ASN: ${hostingInfo.asn}` : "",
        hostingInfo?.organization ? `Org: ${hostingInfo.organization}` : "",
        hostingInfo?.isp ? `ISP: ${hostingInfo.isp}` : "",
      ].filter(Boolean),
    }];
  }, [hasData, hostingInfo, coords, location]);

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Globe2 className="h-4 w-4" />
          <div className="text-sm font-semibold">Hosting &amp; Geo-Location</div>
        </div>
        <div className="text-xs text-muted-foreground">
          {hostingInfo?.ip_address ? (
            <>IP: {hostingInfo.ip_address}</>
          ) : (
            "—"
          )}
        </div>
      </div>

      <div className="relative overflow-hidden rounded-xl border bg-background h-[400px] sm:h-[480px] md:h-[520px]">
        {hasData ? (
          <InteractiveGeoMap
            markers={markers}
            flyTo={flyTo}
            latitude={coords.lat}
            longitude={coords.lon}
            location={location}
            onMarkerSelect={() => { }}
          />
        ) : (
          <div className="flex h-full items-center justify-center">
            <div className="text-center text-muted-foreground">
              <MapPin className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <div className="text-sm">No geo data available</div>
              <div className="text-xs">Run an analysis to see hosting location</div>
            </div>
          </div>
        )}

        {/* Meta strip */}
        {hasData && (
          <div className="mx-4 mt-4 flex flex-wrap items-center justify-between gap-2 rounded-xl border bg-panel/90 px-3 py-2 backdrop-blur sm:absolute sm:left-4 sm:top-4 sm:right-4 sm:mx-0 sm:mt-0 z-[1000]">
            <div className="flex items-center gap-2 text-xs">
              <Crosshair className="h-4 w-4 text-muted-foreground" />
              <div className="font-medium">{formatCoords(coords.lat, coords.lon)}</div>
              <span className="text-muted-foreground">•</span>
              <div className="font-medium">{hostingInfo?.country_code || "—"}</div>
            </div>
          </div>
        )}

        {/* Facts card */}
        {hasData && (
          <div className="mx-4 mt-3 w-auto max-w-none rounded-xl border bg-panel/90 p-4 backdrop-blur sm:absolute sm:bottom-4 sm:right-4 sm:mx-0 sm:mt-0 sm:w-[320px] sm:max-w-[calc(100%-2rem)] z-[1000]">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-[11px] font-semibold tracking-[0.14em] text-muted-foreground">HOSTING NODE</div>
                <div className="mt-1 text-sm font-semibold">{location}</div>
                <div className="mt-0.5 text-xs text-muted-foreground">{hostingInfo?.ip_address || ""}</div>
              </div>
              <div className="rounded-md border bg-background/60 px-2 py-1 text-[11px] font-semibold text-muted-foreground uppercase">
                {hostingInfo?.hosting_type || "unknown"}
              </div>
            </div>

            <div className="mt-3 space-y-3">
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <div className="text-muted-foreground">ASN</div>
                  <div className="font-medium">{hostingInfo?.asn || "—"}</div>
                </div>
                <div>
                  <div className="text-muted-foreground">ORGANIZATION</div>
                  <div className="font-medium">{hostingInfo?.organization || "—"}</div>
                </div>
                <div className="col-span-2">
                  <div className="text-muted-foreground">ISP / PROVIDER</div>
                  <div className="font-medium text-brand">{hostingInfo?.isp || "—"}</div>
                </div>
                <div>
                  <div className="text-muted-foreground">REGION</div>
                  <div className="font-medium">{hostingInfo?.region || "—"}</div>
                </div>
                <div>
                  <div className="text-muted-foreground">COUNTRY</div>
                  <div className="font-medium">{hostingInfo?.country || "—"}</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
