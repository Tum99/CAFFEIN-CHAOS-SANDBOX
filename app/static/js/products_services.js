
/* scroll top */
const st = document.getElementById('scrollTop');
if (st) {
  window.addEventListener('scroll', () => st.classList.toggle('visible', window.scrollY > 400));
}
/* category nav highlight on scroll */
const sections = document.querySelectorAll('section[id]');
const navBtns  = document.querySelectorAll('.cat-nav-btn');
window.addEventListener('scroll', () => {
let cur = '';
sections.forEach(s => { if(s.getBoundingClientRect().top <= 150) cur = s.id; });
navBtns.forEach(b => { b.classList.toggle('active', b.dataset.section === cur); });
});
navBtns.forEach(btn => {
btn.addEventListener('click', () => {
    document.getElementById(btn.dataset.section)?.scrollIntoView({behavior:'smooth'});
});
});

/* scroll reveal */
const obs = new IntersectionObserver(entries => {
entries.forEach(e => {
    if(e.isIntersecting) { e.target.style.opacity='1'; e.target.style.transform='translateY(0)'; }
});
}, {threshold: 0.07});
document.querySelectorAll('.pack-hero-card,.pack-card,.hamper-card,.ind-card').forEach((el,i) => {
el.style.opacity='0'; el.style.transform='translateY(24px)';
el.style.transition=`opacity 0.55s ease ${(i%4)*0.07}s, transform 0.55s cubic-bezier(0.22,1,0.36,1) ${(i%4)*0.07}s`;
obs.observe(el);
});

/* ── PRODUCT MODAL ── */
let prodModalCurrentItem = null;

function openProductModal(card) {
const name        = card.dataset.name        || '';
const price       = parseFloat(card.dataset.price) || 0;
const description = card.dataset.description || 'A Caffeine & Chaos product.';
const tag         = card.dataset.tag         || 'Product';
const img         = card.dataset.img         || '';
const includesRaw = card.dataset.includes    || '';

/* Populate */
document.getElementById('prodModalName').textContent  = name;
document.getElementById('prodModalPrice').textContent = 'KES ' + price.toLocaleString();
document.getElementById('prodModalDesc').textContent  = description;
document.getElementById('prodModalTag').textContent   = tag;

const imgEl = document.getElementById('prodModalImg');
imgEl.src = img; imgEl.alt = name;

/* Includes pills — only for packs */
const includesWrap = document.getElementById('prodModalIncludes');
const pillsEl      = document.getElementById('prodModalPills');
if (includesRaw) {
    const items = includesRaw.split('|').filter(Boolean);
    pillsEl.innerHTML = items.map(i =>
    `<span class="prod-modal-pill">${i.trim()}</span>`
    ).join('');
    includesWrap.style.display = 'block';
} else {
    includesWrap.style.display = 'none';
}

/* Reset button */
const addBtn = document.getElementById('prodModalAddBtn');
addBtn.textContent = 'Add to Cart →';
addBtn.classList.remove('added');

prodModalCurrentItem = { name, price };

document.getElementById('prodModalOverlay').classList.add('open');
document.body.style.overflow = 'hidden';
}

function closeProdModal(e) {
if (e.target === document.getElementById('prodModalOverlay')) closeProdModalBtn();
}
function closeProdModalBtn() {
document.getElementById('prodModalOverlay').classList.remove('open');
document.body.style.overflow = '';
}

document.addEventListener('keydown', e => {
if (e.key === 'Escape') closeProdModalBtn();
});

function addProdFromModal() {
if (!prodModalCurrentItem) return;
/* Hook into your cart system here */
console.log('Add to cart:', prodModalCurrentItem);

const btn = document.getElementById('prodModalAddBtn');
btn.textContent = '✓ Added to Cart';
btn.classList.add('added');
setTimeout(() => {
    btn.textContent = 'Add to Cart →';
    btn.classList.remove('added');
}, 1800);
}