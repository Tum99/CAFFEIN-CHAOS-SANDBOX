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
                style="opacity:1; transform:translateY(18px); transition:opacity 0.45s ease, transform 0.45s cubic-bezier(0.22,1,0.36,1)">
                <div class="listing-card-img">
                    ${l.listing_image 
                        ? `<img src="/static/${l.listing_image}" alt="${l.name}" 
                            style="width:100%;height:100%;object-fit:cover;display:block;"
                            onerror="this.style.display='none'">`
                        : ''
                    }
                    <div class="listing-card-img-ph" style="${l.listing_image ? 'display:none' : ''}"></div>
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
    if (mTitle) mTitle.innerHTML = `${l.varietal || 'Premium Coffee'} <em style="font-style: italic; color: var(--crema)">${l.process || 'Washed'} Process</em>`;

    const imgPlaceholder = document.getElementById('modalImgPh');
    if (imgPlaceholder) {
        if (l.listing_image) {
            // Replicates the same clean card-rendering engine framework
            imgPlaceholder.innerHTML = `
                <img src="/static/${l.listing_image}" 
                     alt="${l.name || 'Listing Image'}" 
                     style="width:100%; height:100%; object-fit:cover; display:block;"
                     onerror="this.style.display='none'">
            `;
        } else {
            // Standard fallback icon if no image path exists in DB payload
            imgPlaceholder.innerHTML = `☕`; 
        }
    }
    
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

function closeModalOverlay(e) {
  if (e.target === document.getElementById('modalOverlay')) {
    closeModalBtn();
  }
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


function handleGrowerMessage() {
    if (!currentModal) return;
    // Redirect buyer directly to their messaging conversation route thread with the grower
    window.location.href = `/messaging/chat?with_user_id=${currentModal.seller_id || ''}`;
}

/* ═══════════════════════════════════════════════════════════════
   MARKETPLACE MPESA ADDITIONS
   Add these functions to the BOTTOM of your existing marketplace.js
   They replace handleOrderPlacement() and handleGrowerMessage()
═══════════════════════════════════════════════════════════════ */


/* ── HANDLE ORDER (replaces handleOrderPlacement) ── */
function handleOrder() {
  if (!currentModal) return;

  const qtyInput = document.getElementById('modalQty');
  const qty = parseFloat(qtyInput ? qtyInput.value : 0);

  if (!qty || qty < (currentModal.minimum_order_kg || 1)) {
    showToast(`Minimum order is ${currentModal.minimum_order_kg || 1} kg`, 'error');
    return;
  }

  if (qty > currentModal.quantity_kg) {
    showToast(`Only ${currentModal.quantity_kg} kg available`, 'error');
    return;
  }

  // Show phone confirmation modal before initiating payment
  showPhoneModal((phone) => {
    initiatePayment(currentModal, qty, phone);
  });
}


/* ── INITIATE PAYMENT ── */
function initiatePayment(listing, quantity, phone) {
  const orderBtn = document.querySelector('.modal-order-btn');
  if (orderBtn) {
    orderBtn.disabled = true;
    orderBtn.textContent = 'Sending M-Pesa request...';
  }

  fetch('/mpesa/initiate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken':  getCsrfToken()
    },
    body: JSON.stringify({
      listing_id: listing.id,
      quantity:   quantity,
      phone:      phone
    })
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      showToast('M-Pesa request sent! Check your phone and enter your PIN.', 'success');

      // Start polling for payment confirmation
      pollPaymentStatus(data.transaction_id, orderBtn);

    } else {
      showToast(data.error || 'Payment failed. Please try again.', 'error');
      if (orderBtn) {
        orderBtn.disabled = false;
        orderBtn.textContent = 'Pay via M-Pesa →';
      }
    }
  })
  .catch(err => {
    console.error('Payment error:', err);
    showToast('Network error. Please try again.', 'error');
    if (orderBtn) {
      orderBtn.disabled = false;
      orderBtn.textContent = 'Pay via M-Pesa →';
    }
  });
}


