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