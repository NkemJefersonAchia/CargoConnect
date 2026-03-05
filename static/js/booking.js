/* ── Booking Form & Truck Search ─────────────────────────── */

document.addEventListener('DOMContentLoaded', function () {
  loadCustomerStats();
  loadActiveBooking();
  loadRecentBookings();
  loadNotifications();
  setupSearchForm();
  setupModal();
});

async function loadCustomerStats() {
  try {
    const res = await fetch('/customer/stats');
    const json = await res.json();
    if (json.status === 'success') {
      const d = json.data;
      setEl('statTotal', d.total_bookings);
      setEl('statCompleted', d.completed_trips);
      setEl('statPending', d.pending_bookings);
      setEl('statSpent', Number(d.total_spent).toLocaleString() + ' RWF');
    }
  } catch (e) { console.error(e); }
}

async function loadActiveBooking() {
  try {
    const res = await fetch('/customer/active-booking');
    const json = await res.json();
    const container = document.getElementById('activeBookingContent');
    if (!container) return;

    if (json.status === 'success' && json.data) {
      const b = json.data;
      container.innerHTML = `
        <dl class="detail-list">
          <dt>Driver</dt><dd>${b.driver_name}</dd>
          <dt>Truck</dt><dd>${b.plate_no}</dd>
          <dt>Pickup</dt><dd>${b.pickup_address}</dd>
          <dt>Dropoff</dt><dd>${b.dropoff_address}</dd>
          <dt>Cost</dt><dd>${Number(b.estimated_cost).toLocaleString()} RWF</dd>
        </dl>
        <div class="btn-row">
          <a href="/track/${b.booking_id}" class="btn btn--action">&#128205; Track Truck</a>
        </div>
      `;
    } else {
      container.innerHTML = `
        <div class="empty-state">
          <p>No active trip right now.</p>
          <a href="#quickbook" class="btn btn--action">Book a Truck</a>
        </div>
      `;
    }
  } catch (e) { console.error(e); }
}

async function loadRecentBookings() {
  try {
    const res = await fetch('/customer/recent-bookings');
    const json = await res.json();
    const tbody = document.getElementById('recentTableBody');
    if (!tbody) return;

    if (json.status === 'success' && json.data.length > 0) {
      tbody.innerHTML = json.data.map(b => `
        <tr>
          <td>#${b.booking_id}</td>
          <td>${b.pickup_address}</td>
          <td>${b.dropoff_address}</td>
          <td>${b.created_at}</td>
          <td><span class="badge badge--${b.status}">${b.status}</span></td>
          <td>${Number(b.estimated_cost).toLocaleString()}</td>
          <td><a href="/track/${b.booking_id}" class="btn btn--sm btn--ghost">View</a></td>
        </tr>
      `).join('');
    } else {
      tbody.innerHTML = '<tr><td colspan="7" class="table-empty">No bookings yet.</td></tr>';
    }
  } catch (e) { console.error(e); }
}

async function loadNotifications() {
  try {
    const res = await fetch('/customer/notifications');
    const json = await res.json();
    if (json.status === 'success') {
      const count = json.data.count;
      ['notifBadge', 'notifBadgeTop'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = count;
      });
    }
  } catch (e) { console.error(e); }
}

// ── Truck Search ────────────────────────────────────────────

let selectedDriver = null;

function setupSearchForm() {
  const form = document.getElementById('searchForm');
  if (!form) return;

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    const pickup = document.getElementById('pickupAddress').value.trim();
    const dropoff = document.getElementById('dropoffAddress').value.trim();
    const weight = parseFloat(document.getElementById('cargoWeight').value) || 1;

    try {
      const res = await fetch('/booking/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pickup_address: pickup,
          dropoff_address: dropoff,
          weight: weight,
          pickup_lat: -1.9441,
          pickup_lng: 30.0619,
        }),
      });
      const json = await res.json();
      if (json.status === 'success') {
        displayTruckResults(json.data);
      } else {
        alert(json.message);
      }
    } catch (e) { console.error(e); }
  });
}

function displayTruckResults(drivers) {
  const container = document.getElementById('truckResults');
  const list = document.getElementById('truckList');
  if (!container || !list) return;

  if (drivers.length === 0) {
    list.innerHTML = '<p class="empty-state__text">No available trucks found matching your criteria.</p>';
  } else {
    list.innerHTML = drivers.map(d => `
      <article class="truck-card">
        <div class="truck-card__info">
          <p class="truck-card__name">${d.driver_name}</p>
          <div class="truck-card__meta">
            <span class="truck-card__rating">&#9733; ${d.rating.toFixed(1)}</span>
            <span>Plate: ${d.plate_no}</span>
            <span>Capacity: ${d.capacity} tons</span>
            ${d.distance_km ? `<span>~${d.distance_km} km away</span>` : ''}
          </div>
        </div>
        <div>
          <p class="truck-card__price">${Number(d.estimated_cost).toLocaleString()} RWF</p>
          <button class="btn btn--action" style="margin-top:8px;" onclick="openBookingModal(${JSON.stringify(d).replace(/"/g, '&quot;')})">
            Book This Truck
          </button>
        </div>
      </article>
    `).join('');
  }
  container.style.display = '';
}

// ── Modal ───────────────────────────────────────────────────

function setupModal() {
  const backdrop = document.getElementById('modalBackdrop');
  const cancelBtn = document.getElementById('modalCancel');
  const confirmBtn = document.getElementById('modalConfirm');

  if (backdrop) backdrop.addEventListener('click', closeModal);
  if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
  if (confirmBtn) confirmBtn.addEventListener('click', confirmBooking);
}

function openBookingModal(driver) {
  selectedDriver = driver;
  const details = document.getElementById('modalDetails');
  const pickup = document.getElementById('pickupAddress').value;
  const dropoff = document.getElementById('dropoffAddress').value;
  const scheduled = document.getElementById('scheduledTime').value;

  details.innerHTML = `
    <dl class="detail-list">
      <dt>Driver</dt><dd>${driver.driver_name}</dd>
      <dt>Truck</dt><dd>${driver.plate_no} (${driver.capacity} tons)</dd>
      <dt>Pickup</dt><dd>${pickup}</dd>
      <dt>Dropoff</dt><dd>${dropoff}</dd>
      <dt>Scheduled</dt><dd>${scheduled}</dd>
      <dt>Estimated Cost</dt><dd>${Number(driver.estimated_cost).toLocaleString()} RWF</dd>
    </dl>
  `;
  document.getElementById('confirmModal').classList.add('modal--open');
}

function closeModal() {
  document.getElementById('confirmModal').classList.remove('modal--open');
  selectedDriver = null;
}

async function confirmBooking() {
  if (!selectedDriver) return;
  const pickup = document.getElementById('pickupAddress').value;
  const dropoff = document.getElementById('dropoffAddress').value;
  const scheduled = document.getElementById('scheduledTime').value;

  try {
    const res = await fetch('/booking/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        truck_id: selectedDriver.truck_id,
        driver_id: selectedDriver.driver_id,
        pickup_address: pickup,
        dropoff_address: dropoff,
        scheduled_time: scheduled,
        estimated_cost: selectedDriver.estimated_cost,
      }),
    });
    const json = await res.json();
    if (json.status === 'success') {
      closeModal();
      alert('Booking created! The driver will confirm shortly.');
      loadActiveBooking();
      loadRecentBookings();
      loadCustomerStats();
    } else {
      alert(json.message);
    }
  } catch (e) { console.error(e); }
}

// ── Utilities ───────────────────────────────────────────────

function setEl(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}
