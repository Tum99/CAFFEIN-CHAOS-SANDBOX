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