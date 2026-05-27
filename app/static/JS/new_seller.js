/* ══════════════ CURSOR LOGIC ══════════════ */
const cur = document.getElementById('cursor'), ring = document.getElementById('cursorRing');
let mx = 0, my = 0, rx = 0, ry = 0;
document.addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; if(cur) cur.style.left = mx + 'px'; if(cur) cur.style.top = my + 'px'; });
(function loop() { rx += (mx - rx) * 0.12; ry += (my - ry) * 0.12; if(ring) ring.style.left = rx + 'px'; if(ring) ring.style.top = ry + 'px'; requestAnimationFrame(loop); })();

/* ══════════════ SECTION SWITCHING ══════════════ */
// 1. Define your available sections (Ensure these match your HTML IDs: sec-overview, etc.)
const sections = ['overview', 'farm-profile', 'messages', 'settings', 'new-listing', 'listings', 'orders', 'earnings'];

/**
 * Main function to toggle dashboard views
 * @param {string} name - The name of the section to show
 * @param {Event} e - Optional event object to handle defaults
 */
function showSection(name, e) {
    if (e) e.preventDefault();

    // Toggle Content Sections
    sections.forEach(s => {
        const el = document.getElementById(`sec-${s}`);
        if (el) {
            el.style.display = (s === name) ? 'block' : 'none';
        }
    });

    // Handle Sidebar Active States
    document.querySelectorAll('.sidebar-link').forEach(link => {
        link.classList.remove('active');
        
        // If this link's onclick contains the section name, highlight it
        // This works even if you triggered the function from a button in the main content
        if (link.getAttribute('onclick') && link.getAttribute('onclick').includes(`'${name}'`)) {
            link.classList.add('active');
        }
    });

    // Optional: Smooth scroll back to top of the dashboard main area
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Updates the Date and Greeting based on local time
 */
function updateDashboardHeader() {
    const dateElement = document.getElementById('currentDate');
    const greetingElement = document.querySelector('.dash-greeting');
    
    if (!dateElement || !greetingElement) return;

    const now = new Date();
    const hours = now.getHours();

    // 1. Dynamic Greeting
    let greeting = "Good evening";
    if (hours < 12) {
        greeting = "Good morning";
    } else if (hours < 18) {
        greeting = "Good afternoon";
    }
    
    // Preserves the username if Flask already rendered it
    const parts = greetingElement.innerText.split(',');
    const userName = parts.length > 1 ? parts[1].trim() : "";
    greetingElement.innerText = `${greeting}, ${userName}`;

    // 2. Accurate Date (Format: Wednesday, 23 April 2026)
    const options = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
    dateElement.textContent = now.toLocaleDateString('en-GB', options);
}

// 3. Initialize on Page Load
document.addEventListener('DOMContentLoaded', () => {
    updateDashboardHeader();
    
    // Optional: Update time every minute to keep the greeting accurate
    setInterval(updateDashboardHeader, 60000);

    // Initial check: if the URL has a hash, show that section
    // e.g. caffeinandchaos.com/setup#new-listing
    const hash = window.location.hash.replace('#', '');
    if (sections.includes(hash)) {
        showSection(hash);
    }
});

/* ══════════════ PROGRESS TRACKING ══════════════ */
// This reads the "1" or "0" we added to the HTML data-attribute
const progressBarEl = document.getElementById('progressBar');
let stepsComplete = parseInt(progressBarEl.getAttribute('data-db-steps')) || 0;

function updateProgress() {
    const pct = Math.round((stepsComplete / 3) * 100);
    const bar = document.getElementById('progressBar');
    const pctLabel = document.getElementById('progressPct');
    const countLabel = document.getElementById('stepsCount');

    if (bar) bar.style.width = pct + '%';
    if (pctLabel) pctLabel.textContent = pct + '%';
    if (countLabel) countLabel.textContent = stepsComplete;
}

/* ══════════════ PERSISTENT UI UPDATES ══════════════ */
/**
 * This function applies all the "Green" visual states and unlocks.
 * It runs automatically if the Database says step 1 is done.
 */
function applyStep1CompletionUI() {
    // 1. Mark step 1 visually done
    const s1 = document.getElementById('step1');
    if (s1) {
        s1.classList.remove('active-step');
        s1.classList.add('completed');
        document.getElementById('step1Status').className = 'step-status done';
        document.getElementById('step1Status').textContent = '✓ Done';
        document.getElementById('step1Btn').className = 'step-cta done-btn';
        document.getElementById('step1Btn').textContent = '✓ Profile Saved';
        document.getElementById('step1Btn').setAttribute('onclick', "showSection('farm-profile', event)");
    }

    // 2. Unlock step 2
    const s2 = document.getElementById('step2');
    if (s2) {
        s2.classList.remove('locked-step');
        s2.classList.add('active-step');
        document.getElementById('step2Status').className = 'step-status next';
        document.getElementById('step2Status').textContent = '→ Up Next';
        const s2Btn = document.getElementById('step2Btn');
        s2Btn.className = 'step-cta green';
        s2Btn.textContent = 'Add First Listing →';
        // Now clicking this button goes to the listing section
        s2Btn.setAttribute('onclick', "showSection('new-listing', event)");
    }

    // 3. Show the farm badge in sidebar
    const badge = document.getElementById('farmBadge');
    if (badge) badge.style.display = 'flex';

    // 4. Unlock listings in sidebar
    ['listingsLink', 'newListingLink', 'ordersLink', 'earningsLink'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.classList.remove('locked');
            const lock = el.querySelector('.sidebar-lock');
            if (lock) lock.remove();
            
            // Map the sidebar clicks to sections
            if(id === 'newListingLink') el.setAttribute('onclick', "showSection('new-listing', event)");
        }
    });
}

