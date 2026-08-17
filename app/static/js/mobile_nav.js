document.addEventListener('DOMContentLoaded', () => {

  /* ── HAMBURGER MENU ── */
  const hamburger = document.getElementById('navHamburger');
  const navLinks  = document.getElementById('navLinks');

  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
      const isOpen = navLinks.classList.toggle('open');
      hamburger.classList.toggle('open', isOpen);
      hamburger.setAttribute('aria-expanded', isOpen);
    });

    /* Close nav when a link is clicked */
    navLinks.querySelectorAll('a, button').forEach(el => {
      el.addEventListener('click', () => {
        navLinks.classList.remove('open');
        hamburger.classList.remove('open');
      });
    });

    /* Close nav when clicking outside */
    document.addEventListener('click', (e) => {
      if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
        navLinks.classList.remove('open');
        hamburger.classList.remove('open');
      }
    });
  }


  /* ── FILTER DRAWER (marketplace mobile) ── */
  const filterToggle  = document.getElementById('filterToggle');
  const filterSidebar = document.querySelector('.filter-sidebar');

  if (filterToggle && filterSidebar) {
    filterToggle.addEventListener('click', () => {
      filterSidebar.classList.toggle('filter-open');
      const arrow = filterToggle.querySelector('.filter-toggle-arrow');
      if (arrow) {
        arrow.textContent = filterSidebar.classList.contains('filter-open') ? '▲' : '▼';
      }
    });
  }

});
// JSEOF
// echo "mobile nav js done"