const CFG = window.FUELTRACK_CONFIG;
const state = { stations: [], filtered: [], map: null, markers: [], userLocation: null, fuel: 'regular', user: null, favorites: new Set(), token: localStorage.getItem('fueltrack_access'), refresh: localStorage.getItem('fueltrack_refresh') };
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];

function api(path, options={}) {
  const headers = {'Content-Type':'application/json', ...(options.headers||{})};
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  return fetch(`${CFG.API_BASE_URL}${path}`, {...options, headers}).then(async r => {
    if (r.status === 401 && state.refresh && !options._retry) {
      const rr = await fetch(`${CFG.API_BASE_URL}/auth/refresh/`, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({refresh:state.refresh})});
      if (rr.ok) { const j=await rr.json(); state.token=j.access; localStorage.setItem('fueltrack_access',j.access); return api(path,{...options,_retry:true}); }
    }
    const text = await r.text(); let data={}; try{data=text?JSON.parse(text):{}}catch{data={detail:text}}
    if (!r.ok) throw new Error(data.detail || Object.values(data).flat().join(' ') || `Request failed (${r.status})`);
    return data;
  });
}
function toast(msg){ $('#toast').textContent=msg; $('#toast').classList.remove('hidden'); setTimeout(()=>$('#toast').classList.add('hidden'),3000); }
function openModal(html){ $('#modalContent').innerHTML=html; $('#modalBackdrop').classList.remove('hidden'); }
function closeModal(){ $('#modalBackdrop').classList.add('hidden'); }
function results(data){ return Array.isArray(data)?data:(data.results||[]); }
function latestPrice(station,fuel=state.fuel){ return (station.latest_prices||[]).find(p=>p.fuel_type===fuel); }
function ageLabel(date){ if(!date)return 'No recent report'; const h=(Date.now()-new Date(date))/36e5; if(h<1)return `${Math.max(1,Math.round(h*60))} min ago`; if(h<24)return `${Math.round(h)} hr ago`; return `${Math.round(h/24)} d ago`; }
function escapeHtml(v=''){ return String(v).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#039;','"':'&quot;'}[c])); }

function initMap(){
  state.map=L.map('map',{zoomControl:true}).setView([CFG.DEFAULT_LAT,CFG.DEFAULT_LON],11);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap contributors'}).addTo(state.map);
}
function drawMarkers(){
  state.markers.forEach(m=>m.remove()); state.markers=[];
  state.filtered.forEach(s=>{
    const p=latestPrice(s); const label=p?`${p.price}¢`:'—';
    const icon=L.divIcon({className:'',html:`<div style="background:#0b6b46;color:white;border:3px solid white;box-shadow:0 4px 12px #0003;padding:7px 9px;border-radius:14px;font:800 12px system-ui;white-space:nowrap">${label}</div>`,iconSize:[54,30],iconAnchor:[27,15]});
    const m=L.marker([Number(s.latitude),Number(s.longitude)],{icon}).addTo(state.map).on('click',()=>showStation(s)); state.markers.push(m);
  });
  if(state.userLocation){ L.circleMarker([state.userLocation.lat,state.userLocation.lon],{radius:7,color:'#2563eb',fillOpacity:1}).addTo(state.map); }
}
async function loadStations(){
  $('#stationList').innerHTML='<div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div>';
  try{
    let path='/stations/?country__code=CA';
    if(state.userLocation) path=`/stations/nearby/?lat=${state.userLocation.lat}&lon=${state.userLocation.lon}&radius=${CFG.DEFAULT_RADIUS_KM}`;
    state.stations=results(await api(path));
    applyFilters();
    $('#nearbyCount').textContent=state.stations.length;
    const a=await api(`/analytics/?city=Montréal&fuel_type=${encodeURIComponent(state.fuel)}`).catch(()=>null);
    $('#avgPrice').textContent=a&&a.average_price?Number(a.average_price).toFixed(1):'—';
  }catch(e){ $('#stationList').innerHTML=`<div class="empty-state">Could not load stations.<br><small>${escapeHtml(e.message)}</small></div>`; }
}
function applyFilters(){
  const q=$('#searchInput').value.trim().toLowerCase(); const sort=$('#sortFilter').value;
  state.filtered=state.stations.filter(s=>!q||[s.name,s.brand,s.address,s.postal_code,s.city_name].join(' ').toLowerCase().includes(q));
  state.filtered.sort((a,b)=>{
    const pa=latestPrice(a),pb=latestPrice(b);
    if(sort==='price')return Number(pa?.price||99999)-Number(pb?.price||99999);
    if(sort==='freshness')return new Date(pb?.updated_at||0)-new Date(pa?.updated_at||0);
    return Number(a.distance_km??99999)-Number(b.distance_km??99999);
  });
  renderStations(); drawMarkers(); updateBest();
}
function updateBest(){ const nums=state.filtered.map(s=>Number(latestPrice(s)?.price)).filter(Number.isFinite); $('#bestPrice').textContent=nums.length?Math.min(...nums).toFixed(1):'—'; }
function renderStations(){
  if(!state.filtered.length){ $('#stationList').innerHTML='<div class="empty-state">No matching stations yet.</div>'; return; }
  $('#stationList').innerHTML=state.filtered.map(s=>{ const p=latestPrice(s); const stale=p&&(Date.now()-new Date(p.updated_at)>24*36e5); return `<article class="station-card" data-id="${s.id}"><div class="station-row"><div><div class="station-name">${escapeHtml(s.brand||s.name)}</div><div class="station-meta">${escapeHtml(s.address)} · ${escapeHtml(s.city_name||'')}</div></div><div class="price">${p?Number(p.price).toFixed(1):'—'}<small> ¢/L</small></div></div><div class="badges">${s.distance_km!=null?`<span class="badge">${Number(s.distance_km).toFixed(1)} km</span>`:''}<span class="badge ${stale?'stale':''}">${p?ageLabel(p.updated_at):'No verified price'}</span>${p?`<span class="badge">${Math.round(Number(p.confidence||.5)*100)}% confidence</span>`:''}</div></article>`}).join('');
  $$('.station-card').forEach(el=>el.addEventListener('click',()=>showStation(state.filtered.find(s=>String(s.id)===el.dataset.id))));
}
function showStation(s){
  const prices=(s.latest_prices||[]).map(p=>`<div class="detail-price"><div><b>${escapeHtml(p.name)}</b><br><small>${ageLabel(p.updated_at)} · ${Math.round(Number(p.confidence||.5)*100)}% confidence</small></div><strong>${Number(p.price).toFixed(1)}¢/L</strong></div>`).join('')||'<p>No verified prices yet.</p>';
  openModal(`<span class="eyebrow">${escapeHtml(s.brand||'FUEL STATION')}</span><h2>${escapeHtml(s.name)}</h2><p>${escapeHtml(s.address)}, ${escapeHtml(s.city_name||'')}</p>${prices}<div class="form-actions"><button class="secondary-btn" onclick="toggleFavorite(${s.id})">♡ Favorite</button><button class="primary-btn" onclick="showReport(${s.id})">Report price</button></div>`);
}
async function toggleFavorite(id){ if(!state.token){showAuth('login');return;} try{await api('/favorites/',{method:'POST',body:JSON.stringify({station:id})});toast('Added to favorites');closeModal();}catch(e){toast(e.message.includes('unique')?'Already in favorites':e.message)} }
function showReport(stationId=''){
  const opts=state.stations.map(s=>`<option value="${s.id}" ${String(s.id)===String(stationId)?'selected':''}>${escapeHtml(s.brand||s.name)} — ${escapeHtml(s.address)}</option>`).join('');
  openModal(`<h2>Report a fuel price</h2><p>Community reports become more trusted when other users confirm them.</p><form id="reportForm" class="form-grid"><label>Station<select name="station" required>${opts}</select></label><label>Fuel type<select name="fuel"><option value="regular">Regular</option><option value="mid-grade">Mid-grade</option><option value="premium">Premium</option><option value="diesel">Diesel</option></select></label><label>Price (¢/L)<input name="price" inputmode="decimal" type="number" min="50" max="500" step="0.1" placeholder="154.9" required></label><label>Note (optional)<textarea name="notes" maxlength="240" placeholder="Price seen on station sign"></textarea></label><button class="primary-btn" type="submit">Submit price</button></form>`);
  $('#reportForm').onsubmit=submitReport;
}
async function submitReport(e){ e.preventDefault(); if(!state.token){showAuth('login');return;} const f=new FormData(e.currentTarget); try{ const fuels=results(await api('/fuel-types/')); const ft=fuels.find(x=>x.code===f.get('fuel')); await api('/prices/',{method:'POST',body:JSON.stringify({station:Number(f.get('station')),fuel_type_id:ft.id,price:Number(f.get('price')),notes:f.get('notes')})}); toast('Price submitted for community verification');closeModal(); }catch(err){toast(err.message)} }
function showAuth(mode='login'){
  const register=mode==='register'; openModal(`<h2>${register?'Create account':'Welcome back'}</h2><form id="authForm" class="form-grid">${register?'<label>Name<input name="name" autocomplete="name" required></label>':''}<label>Email<input type="email" name="email" autocomplete="email" required></label><label>Password<input type="password" name="password" autocomplete="current-password" minlength="8" required></label><button class="primary-btn" type="submit">${register?'Create account':'Sign in'}</button></form><p style="text-align:center;color:var(--muted)">${register?'Already have an account?':'New to FuelTrack?'} <button id="switchAuth" class="secondary-btn">${register?'Sign in':'Create account'}</button></p>`); $('#authForm').onsubmit=e=>authSubmit(e,register); $('#switchAuth').onclick=()=>showAuth(register?'login':'register');
}
async function authSubmit(e,register){ e.preventDefault(); const f=new FormData(e.currentTarget); try{ if(register){ await api('/auth/register/',{method:'POST',body:JSON.stringify({email:f.get('email'),password:f.get('password'),name:f.get('name')})}); }
    const j=await api('/auth/login/',{method:'POST',body:JSON.stringify({email:f.get('email'),password:f.get('password')})}); state.token=j.access; state.refresh=j.refresh; localStorage.setItem('fueltrack_access',j.access);localStorage.setItem('fueltrack_refresh',j.refresh); await loadMe();closeModal();toast('Signed in');
  }catch(err){toast(err.message)} }
async function loadMe(){ if(!state.token){state.user=null;$('#accountBtn').textContent='Sign in';return;} try{state.user=await api('/auth/me/');$('#accountBtn').textContent=state.user.email?.split('@')[0]||'Account';}catch{logout();} }
function logout(){state.token=null;state.refresh=null;state.user=null;localStorage.removeItem('fueltrack_access');localStorage.removeItem('fueltrack_refresh');$('#accountBtn').textContent='Sign in';closeModal();toast('Signed out');}
function showAccount(){ if(!state.user){showAuth('login');return;} openModal(`<h2>Your account</h2><p>${escapeHtml(state.user.email||'')}</p><div class="form-actions"><button class="secondary-btn" onclick="showApiSettings()">API settings</button><button class="primary-btn" onclick="logout()">Sign out</button></div>`); }
function showApiSettings(){ openModal(`<h2>Backend connection</h2><p>Set the public URL of your Django API after deployment.</p><form id="apiForm" class="form-grid"><label>API base URL<input name="url" value="${escapeHtml(CFG.API_BASE_URL)}" placeholder="https://api.example.com/api"></label><button class="primary-btn">Save and reload</button></form>`); $('#apiForm').onsubmit=e=>{e.preventDefault();localStorage.setItem('fueltrack_api_url',new FormData(e.currentTarget).get('url').replace(/\/$/,''));location.reload()}; }

$('#closeModal').onclick=closeModal; $('#modalBackdrop').onclick=e=>{if(e.target.id==='modalBackdrop')closeModal()};
$('#searchInput').oninput=applyFilters; $('#sortFilter').onchange=applyFilters; $('#fuelFilter').onchange=async e=>{state.fuel=e.target.value;await loadStations()};
$('#refreshBtn').onclick=loadStations; $('#quickReportBtn').onclick=()=>showReport(); $('#accountBtn').onclick=showAccount;
$('#locateBtn').onclick=()=>{ if(!navigator.geolocation){toast('Location is not supported by this browser');return;} $('#locateBtn').textContent='Locating…'; navigator.geolocation.getCurrentPosition(async p=>{state.userLocation={lat:p.coords.latitude,lon:p.coords.longitude}; state.map.setView([state.userLocation.lat,state.userLocation.lon],13); $('#mapEmpty').classList.add('hidden'); $('#locateBtn').textContent='Location on'; await loadStations();},e=>{toast('Could not access location. You can still browse Montréal.');$('#locateBtn').textContent='Use my location';},{enableHighAccuracy:true,timeout:10000}); };
$$('.nav-item').forEach(b=>b.onclick=()=>{ $$('.nav-item').forEach(x=>x.classList.remove('active')); b.classList.add('active'); const t=b.dataset.tab; if(t==='account')showAccount(); if(t==='favorites'){ if(!state.token){showAuth('login');return;} api('/favorites/').then(d=>{const rows=results(d);openModal(`<h2>Favorite stations</h2>${rows.length?rows.map(x=>`<div class="detail-price"><b>${escapeHtml(x.station_detail.brand||x.station_detail.name)}</b><span>${escapeHtml(x.station_detail.address)}</span></div>`).join(''):'<p>No favorites yet.</p>'}`)}).catch(e=>toast(e.message)); } if(t==='history') openModal('<h2>Price tracking</h2><p>Open a station to see its current verified prices, or use the + button to submit a new report.</p>'); });
window.toggleFavorite=toggleFavorite; window.showReport=showReport; window.logout=logout; window.showApiSettings=showApiSettings;

initMap(); loadMe(); loadStations(); if('serviceWorker' in navigator)navigator.serviceWorker.register('service-worker.js').catch(()=>{});
