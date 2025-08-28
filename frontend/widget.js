class RAGChatbotWidget {
    constructor(config = {}) {
        this.config = {
            apiBaseUrl: config.apiBaseUrl || this.getApiBaseUrl(),
            position: config.position || 'bottom-right',
            ...config
        };

        this.isOpen = false;
        this.isTyping = false;
        this.recognition = null;
        this.isListening = false;

        this.initializeElements();
        this.bindEvents();
        this.initializeSpeechRecognition();
    }

    getApiBaseUrl() {
        const hostname = window.location.hostname;
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'http://localhost:8000';
        }
        // On Vercel, use relative path so it hits our serverless function
        return '';
    }

    initializeElements() {
        this.toggle = document.getElementById('ragChatbotToggle');
        this.widget = document.getElementById('ragChatbotWidget');
        this.closeBtn = document.getElementById('ragChatbotClose');
        this.messages = document.getElementById('ragChatbotMessages');
        this.inputField = document.getElementById('ragChatbotInputField');
        this.sendBtn = document.getElementById('ragChatbotSendBtn');
        this.voiceBtn = document.getElementById('ragChatbotVoiceBtn');
        this.typing = document.getElementById('ragChatbotTyping');
    }

    bindEvents() {
        this.toggle.addEventListener('click', () => this.toggleWidget());
        this.closeBtn.addEventListener('click', () => this.closeWidget());
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.voiceBtn.addEventListener('click', () => this.toggleVoiceInput());

        this.inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        this.inputField.addEventListener('input', () => {
            const hasText = this.inputField.value.trim().length > 0;
            this.sendBtn.classList.toggle('active', hasText);
        });
    }

    initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.inputField.value = transcript;
                this.sendBtn.classList.add('active');
                this.stopListening();
            };

            this.recognition.onerror = () => { this.stopListening(); };
            this.recognition.onend = () => { this.stopListening(); };
        } else {
            this.voiceBtn.style.display = 'none';
        }
    }

    toggleWidget() {
        if (this.isOpen) this.closeWidget(); else this.openWidget();
    }
    openWidget() { this.widget.classList.add('open'); this.isOpen = true; if (this.toggle) this.toggle.style.display = 'none'; this.inputField.focus(); }
    closeWidget() { this.widget.classList.remove('open'); this.isOpen = false; if (this.toggle) this.toggle.style.display = 'flex'; }

    toggleVoiceInput() {
        if (!this.recognition) return;
        if (this.isListening) this.stopListening(); else this.startListening();
    }
    startListening() {
        if (!this.recognition) return;
        this.isListening = true; this.voiceBtn.style.background = '#ff4444'; this.inputField.placeholder = 'Listening...'; this.recognition.start();
    }
    stopListening() {
        this.isListening = false; this.voiceBtn.style.background = ''; this.inputField.placeholder = 'Type your question ?'; if (this.recognition) this.recognition.stop();
    }

    async sendMessage() {
        const message = this.inputField.value.trim();
        if (!message || this.isTyping) return;
        this.addMessage(message, 'user');
        this.inputField.value = '';
        this.sendBtn.classList.remove('active');
        this.showTyping();
        try {
            const base = this.config.apiBaseUrl;
            const url = base ? `${base}/api/chat` : `/api/chat`;
            const resp = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: message })
            });
            const data = await resp.json();
            this.hideTyping();
            if (resp.ok) {
                const botText = (data && typeof data.response === 'string') ? data.response : '';
                const normalized = botText && botText.toLowerCase().includes('i do not have enough information')
                    ? "Sorry, I don’t have that information right now."
                    : botText;
                this.addMessage(normalized || "Sorry, I don’t have that information right now.", 'bot');
            } else {
                this.addMessage("Sorry, I don’t have that information right now.", 'bot');
            }
        } catch (e) {
            this.hideTyping();
            this.addMessage("Sorry, I don’t have that information right now.", 'bot');
            console.error(e);
        }
    }

    addMessage(text, sender) {
        const row = document.createElement('div');
        row.className = `rag-chatbot-message ${sender}`;
        const bubble = document.createElement('div');
        bubble.className = 'rag-chatbot-message-content';
        bubble.textContent = text;
        row.appendChild(bubble);
        this.messages.insertBefore(row, this.typing);
        this.scrollToBottom();
    }
    showTyping() { this.isTyping = true; this.typing.classList.add('show'); this.scrollToBottom(); }
    hideTyping() { this.isTyping = false; this.typing.classList.remove('show'); }
    scrollToBottom() { setTimeout(() => { this.messages.scrollTop = this.messages.scrollHeight; }, 80); }
}

document.addEventListener('DOMContentLoaded', () => {
    window.ragChatbot = new RAGChatbotWidget({ position: 'bottom-right' });
});



