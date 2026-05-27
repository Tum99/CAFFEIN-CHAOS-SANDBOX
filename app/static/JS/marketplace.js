/* cursor */
const cur=document.getElementById('cursor'),ring=document.getElementById('cursorRing');
let mx=0,my=0,rx=0,ry=0;
document.addEventListener('mousemove',e=>{mx=e.clientX;my=e.clientY;cur.style.left=mx+'px';cur.style.top=my+'px';});
(function loop(){rx+=(mx-rx)*0.12;ry+=(my-ry)*0.12;ring.style.left=rx+'px';ring.style.top=ry+'px';requestAnimationFrame(loop);})();

/* scroll top */
window.addEventListener('scroll',()=>document.getElementById('scrollTop').classList.toggle('visible',window.scrollY>400));

/* ══ AUTH STATE (demo toggle) ══ */
let isLoggedIn = true;
function toggleAuth() {
isLoggedIn = !isLoggedIn;
document.getElementById('navUser').style.display = isLoggedIn ? 'flex' : 'none';
document.querySelector('.btn-dashboard').style.display = isLoggedIn ? '' : 'none';
document.querySelector('.btn-ghost').textContent = isLoggedIn ? 'Logout (demo)' : 'Login';
if (!isLoggedIn) {
    // swap logout for login/signup buttons
    document.querySelector('.btn-ghost').textContent = 'Login (demo)';
}
// update modal state if open
toggleModalAuth();
}

function toggleModalAuth() {
document.getElementById('modalOrderBox').style.display   = isLoggedIn ? 'block' : 'none';
document.getElementById('modalLoginPrompt').style.display= isLoggedIn ? 'none'  : 'block';
}

/* ══ LISTINGS DATA ══ */
const listings = [
{ id:1, farm:'Jepng\'etich Farm', county:'Uasingishu', altitude:'1,850m', verified:true, name:'Arabica Batian — 1kg', varietal:'Batian', process:'Washed', roast:'Medium', harvest:'Oct 2025', stock:100, minOrder:1, price:2800, notes:['Citrus','Molasses','Dark Berry'] },
{ id:2, farm:'Kirinyaga Estate', county:'Kirinyaga', altitude:'1,700m', verified:true, name:'SL28 Natural Process', varietal:'SL28', process:'Natural', roast:'Light', harvest:'Nov 2025', stock:20, minOrder:0.5, price:3800, notes:['Blueberry','Wine','Honey','Tropical'] },
{ id:3, farm:'Nyeri Highlands Co-op', county:'Nyeri', altitude:'1,900m', verified:true, name:'Ruiru 11 Dark Roast', varietal:'Ruiru 11', process:'Washed', roast:'Dark', harvest:'Sep 2025', stock:30, minOrder:1, price:2500, notes:['Dark Chocolate','Roasted Nuts','Brown Sugar'] },
{ id:4, farm:'Murang\'a Valley Farm', county:'Murang\'a', altitude:'1,600m', verified:false, name:'SL34 Honey Process', varietal:'SL34', process:'Honey', roast:'Medium', harvest:'Dec 2025', stock:15, minOrder:1, price:3200, notes:['Stone Fruit','Caramel','Vanilla'] },
{ id:5, farm:'Meru Highlands', county:'Meru', altitude:'1,750m', verified:true, name:'K7 Washed Light Roast', varietal:'K7', process:'Washed', roast:'Light', harvest:'Oct 2025', stock:40, minOrder:1, price:2900, notes:['Bergamot','Lemon','Floral'] },
{ id:6, farm:'Jepng\'etich Farm', county:'Uasingishu', altitude:'1,850m', verified:true, name:'Arabica Batian — 250g', varietal:'Batian', process:'Washed', roast:'Medium', harvest:'Oct 2025', stock:50, minOrder:0.25, price:3400, notes:['Citrus','Molasses'] },
{ id:7, farm:'Kirinyaga Estate', county:'Kirinyaga', altitude:'1,700m', verified:true, name:'SL28 Washed AA', varietal:'SL28', process:'Washed', roast:'Medium', harvest:'Nov 2025', stock:60, minOrder:1, price:3100, notes:['Red Apple','Jasmine','Peach'] },
{ id:8, farm:'Nandi Hills Farm', county:'Nandi', altitude:'2,000m', verified:false, name:'Batian Natural', varietal:'Batian', process:'Natural', roast:'Light', harvest:'Jan 2026', stock:25, minOrder:1, price:3600, notes:['Strawberry','Passion Fruit','Brown Sugar'] },
];

