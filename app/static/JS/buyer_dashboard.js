const cur=document.getElementById('cursor'),ring=document.getElementById('cursorRing');
let mx=0,my=0,rx=0,ry=0;
document.addEventListener('mousemove',e=>{mx=e.clientX;my=e.clientY;cur.style.left=mx+'px';cur.style.top=my+'px';});
(function loop(){rx+=(mx-rx)*0.12;ry+=(my-ry)*0.12;ring.style.left=rx+'px';ring.style.top=ry+'px';requestAnimationFrame(loop);})();

function showSection(name, event) {
    document.querySelectorAll('.content-section').forEach(s=>s.classList.remove('active'));
    document.querySelectorAll('.sidebar-link').forEach(l=>l.classList.remove('active'));
    document.getElementById(`sec-${name}`).classList.add('active');
    event.currentTarget.classList.add('active');
    event.preventDefault();
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




