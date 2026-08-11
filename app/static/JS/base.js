// Fix: Scope variable declarations to prevent redeclaration errors if base.js is imported twice
(function initCustomCursor() {
    const cursor = document.querySelector('.cursor');
    const ring = document.getElementById('cursorRing');
    let mx = 0, my = 0, rx = 0, ry = 0, started = false;

    if (cursor && ring) {
        cursor.style.opacity = '0'; 
        ring.style.opacity = '0';
        
        document.addEventListener('mousemove', e => {
            mx = e.clientX; 
            my = e.clientY;
            if (!started) { 
                cursor.style.opacity = '1'; 
                ring.style.opacity = '1'; 
                started = true; 
            }
            cursor.style.left = mx + 'px'; 
            cursor.style.top = my + 'px';
        });

        (function animRing() {
            rx += (mx - rx) * 0.12; 
            ry += (my - ry) * 0.12;
            ring.style.left = rx + 'px'; 
            ring.style.top = ry + 'px';
            requestAnimationFrame(animRing);
        })();
    }
})();

// Close on Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        if (typeof closeLogout === 'function') closeLogout();
        
        // Also close avatar dropdown on Escape key
        const dropdown = document.getElementById('avatarDropdown');
        const chevron = document.getElementById('avatarChevron');
        const btn = document.getElementById('navAvatarBtn');
        if (dropdown && dropdown.classList.contains('open')) {
            dropdown.classList.remove('open');
            if (chevron) chevron.style.transform = 'rotate(0deg)';
            if (btn) btn.setAttribute('aria-expanded', 'false');
        }
    }
});

/* ── AVATAR DROPDOWN ── */

// 1. Instant Profile Photo Preview Logic
window.previewPhoto = function(input) {
    const previewContainer = document.getElementById('photoPreview');
    if (input.files && input.files[0]) {
        const reader = new FileReader();

        reader.onload = function(e) {
            let img = document.getElementById('photoPreviewImg');
            
            if (!img) {
                previewContainer.innerHTML = '';
                img = document.createElement('img');
                img.id = 'photoPreviewImg';
                img.alt = 'Profile photo preview';
                previewContainer.appendChild(img);
            }
            
            img.src = e.target.result;
            img.style.display = 'block';
        };

        reader.readAsDataURL(input.files[0]);
    }
};

// 2. Toggle Avatar Dropdown
window.toggleAvatarDropdown = function(event) {
    if (event) {
        event.stopPropagation();
    }
    
    const dropdown = document.getElementById('avatarDropdown');
    const chevron = document.getElementById('avatarChevron');
    const btn = document.getElementById('navAvatarBtn');
    
    if (!dropdown) return;
    
    const isOpen = dropdown.classList.toggle('open');
    
    if (chevron) {
        chevron.style.transform = isOpen ? 'rotate(180deg)' : 'rotate(0deg)';
    }
    if (btn) {
        btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    }
};

// 3. Close Dropdown on Outside Click
window.addEventListener('click', function(e) {
    const dropdown = document.getElementById('avatarDropdown');
    const chevron = document.getElementById('avatarChevron');
    const btn = document.getElementById('navAvatarBtn');
    
    if (dropdown && dropdown.classList.contains('open')) {
        const clickedInsideDropdown = dropdown.contains(e.target);
        const clickedAvatarBtn = e.target.closest('.nav-avatar-btn');
        const clickedNameBtn = e.target.closest('.nav-avatar-name-btn');
        
        if (!clickedInsideDropdown && !clickedAvatarBtn && !clickedNameBtn) {
            dropdown.classList.remove('open');
            if (chevron) chevron.style.transform = 'rotate(0deg)';
            if (btn) btn.setAttribute('aria-expanded', 'false');
        }
    }
});

/* ── DASHBOARD HASH ROUTING & TAB SWITCHING ── */

function handleHashChange() {
    const hash = window.location.hash; // e.g., "#sec-settings"
    if (!hash) return;

    // Select potential tab buttons and section elements across dashboards
    const tabs = document.querySelectorAll('.dashboard-tab, .sidebar-link, [data-tab]');
    const sections = document.querySelectorAll('.dashboard-section, .tab-content, section[id^="sec-"]');

    if (sections.length > 0) {
        // Remove active states
        sections.forEach(sec => sec.classList.remove('active'));
        tabs.forEach(tab => tab.classList.remove('active'));

        // Target section element (e.g., #sec-settings)
        const targetSection = document.querySelector(hash);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // Target tab button matching data-tab="sec-settings" or href="#sec-settings"
        const cleanHash = hash.replace('#', '');
        const targetTab = document.querySelector(`[data-tab="${cleanHash}"]`) || 
                          document.querySelector(`a[href="${hash}"]`);
        if (targetTab) {
            targetTab.classList.add('active');
        }
    }
}

// Listen for page loads with a hash and dynamic hash updates
document.addEventListener('DOMContentLoaded', handleHashChange);
window.addEventListener('hashchange', handleHashChange);