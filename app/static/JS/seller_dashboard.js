const cur=document.getElementById('cursor'),ring=document.getElementById('cursorRing');
  let mx=0,my=0,rx=0,ry=0;
  document.addEventListener('mousemove',e=>{mx=e.clientX;my=e.clientY;cur.style.left=mx+'px';cur.style.top=my+'px';});
  (function loop(){rx+=(mx-rx)*0.12;ry+=(my-ry)*0.12;ring.style.left=rx+'px';ring.style.top=ry+'px';requestAnimationFrame(loop);})();
 
  function showSection(name, event) {
    document.querySelectorAll('.content-section').forEach(s=>s.classList.remove('active'));
    document.querySelectorAll('.sidebar-link').forEach(l=>l.classList.remove('active'));
    document.getElementById(`sec-${name}`).classList.add('active');
    if(event && event.currentTarget && event.currentTarget.classList) {
      event.currentTarget.classList.add('active');
      event.preventDefault();
    }
  }

function confirmProfileUpdate(event) {
    // Open the confirmation dialog popup box
    const userConfirmed = confirm("Are you sure you want to update your personal account information?");
    
    if (!userConfirmed) {
        // If the user clicks 'Cancel', stop the form from submitting!
        event.preventDefault();
        return false;
    }
    
    // If they clicked 'OK', the browser continues with the standard form POST request
    return true;
}

function confirmPayoutUpdate(event) {
    const userConfirmed = confirm("Are you sure you want to update your financial payout preferences?");
    if (!userConfirmed) {
        event.preventDefault();
        return false;
    }
    return true;
}

function confirmPasswordUpdate(event) {
    const newPass = document.getElementById("new_password").value;
    const confirmPass = document.getElementById("confirm_password").value;

    if (newPass.length < 8) {
        alert("Security Error: Your new password must be at least 8 characters long.");
        event.preventDefault();
        return false;
    }

    if (newPass !== confirmPass) {
        alert("Input Error: Your new password and confirmation password fields do not match.");
        event.preventDefault();
        return false;
    }

    const userConfirmed = confirm("Are you absolutely sure you want to change your security login password? You will need to use your new password next time you log in.");
    if (!userConfirmed) {
        event.preventDefault();
        return false;
    }
    return true;
}

function confirmNotificationUpdate(event) {
    const userConfirmed = confirm("Save changes to your notification dispatch configurations?");
    if (!userConfirmed) {
        event.preventDefault();
        return false;
    }
    return true;
}

function loadThread(threadId, name, initial) {
// Mark thread as active
document.querySelectorAll('.thread-item').forEach(el => {
    el.classList.toggle('active-thread', parseInt(el.dataset.threadId) === threadId);
});

// Show chat inner, hide empty state
document.getElementById('chatEmpty').style.display  = 'none';
document.getElementById('chatInner').style.display  = 'flex';

// Update header
document.getElementById('chatHeadAvatar').textContent = initial;
document.getElementById('chatHeadName').textContent   = name;

// Load messages
const container = document.getElementById('chatMessagesContainer');
container.innerHTML = '<div style="padding:1rem;font-size:0.75rem;color:rgba(245,236,215,0.3);">Loading...</div>';

fetch(`/api/messages/${threadId}`)
    .then(r => r.json())
    .then(data => {
        if (!data.messages.length) {
            container.innerHTML = '<div style="padding:1.5rem;font-size:0.78rem;color:rgba(245,236,215,0.25);text-align:center;">No messages yet.</div>';
            return;
        }
        container.innerHTML = data.messages.map(m => `
            <div class="msg ${m.is_mine ? 'sent' : 'received'}">
                <div class="msg-bubble">${escapeHtml(m.body)}</div>
                <div class="msg-time">${m.time}</div>
            </div>
        `).join('');
        container.scrollTop = container.scrollHeight;
    })
    .catch(() => {
        container.innerHTML = '<div style="color:#E06C75;padding:1rem;font-size:0.8rem;">Failed to load messages.</div>';
    });
}

// Auto-load first thread if any exist
document.addEventListener('DOMContentLoaded', () => {
const first = document.querySelector('.thread-item');
if (first) first.click();
});

// Send button
document.getElementById('chatSendButton')?.addEventListener('click', sendReply);
document.getElementById('chatInputField')?.addEventListener('keydown', e => {
if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendReply(); }
});

