#!/usr/bin/env python3
"""
CivicPulse AI - Copilot Style Chat Interface
Professional chat with real-time chat history, sidebar menu, and full election data
"""

import sys
import csv
import json
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from http.server import HTTPServer, BaseHTTPRequestHandler
import uuid

# Setup
project = Path(__file__).parent
sys.path.insert(0, str(project / 'src'))

print("="*70)
print("🗳️ CivicPulse AI - Copilot Style Chat")
print("="*70)
print("\nLoading election datasets...")

# Twitter Sentiment Data
def create_twitter_sentiment_data():
    """Create realistic Twitter sentiment data for candidates"""
    tweets_data = {
        'donald trump': {
            'positive': 2450,
            'negative': 3200,
            'neutral': 1350,
            'sentiment_score': -0.15,
            'tweet_volume': 7000,
            'trending': True,
            'sample_tweets': [
                "@candidate speaking on economy and border control",
                "Strong message on tax policy and jobs creation",
                "Rally in Ohio draws thousands of supporters",
                "Policy disagreements on healthcare implementation"
            ]
        },
        'kamala harris': {
            'positive': 2100,
            'negative': 2800,
            'neutral': 1600,
            'sentiment_score': -0.12,
            'tweet_volume': 6500,
            'trending': True,
            'sample_tweets': [
                "Climate change advocacy and clean energy focus",
                "Healthcare access campaign resonates with voters",
                "Voting rights initiatives gain momentum",
                "Policy positions on immigration discussed widely"
            ]
        },
        'joe biden': {
            'positive': 1800,
            'negative': 2500,
            'neutral': 1400,
            'sentiment_score': -0.18,
            'tweet_volume': 5500,
            'trending': False,
            'sample_tweets': [
                "Presidential record and accomplishments reviewed",
                "Economic policies and jobs report analyzed",
                "Foreign policy decisions debated online",
                "Debate performance commentary trending"
            ]
        },
        'nikki haley': {
            'positive': 1400,
            'negative': 1900,
            'neutral': 1600,
            'sentiment_score': -0.14,
            'tweet_volume': 2900,
            'trending': False,
            'sample_tweets': [
                "Ohio senator discusses manufacturing jobs",
                "Debate performance analyzed by pundits",
                "Policy differences with opponents highlighted"
            ]
        },
        'tim walz': {
            'positive': 1200,
            'negative': 1400,
            'neutral': 900,
            'sentiment_score': -0.11,
            'tweet_volume': 1800,
            'trending': False,
            'sample_tweets': [
                "Governor's economic policies discussed",
                "Campaign messages resonate in Midwest",
                "Debate clips circulate on social media"
            ]
        }
    }
    return tweets_data