/* ── POLL PAYMENT STATUS ── */
// Checks every 5 seconds for up to 2 minutes
function pollPaymentStatus(transactionId, orderBtn) {
  let attempts = 0;
  const maxAttempts = 24; // 24 × 5s = 2 minutes

  const interval = setInterval(() => {
    attempts++;

    fetch(`/mpesa/status/${transactionId}`)
      .then(r => r.json())
      .then(data => {
        if (data.paid) {
          clearInterval(interval);
          showToast('Payment confirmed! Your order has been placed.', 'success');
          if (orderBtn) {
            orderBtn.textContent = '✓ Order Placed';
            orderBtn.style.background = '#7AB648';
          }
          // Refresh the listing quantity shown in modal
          if (currentModal) {
            currentModal.quantity_kg = Math.max(0, currentModal.quantity_kg - (parseFloat(document.getElementById('modalQty')?.value) || 0));
            document.getElementById('mStock').textContent = currentModal.quantity_kg + ' kg';
          }

        } else if (data.status === 'cancelled') {
          clearInterval(interval);
          showToast('Payment was cancelled. Please try again.', 'error');
          if (orderBtn) {
            orderBtn.disabled = false;
            orderBtn.textContent = 'Pay via M-Pesa →';
          }

        } else if (attempts >= maxAttempts) {
          clearInterval(interval);
          showToast('Payment is taking longer than expected. Check your M-Pesa messages.', 'warning');
          if (orderBtn) {
            orderBtn.disabled = false;
            orderBtn.textContent = 'Pay via M-Pesa →';
          }
        }
      })
      .catch(() => {
        if (attempts >= maxAttempts) {
          clearInterval(interval);
        }
      });

  }, 5000); // poll every 5 seconds
}


