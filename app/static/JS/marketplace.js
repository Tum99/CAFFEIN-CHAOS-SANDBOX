/* ═══════════════════════════════════════════════════════════════
   CAFFEIN & CHAOS — UNIFIED MARKETPLACE INTERACTIVE ENGINE
   ═══════════════════════════════════════════════════════════════ */

/* ══ CURSOR ANIMATION EFFECT ══ */
const cur = document.getElementById('cursor'), ring = document.getElementById('cursorRing');
let mx = 0, my = 0, rx = 0, ry = 0;

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

/* ══ BACK-TO-TOP BUTTON SCROLL ACTIVATION ══ */
window.addEventListener('scroll', () => {
    document.getElementById('scrollTop').classList.toggle('visible', window.scrollY > 400);
});

/* ══ CONTEXTUAL STATE FROM JINJA INJECTION ══ */
const isLoggedIn = typeof USER_IS_AUTHENTICATED !== 'undefined' ? USER_IS_AUTHENTICATED : false;
const activeUserRole = typeof USER_ROLE !== 'undefined' ? USER_ROLE : 'guest'; 

/* ══ DATA COLLECTION HOOKS ══ */
let listings = [];
let filtered = [];
let currentModal = null;

/* ══ RENDER MARKETPLACE CARDS ══ */
function renderCards(data) {
    const grid = document.getElementById('listingsGrid');
    document.getElementById('emptyState').style.display = data.length ? 'none' : 'block';
    document.getElementById('resultsCount').textContent = data.length;

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
                    <span class="card-varietal">${l.varietal}</span>
                    <span class="card-process">${l.process}</span>
                    ${l.is_verified ? '<span class="card-verified">✓ Verified</span>' : ''}
                    <button class="card-quick-view" onclick="event.stopPropagation(); openModal(${l.id})">Quick View</button>
                </div>
                <div class="listing-card-body">
                    <div class="card-farm">🌿 ${l.farm_name}</div>
                    <div class="card-name">${l.varietal} (${l.process})</div>
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
                            <div class="card-price">KES ${l.price_per_kg.toLocaleString()} <small>/kg</small></div>
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
            openModal(listings.find(l => l.id === id));
        });
    });

    /* Staggered visual reveal transition */
    grid.querySelectorAll('.listing-card').forEach((el, i) => {
        setTimeout(() => { 
            el.style.opacity = '1'; 
            el.style.transform = 'translateY(0)'; 
        }, i * 60);
    });
}

