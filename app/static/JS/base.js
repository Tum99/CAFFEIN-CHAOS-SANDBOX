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
// 1. Instant Profile Photo Preview Logic
function previewPhoto(input) {
    const previewContainer = document.getElementById('photoPreview');
    if (input.files && input.files[0]) {
        const reader = new FileReader();

        reader.onload = function(e) {
            // Check if an img element already exists
            let img = document.getElementById('photoPreviewImg');
            
            if (!img) {
                // If the user had initials displaying, clear them and create an img tag
                previewContainer.innerHTML = '';
                img = document.createElement('img');
                img.id = 'photoPreviewImg';
                img.alt = 'Profile photo preview';
                previewContainer.appendChild(img);
            }
            
            // Assign the file data URL to the source view
            img.src = e.target.result;
            img.style.display = 'block';
        };

        reader.readAsDataURL(input.files[0]);
    }
}

// 2. Navigation Avatar Dropdown Toggle logic
function toggleAvatarDropdown(event) {
    event.stopPropagation(); // Prevents instant closing via window click listener
    const dropdown = document.getElementById('avatarDropdown');
    const chevron = document.getElementById('avatarChevron');
    const btn = document.getElementById('navAvatarBtn');
    
    const isOpen = dropdown.classList.contains('active');
    
    // Toggle current state
    if (isOpen) {
        dropdown.classList.remove('active');
        if (chevron) chevron.style.transform = 'rotate(0deg)';
        btn.setAttribute('aria-expanded', 'false');
    } else {
        dropdown.classList.add('active');
        if (chevron) chevron.style.transform = 'rotate(180deg)';
        btn.setAttribute('aria-expanded', 'true');
    }
}

// Close the dropdown automatically if clicking outside of its area
window.addEventListener('click', function(e) {
    const dropdown = document.getElementById('avatarDropdown');
    const chevron = document.getElementById('avatarChevron');
    const btn = document.getElementById('navAvatarBtn');
    
    if (dropdown && dropdown.classList.contains('active')) {
        if (!dropdown.contains(e.target) && !e.target.closest('.nav-avatar-btn') && !e.target.closest('.nav-avatar-name-btn')) {
            dropdown.classList.remove('active');
            if (chevron) chevron.style.transform = 'rotate(0deg)';
            if (btn) btn.setAttribute('aria-expanded', 'false');
        }
    }
});