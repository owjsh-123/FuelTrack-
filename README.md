# FuelTrack V3 — Full Stack

FuelTrack is a global-ready community fuel-price platform with Montréal as the first launch market.

## Folders
- `backend/` — Django REST Framework API
- `frontend/` — mobile-first installable web app (PWA)

## V3 features
- Countries/regions/cities/stations data model
- Canadian cents-per-litre display with room for other currencies/units
- JWT registration/login
- Nearby station search
- Multiple fuel types
- Historical community price submissions
- Voting/confidence + verified prices
- Favorites
- Analytics
- Admin moderation
- OpenAPI + Swagger docs
- Production PostgreSQL configuration
- Render deployment blueprint
- Responsive map frontend using OpenStreetMap/Leaflet
- Search, sorting, fuel filters, location, favorites and price reporting
- Installable PWA shell

## Local start
### 1. Backend
```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py makemigrations accounts stations
python manage.py migrate
python manage.py seed_montreal
python manage.py createsuperuser
python manage.py runserver
```
API: `http://127.0.0.1:8000/api/`
Swagger: `http://127.0.0.1:8000/api/docs/`

### 2. Frontend
Open a second terminal:
```bash
cd frontend
python -m http.server 5500
```
Open `http://127.0.0.1:5500`.

## Important
The seed command uses fictional demo stations. Do not present those demo records as real-world prices. Real station and price data should come from authorized data sources or verified community submissions.


## Hosting
See [DEPLOYMENT.md](DEPLOYMENT.md) for the updated Render + Netlify production checklist.
