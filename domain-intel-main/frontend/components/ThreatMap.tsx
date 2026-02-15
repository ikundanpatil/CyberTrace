import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import type { ThreatPoint } from "@/lib/api";

interface ThreatMapProps {
    data: ThreatPoint[];
    height?: string;
}

// Custom arrow icon for threat markers
const createArrowIcon = (type: string) => {
    const colors: Record<string, string> = {
        "Phishing/Vishing": "#ef4444",
        "Financial Fraud": "#f97316",
        "Illegal Hosting": "#8b5cf6",
        "Scam Call Center": "#eab308",
        "Crypto Drainer": "#22c55e",
        "Illegal Gambling": "#ec4899",
        "Malware C2": "#3b82f6",
        "Sextortion": "#f43f5e",
        "Investment Fraud": "#14b8a6",
        "Identity Theft": "#a855f7",
        "Data Leak": "#06b6d4",
        "Job Scam": "#84cc16",
    };
    const color = colors[type] || "#ef4444";

    return L.divIcon({
        className: "custom-arrow-icon",
        html: `
      <div style="
        font-size: 28px; 
        color: ${color}; 
        filter: drop-shadow(0 0 6px ${color}) drop-shadow(0 0 12px ${color});
        animation: bounce 1s ease-in-out infinite;
      ">📍</div>
    `,
        iconSize: [28, 28],
        iconAnchor: [14, 28],
    });
};

export function ThreatMap({ data, height = "500px" }: ThreatMapProps) {
    return (
        <div
            className="rounded-xl overflow-hidden border border-border/50 shadow-lg"
            style={{ height }}
        >
            <style>{`
        @keyframes bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-6px); }
        }
        .custom-arrow-icon {
          background: transparent !important;
          border: none !important;
        }
        .leaflet-popup-content-wrapper {
          background: rgba(15, 23, 42, 0.95);
          color: #f1f5f9;
          border: 1px solid rgba(255,255,255,0.1);
          border-radius: 12px;
        }
        .leaflet-popup-tip {
          background: rgba(15, 23, 42, 0.95);
        }
      `}</style>
            <MapContainer
                center={[22.5937, 78.9629]}
                zoom={5}
                style={{ height: "100%", width: "100%", background: "#0f172a" }}
                scrollWheelZoom={true}
                zoomControl={true}
            >
                <TileLayer
                    attribution='&copy; <a href="https://carto.com/">CARTO</a>'
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                />
                {data.map((point, index) => (
                    <Marker
                        key={`threat-${index}`}
                        position={[point.lat, point.lon]}
                        icon={createArrowIcon(point.type)}
                    >
                        <Popup>
                            <div className="text-sm p-1">
                                <div className="font-bold text-red-400 text-base">{point.type}</div>
                                {point.city && (
                                    <div className="text-white text-sm mt-1 font-medium">
                                        📍 {point.city}
                                    </div>
                                )}
                                <div className="text-gray-400 text-xs mt-1">
                                    Coords: {point.lat.toFixed(4)}, {point.lon.toFixed(4)}
                                </div>
                                <div className="text-xs text-yellow-500 mt-2 font-medium">
                                    ⚠️ Active Threat Zone
                                </div>
                            </div>
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>
        </div>
    );
}
