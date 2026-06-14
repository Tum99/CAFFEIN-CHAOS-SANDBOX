/* ═══════════════════════════════════════════════════════════════
   CAFFEIN & CHAOS — UNIFIED MARKETPLACE INTERACTIVE ENGINE
   ═══════════════════════════════════════════════════════════════ */

/* ══ CURSOR ANIMATION EFFECT ══ */
const cur = document.getElementById('cursor'), ring = document.getElementById('cursorRing');
let mx = 0, my = 0, rx = 0, ry = 0;

if (cur && ring) {
    document.addEventListener('mousemove', e => { 
        mx = e.clientX; 
        my = e.clientY; 
        cur.style.left = mx + 'px'; 
        cur.style.top = my + 'px'; 
    });

    (function loop() { 
        rx += (mx - rx) * 0.12; 
        ry += (my - ry) * 0.12; 
        ring.style.left = rx + 'px'; 
        ring.style.top = ry + 'px'; 
        requestAnimationFrame(loop); 
    })();
}

/* ══ BACK-TO-TOP BUTTON SCROLL ACTIVATION ══ */
window.addEventListener('scroll', () => {
    const scrollTopBtn = document.getElementById('scrollTop');
    if (scrollTopBtn) {
        scrollTopBtn.classList.toggle('visible', window.scrollY > 400);
    }
});

/* ══ DATA STATE ENGINE CORE ══ */
let listings = [];
let filtered = [];
let currentModal = null;

// Contextual fallback checks
let isLoggedIn = typeof window.USER_IS_AUTHENTICATED !== 'undefined' ? window.USER_IS_AUTHENTICATED : false;
let activeUserRole = typeof window.USER_ROLE !== 'undefined' ? window.USER_ROLE : 'guest';

/* ══ RENDER MARKETPLACE CARDS ══ */
function renderCards(data) {
    const grid = document.getElementById('listingsGrid');
    const emptyState = document.getElementById('emptyState');
    const resultsCount = document.getElementById('resultsCount');
    
    if (!grid) {
        console.error("Marketplace Error: Target element '#listingsGrid' was not discovered on the page layout.");
        return;
    }

    // Toggle empty state block cleanly
    if (emptyState) emptyState.style.display = data.length ? 'none' : 'block';
    if (resultsCount) resultsCount.textContent = data.length;

    if (data.length === 0) {
        grid.innerHTML = '';
        return;
    }

    grid.innerHTML = data.map(l => {
        // Evaluate user's business role context to draw targeted CTAs
        let actionButtonHtml = '';
        if (isLoggedIn && activeUserRole === 'buyer') {
            actionButtonHtml = `<button class="card-order-btn" onclick="event.stopPropagation(); openModal(${l.id})">Order Now</button>`;
        } else if (isLoggedIn && activeUserRole === 'seller') {
            actionButtonHtml = `<button class="card-order-btn" style="background:#2e2a24; border-color:#444;" onclick="event.stopPropagation(); openModal(${l.id})">Inspect Metrics</button>`;
        } else {
            actionButtonHtml = `<button class="card-order-btn" onclick="event.stopPropagation(); openModal(${l.id})">View Details</button>`;
        }

        return `
            <div class="listing-card" data-id="${l.id}"
                style="opacity:0; transform:translateY(18px); transition:opacity 0.45s ease, transform 0.45s cubic-bezier(0.22,1,0.36,1)">
                <div class="listing-card-img">
                    <div class="listing-card-img-ph">☕</div>
                    <div class="listing-img-overlay"></div>
                    <span class="card-varietal">${l.varietal || 'Premium'}</span>
                    <span class="card-process">${l.process || 'Washed'}</span>
                    <button class="card-quick-view" onclick="event.stopPropagation(); openModal(${l.id})">Quick View</button>
                </div>
                <div class="listing-card-body">
                    <div class="card-farm">🌿 ${l.farm_name}</div>
                    <div class="card-name">${l.name || (l.varietal + ' (' + l.process + ')')}</div>
                    <div class="card-specs">
                        <div><div class="card-spec-lbl">Roast</div><div class="card-spec-val">${l.roast_level}</div></div>
                        <div><div class="card-spec-lbl">County</div><div class="card-spec-val">${l.county}</div></div>
                        <div><div class="card-spec-lbl">Available</div><div class="card-spec-val">${l.quantity_kg} kg</div></div>
                        <div><div class="card-spec-lbl">Min. Order</div><div class="card-spec-val">${l.minimum_order_kg} kg</div></div>
                    </div>
                    <div class="card-notes">
                        ${l.tasting_notes ? l.tasting_notes.split(',').map(n => `<span class="card-note">${n.trim()}</span>`).join('') : '<span class="card-note">Premium Lot</span>'}
                    </div>
                    <div class="card-footer">
                        <div>
                            <div class="card-price">KES ${(l.price_per_kg || 0).toLocaleString()} <small>/kg</small></div>
                            <div class="card-stock">${l.quantity_kg} kg remaining</div>
                        </div>
                        ${actionButtonHtml}
                    </div>
                </div>
            </div>
        `;
    }).join('');

    /* Attach click interface triggers across the wrapper card background layout */
    grid.querySelectorAll('.listing-card').forEach(card => {
        card.addEventListener('click', () => {
            const id = parseInt(card.dataset.id);
            const targetItem = listings.find(item => item.id === id);
            if (targetItem) openModal(targetItem);
        });
    });

    /* Staggered visual reveal transition */
    grid.querySelectorAll('.listing-card').forEach((el, i) => {
        setTimeout(() => { 
            el.style.opacity = '1'; 
            el.style.transform = 'translateY(0)'; 
        }, i * 40);
    });
}

