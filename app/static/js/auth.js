const cur = document.getElementById('cursor');
  const ring = document.getElementById('cursorRing');
  let mx=0,my=0,rx=0,ry=0;
  document.addEventListener('mousemove', e => { mx=e.clientX; my=e.clientY; cur.style.left=mx+'px'; cur.style.top=my+'px'; });
  (function loop(){ rx+=(mx-rx)*0.12; ry+=(my-ry)*0.12; ring.style.left=rx+'px'; ring.style.top=ry+'px'; requestAnimationFrame(loop); })();
 
  function switchTab(tab) {
    document.querySelectorAll('.auth-tab').forEach((t,i) => t.classList.toggle('active', (i===0&&tab==='login')||(i===1&&tab==='signup')));
    document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
    document.getElementById(`form-${tab}`).classList.add('active');
  }
 
  function simulateLogin() {
    // In Flask this is handled by the route — this is just for demo
    alert('In Flask:\n\nif user.role == "buyer" → redirect to /dashboard/buyer\nif user.role == "seller" → redirect to /dashboard/seller\nif user.role == "admin" → redirect to /admin');
  }