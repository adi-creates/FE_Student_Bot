const chat = document.getElementById("chat");
const form = document.getElementById("chat-form");
const input = document.getElementById("question");
const suggestionsList = document.getElementById("suggestions-list");
const healthStatus = document.getElementById("health-status");
const faqCount = document.getElementById("faq-count");
const statusPill = document.getElementById("status-pill");

function appendMessage(role, text, meta = "") {
    const el = document.createElement("article");
    el.className = `message ${role}`;

    const roleTag = document.createElement("span");
    roleTag.className = "message-role";
    roleTag.textContent = role === "user" ? "You" : "Assistant";

    const body = document.createElement("div");
    body.className = "message-text";
    body.textContent = text;

    el.appendChild(roleTag);
    el.appendChild(body);

    if (meta) {
        const metaEl = document.createElement("span");
        metaEl.className = "meta";
        metaEl.textContent = meta;
        el.appendChild(metaEl);
    }

    chat.appendChild(el);
    chat.scrollTop = chat.scrollHeight;
}

appendMessage("bot", "Hello! Ask me anything related to TCET FE FAQs.");

async function loadHealth() {
    try {
        const response = await fetch("/api/health");
        const data = await response.json();

        if (!response.ok || data.status !== "ok") {
            throw new Error("Health check failed");
        }

        if (healthStatus) healthStatus.textContent = "Online";
        if (faqCount) faqCount.textContent = String(data.faq_count ?? "-");
        if (statusPill) statusPill.textContent = "Service online";
    } catch (_error) {
        if (healthStatus) healthStatus.textContent = "Offline";
        if (faqCount) faqCount.textContent = "-";
        if (statusPill) statusPill.textContent = "Service unavailable";
    }
}

function renderSuggestions(questions) {
    if (!suggestionsList) return;
    suggestionsList.innerHTML = "";

    questions.forEach((question) => {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "suggestion-chip";
        chip.textContent = question;
        chip.addEventListener("click", () => {
            input.value = question;
            input.focus();
        });
        suggestionsList.appendChild(chip);
    });
}

async function loadSuggestions() {
    const randomCount = Math.random() < 0.5 ? 3 : 4;

    try {
        const response = await fetch(`/api/suggestions?count=${randomCount}`);
        const data = await response.json();

        if (!response.ok || !Array.isArray(data.questions)) {
            renderSuggestions([]);
            return;
        }

        renderSuggestions(data.questions);
    } catch (_error) {
        renderSuggestions([]);
    }
}

loadSuggestions();
loadHealth();

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const question = input.value.trim();
    if (!question) return;

    appendMessage("user", question);
    input.value = "";

    try {
        const response = await fetch("/api/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question }),
        });

        const data = await response.json();
        if (!response.ok) {
            appendMessage("bot", data.error || "Something went wrong.");
            return;
        }

        const meta = `source: ${data.source_question || "n/a"} | confidence: ${data.confidence ?? "n/a"}`;
        appendMessage("bot", data.answer, meta);
    } catch (error) {
        appendMessage("bot", "Unable to reach the server. Please try again.");
    } finally {
        loadSuggestions();
        loadHealth();
    }
});
