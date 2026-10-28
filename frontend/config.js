// Replace the production URL below with your actual Render API hostname.
// Visitors can override it under Account > API settings.
const localFuelTrack = ['localhost', '127.0.0.1'].includes(window.location.hostname);
window.FUELTRACK_CONFIG = {
  API_BASE_URL: localStorage.getItem('fueltrack_api_url') || (localFuelTrack
    ? 'http://127.0.0.1:8000/api'
    : 'https://fueltrack-api.onrender.com/api'),
  DEFAULT_LAT: 45.5017,
  DEFAULT_LON: -73.5673,
  DEFAULT_RADIUS_KM: 15
};