let filtered = [...listings];
let currentModal = null;

/* ══ RENDER CARDS ══ */
function renderCards(data) {
const grid = document.getElementById('listingsGrid');
document.getElementById('emptyState').style.display = data.length ? 'none' : 'block';
document.getElementById('resultsCount').textContent = data.length;

grid.innerHTML = data.map(l => `
    <div class="listing-card" data-id="${l.id}"
        style="opacity:0;transform:translateY(18px);transition:opacity 0.45s ease,transform 0.45s cubic-bezier(0.22,1,0.36,1)">
    <div class="listing-card-img">
        <div class="listing-card-img-ph">☕</div>
        <div class="listing-img-overlay"></div>
        <span class="card-varietal">${l.varietal}</span>
        <span class="card-process">${l.process}</span>
        ${l.verified ? '<span class="card-verified">✓ Verified</span>' : ''}
        <button class="card-quick-view" onclick="event.stopPropagation();openModal(listings.find(x=>x.id===${l.id}))">Quick View</button>
    </div>
    <div class="listing-card-body">
        <div class="card-farm">🌿 ${l.farm}</div>
        <div class="card-name">${l.name}</div>
        <div class="card-specs">
        <div><div class="card-spec-lbl">Roast</div><div class="card-spec-val">${l.roast}</div></div>
        <div><div class="card-spec-lbl">County</div><div class="card-spec-val">${l.county}</div></div>
        <div><div class="card-spec-lbl">Available</div><div class="card-spec-val">${l.stock} kg</div></div>
        <div><div class="card-spec-lbl">Min. Order</div><div class="card-spec-val">${l.minOrder} kg</div></div>
        </div>
        <div class="card-notes">${l.notes.map(n=>`<span class="card-note">${n}</span>`).join('')}</div>
        <div class="card-footer">
        <div>
            <div class="card-price">KES ${l.price.toLocaleString()} <small>/kg</small></div>
            <div class="card-stock">${l.stock} kg remaining</div>
        </div>
        <button class="card-order-btn" onclick="event.stopPropagation();openModal(listings.find(x=>x.id===${l.id}))">Order Now</button>
        </div>
    </div>
    </div>
`).join('');

/* attach click to whole card */
grid.querySelectorAll('.listing-card').forEach(card => {
    card.addEventListener('click', () => {
    const id = parseInt(card.dataset.id);
    openModal(listings.find(l => l.id === id));
    });
});

/* staggered reveal */
grid.querySelectorAll('.listing-card').forEach((el,i) => {
    setTimeout(() => { el.style.opacity='1'; el.style.transform='translateY(0)'; }, i * 60);
});
}

/* ══ FILTERS ══ */
function filterListings() {
const search = document.getElementById('searchInput').value.toLowerCase();
const varietals = [...document.querySelectorAll('input[id^="v-"]:checked')].map(i=>i.value);
const processes = [...document.querySelectorAll('input[id^="p-"]:checked')].map(i=>i.value);
const roasts    = [...document.querySelectorAll('input[id^="r-"]:checked')].map(i=>i.value);
const counties  = [...document.querySelectorAll('input[id^="c-"]:checked')].map(i=>i.value);
const minP = parseFloat(document.getElementById('priceMin').value) || 0;
const maxP = parseFloat(document.getElementById('priceMax').value) || Infinity;

filtered = listings.filter(l => {
    if (search && !l.name.toLowerCase().includes(search) && !l.farm.toLowerCase().includes(search) && !l.varietal.toLowerCase().includes(search)) return false;
    if (varietals.length && !varietals.includes(l.varietal)) return false;
    if (processes.length && !processes.includes(l.process)) return false;
    if (roasts.length   && !roasts.includes(l.roast))       return false;
    if (counties.length && !counties.includes(l.county))    return false;
    if (l.price < minP || l.price > maxP)                   return false;
    return true;
});

updateActivePills(varietals, processes, roasts, counties);
sortListings();
}

