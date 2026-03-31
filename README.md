# 🚀 Routing App

Full-stack routing app using Vue 3 + FastAPI + Valhalla + PostGIS + Traefik.

## ⚙️ Setup

Create a `.env` file in the root:

APP_BASE_URL=localhost
APP_BASE_PORT=3000

POSTGRES_PASSWORD=postgres
POSTGRES_DB=routing

OSM_PBF=https://download.geofabrik.de/europe/ukraine-latest.osm.pbf

## ▶️ Run

docker compose up --build

Detached mode:

docker compose up -d --build

## 🌐 Access

App: http://localhost:3000  
API: http://localhost:3000/api  
Valhalla: http://localhost:8002  
DB: localhost:5432  

## ⏳ First Run

- Valhalla downloads OSM data and builds tiles (can take time)
- Backend runs deploy.py automatically

Check logs:

docker compose logs -f

## 🧹 Cleanup

docker compose down

Remove volumes (⚠️ deletes DB):

docker compose down -v
