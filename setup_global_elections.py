#!/usr/bin/env python3
"""
CivicPulse AI - Global Elections Edition
Copilot-style chat with US Election + India Election data
Real-time chat history, sidebar menu, and complete datasets
"""

import sys
import csv
import json
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List
from http.server import HTTPServer, BaseHTTPRequestHandler
import uuid

# Setup
project = Path(__file__).parent
sys.path.insert(0, str(project / 'src'))

print("="*70)
print("🗳️ CivicPulse AI - Global Elections Edition")
print("="*70)
print("\nLoading datasets...")

# Create Twitter Sentiment Data for US
def create_us_twitter_sentiment():
    return {
        'donald trump': {
            'positive': 2450, 'negative': 3200, 'neutral': 1350,
            'sentiment_score': -0.15, 'tweet_volume': 7000, 'trending': True,
            'sample_tweets': [
                "Speaking on economy and border control",
                "Tax policy and jobs creation message",
                "Rally in Ohio draws large support"
            ]
        },
        'kamala harris': {
            'positive': 2100, 'negative': 2800, 'neutral': 1600,
            'sentiment_score': -0.12, 'tweet_volume': 6500, 'trending': True,
            'sample_tweets': [
                "Climate change and clean energy focus",
                "Healthcare access campaign",
                "Voting rights initiatives"
            ]
        },
        'joe biden': {
            'positive': 1800, 'negative': 2500, 'neutral': 1400,
            'sentiment_score': -0.18, 'tweet_volume': 5500, 'trending': False,
            'sample_tweets': [
                "Presidential record and accomplishments",
                "Economic policies and jobs report",
                "Foreign policy decisions"
            ]
        },
        'nikki haley': {
            'positive': 1400, 'negative': 1900, 'neutral': 1600,
            'sentiment_score': -0.14, 'tweet_volume': 2900, 'trending': False,
            'sample_tweets': [
                "Manufacturing jobs discussion",
                "Debate performance analysis",
                "Policy differences with opponents"
            ]
        },
    }

# Load US Election Data
class USElectionDataset:
    def __init__(self, project_root):
        self.candidates = {}
        self.polls = defaultdict(list)
        self.twitter_sentiment = create_us_twitter_sentiment()
        
        self.load_candidates(project_root / 'candidates.csv')
        self.load_polls(project_root / 'favorability_polls.csv')
    
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
                        }
            print(f"✓ Loaded {len(self.candidates)} US candidates")
        except Exception as e:
            print(f"✗ Error loading US candidates: {e}")
    
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
                            'pollster': row.get('pollster', 'Unknown'),
                        })
                        count += 1
                        if count >= 500:
                            break
            print(f"✓ Loaded polling data for {len(self.polls)} US politicians")
        except Exception as e:
            print(f"✗ Error loading US polls: {e}")

