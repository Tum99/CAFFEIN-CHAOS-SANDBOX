function openLogout() {
  document.getElementById('logoutOverlay').classList.add('open');
}

function closeLogout() {
  document.getElementById('logoutOverlay').classList.remove('open');
}

// Also close if user clicks the dark background outside the box
document.getElementById('logoutOverlay').addEventListener('click', function(e) {
  if (e.target === this) closeLogout();
});

// Close on Escape key
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') closeLogout();
});

const cursor = document.getElementById('cursor');
const ring   = document.getElementById('cursorRing');
let mx = 0, my = 0, rx = 0, ry = 0, started = false;
if (cursor && ring) {
  cursor.style.opacity = '0'; ring.style.opacity = '0';
  document.addEventListener('mousemove', e => {
    mx = e.clientX; my = e.clientY;
    if (!started) { cursor.style.opacity = '1'; ring.style.opacity = '1'; started = true; }
    cursor.style.left = mx + 'px'; cursor.style.top = my + 'px';
  });
  (function animRing() {
    rx += (mx-rx)*0.12; ry += (my-ry)*0.12;
    ring.style.left = rx+'px'; ring.style.top = ry+'px';
    requestAnimationFrame(animRing);
  })();
}

/* ── AVATAR DROPDOWN ── */
function toggleAvatarDropdown(e) {
  e.stopPropagation();
  const dropdown = document.getElementById('avatarDropdown');
  const chevron  = document.getElementById('avatarChevron');
  const btn      = document.getElementById('navAvatarBtn');
  const isOpen   = dropdown.classList.toggle('open');
  if (chevron) chevron.textContent = isOpen ? '▴' : '▾';
  if (btn) btn.setAttribute('aria-expanded', isOpen);
}

/* Close dropdown when clicking outside */
document.addEventListener('click', e => {
  const wrap = document.getElementById('navAvatarWrap');
  if (wrap && !wrap.contains(e.target)) {
    document.getElementById('avatarDropdown')?.classList.remove('open');
    const chevron = document.getElementById('avatarChevron');
    if (chevron) chevron.textContent = '▾';
  }
});

/* Close dropdown on Escape */
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.getElementById('avatarDropdown')?.classList.remove('open');
  }
});