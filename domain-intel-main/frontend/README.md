# CyberTrace Frontend

**Domain Intelligence & Safety Scoring Dashboard**

A React-based cybersecurity investigation dashboard for analyzing domain safety, detecting threats, and generating comprehensive security reports.

## Features

- 🔍 **Domain Analysis** - Real-time safety scoring with 1-10 scale
- 🗺️ **Geo-Location Mapping** - Visualize hosting infrastructure
- 📊 **WHOIS Intelligence** - Domain registration details
- 🔒 **Security Configuration** - SSL/TLS and blacklist status
- 📄 **PDF Reports** - Generate downloadable investigation reports
- 📜 **Scan History** - Track all previous analyses

## Tech Stack

- **React 18** + TypeScript
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - Component library
- **Leaflet** - Interactive maps
- **TanStack Query** - Data fetching

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL="http://localhost:8000"
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── CyberInvestigationDashboard.tsx
│   │   ├── RiskAssessmentCard.tsx
│   │   ├── HostingGeoPanel.tsx
│   │   └── ...
│   ├── lib/              # Utilities and API client
│   │   └── api.ts        # Backend API functions
│   └── main.tsx          # App entry point
└── index.html            # HTML template
```

## Backend Integration

This frontend connects to the FastAPI backend at `http://localhost:8000`.

**Required API Endpoints:**
- `POST /api/v1/domain/analyze` - Analyze a domain
- `POST /api/v1/report/generate` - Generate PDF report
- `GET /api/v1/domain/history` - Fetch scan history

## License

MIT