# Load India Election Data
class IndiaElectionDataset:
    def __init__(self, project_root):
        self.candidates = defaultdict(list)
        self.parties = defaultdict(lambda: {'votes': 0, 'seats': 0, 'candidates': []})
        self.states = defaultdict(lambda: {'total_votes': 0, 'candidates': []})
        
        self.load_india_data(project_root / 'india' / 'eci_data_2024.csv')
    
    def load_india_data(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    candidate = row.get('Candidate', '').strip()
                    if candidate and candidate != 'NOTA':
                        party = row.get('Party', 'Independent').strip()
                        state = row.get('State', 'Unknown').strip()
                        constituency = row.get('Constituency', '').strip()
                        total_votes = int(row.get('Total Votes', 0) or 0)
                        vote_pct = float(row.get('% of Votes', 0) or 0)
                        
                        candidate_key = candidate.lower()
                        self.candidates[candidate_key].append({
                            'name': candidate,
                            'party': party,
                            'state': state,
                            'constituency': constituency,
                            'votes': total_votes,
                            'vote_percentage': vote_pct
                        })
                        
                        self.parties[party]['votes'] += total_votes
                        self.parties[party]['candidates'].append(candidate)
                        
                        self.states[state]['total_votes'] += total_votes
                        self.states[state]['candidates'].append(candidate)
            
            print(f"✓ Loaded {len(self.candidates)} India candidates")
            print(f"✓ Loaded {len(self.parties)} India parties")
            print(f"✓ Loaded {len(self.states)} India states")
        except Exception as e:
            print(f"✗ Error loading India data: {e}")
    
    def search_candidate(self, name: str):
        name_lower = name.lower().strip()
        
        if name_lower in self.candidates:
            return self.candidates[name_lower]
        
        for key, data in self.candidates.items():
            if name_lower in key or key in name_lower:
                return data
        
        return None
    
    def search_party(self, name: str):
        name_lower = name.lower().strip()
        
        for party, data in self.parties.items():
            if name_lower in party.lower():
                return {'party': party, 'votes': data['votes'], 'candidates_count': len(data['candidates'])}
        
        return None
    
    def search_state(self, name: str):
        name_lower = name.lower().strip()
        
        for state, data in self.states.items():
            if name_lower in state.lower():
                return {'state': state, 'total_votes': data['total_votes'], 'candidates_count': len(data['candidates'])}
        
        return None

# Load datasets
us_data = USElectionDataset(project)
india_data = IndiaElectionDataset(project)

print("\n✓ All datasets loaded!")
print("✓ Starting Global Elections Chatbot...\n")

from main import CivicPulseAssistant

class GlobalAssistant(CivicPulseAssistant):
    def __init__(self, us_data, india_data):
        super().__init__()
        self.us_data = us_data
        self.india_data = india_data
    
    def process_user_input(self, user_input: str) -> str:
        lower_input = user_input.lower()
        
        # Detect if question is about India
        india_keywords = ['india', 'indian', 'lok sabha', 'bharata', 'delhi', 'mumbai', 'bangalore']
        is_india_query = any(keyword in lower_input for keyword in india_keywords)
        
        if is_india_query:
            return self.handle_india_query(user_input, lower_input)
        else:
            return self.handle_us_query(user_input, lower_input)
    
    def handle_india_query(self, user_input: str, lower_input: str) -> str:
        # Search for candidate
        candidate_results = self.india_data.search_candidate(user_input)
        if candidate_results:
            cand = candidate_results[0]
            info = f"🇮🇳 INDIA CANDIDATE: {cand['name']}\n"
            info += f"Party: {cand['party']}\n"
            info += f"State: {cand['state']}\n"
            info += f"Constituency: {cand['constituency']}\n"
            info += f"Total Votes: {cand['votes']:,}\n"
            info += f"Vote Share: {cand['vote_percentage']:.2f}%"
            return info
        
        # Search for party
        party_results = self.india_data.search_party(user_input)
        if party_results:
            info = f"🇮🇳 INDIA PARTY: {party_results['party']}\n"
            info += f"Total Votes: {party_results['votes']:,}\n"
            info += f"Candidates: {party_results['candidates_count']}"
            return info
        
        # Search for state
        state_results = self.india_data.search_state(user_input)
        if state_results:
            info = f"🇮🇳 INDIA STATE: {state_results['state']}\n"
            info += f"Total Votes: {state_results['total_votes']:,}\n"
            info += f"Total Candidates: {state_results['candidates_count']}"
            return info
        
        # Top parties in India
        if 'top' in lower_input or 'leading' in lower_input or 'parties' in lower_input:
            sorted_parties = sorted(self.india_data.parties.items(), key=lambda x: x[1]['votes'], reverse=True)[:5]
            info = "🇮🇳 TOP INDIA PARTIES:\n\n"
            for party, data in sorted_parties:
                info += f"{party}\n"
                info += f"  Votes: {data['votes']:,}\n"
                info += f"  Candidates: {len(data['candidates'])}\n"
            return info
        
        return "Please ask about specific Indian candidates, parties, or states from the 2024 election."
    
    def handle_us_query(self, user_input: str, lower_input: str) -> str:
        # Search US candidate
        matched_name = None
        for candidate_key in self.us_data.candidates.keys():
            if candidate_key in lower_input or lower_input in candidate_key:
                matched_name = self.us_data.candidates[candidate_key]['name']
                break
        
        if not matched_name:
            for candidate_key, candidate_data in self.us_data.candidates.items():
                name_parts = candidate_data['name'].lower().split()
                for part in name_parts:
                    if len(part) > 2 and part in lower_input:
                        matched_name = candidate_data['name']
                        break
                if matched_name:
                    break
        
        if matched_name:
            candidate = self.us_data.candidates[matched_name.lower()]
            info = f"🇺🇸 US CANDIDATE: {candidate['name']}\n"
            info += f"Party: {candidate['party'].upper()}\n"
            
            name_lower = matched_name.lower()
            if name_lower in self.us_data.polls:
                latest = self.us_data.polls[name_lower][-1]
                info += f"\n📊 LATEST POLLING:\n"
                info += f"Favorable: {latest.get('favorable', 'N/A')}%\n"
                info += f"Unfavorable: {latest.get('unfavorable', 'N/A')}%\n"
                info += f"Pollster: {latest.get('pollster', 'Unknown')}"
            
            sentiment = self.us_data.twitter_sentiment.get(name_lower)
            if sentiment:
                info += f"\n\n📱 TWITTER SENTIMENT:\n"
                info += f"Score: {sentiment['sentiment_score']:.2f}\n"
                info += f"Volume: {sentiment['tweet_volume']:,} tweets\n"
                info += f"Trending: {'Yes' if sentiment['trending'] else 'No'}"
            
            return info
        
        return "Ask about US 2024 candidates like Trump, Harris, Biden, or Haley. Or ask about India 2024 election!"

assistant = GlobalAssistant(us_data, india_data)
chat_history = {}

class GlobalChatHandler(BaseHTTPRequestHandler):
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
            greeting = "Hi! Ask about US 2024 Election OR India 2024 Election. Which would you like to explore?"
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
            
            if chat_id not in chat_history:
                chat_history[chat_id] = {'title': 'New Chat', 'messages': [], 'date': 'Today'}
            
            chat_history[chat_id]['messages'].append({'role': 'user', 'content': user_input})
            
            response_text = assistant.process_user_input(user_input)
            chat_history[chat_id]['messages'].append({'role': 'assistant', 'content': response_text})
            
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
    <title>CivicPulse AI - Global Elections</title>
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
    <div class="sidebar">
        <div class="sidebar-header">Elections 🌍</div>
        
        <button class="new-chat-btn" onclick="newChat()">✎ New chat</button>
        
        <div class="sidebar-menu">
            <button class="menu-item">🇺🇸 US Election</button>
            <button class="menu-item">🇮🇳 India Election</button>
            <button class="menu-item">📊 Comparisons</button>
            <button class="menu-item">🔍 Analysis</button>
        </div>
        
        <div class="chat-list" id="chatList"></div>
        
        <div class="sidebar-footer">
            <div class="user-info">
                <div class="user-avatar">🗳️</div>
                <div>
                    <div style="font-size: 13px; font-weight: 500;">CivicPulse</div>
                    <div style="font-size: 12px; color: #808080;">Global Elections</div>
                </div>
            </div>
        </div>
    </div>

    <div class="main-container">
        <div class="chat-area" id="chatArea">
            <div class="greeting">
                <h1 id="greeting">Global Elections Hub</h1>
            </div>
            
            <div class="action-pills">
                <div class="action-pill" onclick="sendMessage('Tell me about Trump')">🇺🇸 US: Trump</div>
                <div class="action-pill" onclick="sendMessage('Harris US election')">🇺🇸 US: Harris</div>
                <div class="action-pill" onclick="sendMessage('Top India parties')">🇮🇳 India: Top Parties</div>
                <div class="action-pill" onclick="sendMessage('India election results Maharashtra')">🇮🇳 India: Maharashtra</div>
                <div class="action-pill" onclick="sendMessage('Compare US and India elections')">⚖️ Comparisons</div>
            </div>
            
            <div class="messages" id="messages"></div>
        </div>
        
        <div class="input-area">
            <div class="input-container">
                <textarea id="input" placeholder="Ask about US or India elections..." rows="1"></textarea>
                <div class="input-actions">
                    <button class="icon-btn">➕</button>
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

        async function newChat() {
            const res = await fetch('/api/start');
            const data = await res.json();
            currentChatId = data.chat_id;
            messages.innerHTML = '';
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
server = HTTPServer(('127.0.0.1', PORT), GlobalChatHandler)

print("\n" + "="*70)
print("🚀 Global Elections Chat Server running!")
print("="*70)
print("✓ http://localhost:8000")
print("✓ US 2024 Election Data")
print("✓ India 2024 Election Data")
print("✓ Real-time chat history")
print("✓ Sidebar menu")
print("="*70)
print("\nPress Ctrl+C to stop\n")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\n\nServer stopped. Thank you!")