/* ── HANDLE MESSAGE (replaces handleGrowerMessage) ── */
function handleMessage() {
  if (!currentModal) return;

  // Remove any existing message modal
  const existing = document.getElementById('msgModal');
  if (existing) existing.remove();

  const listing = currentModal;
  const modal = document.createElement('div');
  modal.id = 'msgModal';
  modal.innerHTML = `
    <div style="
      position:fixed; inset:0; z-index:3000;
      background:rgba(6,4,2,0.92); backdrop-filter:blur(12px);
      display:flex; align-items:center; justify-content:center; padding:1.5rem;
    ">
      <div style="
        background:#1C0F08; border:1px solid rgba(200,135,58,0.2);
        padding:2rem; max-width:440px; width:100%;
      ">
        <div style="font-size:0.58rem;letter-spacing:0.22em;text-transform:uppercase;color:rgba(122,182,72,0.7);margin-bottom:0.5rem;">
          Message Grower
        </div>
        <div style="font-family:'Cormorant Garamond',serif;font-size:1.35rem;color:#FDFAF5;margin-bottom:0.3rem;">
          ${listing.farm_name}
        </div>
        <div style="font-size:0.75rem;color:rgba(245,236,215,0.35);margin-bottom:1.2rem;">
          ${listing.varietal} · ${listing.process} · ${listing.county}
        </div>
        <textarea
          id="msgModalInput"
          placeholder="Hi, I'm interested in your ${listing.varietal} lot. Is the ${listing.quantity_kg}kg still available?..."
          style="
            width:100%; height:120px; padding:0.8rem 1rem; margin-bottom:1rem;
            background:rgba(200,135,58,0.05); border:1px solid rgba(200,135,58,0.12);
            color:#F5ECD7; font-family:'Jost',sans-serif; font-size:0.82rem;
            outline:none; resize:vertical; line-height:1.6;
          "
        ></textarea>
        <div id="msgModalError" style="color:#E06C75;font-size:0.75rem;margin-bottom:0.8rem;display:none;"></div>
        <div style="display:flex;gap:0.8rem;">
          <button onclick="document.getElementById('msgModal').remove()" style="
            flex:1; padding:0.75rem; background:transparent;
            border:1px solid rgba(200,135,58,0.2); color:rgba(245,236,215,0.5);
            font-family:'Jost',sans-serif; font-size:0.7rem;
            letter-spacing:0.14em; text-transform:uppercase; cursor:pointer;
          ">Cancel</button>
          <button id="msgModalSend" style="
            flex:2; padding:0.75rem; background:#7AB648; color:#0A0604;
            border:none; font-family:'Jost',sans-serif; font-size:0.7rem;
            letter-spacing:0.14em; text-transform:uppercase; font-weight:600;
            cursor:pointer;
          ">Send Message →</button>
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(modal);
  document.getElementById('msgModalInput').focus();

  document.getElementById('msgModalSend').addEventListener('click', () => {
    const body    = document.getElementById('msgModalInput').value.trim();
    const errorEl = document.getElementById('msgModalError');
    const sendBtn = document.getElementById('msgModalSend');

    if (!body) {
      errorEl.textContent = 'Please write a message before sending.';
      errorEl.style.display = 'block';
      return;
    }

    sendBtn.disabled = true;
    sendBtn.textContent = 'Sending...';

    fetch('/mpesa/message-grower', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken':  getCsrfToken()
      },
      body: JSON.stringify({
        seller_id:  listing.grower_id,
        listing_id: listing.id,
        body:       body
      })
    })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        document.getElementById('msgModal').remove();
        showToast('Message sent to grower! Check your inbox for their reply.', 'success');
      } else {
        errorEl.textContent = data.error || 'Failed to send message.';
        errorEl.style.display = 'block';
        sendBtn.disabled = false;
        sendBtn.textContent = 'Send Message →';
      }
    })
    .catch(() => {
      errorEl.textContent = 'Network error. Please try again.';
      errorEl.style.display = 'block';
      sendBtn.disabled = false;
      sendBtn.textContent = 'Send Message →';
    });
  });
}


/* ── TOAST NOTIFICATIONS ── */
function showToast(message, type = 'info') {
  const existing = document.getElementById('mpesaToast');
  if (existing) existing.remove();

  const colors = {
    success: { bg: 'rgba(122,182,72,0.15)',  border: '#7AB648', color: '#7AB648' },
    error:   { bg: 'rgba(224,108,117,0.15)', border: '#E06C75', color: '#E06C75' },
    warning: { bg: 'rgba(200,135,58,0.15)',  border: '#C8873A', color: '#C8873A' },
    info:    { bg: 'rgba(74,158,255,0.15)',  border: '#4A9EFF', color: '#4A9EFF' }
  };
  const c = colors[type] || colors.info;

  const toast = document.createElement('div');
  toast.id = 'mpesaToast';
  toast.style.cssText = `
    position:fixed; bottom:2rem; left:50%; transform:translateX(-50%);
    z-index:4000; padding:1rem 1.5rem;
    background:${c.bg}; border:1px solid ${c.border}; border-left:3px solid ${c.border};
    color:${c.color}; font-family:'Jost',sans-serif; font-size:0.82rem;
    max-width:420px; width:calc(100% - 2rem); text-align:center;
    animation: toastIn 0.35s cubic-bezier(0.22,1,0.36,1) both;
  `;
  toast.textContent = message;

  // Add animation keyframes if not already added
  if (!document.getElementById('toastStyle')) {
    const style = document.createElement('style');
    style.id = 'toastStyle';
    style.textContent = `
      @keyframes toastIn {
        from { opacity:0; transform:translateX(-50%) translateY(10px); }
        to   { opacity:1; transform:translateX(-50%) translateY(0); }
      }
    `;
    document.head.appendChild(style);
  }

  document.body.appendChild(toast);
  setTimeout(() => { if (toast.parentNode) toast.remove(); }, 5000);
}


/* ── CSRF TOKEN HELPER ── */
function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  if (meta) return meta.getAttribute('content');
  const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrf_token='));
  return cookie ? cookie.split('=')[1].trim() : '';
}