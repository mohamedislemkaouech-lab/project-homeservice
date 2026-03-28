// static/js/chatbot.js
// Vanilla-JS floating chatbot widget for ServicesDOM.
// Maintains a conversation history array and sends it in full
// to /chatbot/api/chat/ (Django → Ollama tinyllama proxy).
// Shows animated typing dots while waiting. Handles Ollama-offline errors.

(function () {
    "use strict";

    // ── DOM refs ──────────────────────────────────────────────────────────
    const toggle   = document.getElementById("chatbot-toggle");
    const win      = document.getElementById("chatbot-window");
    const closeBtn = document.getElementById("chatbot-close");
    const msgs     = document.getElementById("chatbot-messages");
    const input    = document.getElementById("chatbot-input");
    const sendBtn  = document.getElementById("chatbot-send");
    if (!toggle || !win) return;

    // ── Conversation history (sent in full on every request) ─────────────
    const history = [];

    // ── Open / close with animation ──────────────────────────────────────
    toggle.addEventListener("click", function () {
        win.classList.remove("d-none", "cb-closing");
        win.classList.add("cb-opening");
        toggle.classList.add("d-none");
        input.focus();
    });
    closeBtn.addEventListener("click", function () {
        win.classList.add("cb-closing");
        win.classList.remove("cb-opening");
        toggle.classList.remove("d-none");
        setTimeout(function () { win.classList.add("d-none"); }, 280);
    });

    // ── Send message ─────────────────────────────────────────────────────
    function send() {
        var text = input.value.trim();
        if (!text) return;
        input.value = "";

        // Push to history & render user bubble
        history.push({ role: "user", content: text });
        bubble(text, "user");

        // Typing indicator
        var dots = typingDots();

        // Disable while waiting
        input.disabled = true;
        sendBtn.disabled = true;

        fetch("/chatbot/api/chat/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ messages: history })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            dots.remove();
            if (data.reply) {
                history.push({ role: "assistant", content: data.reply });
                bubble(data.reply, "bot");
                
                if (data.results && data.results.length > 0) {
                    renderCards(data.results);
                }
            } else {
                bubble("⚠️ " + (data.error || "Erreur inconnue."), "bot");
            }
        })
        .catch(function (e) {
            console.error(e);
            dots.remove();
            bubble("⚠️ Impossible de joindre le serveur.", "bot");
        })
        .finally(function () {
            input.disabled = false;
            sendBtn.disabled = false;
            input.focus();
        });
    }

    // ── Helpers ───────────────────────────────────────────────────────────
    function bubble(text, who) {
        var row = document.createElement("div");
        row.className = "cb-row cb-" + who;

        var b = document.createElement("div");
        b.className = "cb-bubble";
        b.style.whiteSpace = "pre-wrap";
        b.textContent = text;

        row.appendChild(b);
        msgs.appendChild(row);
        msgs.scrollTop = msgs.scrollHeight;
        return row;
    }

    function typingDots() {
        var row = document.createElement("div");
        row.className = "cb-row cb-bot";
        row.innerHTML = '<div class="cb-bubble cb-dots"><span></span><span></span><span></span></div>';
        msgs.appendChild(row);
        msgs.scrollTop = msgs.scrollHeight;
        return row;
    }

    function renderCards(results) {
        var row = document.createElement("div");
        row.className = "cb-row cb-bot w-100";
        row.style.display = "block";
        row.style.padding = "5px 15px";
        
        var html = "";
        results.forEach(function(res) {
            html += `
            <div class="card shadow-sm mb-2" style="font-size: 0.85rem; border: 1px solid #dee2e6;">
                <div class="card-body p-2">
                    <h6 class="card-title fw-bold mb-1 text-primary">${res.service_title}</h6>
                    <p class="card-text mb-1"><i class="fas fa-user text-muted me-1"></i>${res.provider_name}</p>
                    <div class="d-flex justify-content-between align-items-center mt-2">
                        <span class="badge bg-secondary">${res.price}</span>
                        <a href="${res.url}" class="btn btn-sm btn-outline-primary" style="padding: 0.1rem 0.5rem; font-size: 0.8rem;">Détails</a>
                    </div>
                </div>
            </div>`;
        });
        
        row.innerHTML = html;
        msgs.appendChild(row);
        msgs.scrollTop = msgs.scrollHeight;
    }

    // ── Events ───────────────────────────────────────────────────────────
    sendBtn.addEventListener("click", send);
    input.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
    });
})();
