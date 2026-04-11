(function () {
    "use strict";

    const toggle    = document.getElementById("chatbot-toggle");
    const win       = document.getElementById("chatbot-window");
    const closeBtn  = document.getElementById("chatbot-close");
    const msgs      = document.getElementById("chatbot-messages");
    const input     = document.getElementById("chatbot-input");
    const sendBtn   = document.getElementById("chatbot-send");
    if (!toggle || !win) return;

    const history = [];

    // ── Open / close ──────────────────────────────────────────────────────
    toggle.addEventListener("click", function () {
        win.classList.remove("d-none", "cb-closing");
        win.classList.add("cb-opening");
        toggle.classList.add("d-none");
        input.focus();
        // Show quick replies on first open
        if (history.length === 0) {
            showQuickReplies([
                "Plombier",
                "Ménage",
                "Baby-sitting",
                "Comment ça marche ?",
                "Annuler une réservation",
            ]);
        }
    });

    closeBtn.addEventListener("click", function () {
        win.classList.add("cb-closing");
        win.classList.remove("cb-opening");
        toggle.classList.remove("d-none");
        setTimeout(function () { win.classList.add("d-none"); }, 280);
    });

    // ── Send ──────────────────────────────────────────────────────────────
    function send(text) {
        text = (text || input.value).trim();
        if (!text) return;
        input.value = "";

        // Remove any existing quick reply row before sending
        removeQuickReplies();

        history.push({ role: "user", content: text });
        bubble(text, "user");

        var dots = typingDots();
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

                // Show service cards if results exist
                if (data.results && data.results.length > 0) {
                    renderCards(data.results);
                }

                // Show quick replies if provided
                if (data.quick_replies && data.quick_replies.length > 0) {
                    showQuickReplies(data.quick_replies);
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

    // ── Quick replies ─────────────────────────────────────────────────────
    function showQuickReplies(replies) {
        removeQuickReplies();

        var row = document.createElement("div");
        row.className = "cb-quick-replies";
        row.id = "cb-quick-row";

        replies.forEach(function (label) {
            var btn = document.createElement("button");
            btn.className = "cb-quick-btn";
            btn.textContent = label;
            btn.addEventListener("click", function () {
                send(label);
            });
            row.appendChild(btn);
        });

        msgs.appendChild(row);
        msgs.scrollTop = msgs.scrollHeight;
    }

    function removeQuickReplies() {
        var existing = document.getElementById("cb-quick-row");
        if (existing) existing.remove();
    }

    // ── Service cards ─────────────────────────────────────────────────────
    function renderCards(results) {
        var row = document.createElement("div");
        row.className = "cb-row cb-bot w-100";
        row.style.display = "block";
        row.style.padding = "4px 12px";

        var html = "";
        results.forEach(function (res) {
            html += `
            <div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:10px 12px;margin-bottom:8px;font-size:0.83rem;">
                <div style="font-weight:700;color:#3B82F6;margin-bottom:4px;">${res.service_title}</div>
                <div style="color:#64748b;margin-bottom:6px;">
                    <i class="fas fa-user" style="font-size:11px;margin-right:4px;"></i>${res.provider_name}
                    &nbsp;·&nbsp;
                    <span style="background:#f1f5f9;padding:1px 7px;border-radius:10px;font-size:0.78rem;">${res.price}</span>
                </div>
                <div style="display:flex;gap:6px;">
                    <a href="${res.url}"
                       style="flex:1;text-align:center;padding:5px 0;border:1px solid #3B82F6;border-radius:7px;color:#3B82F6;text-decoration:none;font-size:0.8rem;">
                        Détails
                    </a>
                    <a href="${res.book_url}"
                       style="flex:1;text-align:center;padding:5px 0;background:#3B82F6;border-radius:7px;color:#fff;text-decoration:none;font-size:0.8rem;">
                        Réserver
                    </a>
                </div>
            </div>`;
        });

        row.innerHTML = html;
        msgs.appendChild(row);
        msgs.scrollTop = msgs.scrollHeight;
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

    // ── Events ────────────────────────────────────────────────────────────
    sendBtn.addEventListener("click", function () { send(); });
    input.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
    });
})();