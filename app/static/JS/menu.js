/* ── CURSOR ── */
const cursor = document.getElementById('cursor');
const ring   = document.getElementById('cursorRing');
let mx=0,my=0,rx=0,ry=0;
document.addEventListener('mousemove', e => {
  mx=e.clientX; my=e.clientY;
  cursor.style.left=mx+'px'; cursor.style.top=my+'px';
});
(function animRing(){
  rx+=(mx-rx)*0.12; ry+=(my-ry)*0.12;
  ring.style.left=rx+'px'; ring.style.top=ry+'px';
  requestAnimationFrame(animRing);
})();


/* ── MENU MODAL STATE ── */
let menuModalCurrentItem = null;

/* ── OPEN ── */
function openMenuModal(card) {
const name   = card.dataset.name;
const price  = parseFloat(card.dataset.price);
const desc   = card.dataset.description;
const cat    = card.dataset.category;
const img    = card.dataset.img;

/* populate modal */
document.getElementById('menuModalName').textContent  = name;
document.getElementById('menuModalPrice').textContent = 'KES ' + price.toLocaleString();
document.getElementById('menuModalDesc').textContent  = desc;
document.getElementById('menuModalCat').textContent   = cat;

const imgEl = document.getElementById('menuModalImg');
imgEl.src = img;
imgEl.alt = name;

/* reset add button */
const addBtn = document.getElementById('menuModalAddBtn');
addBtn.textContent = '+ Add to Order';
addBtn.classList.remove('added');

/* store for add-to-cart */
menuModalCurrentItem = { name, price };

/* open */
document.getElementById('menuModalOverlay').classList.add('open');
document.body.style.overflow = 'hidden';
}

/* ── CLOSE ── */
function closeMenuModal(e) {
if (e.target === document.getElementById('menuModalOverlay')) closeMenuModalBtn();
}
function closeMenuModalBtn() {
document.getElementById('menuModalOverlay').classList.remove('open');
document.body.style.overflow = '';
}

/* Escape key closes */
document.addEventListener('keydown', e => {
if (e.key === 'Escape') closeMenuModalBtn();
});

/* ── ADD TO ORDER FROM MODAL ── */
function addFromModal() {
if (!menuModalCurrentItem) return;
addMenuItemToCart(menuModalCurrentItem.name, menuModalCurrentItem.price);

/* visual feedback */
const btn = document.getElementById('menuModalAddBtn');
btn.textContent = '✓ Added';
btn.classList.add('added');
setTimeout(() => {
  btn.textContent = '+ Add to Order';
  btn.classList.remove('added');
}, 1500);
}

/* ── ADD TO CART (also used by the + button on the card) ── */
function addMenuItemToCart(name, price) {
/* update mini cart totals in sidebar */
const totalEl = document.getElementById('cartTotal');
const countEl = document.getElementById('cartCount');
const current = parseInt(totalEl.textContent.replace(/,/g, '')) || 0;
const count   = parseInt(countEl.textContent) || 0;
totalEl.textContent = (current + price).toLocaleString();
countEl.textContent = count + 1;
}

  /* ── SIDEBAR ACTIVE ON SCROLL ── */
const sections   = document.querySelectorAll('.cat-section');
const catLinks   = document.querySelectorAll('.cat-link');
const mainEl     = document.getElementById('mainContent');

function updateActive(){
  let current = '';
  sections.forEach(sec => {
    const rect = sec.getBoundingClientRect();
    if(rect.top <= 160) current = sec.id;
  });
  catLinks.forEach(lnk => {
    lnk.classList.remove('active');
    if(lnk.getAttribute('data-cat') === current) lnk.classList.add('active');
  });
}
window.addEventListener('scroll', updateActive);
updateActive();

/* ── SCROLL TO TOP ── */
const scrollTopBtn = document.getElementById('scrollTop');
window.addEventListener('scroll', () => {
  scrollTopBtn.classList.toggle('visible', window.scrollY > 400);
});
scrollTopBtn.addEventListener('click', () => window.scrollTo({top:0, behavior:'smooth'}));

  /* ── MINI CART ── */
let cartTotal = 0, cartCount = 0;
const cartTotalEl = document.getElementById('cartTotal');
const cartCountEl = document.getElementById('cartCount');

document.querySelectorAll('.item-add').forEach(btn => {
  btn.addEventListener('click', () => {
    const card  = btn.closest('.item-card');
    const price = parseInt(card.querySelector('.item-price').textContent.replace(/[^0-9]/g,''));
    cartTotal += price;
    cartCount += 1;
    cartTotalEl.textContent = cartTotal.toLocaleString();
    cartCountEl.textContent = cartCount;
    /* quick pulse on btn */
    btn.textContent = '✓';
    btn.style.background = '#4CAF50';
    setTimeout(()=>{ btn.textContent='+'; btn.style.background=''; }, 900);
  });
});

  /* ── SEARCH ── */
const searchInput = document.getElementById('searchInput');
searchInput.addEventListener('input', () => {
  const q = searchInput.value.toLowerCase().trim();
  document.querySelectorAll('.item-card').forEach(card => {
    const name = card.querySelector('.item-name').textContent.toLowerCase();
    card.style.display = (!q || name.includes(q)) ? '' : 'none';
  });
  // hide empty sections
  sections.forEach(sec => {
    const visible = [...sec.querySelectorAll('.item-card')].some(c => c.style.display !== 'none');
    sec.style.display = visible ? '' : 'none';
  });
});

  /* ── SCROLL REVEAL ── */
const revealObs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if(e.isIntersecting){
      e.target.style.opacity='1';
      e.target.style.transform='translateY(0)';
    }
  });
}, {threshold: 0.08});

  document.querySelectorAll('.item-card').forEach((el, i) => {
  el.style.opacity='0';
  el.style.transform='translateY(20px)';
  el.style.transition=`opacity 0.5s ease ${(i%6)*0.06}s, transform 0.5s cubic-bezier(0.22,1,0.36,1) ${(i%6)*0.06}s`;
  revealObs.observe(el);
});