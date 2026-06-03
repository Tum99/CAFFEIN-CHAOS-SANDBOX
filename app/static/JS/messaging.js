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
        fetch(`/api/messages/${threadId}`)
            .then(res => res.json())
            .then(data => {
                chatWindow.style.display = "flex";
                chatHeadName.textContent = data.other_user_name;
                container.innerHTML = ""; // Reset container
                
                data.messages.forEach(msg => {
                    const msgDiv = document.createElement("div");
                    msgDiv.className = `msg ${msg.is_mine ? 'sent' : 'received'}`;
                    msgDiv.innerHTML = `
                        <div class="msg-bubble">${msg.body}</div>
                        <div class="msg-time">${msg.time}</div>
                    `;
                    container.appendChild(msgDiv);
                });
                container.scrollTop = container.scrollHeight; // Auto-scroll down
            });
    }

    // 3. Post Message to Flask API
    function postReply() {
        const text = inputField.value.trim();
        if(!text || !activeThreadId) return;

        fetch(`/api/messages/${activeThreadId}/send`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ body: text })
        })
        .then(res => res.json())
        .then(data => {
            if(data.status === 'success') {
                const msgDiv = document.createElement("div");
                msgDiv.className = "msg sent";
                msgDiv.innerHTML = `
                    <div class="msg-bubble">${text}</div>
                    <div class="msg-time">${data.message.time}</div>
                `;
                container.appendChild(msgDiv);
                inputField.value = ""; // Empty input line
                container.scrollTop = container.scrollHeight;
            }
        });
    }

    sendBtn.addEventListener("click", postReply);
    inputField.addEventListener("keypress", (e) => { if(e.key === "Enter") postReply(); });

    // Load first thread on initialization if available
    if(threads.length > 0) threads[0].click();
});