function sendReply() {
const input     = document.getElementById('chatInputField');
const activeThread = document.querySelector('.thread-item.active-thread');
if (!input || !activeThread) return;

const body     = input.value.trim();
const threadId = parseInt(activeThread.dataset.threadId);
if (!body || !threadId) return;

fetch(`/api/messages/${threadId}/send`, {
    method:  'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken':  document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
    },
    body: JSON.stringify({ body })
})
.then(r => r.json())
.then(data => {
    if (data.status === 'success') {
        input.value = '';
        const container = document.getElementById('chatMessagesContainer');
        const msgEl = document.createElement('div');
        msgEl.className = 'msg sent';
        msgEl.innerHTML = `
            <div class="msg-bubble">${escapeHtml(data.message.body)}</div>
            <div class="msg-time">${data.message.time}</div>
        `;
        container.appendChild(msgEl);
        container.scrollTop = container.scrollHeight;
    }
})
.catch(() => alert('Failed to send. Please try again.'));
}

function escapeHtml(str) {
return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}


/* ── EDIT LISTING MODAL ── */
function openEditModal(listingId, name, price, stock, minOrder, description, varietal, process, roast, harvestDate, tastingNotes) {
    document.getElementById('editListingForm').action = `/seller/edit-listing/${listingId}`;
    document.getElementById('editName').value        = name        || '';
    document.getElementById('editPrice').value       = price       || '';
    document.getElementById('editStock').value       = stock       || '';
    document.getElementById('editMinOrder').value    = minOrder    || 1;
    document.getElementById('editDescription').value = description || '';
    document.getElementById('editNotes').value       = tastingNotes || '';
    document.getElementById('editHarvestDate').value = harvestDate  || '';
    setSelect('editVarietal', varietal);
    setSelect('editProcess',  process);
    setSelect('editRoast',    roast);
    document.getElementById('editModalOverlay').classList.add('open');
    document.body.style.overflow = 'hidden';
}
function setSelect(id, value) {
    const s = document.getElementById(id);
    if (!s || !value) return;
    for (let o of s.options) { if (o.value === value) { o.selected = true; break; } }
}
function closeEditModal(e) { if (e.target === document.getElementById('editModalOverlay')) closeEditModalBtn(); }
function closeEditModalBtn() { document.getElementById('editModalOverlay').classList.remove('open'); document.body.style.overflow = ''; }
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeEditModalBtn(); });

/* ── FILTER ORDERS BY LISTING ── */
function filterOrdersByListing(listingId) {
    const rows    = document.querySelectorAll('#ordersTable tbody tr');
    const bar     = document.getElementById('ordersFilterBar');
    let   visible = 0;

    rows.forEach(row => {
        const match = row.dataset.listingId == listingId;
        row.style.display = match ? '' : 'none';
        if (match) visible++;
    });

    if (bar) { bar.style.display = 'flex'; }
    const count = document.getElementById('ordersShownCount');
    if (count) count.textContent = visible;
}

function clearOrdersFilter() {
    document.querySelectorAll('#ordersTable tbody tr').forEach(r => r.style.display = '');
    const bar = document.getElementById('ordersFilterBar');
    if (bar) bar.style.display = 'none';
    const count = document.getElementById('ordersShownCount');
    if (count) count.textContent = document.querySelectorAll('#ordersTable tbody tr').length;
}


function previewPhoto(input) {
  if (!input.files || !input.files[0]) return;
  const reader = new FileReader();
  reader.onload = e => {
    let img = document.getElementById('photoPreviewImg');
    const preview = img ? img.parentElement : document.querySelector('.profile-photo-preview');
    if (!img) {
      img = document.createElement('img');
      img.id = 'photoPreviewImg';
      img.style.cssText = 'width:100%;height:100%;object-fit:cover;border-radius:50%;';
      preview.innerHTML = '';
      preview.appendChild(img);
    }
    img.src = e.target.result;
  };
  reader.readAsDataURL(input.files[0]);
}


/* ── ROUTING ANCHOR HANDLING ── */
document.addEventListener("DOMContentLoaded", () => {
    // Check if the landing path configuration has a hash layout key (e.g., #sec-listings)
    const hash = window.location.hash;
    
    if (hash) {
        // Strip out the framework's DOM ID prefix string
        const sectionName = hash.replace('#sec-', '').replace('#', '');
        
        // Find if an associated sidebar navigation node control element exists
        // (This lets us pass the current element target context safely)
        const matchedSidebarLink = Array.from(document.querySelectorAll('.sidebar-link'))
            .find(link => {
                const clickAttr = link.getAttribute('onclick');
                return clickAttr && clickAttr.includes(`'${sectionName}'`);
            });

        // Instantiate a synthetic mock interface container object if needed
        const artificialEvent = matchedSidebarLink ? {
            currentTarget: matchedSidebarLink,
            preventDefault: () => {}
        } : null;

        // Try using the main toggle handler system safely
        try {
            // Wait slightly for DOM attributes to render completely before running
            setTimeout(() => {
                // Fetch the actual target structure item to ensure it exists on the layout
                const targetEl = document.getElementById(`sec-${sectionName}`);
                if (targetEl) {
                    showSection(sectionName, artificialEvent);
                }
            }, 50);
        } catch (error) {
            console.warn("Routing layout transition failed:", error);
        }
    }
});