/* ══ SEARCH AND FILTER CRITERIA TRACKING ══ */
function filterListings() {
    const search = document.getElementById('searchInput').value.toLowerCase();
    const varietals = [...document.querySelectorAll('input[id^="v-"]:checked')].map(i => i.value);
    const processes = [...document.querySelectorAll('input[id^="p-"]:checked')].map(i => i.value);
    const roasts    = [...document.querySelectorAll('input[id^="r-"]:checked')].map(i => i.value);
    const counties  = [...document.querySelectorAll('input[id^="c-"]:checked')].map(i => i.value);
    const minP = parseFloat(document.getElementById('priceMin').value) || 0;
    const maxP = parseFloat(document.getElementById('priceMax').value) || Infinity;

    filtered = listings.filter(l => {
        if (search && !l.varietal.toLowerCase().includes(search) && !l.farm_name.toLowerCase().includes(search) && !l.county.toLowerCase().includes(search)) return false;
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

function clearFilter(type) {
    const prefix = type === 'varietal' ? 'v-' : type === 'process' ? 'p-' : type === 'roast' ? 'r-' : 'c-';
    document.querySelectorAll(`input[id^="${prefix}"]`).forEach(cb => cb.checked = false);
    filterListings();
}

function resetFilters() {
    document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
    document.getElementById('searchInput').value = '';
    document.getElementById('priceMin').value = '';
    document.getElementById('priceMax').value = '';
    document.getElementById('activeFilters').innerHTML = '';
    filtered = [...listings];
    renderCards(filtered);
}

/* ══ SORTING RUNTIME LOGIC ══ */
function sortListings() {
    const s = document.getElementById('sortSelect').value;
    const sorted = [...filtered];
    if (s === 'price-asc')  sorted.sort((a, b) => a.price_per_kg - b.price_per_kg);
    if (s === 'price-desc') sorted.sort((a, b) => b.price_per_kg - a.price_per_kg);
    if (s === 'stock')      sorted.sort((a, b) => b.quantity_kg - a.quantity_kg);
    if (s === 'newest')     sorted.sort((a, b) => b.id - a.id);
    renderCards(sorted);
}

/* ══ GRID VS LIST STRUCTURAL VIEW TOGGLE ══ */
function setView(v) {
    const grid = document.getElementById('listingsGrid');
    document.getElementById('gridViewBtn').classList.toggle('active', v === 'grid');
    document.getElementById('listViewBtn').classList.toggle('active', v === 'list');
    grid.classList.toggle('list-view', v === 'list');
}

/* ══ CONTEXTUAL IN-VIEW OVERLAY MODAL MANAGER ══ */
function openModal(l) {
    if (!l) return;
    currentModal = l;

    // Fill details using matching database model schema references
    document.getElementById('modalFarmName').textContent = '🌿 ' + l.farm_name + ' — ' + l.county;
    document.getElementById('modalTitle').innerHTML = `${l.varietal} <em style="font-style: italic; color: var(--green)">${l.process} Process</em>`;
    document.getElementById('mVarietal').textContent = l.varietal;
    document.getElementById('mProcess').textContent  = l.process;
    document.getElementById('mRoast').textContent    = l.roast_level + ' Roast';
    document.getElementById('mHarvest').textContent  = l.harvest_date || 'Current Batch';
    document.getElementById('mStock').textContent    = l.quantity_kg + ' kg';
    document.getElementById('mMin').textContent      = l.minimum_order_kg + ' kg';
    document.getElementById('mLocation').textContent = l.county;
    document.getElementById('mAltitude').textContent = l.altitude_masl + ' masl';
    
    document.getElementById('mNotes').innerHTML = l.tasting_notes ? 
        l.tasting_notes.split(',').map(n => `<span class="modal-note">${n.trim()}</span>`).join('') : '<span class="modal-note">Premium Origin</span>';
    
    document.getElementById('modalQty').value = l.minimum_order_kg;
    document.getElementById('modalQty').min   = l.minimum_order_kg;
    updateModalTotal();

    // Toggle contextual UI card wrappers inside single HTML layout context
    const orderBox = document.getElementById('modalOrderBox');
    const loginPrompt = document.getElementById('modalLoginPrompt');
    
    if (isLoggedIn) {
        if (activeUserRole === 'buyer') {
            if (orderBox) orderBox.style.display = 'block';
        } else {
            // Logged in as Grower/Seller: Hide purchase modules entirely
            if (orderBox) orderBox.style.display = 'none';
        }
        if (loginPrompt) loginPrompt.style.display = 'none';
    } else {
        if (orderBox) orderBox.style.display = 'none';
        if (loginPrompt) loginPrompt.style.display = 'block';
    }

    document.getElementById('modalOverlay').classList.add('open');
    document.body.style.overflow = 'hidden';
}

function updateModalTotal() {
    if (!currentModal) return;
    const qty = parseFloat(document.getElementById('modalQty').value) || 0;
    const total = qty * currentModal.price_per_kg;
    document.getElementById('modalTotal').textContent = 'KES ' + total.toLocaleString();
}

function closeModal(e) {
    if (e.target === document.getElementById('modalOverlay')) closeModalBtn();
}

function closeModalBtn() {
    document.getElementById('modalOverlay').classList.remove('open');
    document.body.style.overflow = '';
}

document.addEventListener('keydown', e => { 
    if (e.key === 'Escape') closeModalBtn(); 
});

/* ══ TRANSACTION HANDLERS ══ */
function handleOrder() {
    if (!isLoggedIn) return;
    const qty = document.getElementById('modalQty').value;
    alert(`In Flask Ecosystem:\nPOST /marketplace/order\n{\n  listing_id: ${currentModal.id},\n  quantity_kg: ${qty}\n}\n\nInitiating secure M-Pesa STK Push sequence...`);
}

function handleMessage() {
    if (!isLoggedIn) return;
    alert(`Redirecting to buyer context thread manager...\nOpening message pipeline channel directly with: ${currentModal.farm_name}`);
}

/* ══ INITIALIZATION MOUNT ══ */
if (typeof DATABASE_PAYLOAD !== 'undefined') {
    listings = DATABASE_PAYLOAD;
    filtered = [...listings];
    renderCards(listings);
}