/* ══ SEARCH AND FILTER CRITERIA TRACKING ══ */
function filterListings() {
    const searchInput = document.getElementById('searchInput');
    const search = searchInput ? searchInput.value.toLowerCase() : '';
    
    const varietals = [...document.querySelectorAll('input[id^="v-"]:checked')].map(i => i.value);
    const processes = [...document.querySelectorAll('input[id^="p-"]:checked')].map(i => i.value);
    const roasts    = [...document.querySelectorAll('input[id^="r-"]:checked')].map(i => i.value);
    const counties  = [...document.querySelectorAll('input[id^="c-"]:checked')].map(i => i.value);
    
    const minPInput = document.getElementById('priceMin');
    const maxPInput = document.getElementById('priceMax');
    const minP = minPInput ? parseFloat(minPInput.value) || 0 : 0;
    const maxP = maxPInput ? parseFloat(maxPInput.value) || Infinity : Infinity;

    filtered = listings.filter(l => {
        if (search && 
            !(l.varietal || '').toLowerCase().includes(search) && 
            !(l.farm_name || '').toLowerCase().includes(search) && 
            !(l.county || '').toLowerCase().includes(search) && 
            !(l.name || '').toLowerCase().includes(search)) return false;
            
        if (varietals.length && !varietals.includes(l.varietal)) return false;
        if (processes.length && !processes.includes(l.process)) return false;
        if (roasts.length   && !roasts.includes(l.roast_level))  return false;
        if (counties.length && !counties.includes(l.county))    return false;
        if (l.price_per_kg < minP || l.price_per_kg > maxP)     return false;
        return true;
    });

    updateActivePills(varietals, processes, roasts, counties);
    sortListings();
}

function updateActivePills(v, p, r, c) {
    const container = document.getElementById('activeFilters');
    if (!container) return;
    container.innerHTML = [...v, ...p, ...r, ...c].map(f =>
        `<div class="active-filter-pill">${f} <span onclick="removeFilter('${f}')">✕</span></div>`
    ).join('');
}

function removeFilter(val) {
    document.querySelectorAll('input[type="checkbox"]').forEach(cb => { 
        if (cb.value === val) cb.checked = false; 
    });
    filterListings();
}

function resetFilters() {
    document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
    const searchInput = document.getElementById('searchInput');
    const minP = document.getElementById('priceMin');
    const maxP = document.getElementById('priceMax');
    const activeFilters = document.getElementById('activeFilters');
    
    if (searchInput) searchInput.value = '';
    if (minP) minP.value = '';
    if (maxP) maxP.value = '';
    if (activeFilters) activeFilters.innerHTML = '';
    
    filtered = [...listings];
    renderCards(filtered);
}

