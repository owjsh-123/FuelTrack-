# FuelTrack Backend — Global-ready, Montréal first

FuelTrack is a Django REST API for community-powered fuel price tracking. The data model is international from day one (country → region → city → station), while the first launch configuration is Canada / Québec / Montréal.

## Included in V2
- Email-based user accounts + JWT login/refresh
- Global geography and per-country currency/unit metadata
- Multiple fuel types per station (Regular, Mid-Grade, Premium, Diesel seeded for Canada)
- Historical price submissions instead of overwriting one station price
- Community voting + basic automatic verification threshold
- User reputation field ready for future scoring logic
- Nearby-station endpoint using latitude/longitude
- Search/filter/sort station and price APIs
- Favorite stations
- Basic analytics endpoint
- Django admin moderation
- API throttling and restrictive CORS defaults
- Montréal/Brossard/Laval demo seed command

> Demo station addresses in the seed command are intentionally fictional. Real station data should come from a licensed/authorized source or verified community submissions.

## Quick start
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
python manage.py makemigrations accounts stations
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_montreal
python manage.py runserver
```
Open admin: http://127.0.0.1:8000/admin/

## Main API routes
- POST `/api/auth/register/`
- POST `/api/auth/login/`
- POST `/api/auth/refresh/`
- GET `/api/auth/me/`
- GET `/api/countries/`
- GET `/api/regions/?country__code=CA`
- GET `/api/cities/?region__code=QC`
- GET `/api/fuel-types/`
- GET/POST `/api/stations/`
- GET `/api/stations/nearby/?lat=45.5017&lon=-73.5673&radius=10`
- GET/POST `/api/prices/`
- POST `/api/prices/{id}/vote/` body: `{"value": 1}` or `{"value": -1}`
- GET/POST `/api/favorites/`
- GET `/api/analytics/?city=Montréal&fuel_type=regular`

## Price convention
`PriceSubmission.price` stores the local display price. For Canada, `154.9` means **154.9 cents/L**. The related `Country` record tells the client how to display it. This keeps the schema ready for countries that use dollars/gallon or other formats.

## Next build targets
1. Real licensed Canadian station/data source integration
2. PostGIS + GeoDjango for scalable geospatial search
3. Stronger reputation/confidence algorithm and abuse controls
4. Swagger/OpenAPI docs
5. Redis/Celery background imports
6. React/Next.js or mobile frontend with map
7. Docker + PostgreSQL deployment
