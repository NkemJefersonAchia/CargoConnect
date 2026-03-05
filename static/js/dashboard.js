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
