const cur=document.getElementById('cursor'),ring=document.getElementById('cursorRing');
let mx=0,my=0,rx=0,ry=0;
document.addEventListener('mousemove',e=>{mx=e.clientX;my=e.clientY;cur.style.left=mx+'px';cur.style.top=my+'px';});
(function loop(){rx+=(mx-rx)*0.12;ry+=(my-ry)*0.12;ring.style.left=rx+'px';ring.style.top=ry+'px';requestAnimationFrame(loop);})();

function showSection(name, event) {
    if (event) {
        event.preventDefault();
    }
    
    // Hide all sections and deactivate links
    document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.sidebar-link').forEach(l => l.classList.remove('active'));
    
    const targetSection = document.getElementById(`sec-${name}`);
    if (targetSection) {
        targetSection.classList.add('active');
    }

    // Update active state on matching sidebar link
    const targetLink = document.querySelector(`.sidebar-link[onclick*="'${name}'"]`);
    if (targetLink) {
        targetLink.classList.add('active');
    }

    // Update the URL hash without triggering a full page reload
    if (window.location.hash !== `#sec-${name}`) {
        history.pushState(null, null, `#sec-${name}`);
    }
}

function handleUrlHash() {
    const hash = window.location.hash; // e.g., "#sec-settings"
    if (hash && hash.startsWith('#sec-')) {
        const sectionName = hash.replace('#sec-', '');
        const targetSection = document.getElementById(`sec-${sectionName}`);
        if (targetSection) {
            showSection(sectionName);
        }
    }
}

// 3. Run on page load and when hash changes
document.addEventListener('DOMContentLoaded', handleUrlHash);
window.addEventListener('hashchange', handleUrlHash);


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




