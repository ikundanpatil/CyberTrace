const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

// --- Types based on Backend Pydantic Models ---
export interface AnalysisRequest {
    domain: string;
    analyst_name?: string;
    case_id?: string;
}

export interface RiskAssessment {
    risk_score: number;       // 1.0 to 10.0 (Safety Score)
    risk_level: "LOW" | "MEDIUM" | "HIGH";
    confidence: string;
    reasons: string[];
    explanation: string;
}

export interface DomainInfo {
    registrar?: string;
    creation_date?: string;
    expiry_date?: string;
    domain_age_days?: number;
    nameservers?: string[];
    status?: string[];
}

export interface HostingInfo {
    ip_address?: string;
    country?: string;
    country_code?: string;
    city?: string;
    region?: string;
    isp?: string;
    asn?: string;
    organization?: string;
    hosting_type?: string;
}

export interface SecurityInfo {
    https_enabled: boolean;
    ssl_valid: boolean;
    ssl_issuer?: string;
    ssl_expiry?: string;
    blacklisted: boolean;
    blacklist_sources?: string[];
}

export interface AnalysisResponse {
    domain: string;
    risk_assessment: RiskAssessment;
    domain_info: DomainInfo;
    hosting_info: HostingInfo;
    security_info: SecurityInfo;
}

// --- API Functions ---

export async function analyzeDomain(req: AnalysisRequest): Promise<AnalysisResponse> {
    const res = await fetch(`${API_BASE}/api/v1/domain/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req),
    });

    if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`API Error (${res.status}): ${errorText}`);
    }

    const json = await res.json();
    return json.data; // Unwrap the "data" envelope
}

export async function generateReport(req: AnalysisRequest): Promise<string> {
    const res = await fetch(`${API_BASE}/api/v1/report/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req),
    });

    if (!res.ok) {
        throw new Error(`Report Generation Failed: ${await res.text()}`);
    }

    const json = await res.json();
    // Return the full download URL
    return `${API_BASE}${json.data.download_url}`;
}

// --- Utility: Check API Health ---
export async function checkApiHealth(): Promise<boolean> {
    try {
        const res = await fetch(`${API_BASE}/`);
        return res.ok;
    } catch {
        return false;
    }
}

// --- Scan History Types ---
export interface ScanHistoryItem {
    id: number;
    domain: string;
    risk_score: number;
    risk_level: "LOW" | "MEDIUM" | "HIGH";
    scan_date: string;  // ISO string
    analyst_name?: string;
    case_id?: string;
}

// --- Fetch Scan History from Backend ---
export async function getScanHistory(limit: number = 50): Promise<ScanHistoryItem[]> {
    const res = await fetch(`${API_BASE}/api/v1/domain/history?limit=${limit}`);

    if (!res.ok) {
        throw new Error(`Failed to fetch history: ${await res.text()}`);
    }

    const json = await res.json();
    return json.data;  // Backend returns { status, count, data: [...] }
}

// =====================================================
// AUTHENTICATION
// =====================================================

// --- Auth Types ---
export interface LoginPayload {
    email: string;
    password: string;
}

export interface SignupPayload {
    email: string;
    password: string;
    fullName: string;
    organization: string;
}

export interface AuthResponse {
    token: string;
    message: string;
    user_name: string;
    organization: string;
}

// --- Auth API Functions ---
export async function login(payload: LoginPayload): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Login failed" }));
        throw new Error(err.detail || "Invalid credentials");
    }
    const data: AuthResponse = await res.json();

    // Save user details to localStorage
    localStorage.setItem(TOKEN_KEY, data.token);
    localStorage.setItem(USER_KEY, data.user_name);
    localStorage.setItem(ORG_KEY, data.organization);

    return data;
}

export async function signup(payload: SignupPayload): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/api/v1/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Signup failed" }));
        throw new Error(err.detail || "Could not create account");
    }
    const data: AuthResponse = await res.json();

    // Save user details to localStorage
    localStorage.setItem(TOKEN_KEY, data.token);
    localStorage.setItem(USER_KEY, data.user_name);
    localStorage.setItem(ORG_KEY, data.organization);

    return data;
}

// --- Auth Helper Functions ---
const TOKEN_KEY = "cybertrace_token";
const USER_KEY = "cybertrace_user";
const ORG_KEY = "cybertrace_org";

export function getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
}

export function isAuthenticated(): boolean {
    const token = getToken();
    if (!token) return false;

    // Optionally check token expiry (JWT contains exp claim)
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const exp = payload.exp * 1000; // Convert to milliseconds
        return Date.now() < exp;
    } catch {
        return false;
    }
}

