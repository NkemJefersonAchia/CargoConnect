/* ── Booking Form, Truck Search & MoMo Payment ────────────── */

document.addEventListener('DOMContentLoaded', function () {
  loadCustomerStats();
  loadActiveBooking();
  loadRecentBookings();
  loadNotifications();
  setupSearchForm();
  setupModal();
  setupMarkRead();
  setupPaymentModal();
});

function setupMarkRead() {
  const btn = document.getElementById('markReadBtn');
  if (btn) btn.addEventListener('click', markAllNotificationsRead);
}

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
      const isPaid = b.payment_status === 'paid';
      const payBtn = !isPaid
        ? `<button class="btn btn--momo" onclick="openPaymentModal(${b.booking_id}, ${b.estimated_cost})">
             <i class="fa-solid fa-mobile-screen-button"></i> Pay via MTN MoMo
           </button>`
        : `<span class="badge badge--paid">Paid</span>`;

      container.innerHTML = `
        <dl class="detail-list">
          <dt>Driver</dt><dd>${b.driver_name}</dd>
          <dt>Truck</dt><dd>${b.plate_no}</dd>
          <dt>Pickup</dt><dd>${b.pickup_address}</dd>
          <dt>Dropoff</dt><dd>${b.dropoff_address}</dd>
          <dt>Cost</dt><dd>${Number(b.estimated_cost).toLocaleString()} RWF</dd>
        </dl>
        <div class="btn-row" style="margin-top:1rem; gap:0.75rem; display:flex; flex-wrap:wrap; align-items:center;">
          <a href="/track/${b.booking_id}" class="btn btn--action">
            <i class="fa-solid fa-location-dot"></i> Track Truck
          </a>
          ${payBtn}
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
      tbody.innerHTML = json.data.map(b => {
        const isPaid = b.payment_status === 'paid';
        const canPay = !isPaid && (b.status === 'confirmed' || b.status === 'completed' || b.status === 'pending');
        const actionCell = canPay
          ? `<button class="btn btn--sm btn--momo" onclick="openPaymentModal(${b.booking_id}, ${b.estimated_cost})">
               <i class="fa-solid fa-mobile-screen-button"></i> Pay
             </button>`
          : isPaid
            ? `<span class="badge badge--paid">Paid</span>`
            : `<a href="/track/${b.booking_id}" class="btn btn--sm btn--ghost">View</a>`;

        return `
          <tr>
            <td>#${b.booking_id}</td>
            <td>${b.pickup_address}</td>
            <td>${b.dropoff_address}</td>
            <td>${b.created_at}</td>
            <td><span class="badge badge--${b.status}">${b.status}</span></td>
            <td>${Number(b.estimated_cost).toLocaleString()}</td>
            <td>${actionCell}</td>
          </tr>
        `;
      }).join('');
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

      const listEl = document.getElementById('notificationsList');
      if (listEl) {
        const items = json.data.items || [];
        if (items.length === 0) {
          listEl.innerHTML = '<p class="empty-state__text">No unread notifications.</p>';
        } else {
          listEl.innerHTML = items.map(n => `
            <div class="notification-item">
              <p class="notification-item__msg">${n.message}</p>
              <p class="notification-item__time">${new Date(n.sent_at).toLocaleString('en-RW', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</p>
            </div>
          `).join('');
        }
      }
    }
  } catch (e) { console.error(e); }
}

async function markAllNotificationsRead() {
  try {
    await fetch('/customer/notifications/mark-read', { method: 'POST' });
    loadNotifications();
  } catch (e) { console.error(e); }
}

// ── Truck Search ─────────────────────────────────────────────

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
            <span class="truck-card__rating"><i class="fa-solid fa-star" style="color:#E85D04;font-size:0.85rem;"></i> ${d.rating.toFixed(1)}</span>
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

// ── Booking Confirmation Modal ────────────────────────────────

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

// ── MTN MoMo Payment Modal ───────────────────────────────────

let momoBookingId = null;
let momoPin = '';

function setupPaymentModal() {
  const backdrop = document.getElementById('momoBackdrop');
  if (backdrop) backdrop.addEventListener('click', closePaymentModal);

  const cancelBtn = document.getElementById('momoCancelBtn');
  if (cancelBtn) cancelBtn.addEventListener('click', closePaymentModal);

  const doneBtn = document.getElementById('momoDoneBtn');
  if (doneBtn) doneBtn.addEventListener('click', closePaymentModal);

  const clearBtn = document.getElementById('momoClear');
  if (clearBtn) clearBtn.addEventListener('click', () => { momoPin = ''; updatePinDots(); });

  const backBtn = document.getElementById('momoBack');
  if (backBtn) backBtn.addEventListener('click', () => { momoPin = momoPin.slice(0, -1); updatePinDots(); });

  // Digit keys
  document.querySelectorAll('.momo-key[data-digit]').forEach(btn => {
    btn.addEventListener('click', function () {
      if (momoPin.length < 4) {
        momoPin += this.dataset.digit;
        updatePinDots();
      }
    });
  });

  const payBtn = document.getElementById('momoPayBtn');
  if (payBtn) payBtn.addEventListener('click', submitPayment);
}

function openPaymentModal(bookingId, amount) {
  momoBookingId = bookingId;
  momoPin = '';
  updatePinDots();

  // Show amount and phone
  setEl('momoAmountLabel', Number(amount).toLocaleString() + ' RWF');
  setEl('momoSuccessAmount', Number(amount).toLocaleString() + ' RWF');

  // Reset to PIN step
  document.getElementById('momoStepPin').style.display = '';
  document.getElementById('momoStepProcessing').style.display = 'none';
  document.getElementById('momoStepSuccess').style.display = 'none';

  document.getElementById('momoModal').style.display = 'flex';
}

function closePaymentModal() {
  document.getElementById('momoModal').style.display = 'none';
  momoBookingId = null;
  momoPin = '';
  // Refresh data in case payment completed
  loadActiveBooking();
  loadRecentBookings();
  loadNotifications();
  loadCustomerStats();
}

function updatePinDots() {
  for (let i = 0; i < 4; i++) {
    const dot = document.getElementById('momoDot' + i);
    if (dot) {
      if (i < momoPin.length) {
        dot.classList.add('momo-dot--filled');
      } else {
        dot.classList.remove('momo-dot--filled');
      }
    }
  }
  const payBtn = document.getElementById('momoPayBtn');
  if (payBtn) payBtn.disabled = momoPin.length < 4;
}

async function submitPayment() {
  if (!momoBookingId || momoPin.length < 4) return;

  // Show processing step
  document.getElementById('momoStepPin').style.display = 'none';
  document.getElementById('momoStepProcessing').style.display = '';
  document.getElementById('momoStepSuccess').style.display = 'none';

  try {
    // Simulate processing delay (1.5s) for realism
    await new Promise(resolve => setTimeout(resolve, 1500));

    const res = await fetch(`/payment/simulate/${momoBookingId}`, { method: 'POST' });
    const json = await res.json();

    if (json.status === 'success') {
      document.getElementById('momoStepProcessing').style.display = 'none';
      document.getElementById('momoStepSuccess').style.display = '';
    } else {
      document.getElementById('momoStepProcessing').style.display = 'none';
      document.getElementById('momoStepPin').style.display = '';
      alert(json.message || 'Payment failed. Please try again.');
    }
  } catch (e) {
    console.error(e);
    document.getElementById('momoStepProcessing').style.display = 'none';
    document.getElementById('momoStepPin').style.display = '';
    alert('Network error. Please try again.');
  }
}

// ── Utilities ────────────────────────────────────────────────

function setEl(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}
