# FuelTrack Frontend

A dependency-free mobile-first PWA that connects to the FuelTrack Django REST API.

## Run locally
From this folder:

```bash
python -m http.server 5500
```

Open `http://127.0.0.1:5500`.

The default API URL is `http://127.0.0.1:8000/api`. You can change it in `config.js` or from Account → API settings after sign-in.

## Deploy
This folder can be deployed directly to Cloudflare Pages, Netlify, GitHub Pages (if API CORS is configured), or any static host. No build command is required.
