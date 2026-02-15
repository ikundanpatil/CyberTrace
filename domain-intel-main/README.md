# 🔍 DomainIntel - Cyber Investigation Platform

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)
![React](https://img.shields.io/badge/react-18.3-61dafb.svg)

**A comprehensive cyber investigation and domain intelligence platform for law enforcement and security professionals.**

</div>

---

## ✨ Features

### 🔎 Domain Investigation
- **WHOIS Lookup** - Domain registration details, ownership information
- **DNS Resolution** - A, AAAA, MX, NS, TXT records
- **SSL Certificate Analysis** - Issuer, validity, chain inspection
- **Reputation Scoring** - Multi-source threat intelligence

### 🗺️ National Cybercrime Surveillance (India)
- **Live Threat Map** - Real-time geospatial threat visualization
- **Hotspot Monitoring** - Jamtara, Nuh, Mumbai, Delhi, Bangalore
- **Deep Filtering** - Search by city or threat type
- **Dynamic Analytics** - Charts update based on filtered data

### 📊 Investigation Dashboard
- Scan history with persistent storage
- PDF report generation
- Case management interface
- Real-time status indicators

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, TypeScript, Vite, TailwindCSS, Shadcn/UI |
| **Backend** | FastAPI, Python 3.10+, SQLAlchemy, SQLite |
| **Mapping** | Leaflet, React-Leaflet, CARTO Dark Tiles |
| **Charts** | Recharts |
| **State** | TanStack Query (React Query) |

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python run.py
```

Backend runs at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:8080`

---

## 🚂 Railway Deployment

This project is configured for **Railway** deployment with separate services.

### Deploy Steps:

1. **Create a Railway Project**
   - Go to [railway.app](https://railway.app)
   - Create new project → "Deploy from GitHub repo"

2. **Deploy Backend Service**
   - Add service → Select GitHub repo
   - Set **Root Directory**: `backend`
   - Add environment variables:
     ```
     DATABASE_URL=sqlite:///./domainintel.db
     DEBUG=false
     SECRET_KEY=your-secret-key
     ALLOWED_ORIGINS=https://your-frontend.railway.app
     ```

3. **Deploy Frontend Service**
   - Add another service → Same repo
   - Set **Root Directory**: `frontend`
   - Add environment variables:
     ```
     VITE_API_URL=https://your-backend.railway.app
     ```

4. **Generate Domains**
   - Go to each service → Settings → Generate Domain

### Environment Variables

| Service | Variable | Description |
|---------|----------|-------------|
| Backend | `DATABASE_URL` | SQLite or PostgreSQL connection |
| Backend | `SECRET_KEY` | JWT secret key |
| Backend | `ALLOWED_ORIGINS` | Frontend URL for CORS |
| Frontend | `VITE_API_URL` | Backend API URL |

---

## 📁 Project Structure

```
Domain-Intel/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # API routes
│   │   │   ├── domain.py        # Domain scanning
│   │   │   ├── intel.py         # Threat intelligence
│   │   │   └── auth.py          # Authentication
│   │   ├── services/            # Business logic
│   │   └── main.py              # FastAPI app
│   ├── requirements.txt
│   ├── Procfile                 # Railway/Heroku
│   ├── nixpacks.toml            # Nixpacks config
│   └── railway.toml             # Railway config
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Route pages
│   │   └── lib/api.ts           # API client
│   ├── package.json
│   ├── nixpacks.toml            # Nixpacks config
│   └── railway.toml             # Railway config
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/scan/quick` | Quick domain scan |
| `POST` | `/api/v1/scan/full` | Full domain investigation |
| `GET` | `/api/v1/intel/map` | Threat map coordinates |
| `GET` | `/api/v1/intel/stats` | Aggregated threat statistics |

---

## 🇮🇳 India Cybercrime Hotspots

| Location | Threat Type | Severity |
|----------|-------------|----------|
| Jamtara, JH | Phishing/Vishing | Critical |
| Nuh, HR | Financial Fraud | Critical |
| Mumbai, MH | Dark Web Nodes | Critical |
| Delhi NCR | Crypto Drainer | Critical |
| Bangalore, KA | Tech Support Scam | High |

---

## 📄 License

MIT License

---

<div align="center">
Made with ❤️ for Cyber Investigation
</div>
