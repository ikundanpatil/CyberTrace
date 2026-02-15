import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    Legend,
} from "recharts";
import type { ThreatPoint } from "@/lib/api";

interface ThreatStatsChartsProps {
    data: ThreatPoint[];
}

const COLORS = ["#ef4444", "#f97316", "#eab308", "#22c55e", "#3b82f6", "#8b5cf6", "#ec4899"];

export function ThreatStatsCharts({ data }: ThreatStatsChartsProps) {
    // Calculate Threat Types Distribution from data prop
    const typeCount = data.reduce((acc: Record<string, number>, curr) => {
        acc[curr.type] = (acc[curr.type] || 0) + 1;
        return acc;
    }, {});

    const pieData = Object.keys(typeCount).map((key) => ({
        name: key,
        value: typeCount[key],
    }));

    // Calculate Location Distribution from data prop
    const cityCount = data.reduce((acc: Record<string, number>, curr) => {
        acc[curr.city] = (acc[curr.city] || 0) + 1;
        return acc;
    }, {});

    const barData = Object.keys(cityCount)
        .map((key) => ({
            name: key,
            count: cityCount[key],
        }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 5);

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Bar Chart - Location Distribution */}
            <div className="bg-panel/50 border border-border/50 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-muted-foreground mb-4 uppercase tracking-wider">
                    Threats by Location
                </h3>
                {barData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={200}>
                        <BarChart data={barData} layout="vertical">
                            <XAxis type="number" stroke="#64748b" fontSize={10} />
                            <YAxis
                                type="category"
                                dataKey="name"
                                stroke="#64748b"
                                fontSize={10}
                                width={80}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: "#1e293b",
                                    border: "1px solid #334155",
                                    borderRadius: "8px",
                                }}
                            />
                            <Bar dataKey="count" fill="#f97316" radius={[0, 4, 4, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                ) : (
                    <div className="h-[200px] flex items-center justify-center text-muted-foreground text-sm">
                        No location data
                    </div>
                )}
            </div>

            {/* Pie Chart - Threat Types */}
            <div className="bg-panel/50 border border-border/50 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-muted-foreground mb-4 uppercase tracking-wider">
                    Threat Categories
                </h3>
                {pieData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={200}>
                        <PieChart>
                            <Pie
                                data={pieData}
                                dataKey="value"
                                nameKey="name"
                                cx="50%"
                                cy="50%"
                                outerRadius={70}
                                label={({ name, percent }) =>
                                    `${name.length > 10 ? name.slice(0, 10) + "..." : name} (${(percent * 100).toFixed(0)}%)`
                                }
                                labelLine={false}
                            >
                                {pieData.map((_, index) => (
                                    <Cell
                                        key={`cell-${index}`}
                                        fill={COLORS[index % COLORS.length]}
                                    />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: "#1e293b",
                                    border: "1px solid #334155",
                                    borderRadius: "8px",
                                }}
                            />
                            <Legend wrapperStyle={{ fontSize: "11px" }} iconType="circle" />
                        </PieChart>
                    </ResponsiveContainer>
                ) : (
                    <div className="h-[200px] flex items-center justify-center text-muted-foreground text-sm">
                        No threat data
                    </div>
                )}
            </div>
        </div>
    );
}
