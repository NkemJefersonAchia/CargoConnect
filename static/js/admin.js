/* ── Admin UI: sidebar toggle, dates, API helpers ─────────── */

document.addEventListener('DOMContentLoaded', function () {
  setupHamburger();
});

function setupHamburger() {
  const btn = document.getElementById('hamburgerBtn');
  const sidebar = document.getElementById('sidebar');
  if (!btn || !sidebar) return;

  btn.addEventListener('click', function () {
    sidebar.classList.toggle('sidebar--open');
  });
}

function truncate(str, maxLen) {
  if (!str) return '';
  return str.length > maxLen ? str.slice(0, maxLen) + '…' : str;
}

function formatDate(isoString) {
  if (!isoString) return '—';
  const d = new Date(isoString);
  return d.toLocaleDateString('en-RW', { day: '2-digit', month: 'short', year: 'numeric' });
}

async function apiRequest(url, method = 'GET', body = null) {
  const options = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) options.body = JSON.stringify(body);
  const res = await fetch(url, options);
  return res.json();
}