/* ── DYNAMIC ORDERS FETCHING ── */
function fetchDynamicOrders() {
    const url = typeof ORDERS_API_URL !== 'undefined' ? ORDERS_API_URL : '/seller/api/orders';

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server returned ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                renderOrdersData(data.orders);
                updateOrderBadges(data.total_orders, data.pending_orders);
            }
        })
        .catch(err => console.error('Error fetching dynamic orders:', err));
}

function renderOrdersData(orders) {
    const recentBody = document.getElementById('recentOrdersBody');
    const allBody = document.getElementById('ordersTableBody');
    const recentTable = document.getElementById('recentOrdersTable');
    const recentEmpty = document.getElementById('recentOrdersEmpty');
    const allTable = document.getElementById('ordersTable');
    const allEmpty = document.getElementById('allOrdersEmpty');

    if (!orders || orders.length === 0) {
        if (recentTable) recentTable.style.display = 'none';
        if (recentEmpty) recentEmpty.style.display = 'block';
        if (allTable) allTable.style.display = 'none';
        if (allEmpty) allEmpty.style.display = 'block';
        return;
    }

    if (recentTable) recentTable.style.display = 'table';
    if (recentEmpty) recentEmpty.style.display = 'none';
    if (allTable) allTable.style.display = 'table';
    if (allEmpty) allEmpty.style.display = 'none';

    // Render Recent Orders (Top 5)
    if (recentBody) {
        recentBody.innerHTML = orders.slice(0, 5).map(o => `
            <tr>
                <td>${escapeHtml(o.order_code)}</td>
                <td>${escapeHtml(o.buyer_name)}</td>
                <td>${escapeHtml(o.coffee_lot)}</td>
                <td>${o.quantity_kg} kg</td>
                <td>KES ${escapeHtml(o.total_amount)}</td>
                <td>
                    <span class="order-status status-${o.status.toLowerCase()}">
                        ${o.status.charAt(0).toUpperCase() + o.status.slice(1)}
                    </span>
                </td>
            </tr>
        `).join('');
    }

    // Render Full Orders Table
    if (allBody) {
        allBody.innerHTML = orders.map(o => `
            <tr data-listing-id="${o.listing_id}">
                <td>${escapeHtml(o.order_code)}</td>
                <td>${escapeHtml(o.buyer_name)}</td>
                <td>${escapeHtml(o.coffee_lot)}</td>
                <td>${o.quantity_kg} kg</td>
                <td>${escapeHtml(o.total_amount)}</td>
                <td style="font-family:monospace;font-size:0.78rem;">${escapeHtml(o.mpesa_ref)}</td>
                <td>
                    <span class="order-status status-${o.status.toLowerCase()}">
                        ${o.status.charAt(0).toUpperCase() + o.status.slice(1)}
                    </span>
                </td>
            </tr>
        `).join('');
    }

    const count = document.getElementById('ordersShownCount');
    if (count) count.textContent = orders.length;
}

function updateOrderBadges(totalOrders, pendingOrders) {
    const badges = document.querySelectorAll('a[onclick*="orders"] .sidebar-badge');
    badges.forEach(sidebarBadge => {
        sidebarBadge.textContent = totalOrders;
        sidebarBadge.style.display = totalOrders > 0 ? 'inline-block' : 'none';
    });
}

function filterOrdersByListing(listingId) {
    const rows = document.querySelectorAll('#ordersTableBody tr');
    const bar = document.getElementById('ordersFilterBar');
    let visible = 0;

    rows.forEach(row => {
        const match = row.dataset.listingId == listingId;
        row.style.display = match ? '' : 'none';
        if (match) visible++;
    });

    if (bar) bar.style.display = 'flex';
    const count = document.getElementById('ordersShownCount');
    if (count) count.textContent = visible;
}

function clearOrdersFilter() {
    const rows = document.querySelectorAll('#ordersTableBody tr');
    rows.forEach(r => r.style.display = '');
    const bar = document.getElementById('ordersFilterBar');
    if (bar) bar.style.display = 'none';
    const count = document.getElementById('ordersShownCount');
    if (count) count.textContent = rows.length;
}

// Polling interval
document.addEventListener('DOMContentLoaded', () => {
    fetchDynamicOrders();
    setInterval(fetchDynamicOrders, 15000);
});

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