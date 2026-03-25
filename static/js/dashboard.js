/* ── Shared Dashboard Utilities ──────────────────────────── */

document.addEventListener('DOMContentLoaded', function () {
  setupHamburger();
  autoCloseSidebar();
});

function setupHamburger() {
  const btn = document.getElementById('hamburgerBtn');
  const sidebar = document.getElementById('sidebar');
  if (!btn || !sidebar) return;

  btn.addEventListener('click', function () {
    sidebar.classList.toggle('sidebar--open');
  });
}

function autoCloseSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;

  document.addEventListener('click', function (e) {
    if (window.innerWidth <= 768 && sidebar.classList.contains('sidebar--open')) {
      if (!sidebar.contains(e.target) && e.target.id !== 'hamburgerBtn') {
        sidebar.classList.remove('sidebar--open');
      }
    }
  });
}

function formatRWF(value) {
  return Number(value).toLocaleString('en-RW');
}

function formatDate(isoString) {
  if (!isoString) return '—';
  const d = new Date(isoString);
  return d.toLocaleDateString('en-RW', { day: '2-digit', month: 'short', year: 'numeric' });
}

function formatDateTime(isoString) {
  if (!isoString) return '—';
  const d = new Date(isoString);
  return d.toLocaleString('en-RW', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function showAlert(message, type = 'danger') {
  const el = document.createElement('div');
  el.className = `alert alert--${type}`;
  el.textContent = message;
  document.querySelector('.page-content')?.prepend(el);
  setTimeout(() => el.remove(), 5000);
}

/* ── MoMo Success + Local Tracking Simulation ─────────────── */
let trackingTimer = null;

window.handleMomoPaymentSuccessFlow = function (bookingId) {
  const actionsWrap = document.querySelector(`.js-active-booking-actions[data-booking-id="${bookingId}"]`);
  if (!actionsWrap) return;

  const payBtn = actionsWrap.querySelector('.js-active-pay-btn');
  if (payBtn) payBtn.remove();

  const paidBadge = document.createElement('span');
  paidBadge.className = 'badge badge--paid';
  paidBadge.textContent = 'Paid';
  actionsWrap.appendChild(paidBadge);

  window.setTimeout(function () {
    paidBadge.remove();
    const trackBtn = document.createElement('button');
    trackBtn.type = 'button';
    trackBtn.className = 'btn btn--action';
    trackBtn.innerHTML = '<i class="fa-solid fa-location-dot"></i> Track Truck';
    trackBtn.addEventListener('click', function () {
      startMapTrackingSimulation(bookingId);
    });
    actionsWrap.appendChild(trackBtn);
  }, 3000);
};

function startMapTrackingSimulation(bookingId) {
  const container = ensureTrackingSimContainer();
  const progressBar = container.querySelector('#simProgressFill');
  const percentEl = container.querySelector('#simProgressPercent');
  const etaEl = container.querySelector('#simEta');
  const statusEl = container.querySelector('#simStatus');
  const truckEl = container.querySelector('#simTruck');

  if (!progressBar || !percentEl || !etaEl || !statusEl || !truckEl) return;
  container.classList.add('modal--open');

  const points = [
    { x: 8, y: 72 }, { x: 16, y: 68 }, { x: 24, y: 61 }, { x: 33, y: 56 },
    { x: 40, y: 50 }, { x: 48, y: 45 }, { x: 57, y: 40 }, { x: 66, y: 33 },
    { x: 74, y: 28 }, { x: 83, y: 20 }, { x: 92, y: 14 }
  ];

  const stopLabels = [
    'Driver picked up cargo',
    'Truck cleared city center',
    'Truck approaching destination',
    'Truck arrived near dropoff'
  ];

  let step = 0;
  const maxSteps = 80;
  if (trackingTimer) window.clearInterval(trackingTimer);
  statusEl.textContent = 'Driver en route';

  trackingTimer = window.setInterval(function () {
    step += 1;
    const t = Math.min(step / maxSteps, 1);
    const pathIndex = t * (points.length - 1);
    const i = Math.floor(pathIndex);
    const localT = pathIndex - i;
    const p1 = points[i];
    const p2 = points[Math.min(i + 1, points.length - 1)];
    const x = p1.x + (p2.x - p1.x) * localT;
    const y = p1.y + (p2.y - p1.y) * localT;

    truckEl.style.left = `${x}%`;
    truckEl.style.top = `${y}%`;
    progressBar.style.width = `${Math.round(t * 100)}%`;
    percentEl.textContent = `${Math.round(t * 100)}%`;
    etaEl.textContent = `${Math.max(1, Math.ceil((1 - t) * 18))} min`;

    if (t > 0.2 && t <= 0.5) statusEl.textContent = stopLabels[1];
    else if (t > 0.5 && t <= 0.8) statusEl.textContent = stopLabels[2];
    else if (t > 0.8 && t < 1) statusEl.textContent = stopLabels[3];

    if (t >= 1) {
      statusEl.textContent = `Booking #${bookingId} is arriving now`;
      window.clearInterval(trackingTimer);
      trackingTimer = null;
    }
  }, 220);
}

function ensureTrackingSimContainer() {
  let modal = document.getElementById('trackingSimModal');
  if (modal) return modal;

  modal = document.createElement('div');
  modal.id = 'trackingSimModal';
  modal.className = 'modal';
  modal.innerHTML = `
    <div class="modal__backdrop"></div>
    <div class="modal__box modal__box--wide" style="max-width:740px;">
      <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:10px;">
        <h3 class="modal__title" style="margin-bottom:0;">Live Tracking</h3>
        <button id="simCloseBtn" class="btn btn--ghost btn--sm" type="button">Close</button>
      </div>
      <p id="simStatus" style="font-size:0.9rem;color:var(--color-text-secondary);margin-bottom:14px;">Driver en route</p>

      <div style="position:relative;height:360px;border:1px solid var(--color-border);border-radius:14px;background:linear-gradient(180deg,#f7f9ff,#eef3ff);overflow:hidden;">
        <div style="position:absolute;inset:0;background-image:linear-gradient(to right, rgba(10,31,68,0.06) 1px, transparent 1px), linear-gradient(to bottom, rgba(10,31,68,0.06) 1px, transparent 1px);background-size:32px 32px;"></div>
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute;inset:0;width:100%;height:100%;">
          <defs>
            <linearGradient id="simRouteGrad" x1="0%" y1="100%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#E85D04"></stop>
              <stop offset="100%" stop-color="#0A1F44"></stop>
            </linearGradient>
          </defs>
          <polyline points="8,72 16,68 24,61 33,56 40,50 48,45 57,40 66,33 74,28 83,20 92,14" fill="none" stroke="url(#simRouteGrad)" stroke-width="2.6" stroke-linecap="round"></polyline>
        </svg>
        <div style="position:absolute;left:8%;top:72%;width:12px;height:12px;border-radius:999px;background:#16A34A;box-shadow:0 0 0 6px rgba(22,163,74,.16);transform:translate(-50%,-50%);" title="Pickup"></div>
        <div style="position:absolute;left:92%;top:14%;width:12px;height:12px;border-radius:999px;background:#0A1F44;box-shadow:0 0 0 6px rgba(10,31,68,.14);transform:translate(-50%,-50%);" title="Dropoff"></div>
        <div id="simTruck" style="position:absolute;left:8%;top:72%;transform:translate(-50%,-50%);width:34px;height:34px;border-radius:10px;background:#E85D04;color:#fff;display:flex;align-items:center;justify-content:center;box-shadow:0 8px 20px rgba(232,93,4,.35);">
          <i class="fa-solid fa-truck"></i>
        </div>
      </div>

      <div style="margin-top:14px;">
        <div style="display:flex;justify-content:space-between;font-size:0.84rem;color:var(--color-text-secondary);margin-bottom:6px;">
          <span>Progress: <strong id="simProgressPercent" style="color:var(--color-primary-navy)">0%</strong></span>
          <span>ETA: <strong id="simEta" style="color:var(--color-primary-navy)">18 min</strong></span>
        </div>
        <div style="height:8px;border-radius:999px;background:#dbe6ff;overflow:hidden;">
          <div id="simProgressFill" style="height:100%;width:0%;background:linear-gradient(90deg,#E85D04,#0A1F44);"></div>
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  const close = function () {
    modal.classList.remove('modal--open');
    if (trackingTimer) {
      window.clearInterval(trackingTimer);
      trackingTimer = null;
    }
  };

  modal.querySelector('.modal__backdrop')?.addEventListener('click', close);
  modal.querySelector('#simCloseBtn')?.addEventListener('click', close);
  return modal;
}
/* ── Shared Dashboard Utilities ──────────────────────────── */
document.addEventListener('DOMContentLoaded', function () {
  setupHamburger();
  autoCloseSidebar();
});

function setupHamburger() {
  const btn = document.getElementById('hamburgerBtn');
  const sidebar = document.getElementById('sidebar');
  if (btn && sidebar) btn.addEventListener('click', () => sidebar.classList.toggle('sidebar--open'));
}

function autoCloseSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;
  document.addEventListener('click', function (e) {
    if (window.innerWidth <= 768 && sidebar.classList.contains('sidebar--open')) {
      if (!sidebar.contains(e.target) && e.target.id !== 'hamburgerBtn') sidebar.classList.remove('sidebar--open');
    }
  });
}

function formatRWF(value) { return Number(value).toLocaleString('en-RW'); }
function showAlert(message, type = 'danger') {
  const el = document.createElement('div');
  el.className = `alert alert--${type}`;
  el.textContent = message;
  document.querySelector('.page-content')?.prepend(el);
  setTimeout(() => el.remove(), 5000);
}

/* ── MoMo Success Flow (3-Second Delay & Track Button) ─────────────── */
window.handleMomoPaymentSuccessFlow = function (bookingId) {
  const actionsWrap = document.querySelector(`.js-active-booking-actions[data-booking-id="${bookingId}"]`);
  if (!actionsWrap) return;

  const payBtn = actionsWrap.querySelector('.js-active-pay-btn');
  if (payBtn) payBtn.remove();

  // Show "Paid" badge
  const paidBadge = document.createElement('span');
  paidBadge.className = 'badge badge--paid';
  paidBadge.textContent = 'Paid';
  actionsWrap.appendChild(paidBadge);

  // After 3 seconds, turn "Paid" into the "Track" button
  window.setTimeout(function () {
    paidBadge.remove();
    const trackBtn = document.createElement('button');
    trackBtn.type = 'button';
    trackBtn.className = 'btn btn--action';
    trackBtn.innerHTML = '<i class="fa-solid fa-location-dot"></i> Track';
    trackBtn.addEventListener('click', function () {
      startMapTrackingSimulation();
    });
    actionsWrap.appendChild(trackBtn);
  }, 3000);
};

/* ── Pro Tracking Simulation Engine ─────────────── */
let trackingFrameRef = null;

function startMapTrackingSimulation() {
  const modal = document.getElementById('trackingSimModal');
  modal.classList.add('modal--open');

  document.getElementById('simCloseBtn').onclick = () => {
    modal.classList.remove('modal--open');
    if (trackingFrameRef) window.cancelAnimationFrame(trackingFrameRef);
  };
  document.getElementById('simModalBackdrop').onclick = document.getElementById('simCloseBtn').onclick;

  // Wait briefly so the modal opens and Leaflet calculates the correct map width
  setTimeout(() => {
    // Clear the map if opened previously
    if (window._simMapInstance) {
      window._simMapInstance.remove();
      document.getElementById('simMap').innerHTML = '';
    }

    const CONFIG = {
      durationMs: 7000,
      center: [-1.9497, 30.0588],
      zoom: 15,
      fitBoundsPadding: [24, 24],
      route: [
        { lat: -1.9545, lng: 30.0528, street: "KG 11 Ave" },
        { lat: -1.9534, lng: 30.0538, street: "KG 11 Ave" },
        { lat: -1.9527, lng: 30.0552, street: "KK 5 Rd" },
        { lat: -1.9517, lng: 30.0561, street: "KK 5 Rd" },
        { lat: -1.9506, lng: 30.0568, street: "KG 17 Ave" },
        { lat: -1.9493, lng: 30.0577, street: "KG 17 Ave" },
        { lat: -1.9484, lng: 30.0588, street: "KN 3 Rd" },
        { lat: -1.9474, lng: 30.06, street: "KN 3 Rd" },
        { lat: -1.9466, lng: 30.0613, street: "Destination Street" }
      ]
    };

    function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }
    function lerp(a, b, t) { return a + (b - a) * t; }

    // Init Map
    const map = L.map("simMap", { zoomControl: false, attributionControl: false }).setView(CONFIG.center, CONFIG.zoom);
    window._simMapInstance = map;
    L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", { maxZoom: 19 }).addTo(map);

    const latlngs = CONFIG.route.map((p) => [p.lat, p.lng]);
    const baseRoute = L.polyline(latlngs, { color: "#9eb5de", weight: 7, opacity: 0.85, lineCap: "round", lineJoin: "round" }).addTo(map);
    const progressRoute = L.polyline([latlngs[0]], { color: "#16A34A", weight: 7, opacity: 0.95, lineCap: "round", lineJoin: "round" }).addTo(map);

    L.circleMarker(latlngs[0], { radius: 7, color: "#E85D04", weight: 3, fillColor: "#E85D04", fillOpacity: 1 }).addTo(map).bindTooltip("Pickup", { permanent: true, direction: "right", className: "map-tooltip", offset: [10, 0] });
    L.circleMarker(latlngs[latlngs.length - 1], { radius: 7, color: "#0A1F44", weight: 3, fillColor: "#0A1F44", fillOpacity: 1 }).addTo(map).bindTooltip("Customer", { permanent: true, direction: "right", className: "map-tooltip", offset: [10, 0] });

    const icon = L.divIcon({ className: "", html: `<div class="truck-marker"><span class="truck-marker__body"></span><span class="truck-marker__cab"></span><span class="truck-marker__wheel truck-marker__wheel--back"></span><span class="truck-marker__wheel truck-marker__wheel--front"></span></div>`, iconSize: [44, 24], iconAnchor: [22, 12] });
    const truckMarker = L.marker(latlngs[0], { icon, keyboard: false }).addTo(map).bindTooltip("Driver", { permanent: true, direction: "bottom", className: "map-tooltip", offset: [0, 15] });

    map.fitBounds(baseRoute.getBounds(), { padding: CONFIG.fitBoundsPadding });

    // Pre-calculate animation timeline distances
    let cumulative = 0;
    let timeline = [{ ...CONFIG.route[0], t: 0, cumulativeKm: 0 }];
    for (let i = 1; i < CONFIG.route.length; i += 1) {
      const a = CONFIG.route[i - 1], b = CONFIG.route[i];
      const dLat = ((b.lat - a.lat) * Math.PI) / 180, dLng = ((b.lng - a.lng) * Math.PI) / 180;
      const q = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos((a.lat * Math.PI) / 180) * Math.cos((b.lat * Math.PI) / 180) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
      cumulative += 2 * 6371 * Math.atan2(Math.sqrt(q), Math.sqrt(1 - q));
      timeline.push({ ...b, cumulativeKm: cumulative, t: 0 });
    }
    const totalDistanceKm = cumulative;
    timeline.forEach(p => p.t = (cumulative > 0 ? p.cumulativeKm / cumulative : 0) * CONFIG.durationMs);

    const startMs = performance.now();
    let cameraMode = "overview";

    function frame(now) {
      const elapsed = now - startMs;
      const t = clamp(elapsed, 0, CONFIG.durationMs);
      const progress = t / CONFIG.durationMs;

      // Find current segment
      let i = 0;
      while (i < timeline.length - 1 && timeline[i + 1].t < t) i += 1;
      const a = timeline[i], b = timeline[Math.min(i + 1, timeline.length - 1)];
      const segmentT = b.t === a.t ? 0 : (t - a.t) / (b.t - a.t);

      // Interpolate Location and Heading
      const lat = lerp(a.lat, b.lat, segmentT), lng = lerp(a.lng, b.lng, segmentT);
      const traveledKm = lerp(a.cumulativeKm, b.cumulativeKm, segmentT);
      const headingDeg = Math.atan2(a.lat - b.lat, b.lng - a.lng) * (180 / Math.PI);

      const completedCoords = timeline.slice(0, i + 1);
      completedCoords.push({ lat, lng });

      // Move marker & rotate truck
      truckMarker.setLatLng([lat, lng]);
      const markerEl = truckMarker.getElement();
      if (markerEl) {
        const truckEl = markerEl.querySelector(".truck-marker");
        if (truckEl) truckEl.style.transform = `rotate(${headingDeg}deg)`;
      }
      progressRoute.setLatLngs(completedCoords.map((p) => [p.lat, p.lng]));

      // Handle map pan
      if (cameraMode === "follow") {
        map.panTo([lat, lng], { animate: true, duration: 0.2 });
      } else if (cameraMode === "overview") {
        map.fitBounds(baseRoute.getBounds(), { padding: CONFIG.fitBoundsPadding });
        cameraMode = "follow";
      }

      // Update UI Text
      let stateLabel = "Driver assigned", subLabel = "Trip state machine is controlling updates.";
      if (progress > 0.08) stateLabel = "Arriving pickup";
      if (progress > 0.22) stateLabel = "Cargo loading";
      if (progress > 0.30) { stateLabel = "En route to customer"; subLabel = "Camera is following truck in real time."; }
      if (progress > 0.86) stateLabel = "Approaching customer";
      if (progress >= 1) { stateLabel = "Delivered"; subLabel = "Delivery completed successfully."; }

      document.getElementById("statusLabel").textContent = stateLabel;
      document.getElementById("etaLabel").textContent = `${Math.max(0, Math.ceil((CONFIG.durationMs - elapsed) / 1000))} min`;
      document.getElementById("distanceLabel").textContent = `${traveledKm.toFixed(1)} / ${totalDistanceKm.toFixed(1)} km`;
      document.getElementById("progressFill").style.width = `${Math.round(progress * 100)}%`;
      document.getElementById("streetChip").textContent = b.street;
      document.getElementById("subStatus").textContent = subLabel;

      if (elapsed < CONFIG.durationMs) {
        trackingFrameRef = window.requestAnimationFrame(frame);
      }
    }

    trackingFrameRef = window.requestAnimationFrame(frame);
  }, 200);
}