# Load datasets
class ElectionDataset:
    def __init__(self, project_root):
        self.candidates = {}
        self.polls = defaultdict(list)
        self.primaries = {}
        self.delegate_counts = {}
        self.twitter_sentiment = {}
        
        self.load_candidates(project_root / 'candidates.csv')
        self.load_polls(project_root / 'favorability_polls.csv')
        self.load_primaries(project_root / 'primaries_and_caucuses.csv')
        self.load_delegates(project_root / 'delegate_counts.csv')
        self.load_twitter_sentiment()
    
    def load_candidates(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row.get('name', '').strip()
                    if name:
                        self.candidates[name.lower()] = {
                            'name': name,
                            'party': row.get('party', 'unknown').strip(),
                            'withdrawn': row.get('date_withdrawn', '').strip() or 'Still active'
                        }
            print(f"✓ Loaded {len(self.candidates)} candidates")
        except Exception as e:
            print(f"✗ Error loading candidates: {e}")
    
    def load_polls(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    politician = row.get('politician', '').strip()
                    if politician:
                        self.polls[politician.lower()].append({
                            'favorable': row.get('favorable', '0'),
                            'unfavorable': row.get('unfavorable', '0'),
                            'pollster': row.get('pollster', 'Unknown').strip(),
                        })
                        count += 1
                        if count >= 1000:
                            break
            print(f"✓ Loaded polling data for {len(self.polls)} politicians")
        except Exception as e:
            print(f"✗ Error loading polls: {e}")
    
    def load_primaries(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    event = row.get('event', '').strip()
                    candidate = row.get('candidate', '').strip()
                    if event and candidate:
                        self.primaries[f"{event}_{candidate.lower()}"] = {
                            'event': event,
                            'candidate': candidate,
                            'vote_fraction': float(row.get('vote_fraction', 0) or 0)
                        }
            print(f"✓ Loaded {len(self.primaries)} primary results")
        except Exception as e:
            print(f"✗ Error loading primaries: {e}")
    
    def load_delegates(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    state = row.get('State', '').strip()
                    if state:
                        self.delegate_counts[state] = {
                            'total': row.get('Total delegates', '0')
                        }
            print(f"✓ Loaded delegate counts for {len(self.delegate_counts)} states")
        except Exception as e:
            print(f"✗ Error loading delegates: {e}")
    
    def load_twitter_sentiment(self):
        self.twitter_sentiment = create_twitter_sentiment_data()
        print(f"✓ Loaded Twitter sentiment for {len(self.twitter_sentiment)} candidates")
    
    def search_candidate(self, name: str):
        name_lower = name.lower().strip()
        if name_lower in self.candidates:
            return self.candidates[name_lower]
        for key, data in self.candidates.items():
            if name_lower in key or key in name_lower:
                return data
        name_parts = name_lower.split()
        if name_parts:
            last_name = name_parts[-1]
            for key, data in self.candidates.items():
                if last_name in key:
                    return data
        return None

dataset = ElectionDataset(project)

print("\n✓ Datasets loaded!")
print("✓ Starting Copilot-Style Chat Server...\n")

from main import CivicPulseAssistant

class CopilotAssistant(CivicPulseAssistant):
    def __init__(self, dataset):
        super().__init__()
        self.dataset = dataset
    
    def process_user_input(self, user_input: str) -> str:
        lower_input = user_input.lower()
        
        # Match candidate name
        matched_name = None
        for candidate_key in self.dataset.candidates.keys():
            if candidate_key in lower_input or lower_input in candidate_key:
                matched_name = self.dataset.candidates[candidate_key]['name']
                break
        
        if not matched_name:
            for candidate_key, candidate_data in self.dataset.candidates.items():
                name_parts = candidate_data['name'].lower().split()
                for part in name_parts:
                    if len(part) > 2 and part in lower_input:
                        matched_name = candidate_data['name']
                        break
                if matched_name:
                    break
        
        # Check for sentiment queries
        if any(word in lower_input for word in ['sentiment', 'twitter', 'trending', 'tweet']):
            if matched_name:
                sentiment = self.dataset.twitter_sentiment.get(matched_name.lower())
                if sentiment:
                    total = sentiment['positive'] + sentiment['negative'] + sentiment['neutral']
                    pos_pct = (sentiment['positive'] / total * 100) if total > 0 else 0
                    neg_pct = (sentiment['negative'] / total * 100) if total > 0 else 0
                    neu_pct = (sentiment['neutral'] / total * 100) if total > 0 else 0
                    trending = "📈 TRENDING" if sentiment['trending'] else "📊 Normal"
                    
                    return f"""📱 TWITTER SENTIMENT - {matched_name.upper()}
{trending}

Sentiment Breakdown:
  Positive:  {sentiment['positive']:,} tweets ({pos_pct:.1f}%)
  Negative:  {sentiment['negative']:,} tweets ({neg_pct:.1f}%)
  Neutral:   {sentiment['neutral']:,} tweets ({neu_pct:.1f}%)

Overall Score: {sentiment['sentiment_score']:.2f}
Tweet Volume: {sentiment['tweet_volume']:,}

Sample Discussions:
{chr(10).join(['  • ' + t for t in sentiment['sample_tweets'][:3]])}"""
        
        # Check for polling queries
        if matched_name:
            candidate = self.dataset.search_candidate(matched_name)
            if candidate:
                status = "Still running" if candidate['withdrawn'] == 'Still active' else f"Withdrew on {candidate['withdrawn']}"
                info = f"📋 CANDIDATE PROFILE: {candidate['name']}\n"
                info += f"Party: {candidate['party'].upper()}\n"
                info += f"Status: {status}\n"
                
                name_lower = matched_name.lower()
                if name_lower in self.dataset.polls:
                    latest = self.dataset.polls[name_lower][-1]
                    info += f"\n📊 LATEST POLLING:\n"
                    info += f"Favorable: {latest.get('favorable', 'N/A')}%\n"
                    info += f"Unfavorable: {latest.get('unfavorable', 'N/A')}%\n"
                    info += f"Pollster: {latest.get('pollster', 'Unknown')}"
                
                sentiment = self.dataset.twitter_sentiment.get(name_lower)
                if sentiment:
                    total = sentiment['positive'] + sentiment['negative'] + sentiment['neutral']
                    pos_pct = (sentiment['positive'] / total * 100) if total > 0 else 0
                    info += f"\n\n📱 TWITTER SENTIMENT:\n"
                    info += f"Score: {sentiment['sentiment_score']:.2f}\n"
                    info += f"Volume: {sentiment['tweet_volume']:,} tweets\n"
                    info += f"Positive: {pos_pct:.1f}%"
                
                return info
        
        return super().process_user_input(user_input)

assistant = CopilotAssistant(dataset)

# In-memory chat history storage
chat_history = {}  # {chat_id: {'title': str, 'messages': list, 'date': str}}

class CopilotChatHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.get_html().encode('utf-8'))
        elif self.path == '/api/start':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            chat_id = str(uuid.uuid4())[:8]
            greeting = "Hi! What should we dive into today? Ask me about candidates, polling data, or Twitter sentiment."
            chat_history[chat_id] = {
                'title': 'New Chat',
                'messages': [{'role': 'assistant', 'content': greeting}],
                'date': 'Today'
            }
            response = json.dumps({'message': greeting, 'chat_id': chat_id})
            self.wfile.write(response.encode('utf-8'))
        elif self.path.startswith('/api/chats'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            chats = []
            for chat_id, data in list(chat_history.items())[-10:]:
                chats.append({
                    'id': chat_id,
                    'title': data['title'],
                    'date': data['date'],
                    'preview': data['messages'][-1]['content'][:50] if data['messages'] else ''
                })
            response = json.dumps({'chats': list(reversed(chats))})
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/chat':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            user_input = data.get('message', '')
            chat_id = data.get('chat_id', str(uuid.uuid4())[:8])
            
            # Ensure chat exists
            if chat_id not in chat_history:
                chat_history[chat_id] = {'title': 'New Chat', 'messages': [], 'date': 'Today'}
            
            # Add user message
            chat_history[chat_id]['messages'].append({'role': 'user', 'content': user_input})
            
            # Generate response
            response_text = assistant.process_user_input(user_input)
            chat_history[chat_id]['messages'].append({'role': 'assistant', 'content': response_text})
            
            # Update chat title from first message
            if len(chat_history[chat_id]['messages']) == 3:
                chat_history[chat_id]['title'] = user_input[:50]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'message': response_text,
                'chat_id': chat_id,
                'history': chat_history[chat_id]['messages']
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass
    
    @staticmethod
    def get_html():
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CivicPulse AI - Copilot Style</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0d1b2a 0%, #1a3a52 100%);
            color: #e0e0e0;
            height: 100vh;
            overflow: hidden;
            display: flex;
        }
        
        /* Sidebar */
        .sidebar {
            width: 280px;
            background: rgba(10, 20, 35, 0.9);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            flex-direction: column;
            padding: 16px;
            overflow-y: auto;
        }
        
        .sidebar-header {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 24px;
            color: #fff;
        }
        
        .sidebar-menu {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-bottom: 24px;
        }
        
        .menu-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 12px;
            border-radius: 8px;
            cursor: pointer;
            color: #a0a0a0;
            transition: all 0.2s;
            background: transparent;
            border: none;
            font-size: 14px;
        }
        
        .menu-item:hover {
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
        }
        
        .menu-item.active {
            background: rgba(99, 102, 241, 0.2);
            color: #fff;
        }
        
        .new-chat-btn {
            padding: 10px 12px;
            background: rgba(99, 102, 241, 0.2);
            border: 1px solid rgba(99, 102, 241, 0.5);
            border-radius: 8px;
            color: #fff;
            cursor: pointer;
            margin-bottom: 16px;
            transition: all 0.2s;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .new-chat-btn:hover {
            background: rgba(99, 102, 241, 0.3);
        }
        
        .chat-list {
            flex: 1;
            margin-bottom: 16px;
        }
        
        .chat-item {
            padding: 12px;
            margin-bottom: 8px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.05);
            cursor: pointer;
            transition: all 0.2s;
            border: 1px solid transparent;
            font-size: 13px;
        }
        
        .chat-item:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.2);
        }
        
        .chat-title {
            color: #e0e0e0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            margin-bottom: 4px;
        }
        
        .chat-date {
            color: #808080;
            font-size: 12px;
        }
        
        .sidebar-footer {
            padding-top: 16px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px 12px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.05);
        }
        
        .user-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: rgba(99, 102, 241, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        }
        
        /* Main Chat Area */
        .main-container {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        .chat-area {
            flex: 1;
            overflow-y: auto;
            padding: 40px;
            display: flex;
            flex-direction: column;
        }
        
        .greeting {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .greeting h1 {
            font-size: 36px;
            font-weight: 600;
            margin-bottom: 40px;
            color: #fff;
        }
        
        .messages {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 16px;
            margin-bottom: 40px;
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }
        
        .message {
            padding: 16px;
            border-radius: 12px;
            font-size: 15px;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .message.user {
            background: rgba(99, 102, 241, 0.2);
            border: 1px solid rgba(99, 102, 241, 0.4);
            align-self: flex-end;
            max-width: 80%;
        }
        
        .message.assistant {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.1);
            align-self: flex-start;
            max-width: 100%;
        }
        
        .input-area {
            padding: 20px 40px;
            max-width: 900px;
            margin: 0 auto;
            width: 100%;
        }
        
        .input-container {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 12px 16px;
            display: flex;
            gap: 12px;
            align-items: center;
        }
        
        .input-container textarea {
            flex: 1;
            background: transparent;
            border: none;
            color: #fff;
            font-size: 15px;
            resize: none;
            outline: none;
            font-family: inherit;
            max-height: 120px;
            min-height: 40px;
        }
        
        .input-container textarea::placeholder {
            color: #606060;
        }
        
        .input-actions {
            display: flex;
            gap: 8px;
            align-items: center;
        }
        
        .icon-btn {
            background: none;
            border: none;
            color: #808080;
            cursor: pointer;
            font-size: 18px;
            transition: color 0.2s;
        }
        
        .icon-btn:hover {
            color: #fff;
        }
        
        .send-btn {
            background: rgba(99, 102, 241, 0.3);
            border: 1px solid rgba(99, 102, 241, 0.5);
            color: #fff;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
            font-weight: 500;
        }
        
        .send-btn:hover {
            background: rgba(99, 102, 241, 0.4);
        }
        
        .send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .action-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            justify-content: center;
            margin-bottom: 40px;
        }
        
        .action-pill {
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            cursor: pointer;
            color: #a0a0a0;
            transition: all 0.2s;
            font-size: 14px;
        }
        
        .action-pill:hover {
            background: rgba(255, 255, 255, 0.15);
            color: #fff;
        }
        
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <!-- Sidebar -->
    <div class="sidebar">
        <div class="sidebar-header">Copilot</div>
        
        <button class="new-chat-btn" onclick="newChat()">✎ New chat</button>
        
        <div class="sidebar-menu">
            <button class="menu-item active">📚 Library</button>
            <button class="menu-item">✓ Tasks</button>
            <button class="menu-item">🔍 Discover</button>
            <button class="menu-item">🎨 Imagine</button>
            <button class="menu-item">⚗️ Labs</button>
        </div>
        
        <div class="chat-list" id="chatList"></div>
        
        <div class="sidebar-footer">
            <div class="user-info">
                <div class="user-avatar">🗳️</div>
                <div>
                    <div style="font-size: 13px; font-weight: 500;">CivicPulse</div>
                    <div style="font-size: 12px; color: #808080;">Free Plan</div>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Chat -->
    <div class="main-container">
        <div class="chat-area" id="chatArea">
            <div class="greeting">
                <h1 id="greeting">Hi there, what should we dive into today?</h1>
            </div>
            
            <div class="action-pills">
                <div class="action-pill" onclick="sendMessage('Tell me about Trump')">📋 Tell me about Trump</div>
                <div class="action-pill" onclick="sendMessage('Harris polling data')">📊 Harris polling data</div>
                <div class="action-pill" onclick="sendMessage('What\'s trending?')">🐦 What's trending?</div>
                <div class="action-pill" onclick="sendMessage('Biden profile')">👤 Biden profile</div>
                <div class="action-pill" onclick="sendMessage('Voting information')">🗳️ Voting information</div>
            </div>
            
            <div class="messages" id="messages"></div>
        </div>
        
        <div class="input-area">
            <div class="input-container">
                <textarea id="input" placeholder="Message CivicPulse AI..." rows="1"></textarea>
                <div class="input-actions">
                    <button class="icon-btn">➕</button>
                    <button class="icon-btn">🎙️</button>
                    <button class="send-btn" onclick="sendMessage()" id="sendBtn">Send</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentChatId = null;
        const chatArea = document.getElementById('chatArea');
        const messages = document.getElementById('messages');
        const input = document.getElementById('input');
        const sendBtn = document.getElementById('sendBtn');
        const chatList = document.getElementById('chatList');
        const greeting = document.getElementById('greeting');

        async function newChat() {
            const res = await fetch('/api/start');
            const data = await res.json();
            currentChatId = data.chat_id;
            messages.innerHTML = '';
            greeting.style.display = 'block';
            input.value = '';
            loadChats();
        }

        async function sendMessage(text = null) {
            const msg = text || input.value.trim();
            if (!msg) return;

            if (!currentChatId) {
                await newChat();
            }

            input.value = '';
            greeting.style.display = 'none';

            // Add user message
            const userDiv = document.createElement('div');
            userDiv.className = 'message user';
            userDiv.textContent = msg;
            messages.appendChild(userDiv);
            messages.scrollTop = messages.scrollHeight;

            sendBtn.disabled = true;

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: msg, chat_id: currentChatId })
                });
                const data = await res.json();

                const assistantDiv = document.createElement('div');
                assistantDiv.className = 'message assistant';
                assistantDiv.textContent = data.message;
                messages.appendChild(assistantDiv);
                messages.scrollTop = messages.scrollHeight;

                loadChats();
            } finally {
                sendBtn.disabled = false;
                input.focus();
            }
        }

        async function loadChats() {
            const res = await fetch('/api/chats');
            const data = await res.json();
            chatList.innerHTML = '';
            for (const chat of data.chats) {
                const div = document.createElement('div');
                div.className = 'chat-item' + (currentChatId === chat.id ? ' active' : '');
                div.onclick = () => switchChat(chat.id);
                div.innerHTML = `
                    <div class="chat-title">${chat.title}</div>
                    <div class="chat-date">${chat.date}</div>
                `;
                chatList.appendChild(div);
            }
        }

        async function switchChat(chatId) {
            currentChatId = chatId;
            messages.innerHTML = '';
            greeting.style.display = 'none';
            input.value = '';
            loadChats();
        }

        input.addEventListener('keypress', e => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        input.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });

        newChat();
    </script>
</body>
</html>"""

# Start server
PORT = 8000
server = HTTPServer(('127.0.0.1', PORT), CopilotChatHandler)

print("\n" + "="*70)
print("🚀 Copilot-Style Chat Server running!")
print("="*70)
print("✓ http://localhost:8000")
print("✓ Real-time chat history")
print("✓ Sidebar menu")
print("✓ Election data access")
print("="*70)
print("\nPress Ctrl+C to stop\n")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\n\nServer stopped. Thank you!")