function applyStep2CompletionUI() {
    // 1. Mark step 1 visually done
    const s1 = document.getElementById('step1');
    if (s1) {
        s1.classList.remove('active-step');
        s1.classList.add('completed');
        const s1Status = document.getElementById('step1Status');
        const s1Btn = document.getElementById('step1Btn');
        
        if(s1Status) {
            s1Status.className = 'step-status done';
            s1Status.textContent = '✓ Done';
        }
        if(s1Btn) {
            s1Btn.className = 'step-cta done-btn';
            s1Btn.textContent = '✓ Profile Saved';
            s1Btn.setAttribute('onclick', "showSection('farm-profile', event)");
        }
    }

    // 2. Mark step 2 visually done
    const s2 = document.getElementById('step2');
    if (s2) {
        s2.classList.remove('active-step');
        s2.classList.add('completed');
        const s2Status = document.getElementById('step2Status');
        const s2Btn = document.getElementById('step2Btn');

        if(s2Status) {
            s2Status.className = 'step-status done';
            s2Status.textContent = '✓ Done';
        }
        if(s2Btn) {
            s2Btn.className = 'step-cta done-btn';
            s2Btn.textContent = '✓ Listing Added';
            s2Btn.setAttribute('onclick', "showSection('new-listing', event)");
        }
    }

    // 3. Unlock step 3
    const s3 = document.getElementById('step3');
    const s3Btn = document.getElementById('step3Btn'); // FIXED: Defined the variable
    
    if (s3 && s3Btn) {
        s3.classList.remove('locked-step');
        s3.classList.add('active-step');
        const s3Status = document.getElementById('step3Status');
        
        if(s3Status) {
            s3Status.className = 'step-status next';
            s3Status.textContent = '→ Up Next';
        }
        
        s3Btn.className = 'step-cta green';
        s3Btn.textContent = 'Go live now →';
        s3Btn.setAttribute('onclick', "showSection('new-marketplace', event)");
    }
}

// 4. Trigger logic after redirect
document.addEventListener('DOMContentLoaded', () => {
    // We check a hidden element or a JS variable rendered by Flask
    const step2IsDone = document.body.dataset.step2Done === 'true'; 
    if (step2IsDone) {
        applyStep2CompletionUI();
    }
});

/* ══════════════ LOGOUT OVERLAY ══════════════ */
function openLogout() { document.getElementById('logoutOverlay').classList.add('open'); }
function closeLogout() { document.getElementById('logoutOverlay').classList.remove('open'); }

/* ══════════════ INITIALIZATION ══════════════ */
// This runs every time the page loads
function init() {
    // If Python told us Step 1 is done, unlock everything
    if (stepsComplete >= 1) {
        applyStep1CompletionUI();
    }
    updateProgress();
}

init();

/* ══════════════ REVEAL ANIMATIONS ══════════════ */
const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
        if (e.isIntersecting) { 
            e.target.style.opacity = '1'; 
            e.target.style.transform = 'translateY(0)'; 
        }
    });
}, { threshold: 0.08 });

document.querySelectorAll('.setup-step, .stat-card, .zero-panel').forEach((el, i) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = `opacity 0.5s ease ${i * 0.07}s, transform 0.5s cubic-bezier(0.22,1,0.36,1) ${i * 0.07}s`;
    obs.observe(el);
});