export function logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(ORG_KEY);
}

export function getUserDetails(): { name: string; org: string } {
    return {
        name: localStorage.getItem(USER_KEY) || "Unknown Agent",
        org: localStorage.getItem(ORG_KEY) || "Cyber Cell"
    };
}

export function getAuthHeader(): Record<string, string> {
    const token = getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
}

// =====================================================
// THREAT INTELLIGENCE
// =====================================================

export interface ThreatPoint {
    lat: number;
    lon: number;
    type: string;
    city: string;
    severity?: "Critical" | "High" | "Medium" | "Low";
}

export interface ThreatStats {
    total_threats: number;
    by_country: { country: string; count: number }[];
    by_type: { type: string; count: number }[];
}

// Demo fallback data - INDIA CYBERCRIME HOTSPOTS (Expanded)
export const DEMO_MAP_DATA: ThreatPoint[] = [
    { lat: 24.1760, lon: 86.9976, type: "Phishing", city: "Jamtara", severity: "Critical" },
    { lat: 24.1800, lon: 87.0000, type: "Vishing", city: "Jamtara", severity: "High" },
    { lat: 24.1700, lon: 86.9900, type: "Phishing", city: "Jamtara", severity: "Critical" },
    { lat: 28.1133, lon: 77.0019, type: "Financial Fraud", city: "Nuh", severity: "Critical" },
    { lat: 28.1200, lon: 77.0100, type: "Sextortion", city: "Nuh", severity: "High" },
    { lat: 19.0760, lon: 72.8777, type: "Illegal Hosting", city: "Mumbai", severity: "Medium" },
    { lat: 19.0800, lon: 72.8800, type: "Dark Web Node", city: "Mumbai", severity: "Critical" },
    { lat: 12.9716, lon: 77.5946, type: "Tech Support Scam", city: "Bangalore", severity: "High" },
    { lat: 12.9750, lon: 77.5980, type: "Call Center Fraud", city: "Bangalore", severity: "High" },
    { lat: 28.7041, lon: 77.1025, type: "Crypto Drainer", city: "Delhi", severity: "Critical" },
    { lat: 28.6500, lon: 77.2000, type: "UPI Fraud", city: "Delhi", severity: "High" },
    { lat: 22.5726, lon: 88.3639, type: "Betting App", city: "Kolkata", severity: "Medium" },
    { lat: 17.3850, lon: 78.4867, type: "Identity Theft", city: "Hyderabad", severity: "Medium" },
    { lat: 18.5204, lon: 73.8567, type: "Malware C2", city: "Pune", severity: "High" },
    { lat: 26.9124, lon: 75.7873, type: "Sextortion", city: "Jaipur", severity: "High" },
    { lat: 23.0225, lon: 72.5714, type: "Investment Fraud", city: "Ahmedabad", severity: "Medium" },
];

const DEMO_STATS_DATA: ThreatStats = {
    total_threats: 2847,
    by_country: [
        { country: "NCR (Delhi-NCR)", count: 892 },
        { country: "Jamtara, JH", count: 645 },
        { country: "Maharashtra", count: 534 },
        { country: "Karnataka", count: 421 },
        { country: "Haryana (Nuh)", count: 355 },
    ],
    by_type: [
        { type: "UPI Fraud", count: 1120 },
        { type: "Phishing/Vishing", count: 680 },
        { type: "Investment Fraud", count: 450 },
        { type: "Sextortion", count: 320 },
        { type: "Job Scam", count: 277 },
    ],
};

export async function getThreatMap(limit: number = 1000): Promise<ThreatPoint[]> {
    try {
        const res = await fetch(`${API_BASE}/api/v1/intel/map?limit=${limit}`);
        if (!res.ok) throw new Error("API Error");
        const data = await res.json();
        return data.length > 0 ? data : DEMO_MAP_DATA;
    } catch {
        console.warn("Using Demo Map Data");
        return DEMO_MAP_DATA;
    }
}

export async function getThreatStats(): Promise<ThreatStats> {
    try {
        const res = await fetch(`${API_BASE}/api/v1/intel/stats`);
        if (!res.ok) throw new Error("API Error");
        const data = await res.json();
        return data.total_threats > 0 ? data : DEMO_STATS_DATA;
    } catch {
        console.warn("Using Demo Stats Data");
        return DEMO_STATS_DATA;
    }
}
