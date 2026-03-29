/* ── Dashboards: nav, money/date formatting, shared tables ─ */

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
      if (!sidebar.contains(e.target) && e.target.id !== 'hamburgerBtn') {
        sidebar.classList.remove('sidebar--open');
      }
    }
  });
}

function formatRWF(value) { return Number(value).toLocaleString('en-RW'); }

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

/* ── MoMo Success Flow (3-Second Delay & Track Button) ─────── */
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
    trackBtn.innerHTML = '<i class="fa-solid fa-location-dot"></i> Track';
    trackBtn.addEventListener('click', function () { startMapTrackingSimulation(); });
    actionsWrap.appendChild(trackBtn);
  }, 3000);
};

/* ── Tracking Simulation Engine ─────────────────────────────── */
let trackingFrameRef = null;

function startMapTrackingSimulation() {
  const modal = document.getElementById('trackingSimModal');
  if (!modal) return;
  modal.classList.add('modal--open');

  const closeBtn     = document.getElementById('simCloseBtn');
  const backdropBtn  = document.getElementById('simModalBackdrop');

  function closeModal() {
    modal.classList.remove('modal--open');
    if (trackingFrameRef) { window.cancelAnimationFrame(trackingFrameRef); trackingFrameRef = null; }
    if (window._simMapInstance) {
      window._simMapInstance.remove();
      window._simMapInstance = null;
      const mapEl = document.getElementById('simMap');
      if (mapEl) mapEl.innerHTML = '';
    }
  }

  if (closeBtn)    closeBtn.onclick    = closeModal;
  if (backdropBtn) backdropBtn.onclick = closeModal;

  /* Wait briefly so modal is visible before Leaflet measures the container */
  setTimeout(function () {
    if (window._simMapInstance) {
      window._simMapInstance.remove();
      window._simMapInstance = null;
      const mapEl = document.getElementById('simMap');
      if (mapEl) mapEl.innerHTML = '';
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
        { lat: -1.9474, lng: 30.0600, street: "KN 3 Rd" },
        { lat: -1.9466, lng: 30.0613, street: "Destination Street" },
      ],
    };

    function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }
    function lerp(a, b, t)      { return a + (b - a) * t; }

    const map = L.map('simMap', { zoomControl: false, attributionControl: false })
                  .setView(CONFIG.center, CONFIG.zoom);
    window._simMapInstance = map;

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', { maxZoom: 19 }).addTo(map);

    const latlngs     = CONFIG.route.map(p => [p.lat, p.lng]);
    const baseRoute   = L.polyline(latlngs,     { color: '#9eb5de', weight: 7, opacity: 0.85, lineCap: 'round', lineJoin: 'round' }).addTo(map);
    const progressRoute = L.polyline([latlngs[0]], { color: '#16A34A', weight: 7, opacity: 0.95, lineCap: 'round', lineJoin: 'round' }).addTo(map);

    L.circleMarker(latlngs[0], { radius: 7, color: '#E85D04', weight: 3, fillColor: '#E85D04', fillOpacity: 1 })
      .addTo(map)
      .bindTooltip('Pickup',   { permanent: true, direction: 'right', className: 'map-tooltip', offset: [10, 0] });

    L.circleMarker(latlngs[latlngs.length - 1], { radius: 7, color: '#0A1F44', weight: 3, fillColor: '#0A1F44', fillOpacity: 1 })
      .addTo(map)
      .bindTooltip('Customer', { permanent: true, direction: 'right', className: 'map-tooltip', offset: [10, 0] });

    const icon = L.divIcon({
      className: '',
      html: `<div class="truck-marker">
               <span class="truck-marker__body"></span>
               <span class="truck-marker__cab"></span>
               <span class="truck-marker__wheel truck-marker__wheel--back"></span>
               <span class="truck-marker__wheel truck-marker__wheel--front"></span>
             </div>`,
      iconSize: [44, 24],
      iconAnchor: [22, 12],
    });
    const truckMarker = L.marker(latlngs[0], { icon, keyboard: false })
      .addTo(map)
      .bindTooltip('Driver', { permanent: true, direction: 'bottom', className: 'map-tooltip', offset: [0, 15] });

    map.fitBounds(baseRoute.getBounds(), { padding: CONFIG.fitBoundsPadding });

    /* Build cumulative-distance timeline */
    let cumulative = 0;
    const timeline = [{ ...CONFIG.route[0], t: 0, cumulativeKm: 0 }];
    for (let i = 1; i < CONFIG.route.length; i++) {
      const a = CONFIG.route[i - 1], b = CONFIG.route[i];
      const dLat = ((b.lat - a.lat) * Math.PI) / 180;
      const dLng = ((b.lng - a.lng) * Math.PI) / 180;
      const q    = Math.sin(dLat / 2) ** 2 +
                   Math.cos((a.lat * Math.PI) / 180) * Math.cos((b.lat * Math.PI) / 180) *
                   Math.sin(dLng / 2) ** 2;
      cumulative += 2 * 6371 * Math.atan2(Math.sqrt(q), Math.sqrt(1 - q));
      timeline.push({ ...b, cumulativeKm: cumulative, t: 0 });
    }
    const totalDistanceKm = cumulative;
    timeline.forEach(p => { p.t = cumulative > 0 ? (p.cumulativeKm / cumulative) * CONFIG.durationMs : 0; });

    const startMs    = performance.now();
    let cameraMode   = 'overview';

    function frame(now) {
      const elapsed  = now - startMs;
      const t        = clamp(elapsed, 0, CONFIG.durationMs);
      const progress = t / CONFIG.durationMs;

      let i = 0;
      while (i < timeline.length - 1 && timeline[i + 1].t < t) i++;
      const a = timeline[i];
      const b = timeline[Math.min(i + 1, timeline.length - 1)];
      const segT = b.t === a.t ? 0 : (t - a.t) / (b.t - a.t);

      const lat        = lerp(a.lat, b.lat, segT);
      const lng        = lerp(a.lng, b.lng, segT);
      const traveledKm = lerp(a.cumulativeKm, b.cumulativeKm, segT);
      const headingDeg = Math.atan2(a.lat - b.lat, b.lng - a.lng) * (180 / Math.PI);

      truckMarker.setLatLng([lat, lng]);
      const markerEl = truckMarker.getElement();
      if (markerEl) {
        const truckEl = markerEl.querySelector('.truck-marker');
        if (truckEl) truckEl.style.transform = `rotate(${headingDeg}deg)`;
      }

      const completedCoords = timeline.slice(0, i + 1).map(p => [p.lat, p.lng]);
      completedCoords.push([lat, lng]);
      progressRoute.setLatLngs(completedCoords);

      if (cameraMode === 'follow') {
        map.panTo([lat, lng], { animate: true, duration: 0.2 });
      } else {
        map.fitBounds(baseRoute.getBounds(), { padding: CONFIG.fitBoundsPadding });
        cameraMode = 'follow';
      }

      let stateLabel = 'Driver assigned';
      let subLabel   = 'Trip state machine is controlling updates.';
      if (progress > 0.08) stateLabel = 'Arriving at pickup';
      if (progress > 0.22) stateLabel = 'Cargo loading';
      if (progress > 0.30) { stateLabel = 'En route to customer'; subLabel = 'Camera is following truck in real time.'; }
      if (progress > 0.86) stateLabel = 'Approaching customer';
      if (progress >= 1)   { stateLabel = 'Delivered'; subLabel = 'Delivery completed successfully.'; }

      const statusEl   = document.getElementById('statusLabel');
      const etaEl      = document.getElementById('etaLabel');
      const distEl     = document.getElementById('distanceLabel');
      const fillEl     = document.getElementById('progressFill');
      const chipEl     = document.getElementById('streetChip');
      const subEl      = document.getElementById('subStatus');

      if (statusEl) statusEl.textContent = stateLabel;
      if (etaEl)    etaEl.textContent    = `${Math.max(0, Math.ceil((CONFIG.durationMs - elapsed) / 1000))} min`;
      if (distEl)   distEl.textContent   = `${traveledKm.toFixed(1)} / ${totalDistanceKm.toFixed(1)} km`;
      if (fillEl)   fillEl.style.width   = `${Math.round(progress * 100)}%`;
      if (chipEl)   chipEl.textContent   = b.street;
      if (subEl)    subEl.textContent    = subLabel;

      if (elapsed < CONFIG.durationMs) {
        trackingFrameRef = window.requestAnimationFrame(frame);
      }
    }

    trackingFrameRef = window.requestAnimationFrame(frame);
  }, 200);
}
