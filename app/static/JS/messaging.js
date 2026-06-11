document.addEventListener("DOMContentLoaded", function() {
    const threads = document.querySelectorAll(".thread-item");
    const container = document.getElementById("chatMessagesContainer");
    const chatWindow = document.getElementById("chatWindow");
    const chatHeadName = document.getElementById("chatHeadName");
    const inputField = document.getElementById("chatInputField");
    const sendBtn = document.getElementById("chatSendButton");
    
    let activeThreadId = null;

    // 1. Click Handler for Thread Switching
    threads.forEach(thread => {
        thread.addEventListener("click", function() {
            threads.forEach(t => t.classList.remove("active-thread"));
            this.classList.add("active-thread");
            
            activeThreadId = this.getAttribute("data-thread-id");
            loadThread(activeThreadId);
        });
    });

    // 2. Fetch Thread Data from Flask JSON API
    function loadThread(threadId) {
        if (!threadId) return;
        fetch(`/api/messages/${threadId}`)
            .then(res => {
                if (!res.ok) throw new Error("Unauthorized or server crash configuration state");
                return res.json();
            })
            .then(data => {
                if (chatWindow) chatWindow.style.display = "flex";
                if (chatHeadName) chatHeadName.textContent = data.other_user_name;
                container.innerHTML = ""; // Reset container text strings completely
                
                data.messages.forEach(msg => {
                    const msgDiv = document.createElement("div");
                    msgDiv.className = `msg ${msg.is_mine ? 'sent' : 'received'}`;
                    msgDiv.innerHTML = `
                        <div class="msg-bubble">${escapeHTML(msg.body)}</div>
                        <div class="msg-time">${msg.time}</div>
                    `;
                    container.appendChild(msgDiv);
                });
                container.scrollTop = container.scrollHeight; // Auto-scroll down
            })
            .catch(err => console.error("Error reading thread details:", err));
    }

    // 3. Post Message to Flask API
    function postReply() {
        const text = inputField.value.trim();
        if(!text || !activeThreadId) return;

        // Fetch verification CSRF token directly from meta tags or forms if globally configured
        const csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');
        const headers = { "Content-Type": "application/json" };
        if (csrfTokenMeta) {
            headers["X-CSRFToken"] = csrfTokenMeta.getAttribute("content");
        }

        fetch(`/api/messages/${activeThreadId}/send`, {
            method: "POST",
            headers: headers,
            body: JSON.stringify({ body: text })
        })
        .then(res => res.json())
        .then(data => {
            if(data.status === 'success') {
                const msgDiv = document.createElement("div");
                msgDiv.className = "msg sent";
                msgDiv.innerHTML = `
                    <div class="msg-bubble">${escapeHTML(text)}</div>
                    <div class="msg-time">${data.message.time}</div>
                `;
                container.appendChild(msgDiv);
                inputField.value = ""; // Empty input line
                container.scrollTop = container.scrollHeight;
            }
        });
    }

    if (sendBtn) sendBtn.addEventListener("click", postReply);
    if (inputField) {
        inputField.addEventListener("keypress", (e) => { if(e.key === "Enter") postReply(); });
    }

    // Utility text verification escape parsing tool to mitigate XSS exposure injection scripts
    function escapeHTML(str) {
        return str.replace(/[&<>'"]/g, 
            tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
        );
    }

    // Load first thread on initialization if available
    if(threads.length > 0) threads[0].click();
});