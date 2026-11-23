document.addEventListener("DOMContentLoaded", function () {
    const assistantBtn = Array.from(document.querySelectorAll("button")).find(btn => btn.textContent.includes("ИИ-Ассистент"));
    if (!assistantBtn) return;

    const STORAGE_KEY = "my_relax_chat_history";
    const chatContainer = document.createElement("div");
    chatContainer.id = "ai-chat-window";
    chatContainer.className = "shadow chat-window d-none";

    chatContainer.innerHTML = `
        <div class="chat-header d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center gap-2">
                <span class="emoji-robot">🤖</span>
                <span class="fw-bold">ИИ-Ассистент</span>
            </div>
            <div class="d-flex gap-2 align-items-center">
                <button type="button" id="clear-chat" title="Очистить чат" style="background:none;border:none;color:white;cursor:pointer;font-size:16px;padding:0;">
                    <span class="emoji-trash">🗑️</span>
                </button>
                <button type="button" id="close-chat" aria-label="Закрыть">×</button>
            </div>
        </div>
        <div class="chat-body d-flex flex-column" id="chat-messages"></div>
        <div class="chat-footer">
            <div class="d-flex gap-2">
                <input type="text" id="chat-input" class="form-control form-control-sm"
                       placeholder="Введите сообщение..."
                       style="border:1px solid #ced4da!important;border-radius:4px!important;">
                <button class="btn btn-primary btn-sm fw-bold text-nowrap" id="send-msg-btn">Отправить</button>
            </div>
        </div>
    `;

    document.body.appendChild(chatContainer);

    const messagesBody = document.getElementById("chat-messages");
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-msg-btn");
    const closeBtn = document.getElementById("close-chat");
    const clearBtn = document.getElementById("clear-chat");

    let isInitialized = false;
    let isSending = false;
    let chatHistory = [];

    // Скролл чата вниз
    const scrollToBottom = () => setTimeout(() => { messagesBody.scrollTop = messagesBody.scrollHeight; }, 50);

    // Обработка спецсимволов
    const escapeHtml = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

    // Поиск Markdown ссылок и жирного текста
    function linkify(text) {
        return escapeHtml(text)
            .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
            .replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, linkText, url) => `<a href="${url.replace(/[^a-zA-Z0-9/#?=:-]/g, "")}" class="chat-link">${linkText}</a>`);
    }

    // Добавление сообщений
    function appendMessage(text, type, shouldSave = true) {
        const msgDiv = document.createElement("div");
        const role = (type === "robot" || type === "assistant") ? "assistant" : "user";
        msgDiv.className = `msg ${role === "assistant" ? "msg-robot me-auto" : "msg-user ms-auto"}`;
        role === "assistant" ? (msgDiv.innerHTML = linkify(text)) : (msgDiv.textContent = text);

        messagesBody.appendChild(msgDiv);
        scrollToBottom();

        if (shouldSave) {
            chatHistory.push({ role, content: text });
            saveToLocalStorage();
        }
    }

    // Сохранение в LocalStorage
    function saveToLocalStorage() {
        try { localStorage.setItem(STORAGE_KEY, JSON.stringify(chatHistory)); }
        catch (e) { console.error("Ошибка сохранения в LocalStorage:", e); }
    }

    // Загрузка истории из памяти
    function loadLocalStorageHistory() {
        try {
            const savedData = localStorage.getItem(STORAGE_KEY);
            if (savedData) {
                chatHistory = JSON.parse(savedData);
                chatHistory.forEach(item => appendMessage(item.content, item.role, false));
                isInitialized = true;
                scrollToBottom();
            }
        } catch (e) { console.error("Ошибка загрузки истории из LocalStorage:", e); }
    }

    // Запросы к серверу
    async function loadGreeting() {
        try {
            const response = await fetch("/api/ai-init/");
            appendMessage(await response.text(), "assistant");
        } catch {
            appendMessage("Привет! Я твой ИИ-помощник магазина MY-RELAX. Помогу выбрать товары для отдыха!", "assistant");
        } finally {
            isInitialized = true;
        }
    }

    // Отправка сообщений на бэкенд
    async function handleSendMessage() {
        if (isSending) return;
        const text = chatInput.value.trim();
        if (!text) return;

        appendMessage(text, "user");
        chatInput.value = "";
        isSending = chatInput.disabled = sendBtn.disabled = true;

        const statusDiv = document.createElement("div");
        statusDiv.className = "msg msg-robot me-auto";
        statusDiv.innerHTML = "<em>Думаю...</em>";
        messagesBody.appendChild(statusDiv);
        scrollToBottom();

        try {
            const response = await fetch("/api/ai-chat/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text, history: chatHistory.slice(-10) })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.reply || "Ошибка");

            statusDiv.remove();
            appendMessage(data.reply, "assistant");
        } catch {
            statusDiv.remove();
            appendMessage("Не удалось получить ответ от ИИ.", "assistant");
        } finally {
            isSending = chatInput.disabled = sendBtn.disabled = false;
            chatInput.focus();
        }
    }

    // Инициализация чата
    loadLocalStorageHistory();

    if (localStorage.getItem("ai_chat_open") === "true") {
        chatContainer.classList.remove("d-none");
        scrollToBottom();
        chatInput.focus();
    }

    // Кнопки и клики
    assistantBtn.addEventListener("click", () => {
        const isOpen = !chatContainer.classList.toggle("d-none");
        localStorage.setItem("ai_chat_open", isOpen);
        if (isOpen) {
            scrollToBottom();
            chatInput.focus();
            if (!isInitialized) loadGreeting();
        }
    });

    closeBtn.addEventListener("click", () => {
        chatContainer.classList.add("d-none");
        localStorage.setItem("ai_chat_open", "false");
    });

    if (clearBtn) {
        clearBtn.addEventListener("click", () => {
            if (confirm("Очистить историю чата?")) {
                localStorage.removeItem(STORAGE_KEY);
                chatHistory = [];
                messagesBody.innerHTML = "";
                isInitialized = false;
                loadGreeting();
            }
        });
    }

    sendBtn.addEventListener("click", handleSendMessage);
    chatInput.addEventListener("keypress", e => { if (e.key === "Enter") handleSendMessage(); });
});
