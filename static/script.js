// Travel Weather Planner - Frontend JavaScript

class ChatApp {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.messageInput = document.getElementById('messageInput');
        this.chatMessages = document.getElementById('chatMessages');
        this.chatForm = document.getElementById('chatForm');
        this.sendButton = document.getElementById('sendButton');
        this.toolStatus = document.getElementById('toolStatus');
        this.toolStatusText = document.getElementById('toolStatusText');
        
        this.currentAssistantMessage = null;
        
        this.init();
    }
    
    init() {
        // Connect to WebSocket
        this.connectWebSocket();
        
        // Setup event listeners
        this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => this.autoResize());
        
        // Example buttons
        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const prompt = e.target.getAttribute('data-prompt');
                this.messageInput.value = prompt;
                this.messageInput.focus();
                this.autoResize();
            });
        });
        
        // Enter to send (Shift+Enter for new line)
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.chatForm.dispatchEvent(new Event('submit'));
            }
        });
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.isConnected = true;
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.addSystemMessage('Connection error. Please refresh the page.');
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.isConnected = false;
            this.addSystemMessage('Disconnected. Reconnecting...');
            
            // Attempt to reconnect after 3 seconds
            setTimeout(() => this.connectWebSocket(), 3000);
        };
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'user_message':
                // Echo handled by frontend
                break;
                
            case 'tool_call':
                this.showToolCall(data.function, data.arguments);
                break;
                
            case 'tool_result':
                this.showToolResult(data.function, data.result);
                break;
                
            case 'assistant_stream':
                this.streamAssistantMessage(data.content);
                break;
                
            case 'assistant_complete':
                this.completeAssistantMessage();
                break;
                
            case 'error':
                this.addSystemMessage(`Error: ${data.content}`);
                this.hideToolStatus();
                this.enableInput();
                break;
        }
    }
    
    handleSubmit(e) {
        e.preventDefault();
        
        const message = this.messageInput.value.trim();
        if (!message || !this.isConnected) return;
        
        // Add user message to UI
        this.addUserMessage(message);
        
        // Clear input
        this.messageInput.value = '';
        this.autoResize();
        
        // Disable input while processing
        this.disableInput();
        
        // Send to server
        this.ws.send(JSON.stringify({ message }));
        
        // Show typing indicator
        this.showToolStatus('Thinking...');
    }
    
    addUserMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `
            <div class="message-avatar">👤</div>
            <div class="message-content">
                <p>${this.escapeHtml(text)}</p>
            </div>
        `;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    startAssistantMessage() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant-message';
        messageDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <p class="assistant-text"></p>
            </div>
        `;
        this.chatMessages.appendChild(messageDiv);
        this.currentAssistantMessage = messageDiv.querySelector('.assistant-text');
        this.scrollToBottom();
        return messageDiv;
    }
    
    streamAssistantMessage(content) {
        if (!this.currentAssistantMessage) {
            this.startAssistantMessage();
        }
        
        this.currentAssistantMessage.textContent += content;
        this.scrollToBottom();
    }
    
    completeAssistantMessage() {
        // Format the message
        if (this.currentAssistantMessage) {
            const text = this.currentAssistantMessage.textContent;
            this.currentAssistantMessage.innerHTML = this.formatMessage(text);
        }
        
        this.currentAssistantMessage = null;
        this.hideToolStatus();
        this.enableInput();
        this.scrollToBottom();
    }
    
    showToolCall(functionName, args) {
        this.showToolStatus(`🔧 Calling: ${this.formatFunctionName(functionName)}`);
    }
    
    showToolResult(functionName, result) {
        // Optionally show brief result in chat
        const resultSummary = this.getResultSummary(functionName, result);
        if (resultSummary) {
            const toolCallDiv = document.createElement('div');
            toolCallDiv.className = 'tool-call';
            toolCallDiv.innerHTML = `
                <span class="tool-call-icon">✓</span>
                ${resultSummary}
            `;
            
            // Add to last assistant message or create new one
            const lastMessage = this.chatMessages.querySelector('.message:last-child .message-content');
            if (lastMessage) {
                lastMessage.appendChild(toolCallDiv);
            }
        }
        
        this.showToolStatus(`✓ ${this.formatFunctionName(functionName)} complete`);
    }
    
    getResultSummary(functionName, result) {
        switch (functionName) {
            case 'get_current_date':
                return `Today: ${result.formatted}`;
            case 'calculate_travel_dates':
                return `Travel dates: ${result.start_date} to ${result.end_date}`;
            case 'get_city_coordinates':
                return `Found: ${result.city}`;
            case 'get_historical_weather':
                return `Weather data retrieved`;
            default:
                return null;
        }
    }
    
    formatFunctionName(name) {
        return name
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    }
    
    formatMessage(text) {
        // Simple markdown-like formatting
        let formatted = this.escapeHtml(text);
        
        // Bold: **text** or __text__
        formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        formatted = formatted.replace(/__(.+?)__/g, '<strong>$1</strong>');
        
        // Italic: *text* or _text_
        formatted = formatted.replace(/\*(.+?)\*/g, '<em>$1</em>');
        formatted = formatted.replace(/_(.+?)_/g, '<em>$1</em>');
        
        // Line breaks
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Lists (simple detection)
        formatted = formatted.replace(/^- (.+)$/gm, '<li>$1</li>');
        if (formatted.includes('<li>')) {
            formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        }
        
        return formatted;
    }
    
    addSystemMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant-message';
        messageDiv.innerHTML = `
            <div class="message-avatar">ℹ️</div>
            <div class="message-content">
                <p>${this.escapeHtml(text)}</p>
            </div>
        `;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    showToolStatus(text) {
        this.toolStatusText.textContent = text;
        this.toolStatus.style.display = 'block';
    }
    
    hideToolStatus() {
        this.toolStatus.style.display = 'none';
    }
    
    disableInput() {
        this.messageInput.disabled = true;
        this.sendButton.disabled = true;
    }
    
    enableInput() {
        this.messageInput.disabled = false;
        this.sendButton.disabled = false;
        this.messageInput.focus();
    }
    
    autoResize() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 150) + 'px';
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.chatApp = new ChatApp();
});
