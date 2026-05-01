#!/usr/bin/env python3
"""
CivicPulse - Localhost Election Assistant
Interactive web-based interface running on localhost
"""

import os
import sys
from pathlib import Path
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

# Import assistant
try:
    from main import CivicPulseAssistant
except ImportError:
    print("⚠️  Creating source files first...")
    # Files will be created by run_localhost.py
    sys.exit(1)

# Global assistant instance
assistant = CivicPulseAssistant()

class CivicPulseHandler(BaseHTTPRequestHandler):
    """HTTP request handler for CivicPulse web interface."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = self.get_html()
            self.wfile.write(html.encode())
        elif self.path == '/api/start':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            assistant.reset()
            greeting = assistant.start_conversation()
            response = json.dumps({'message': greeting, 'state': assistant.current_state.value})
            self.wfile.write(response.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/api/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()
            data = json.loads(post_data)
            user_input = data.get('message', '')
            
            response_text = assistant.process_user_input(user_input)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'message': response_text,
                'state': assistant.current_state.value,
                'user_profile': assistant.user_profile
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass
    
    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/api/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()
            data = json.loads(post_data)
            user_input = data.get('message', '')
            
            response_text = assistant.process_user_input(user_input)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'message': response_text,
                'state': assistant.current_state.value,
                'user_profile': assistant.user_profile
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/api/history':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            history = getattr(self.server, 'chat_history', [])
            self.wfile.write(json.dumps(history).encode())
        elif self.path == '/api/new-chat':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            if not hasattr(self.server, 'chat_history'):
                self.server.chat_history = []
            if not hasattr(self.server, 'current_chat'):
                self.server.current_chat = []
            self.server.chat_history.append({'title': 'New Chat', 'messages': []})
            self.wfile.write(json.dumps({'status': 'ok'}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    @staticmethod
    def get_html():
        """Return the HTML interface with Copilot-style UI."""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CivicPulse 🗳️ - Election Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto Mono', sans-serif;
            background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0d1625 100%);
            color: #c9d1d9;
            height: 100vh;
            overflow: hidden;
        }
        
        .app-container {
            display: flex;
            height: 100vh;
        }
        
        /* SIDEBAR */
        .sidebar {
            width: 260px;
            background: #161b22;
            border-right: 1px solid #30363d;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
        }
        
        .sidebar-header {
            padding: 16px;
            border-bottom: 1px solid #30363d;
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
            font-size: 16px;
        }
        
        .sidebar-logo {
            font-size: 20px;
        }
        
        .new-chat-btn {
            margin: 12px;
            padding: 10px 16px;
            background: #238636;
            border: 1px solid #2ea043;
            color: white;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
            justify-content: center;
        }
        
        .new-chat-btn:hover {
            background: #2ea043;
        }
        
        .sidebar-section {
            padding: 12px 0;
            border-bottom: 1px solid #30363d;
        }
        
        .sidebar-section-title {
            padding: 8px 16px;
            font-size: 12px;
            font-weight: 600;
            color: #8b949e;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .sidebar-item {
            padding: 10px 16px;
            color: #c9d1d9;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            border-left: 2px solid transparent;
        }
        
        .sidebar-item:hover {
            background: #21262d;
            color: #f0f6fc;
        }
        
        .sidebar-item.active {
            background: #0d419f;
            border-left-color: #58a6ff;
            color: #58a6ff;
        }
        
        .sidebar-icon {
            width: 16px;
            height: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .chat-history {
            flex: 1;
            overflow-y: auto;
            padding: 8px 0;
        }
        
        .history-item {
            padding: 8px 16px;
            color: #c9d1d9;
            font-size: 12px;
            cursor: pointer;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            transition: all 0.2s;
        }
        
        .history-item:hover {
            background: #21262d;
            color: #f0f6fc;
        }
        
        .sidebar-footer {
            padding: 12px;
            border-top: 1px solid #30363d;
            font-size: 12px;
        }
        
        .user-profile {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px;
            background: #21262d;
            border-radius: 6px;
            cursor: pointer;
        }
        
        .avatar {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea, #764ba2);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 11px;
        }
        
        /* MAIN CONTENT */
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #0d1117;
        }
        
        .chat-header {
            padding: 12px 24px;
            border-bottom: 1px solid #30363d;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .chat-title {
            font-size: 14px;
            font-weight: 600;
        }
        
        .header-actions {
            display: flex;
            gap: 8px;
        }
        
        .icon-btn {
            width: 32px;
            height: 32px;
            border: 1px solid #30363d;
            background: #0d1117;
            color: #c9d1d9;
            border-radius: 6px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }
        
        .icon-btn:hover {
            background: #21262d;
            border-color: #58a6ff;
            color: #58a6ff;
        }
        
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        
        .welcome-section {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            text-align: center;
            gap: 24px;
        }
        
        .welcome-title {
            font-size: 32px;
            font-weight: 600;
            color: #f0f6fc;
        }
        
        .welcome-subtitle {
            font-size: 16px;
            color: #8b949e;
        }
        
        .quick-actions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 12px;
            max-width: 600px;
            margin-top: 24px;
        }
        
        .action-btn {
            padding: 12px 16px;
            background: #21262d;
            border: 1px solid #30363d;
            color: #c9d1d9;
            border-radius: 8px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s;
        }
        
        .action-btn:hover {
            background: #30363d;
            border-color: #58a6ff;
            color: #58a6ff;
        }
        
        .message {
            display: flex;
            gap: 12px;
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .message.user {
            flex-direction: row-reverse;
            justify-content: flex-start;
        }
        
        .message.assistant {
            flex-direction: row;
        }
        
        .message-avatar {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 12px;
        }
        
        .message.user .message-avatar {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        
        .message.assistant .message-avatar {
            background: #21262d;
            color: #58a6ff;
            border: 1px solid #30363d;
        }
        
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 8px;
            line-height: 1.4;
            word-wrap: break-word;
            font-size: 14px;
        }
        
        .message.user .message-content {
            background: #238636;
            color: white;
            margin-left: 8px;
        }
        
        .message.assistant .message-content {
            background: #21262d;
            border: 1px solid #30363d;
            color: #c9d1d9;
        }
        
        /* INPUT AREA */
        .input-area {
            padding: 16px 24px;
            border-top: 1px solid #30363d;
            display: flex;
            gap: 12px;
        }
        
        .input-wrapper {
            flex: 1;
            display: flex;
            align-items: flex-end;
            gap: 8px;
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 8px;
            transition: border-color 0.2s;
        }
        
        .input-wrapper:focus-within {
            border-color: #58a6ff;
        }
        
        .input-wrapper input {
            flex: 1;
            background: transparent;
            border: none;
            color: #c9d1d9;
            padding: 8px;
            font-size: 14px;
            outline: none;
        }
        
        .input-wrapper input::placeholder {
            color: #6e7681;
        }
        
        .input-actions {
            display: flex;
            gap: 4px;
        }
        
        .input-action-btn {
            width: 28px;
            height: 28px;
            border: none;
            background: transparent;
            color: #6e7681;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 4px;
            transition: all 0.2s;
        }
        
        .input-action-btn:hover {
            background: #21262d;
            color: #58a6ff;
        }
        
        .send-btn {
            width: 36px;
            height: 36px;
            border: 1px solid #30363d;
            background: #238636;
            color: white;
            border-radius: 6px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
            font-weight: 500;
        }
        
        .send-btn:hover {
            background: #2ea043;
            border-color: #2ea043;
        }
        
        .send-btn:active {
            transform: scale(0.95);
        }
        
        .send-btn:disabled {
            background: #1f6feb;
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        /* SCROLLBAR */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #30363d;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #484f58;
        }
    </style>
</head>
<body>
    <div class="app-container">
        <!-- SIDEBAR -->
        <div class="sidebar">
            <div class="sidebar-header">
                <div class="sidebar-logo">🗳️</div>
                <div>CivicPulse</div>
            </div>
            
            <button class="new-chat-btn" onclick="newChat()">
                <span>+ New Chat</span>
            </button>
            
            <div class="sidebar-section">
                <div class="sidebar-section-title">Navigation</div>
                <div class="sidebar-item active" onclick="selectNav('chat')">
                    <div class="sidebar-icon">💬</div>
                    <span>Chat</span>
                </div>
                <div class="sidebar-item" onclick="selectNav('library')">
                    <div class="sidebar-icon">📚</div>
                    <span>Resources</span>
                </div>
                <div class="sidebar-item" onclick="selectNav('guides')">
                    <div class="sidebar-icon">📖</div>
                    <span>Guides</span>
                </div>
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-section-title">Chat History</div>
                <div class="chat-history" id="chatHistory">
                    <!-- Chat history will be loaded here -->
                </div>
            </div>
            
            <div class="sidebar-footer">
                <div class="user-profile">
                    <div class="avatar">CP</div>
                    <div>
                        <div style="font-weight: 500;">User</div>
                        <div style="color: #6e7681; font-size: 11px;">Free Plan</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- MAIN CONTENT -->
        <div class="main-content">
            <div class="chat-header">
                <div class="chat-title" id="chatTitle">Election Assistant</div>
                <div class="header-actions">
                    <button class="icon-btn" title="Settings">⚙️</button>
                    <button class="icon-btn" title="Info">ℹ️</button>
                </div>
            </div>
            
            <div class="chat-container" id="chatContainer">
                <div class="welcome-section">
                    <div class="welcome-title">Hi, what should we dive into today?</div>
                    <div class="welcome-subtitle">Your election preparation assistant</div>
                    <div class="quick-actions">
                        <button class="action-btn" onclick="quickAction('election')">📋 Election Info</button>
                        <button class="action-btn" onclick="quickAction('register')">✅ Register to Vote</button>
                        <button class="action-btn" onclick="quickAction('polling')">📍 Polling Location</button>
                        <button class="action-btn" onclick="quickAction('candidates')">👥 Candidates</button>
                        <button class="action-btn" onclick="quickAction('prepare')">🎯 Prepare</button>
                        <button class="action-btn" onclick="quickAction('guides')">📚 Guides</button>
                    </div>
                </div>
            </div>
            
            <div class="input-area">
                <div class="input-wrapper">
                    <button class="input-action-btn" title="Attach file">📎</button>
                    <input 
                        type="text" 
                        id="messageInput" 
                        placeholder="Message CivicPulse..."
                        onkeypress="handleKeyPress(event)"
                    >
                    <button class="input-action-btn" title="Voice">🎤</button>
                </div>
                <button class="send-btn" id="sendBtn" onclick="sendMessage()">⬆️</button>
            </div>
        </div>
    </div>

    <script>
        let currentChatId = null;
        let currentMessages = [];
        const chatContainer = document.getElementById('chatContainer');
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const chatHistory = document.getElementById('chatHistory');
        
        // Initialize
        loadChatHistory();
        
        function newChat() {
            currentChatId = Date.now();
            currentMessages = [];
            chatContainer.innerHTML = `
                <div class="welcome-section">
                    <div class="welcome-title">Hi, what should we dive into today?</div>
                    <div class="welcome-subtitle">Your election preparation assistant</div>
                    <div class="quick-actions">
                        <button class="action-btn" onclick="quickAction('election')">📋 Election Info</button>
                        <button class="action-btn" onclick="quickAction('register')">✅ Register to Vote</button>
                        <button class="action-btn" onclick="quickAction('polling')">📍 Polling Location</button>
                        <button class="action-btn" onclick="quickAction('candidates')">👥 Candidates</button>
                        <button class="action-btn" onclick="quickAction('prepare')">🎯 Prepare</button>
                        <button class="action-btn" onclick="quickAction('guides')">📚 Guides</button>
                    </div>
                </div>
            `;
            messageInput.focus();
        }
        
        function quickAction(action) {
            const messages = {
                'election': 'Tell me about the upcoming elections',
                'register': 'How do I register to vote?',
                'polling': 'Where is my polling location?',
                'candidates': 'Who are the candidates running?',
                'prepare': 'How should I prepare for voting?',
                'guides': 'Show me voting guides'
            };
            messageInput.value = messages[action] || '';
            messageInput.focus();
            setTimeout(() => sendMessage(), 100);
        }
        
        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;
            
            // Clear welcome section if first message
            if (currentMessages.length === 0) {
                chatContainer.innerHTML = '';
            }
            
            // Display user message
            displayMessage(message, 'user');
            currentMessages.push({role: 'user', content: message});
            messageInput.value = '';
            messageInput.focus();
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                displayMessage(data.message, 'assistant');
                currentMessages.push({role: 'assistant', content: data.message});
                
                // Add to history
                saveChatToHistory();
                
                chatContainer.scrollTop = chatContainer.scrollHeight;
            } catch (error) {
                console.error('Error:', error);
                displayMessage('Sorry, I encountered an error. Please try again.', 'assistant');
            }
        }
        
        function displayMessage(text, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            const avatar = document.createElement('div');
            avatar.className = 'message-avatar';
            avatar.textContent = sender === 'user' ? 'You' : '🤖';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = text;
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(contentDiv);
            chatContainer.appendChild(messageDiv);
            
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        function saveChatToHistory() {
            const title = currentMessages[0]?.content?.substring(0, 30) + '...' || 'Chat';
            const historyItem = {
                id: currentChatId,
                title: title,
                date: new Date().toLocaleDateString(),
                messages: currentMessages
            };
            // Store in localStorage
            let history = JSON.parse(localStorage.getItem('chatHistory') || '[]');
            history.unshift(historyItem);
            localStorage.setItem('chatHistory', JSON.stringify(history.slice(0, 20)));
            loadChatHistory();
        }
        
        function loadChatHistory() {
            const history = JSON.parse(localStorage.getItem('chatHistory') || '[]');
            chatHistory.innerHTML = history.map(chat => `
                <div class="history-item" onclick="loadChat(${chat.id})" title="${chat.title}">
                    ${chat.title}
                    <div style="font-size: 11px; color: #6e7681;">
                        ${chat.date}
                    </div>
                </div>
            `).join('');
        }
        
        function loadChat(id) {
            const history = JSON.parse(localStorage.getItem('chatHistory') || '[]');
            const chat = history.find(c => c.id === id);
            if (chat) {
                currentChatId = id;
                currentMessages = chat.messages;
                chatContainer.innerHTML = '';
                chat.messages.forEach(msg => {
                    displayMessage(msg.content, msg.role);
                });
            }
        }
        
        function selectNav(nav) {
            document.querySelectorAll('.sidebar-item').forEach(item => {
                item.classList.remove('active');
            });
            event.target.closest('.sidebar-item').classList.add('active');
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }
        
        messageInput.focus();
    </script>
</body>
</html>'''

def start_server(port=8000):
    """Start the CivicPulse localhost server."""
    server_address = ('localhost', port)
    httpd = HTTPServer(server_address, CivicPulseHandler)
    
    print("\n" + "="*60)
    print("🗳️  CivicPulse - Election Assistant Running")
    print("="*60)
    print(f"\n✅ Server running on: http://localhost:{port}")
    print(f"📱 Open your browser and navigate to: http://localhost:{port}")
    print(f"\n🎯 Features:")
    print("   • Interactive election assistant")
    print("   • Voter education & registration guidance")
    print("   • Polling location finder")
    print("   • Calendar reminder setup")
    print("   • Accessibility support")
    print(f"\n⌨️  Press Ctrl+C to stop the server\n")
    print("="*60 + "\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped. Thank you for using CivicPulse! 🗳️")
        sys.exit(0)

if __name__ == '__main__':
    start_server(port=8000)