function updateActivePills(v,p,r,c) {
const container = document.getElementById('activeFilters');
container.innerHTML = [...v,...p,...r,...c].map(f=>
    `<div class="active-filter-pill">${f} <span onclick="removeFilter('${f}')">✕</span></div>`
).join('');
}

function removeFilter(val) {
document.querySelectorAll('input[type="checkbox"]').forEach(cb => { if(cb.value===val) cb.checked=false; });
filterListings();
}

function clearFilter(type) {
const prefix = type==='varietal'?'v-':type==='process'?'p-':type==='roast'?'r-':'c-';
document.querySelectorAll(`input[id^="${prefix}"]`).forEach(cb => cb.checked=false);
filterListings();
}

function resetFilters() {
document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked=false);
document.getElementById('searchInput').value='';
document.getElementById('priceMin').value='';
document.getElementById('priceMax').value='';
document.getElementById('activeFilters').innerHTML='';
filtered=[...listings];
renderCards(filtered);
}

/* ══ SORT ══ */
function sortListings() {
const s = document.getElementById('sortSelect').value;
const sorted = [...filtered];
if (s==='price-asc')  sorted.sort((a,b)=>a.price-b.price);
if (s==='price-desc') sorted.sort((a,b)=>b.price-a.price);
if (s==='stock')      sorted.sort((a,b)=>b.stock-a.stock);
renderCards(sorted);
}

/* ══ VIEW TOGGLE ══ */
function setView(v) {
const grid = document.getElementById('listingsGrid');
document.getElementById('gridViewBtn').classList.toggle('active', v==='grid');
document.getElementById('listViewBtn').classList.toggle('active', v==='list');
grid.classList.toggle('list-view', v==='list');
}

/* ══ MODAL ══ */
function openModal(l) {
if (!l) return;
currentModal = l;

document.getElementById('modalFarmName').textContent = '🌿 ' + l.farm + ' — ' + l.county;
document.getElementById('modalTitle').innerHTML = l.name;
document.getElementById('mVarietal').textContent = l.varietal;
document.getElementById('mProcess').textContent  = l.process;
document.getElementById('mRoast').textContent    = l.roast + ' Roast';
document.getElementById('mHarvest').textContent  = l.harvest;
document.getElementById('mStock').textContent    = l.stock + ' kg';
document.getElementById('mMin').textContent      = l.minOrder + ' kg';
document.getElementById('mLocation').textContent = l.county;
document.getElementById('mAltitude').textContent = l.altitude + ' masl';
document.getElementById('mNotes').innerHTML = l.notes.map(n=>`<span class="modal-note">${n}</span>`).join('');
document.getElementById('modalQty').value = l.minOrder;
document.getElementById('modalQty').min   = l.minOrder;
updateModalTotal();
toggleModalAuth();

document.getElementById('modalOverlay').classList.add('open');
document.body.style.overflow = 'hidden';
}

function updateModalTotal() {
if (!currentModal) return;
const qty = parseFloat(document.getElementById('modalQty').value) || 0;
const total = qty * currentModal.price;
document.getElementById('modalTotal').textContent = 'KES ' + total.toLocaleString();
}

function closeModal(e) {
if (e.target === document.getElementById('modalOverlay')) closeModalBtn();
}
function closeModalBtn() {
document.getElementById('modalOverlay').classList.remove('open');
document.body.style.overflow = '';
}
document.addEventListener('keydown', e => { if(e.key==='Escape') closeModalBtn(); });

function handleOrder() {
if (!isLoggedIn) { alert('Please login to place an order.'); return; }
const qty = document.getElementById('modalQty').value;
alert(`In Flask:\nPOST /marketplace/order\n{\n  listing_id: ${currentModal.id},\n  quantity_kg: ${qty}\n}\n→ M-Pesa STK Push sent to buyer's registered number`);
}

function handleMessage() {
if (!isLoggedIn) { alert('Please login to message growers.'); return; }
alert(`In Flask:\nredirect → /dashboard/buyer#messages\nPre-loaded with conversation to: ${currentModal.farm}`);
}

/* ══ INIT ══ */
renderCards(listings);