/* ── Live GPS Tracking — Customer View ───────────────────── */
/* Renders Leaflet map and listens for real-time driver location via SocketIO */

document.addEventListener('DOMContentLoaded', function () {
  initMap();
  connectSocket();
});

const KIGALI_LAT = -1.9441;
const KIGALI_LNG = 30.0619;
const ZOOM_LEVEL = 14;

let map = null;
let driverMarker = null;
let dropoffMarker = null;

function initMap() {
  map = L.map('map').setView([KIGALI_LAT, KIGALI_LNG], ZOOM_LEVEL);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
  }).addTo(map);

  const dropoffIcon = L.divIcon({
    html: '<div style="background:#0A1F44;width:16px;height:16px;border-radius:50%;border:3px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.3);"></div>',
    className: '',
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  });

  if (typeof DROPOFF_LAT !== 'undefined' && typeof DROPOFF_LNG !== 'undefined') {
    dropoffMarker = L.marker([DROPOFF_LAT, DROPOFF_LNG], { icon: dropoffIcon })
      .addTo(map)
      .bindPopup('Dropoff destination');
  }
}

function createDriverIcon() {
  return L.divIcon({
    html: '<div style="background:#E85D04;width:20px;height:20px;border-radius:50%;border:3px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center;font-size:10px;">&#128666;</div>',
    className: '',
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });
}

function connectSocket() {
  const socket = io();

  socket.on('connect', function () {
    if (typeof BOOKING_ID !== 'undefined') {
      socket.emit('join_tracking_room', { booking_id: BOOKING_ID });
    }
  });

  socket.on('location_update', function (data) {
    const lat = data.latitude;
    const lng = data.longitude;

    const statusEl = document.getElementById('locationStatus');
    if (statusEl) {
      statusEl.textContent = `Driver location updated: ${lat.toFixed(4)}, ${lng.toFixed(4)}`;
    }

    if (driverMarker) {
      driverMarker.setLatLng([lat, lng]);
    } else {
      driverMarker = L.marker([lat, lng], { icon: createDriverIcon() })
        .addTo(map)
        .bindPopup('Your driver');
    }

    map.panTo([lat, lng]);
  });

  socket.on('disconnect', function () {
    const statusEl = document.getElementById('locationStatus');
    if (statusEl) statusEl.textContent = 'Connection lost. Reconnecting...';
  });
}