function sortListings() {
    const sortSelect = document.getElementById('sortSelect');
    const s = sortSelect ? sortSelect.value : 'newest';
    const sorted = [...filtered];
    
    if (s === 'price-asc')  sorted.sort((a, b) => a.price_per_kg - b.price_per_kg);
    if (s === 'price-desc') sorted.sort((a, b) => b.price_per_kg - a.price_per_kg);
    if (s === 'stock')      sorted.sort((a, b) => b.quantity_kg - a.quantity_kg);
    if (s === 'newest')     sorted.sort((a, b) => b.id - a.id);
    renderCards(sorted);
}

/* ══ CONTEXTUAL IN-VIEW OVERLAY MODAL MANAGER ══ */
function openModal(l) {
    if (!l) return;
    currentModal = l;

    const mFarm = document.getElementById('modalFarmName');
    const mTitle = document.getElementById('modalTitle');
    
    if (mFarm) mFarm.textContent = '🌿 ' + l.farm_name + ' — ' + l.county;
    if (mTitle) mTitle.innerHTML = `${l.varietal || 'Premium Coffee'} <em style="font-style: italic; color: var(--green)">${l.process || 'Washed'} Process</em>`;
    
    const setEl = (id, text) => { const el = document.getElementById(id); if(el) el.textContent = text; };
    setEl('mVarietal', l.varietal || 'Premium');
    setEl('mProcess', l.process || 'Washed');
    setEl('mRoast', (l.roast_level || 'Medium') + ' Roast');
    setEl('mHarvest', l.harvest_date || 'Recent Harvest');
    setEl('mStock', (l.quantity_kg || 0) + ' kg');
    setEl('mMin', (l.minimum_order_kg || 1) + ' kg');
    setEl('mLocation', l.county || 'Kenya');
    setEl('mAltitude', l.altitude || '1,750m');
    
    const mNotes = document.getElementById('mNotes');
    if (mNotes) {
        mNotes.innerHTML = l.tasting_notes ? 
            l.tasting_notes.split(',').map(n => `<span class="modal-note">${n.trim()}</span>`).join('') : '<span class="modal-note">Premium Origin</span>';
    }
    
    const qtyInput = document.getElementById('modalQty');
    if (qtyInput) {
        qtyInput.value = l.minimum_order_kg || 1;
        qtyInput.min   = l.minimum_order_kg || 1;
    }
    updateModalTotal();

    const orderBox = document.getElementById('modalOrderBox');
    const loginPrompt = document.getElementById('modalLoginPrompt');
    
    if (isLoggedIn) {
        if (activeUserRole === 'buyer') {
            if (orderBox) orderBox.style.display = 'block';
        } else {
            if (orderBox) orderBox.style.display = 'none';
        }
        if (loginPrompt) loginPrompt.style.display = 'none';
    } else {
        if (orderBox) orderBox.style.display = 'none';
        if (loginPrompt) loginPrompt.style.display = 'block';
    }

    const overlay = document.getElementById('modalOverlay');
    if (overlay) overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
}

function updateModalTotal() {
    if (!currentModal) return;
    const qtyInput = document.getElementById('modalQty');
    const totalEl = document.getElementById('modalTotal');
    if (!qtyInput || !totalEl) return;
    
    const qty = parseFloat(qtyInput.value) || 0;
    const total = qty * currentModal.price_per_kg;
    totalEl.textContent = 'KES ' + total.toLocaleString();
}

function closeModalBtn() {
    const overlay = document.getElementById('modalOverlay');
    if (overlay) overlay.classList.remove('open');
    document.body.style.overflow = '';
}

/* ══ INITIALIZATION MOUNT ENGINE ══ */
function startMarketplaceEngine() {
    console.log("== Marketplace Core Pipeline Initializing ==");
    
    // Snatch data structures safely from the window global scope
    const dataSource = window.DATABASE_PAYLOAD || window.listings || [];
    isLoggedIn = window.USER_IS_AUTHENTICATED || false;
    activeUserRole = window.USER_ROLE || 'guest';

    console.log("Target Context Payload Count:", dataSource.length);

    if (dataSource.length > 0) {
        listings = [...dataSource];
        filtered = [...listings];
        renderCards(listings);
    } else {
        console.warn("Marketplace Warning: Raw array loaded completely empty.");
        const emptyState = document.getElementById('emptyState');
        if (emptyState) emptyState.style.display = 'block';
    }
}

// Bulletproof execution trigger regardless of window load speeds
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startMarketplaceEngine);
} else {
    startMarketplaceEngine();
}