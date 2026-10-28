# FuelTrack: Deploy to the internet

This is the existing FuelTrack project, prepared for a **Render Django API + PostgreSQL** backend and **Netlify** static PWA frontend. It has **not been deployed for you**; you need to connect your own GitHub and hosting accounts.

## Critical prerequisite: Django migrations

The original repository contained no committed application migration files beyond `__init__.py`. Before your first production deployment, generate and commit them locally:

```powershell
cd backend
py -m pip install -r requirements.txt
py manage.py makemigrations accounts stations
py manage.py migrate
cd ..
git add backend/accounts/migrations backend/stations/migrations
```

Do not skip this. `migrate` alone cannot create the application's tables without these initial migrations. Review generated migration files before committing them. To seed **fictional example stations**, optionally run `py manage.py seed_montreal` (never present these as live prices).

## A. Push deployment files to GitHub

Copy the modified files to your FuelTrack repository, or upload this unzipped folder to a NEW branch. Verify secrets and local databases are not committed. Make sure `render.yaml`, `netlify.toml`, `frontend/` and `backend/` are all at the repository root.

## B. Deploy backend on Render

1. At https://dashboard.render.com/ choose **New > Blueprint**. Link your FuelTrack repository, selecting the `render.yaml` in the root.
2. Review **pricing** before approval (database plans and service costs can vary). The Blueprint will create `fueltrack-api` and `fueltrack-db` if the names are available.
3. Set `CORS_ALLOWED_ORIGINS` to your future exact HTTPS Netlify site URL (you may update it after step C). Set `CSRF_TRUSTED_ORIGINS` to that URL as well.
4. Deploy. Wait until the backend is healthy. Record its actual HTTPS URL, e.g. `https://fueltrack-api-xxxx.onrender.com` (do NOT assume this example hostname exists).
5. Confirm the API documentation responds at `https://YOUR-RENDER-HOST/api/docs/` (the URL path depends on your configured Django routes).

If Render's free or chosen plan does not support the pre-deploy command, set the service start command temporarily to `python manage.py migrate --noinput && gunicorn fueltrack.wsgi:application --bind 0.0.0.0:$PORT` or use a managed migration workflow. Ensure migrations run before traffic is served.

## C. Deploy frontend on Netlify

1. In `frontend/config.js`, replace `https://fueltrack-api.onrender.com/api` with your **actual** Render service hostname plus `/api`.
2. Commit and push this change to GitHub.
3. Open https://app.netlify.com/start and connect the same GitHub repository.
4. Netlify will read `netlify.toml`: publish directory `frontend`; no build command necessary.
5. Deploy and copy your HTTPS `https://YOUR-SITE.netlify.app` URL.
6. In Render > service > Environment, update `CORS_ALLOWED_ORIGINS` to the exact frontend origin (no trailing slash), e.g. `https://YOUR-SITE.netlify.app`. Update `CSRF_TRUSTED_ORIGINS` similarly; save and redeploy.
7. Visit the Netlify site. Test station listings, register/login, a new submission, favorites, and refresh. Any 404 / CORS messages should be resolved before launch.

## D. Install on phone

- iPhone: open the deployed HTTPS site in Safari > Share > Add to Home Screen.
- Android: open in Chrome > menu > Add to Home screen / Install app.
- Location permission requires HTTPS and user approval. Keep OpenStreetMap/Leaflet attribution in the UI.

## Before public launch

- Test CORS, authentication, allowed hosts, database migrations and moderation; review all public-write endpoints.
- No real fuel prices arrive automatically. `seed_montreal` makes explicitly fictional demo stations; add real verified station information from authorized data or verified community submissions.
- Configure and monitor database backups, billing, error logs, password recovery and abuse prevention; security review is recommended before opening registrations publicly.
- Do not commit `.env`, the SQLite database, tokens, or other secrets.
