/* ── Auth Page Logic ──────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', function () {
  setupRoleToggle();
  setupFlashDismiss();
});

function setupRoleToggle() {
  const roleInputs = document.querySelectorAll('input[name="role"]');
  const licenceGroup = document.getElementById('licenceGroup');
  if (!licenceGroup) return;

  roleInputs.forEach(function (input) {
    input.addEventListener('change', function () {
      licenceGroup.style.display = this.value === 'driver' ? '' : 'none';
    });
  });
}

function setupFlashDismiss() {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(function (el) {
    setTimeout(function () {
      el.style.opacity = '0';
      el.style.transition = 'opacity 0.3s';
      setTimeout(function () { el.remove(); }, 300);
    }, 4000);
  });
}
