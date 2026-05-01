#!/usr/bin/env python3
"""
CivicPulse - Data-Trained Election Assistant
Uses election dataset archive to provide real information
"""

import sys
import csv
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Setup
project = Path(__file__).parent
sys.path.insert(0, str(project / 'src'))

print("Loading election datasets...")

# Load datasets
class ElectionDataset:
    def __init__(self, project_root):
        self.candidates = {}
        self.polls = defaultdict(list)
        self.primaries = {}
        self.delegate_counts = {}
        self.favorability = defaultdict(list)
        
        self.load_candidates(project_root / 'candidates.csv')
        self.load_polls(project_root / 'favorability_polls.csv')
        self.load_primaries(project_root / 'primaries_and_caucuses.csv')
        self.load_delegates(project_root / 'delegate_counts.csv')
    
    def load_candidates(self, filepath):
        """Load candidate information"""
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row.get('name', '').strip()
                    if name:
                        self.candidates[name.lower()] = {
                            'name': name,
                            'party': row.get('party', 'unknown').strip(),
                            'announced': row.get('date_announced', '').strip(),
                            'withdrawn': row.get('date_withdrawn', '').strip() or 'Still active'
                        }
            print(f"Loaded {len(self.candidates)} candidates")
        except Exception as e:
            print(f"Error loading candidates: {e}")
    
    def load_polls(self, filepath):
        """Load polling data"""
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    politician = row.get('politician', '').strip()
                    if politician:
                        favorable = row.get('favorable', '0')
                        unfavorable = row.get('unfavorable', '0')
                        pollster = row.get('pollster', 'Unknown').strip()
                        date = row.get('end_date', '').strip()
                        
                        self.polls[politician.lower()].append({
                            'favorable': favorable,
                            'unfavorable': unfavorable,
                            'pollster': pollster,
                            'date': date
                        })
                        count += 1
                        if count >= 1000:  # Limit for performance
                            break
            print(f"Loaded {len(self.polls)} politicians with polling data")
        except Exception as e:
            print(f"Error loading polls: {e}")
    
    def load_primaries(self, filepath):
        """Load primary results"""
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    event = row.get('event', '').strip()
                    candidate = row.get('candidate', '').strip()
                    vote_frac = row.get('vote_fraction', '0')
                    
                    if event and candidate:
                        key = f"{event}_{candidate.lower()}"
                        self.primaries[key] = {
                            'event': event,
                            'candidate': candidate,
                            'vote_fraction': float(vote_frac) if vote_frac else 0
                        }
            print(f"Loaded {len(self.primaries)} primary results")
        except Exception as e:
            print(f"Error loading primaries: {e}")
    
    def load_delegates(self, filepath):
        """Load delegate counts"""
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    state = row.get('State', '').strip()
                    if state:
                        self.delegate_counts[state] = {
                            'total': row.get('Total delegates', '0'),
                            'trump': row.get('Trump', '0'),
                            'haley': row.get('Haley', '0'),
                            'desantis': row.get('DeSantis', '0')
                        }
            print(f"Loaded delegate counts for {len(self.delegate_counts)} states")
        except Exception as e:
            print(f"Error loading delegates: {e}")
    
    def search_candidate(self, name):
        """Search for candidate info"""
        name_lower = name.lower()
        for key, data in self.candidates.items():
            if name_lower in key or key in name_lower:
                return data
        return None
    
    def get_candidate_info(self, name):
        """Get detailed candidate info"""
        candidate = self.search_candidate(name)
        if candidate:
            status = "Still running" if candidate['withdrawn'] == 'Still active' else f"Withdrew on {candidate['withdrawn']}"
            return f"{candidate['name']} ({candidate['party'].upper()}): {status}"
        return None
    
    def get_poll_info(self, name):
        """Get polling data for candidate"""
        name_lower = name.lower()
        if name_lower in self.polls:
            latest = self.polls[name_lower][-1]  # Most recent
            fav = latest.get('favorable', 'N/A')
            unfav = latest.get('unfavorable', 'N/A')
            return f"{name}: Favorable {fav}%, Unfavorable {unfav}% ({latest.get('pollster', 'Unknown')})"
        return None

# Create dataset instance
dataset = ElectionDataset(project)

print("Source files created successfully!")
print("Starting Web Server with Trained Dataset...\n")

# Import assistant
from main import CivicPulseAssistant
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrainedAssistant(CivicPulseAssistant):
    """Extended assistant with dataset knowledge"""
    
    def __init__(self, dataset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dataset = dataset
        self.conversation_context = []
    
    def process_user_input(self, user_input: str) -> str:
        """Process input with dataset knowledge"""
        lower_input = user_input.lower()
        
        # Check for candidate information requests
        for candidate_name in self.dataset.candidates.keys():
            if candidate_name in lower_input:
                info = self.dataset.get_candidate_info(candidate_name.title())
                if info:
                    return f"Candidate Info: {info}\n\nWould you like to know more about this candidate? (yes/no)"
        
        # Check for polling information
        for politician in self.dataset.polls.keys():
            if politician in lower_input:
                poll_info = self.dataset.get_poll_info(politician.title())
                if poll_info:
                    return f"Recent Polling: {poll_info}\n\nWould you like more election information? (yes/no)"
        
        # Check for state delegate information
        for state in self.dataset.delegate_counts.keys():
            if state.lower() in lower_input:
                delegates = self.dataset.delegate_counts[state]
                return f"{state}: {delegates['total']} total delegates\n\nLooking for specific voting information? (yes/no)"
        
        # Check for registration/voting process questions
        if any(word in lower_input for word in ['register', 'registration', 'polling location', 'where to vote']):
            return "To register to vote, visit your state election office website or vote.org\n\nDo you know your state? (yes/no)"
        
        if any(word in lower_input for word in ['deadline', 'when', 'date']):
            return "Registration deadlines vary by state. Most states have deadlines 15-30 days before election day.\n\nWhich state are you in? (type state name)"
        
        # Fall back to parent logic
        return super().process_user_input(user_input)

# Create trained assistant
assistant = TrainedAssistant(dataset)

class CivicPulseHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = self.get_html()
            self.wfile.write(html.encode('utf-8'))
        elif self.path == '/api/start':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            assistant.reset()
            greeting = "Welcome to CivicPulse! I'm trained with 2024 election data.\n\nAsk me about:\n• Candidates\n• Polling data\n• Election deadlines\n• Voting locations\n• Delegate counts\n\nWhat would you like to know?"
            response = json.dumps({'message': greeting, 'state': 'ready'})
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
            
            response_text = assistant.process_user_input(user_input)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'message': response_text,
                'state': 'ready',
                'user_profile': {}
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass
    
    @staticmethod
    def get_html():
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CivicPulse - AI Election Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html, body {
            width: 100%;
            height: 100%;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: white;
            overflow: hidden;
        }

        .background {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: -1;
            overflow: hidden;
        }

        .bg-blur {
            position: absolute;
            border-radius: 50%;
            mix-blend-mode: screen;
            filter: blur(128px);
            opacity: 0.15;
        }

        .bg-blur-1 {
            top: 0;
            left: 25%;
            width: 400px;
            height: 400px;
            background: #8b5cf6;
            animation: float 15s ease-in-out infinite;
        }

        .bg-blur-2 {
            bottom: 0;
            right: 25%;
            width: 400px;
            height: 400px;
            background: #6366f1;
            animation: float 15s ease-in-out infinite 1s;
        }

        .bg-blur-3 {
            top: 25%;
            right: 33%;
            width: 300px;
            height: 300px;
            background: #ec4899;
            animation: float 15s ease-in-out infinite 2s;
        }

        @keyframes float {
            0%, 100% { transform: translate(0, 0); }
            50% { transform: translate(30px, 30px); }
        }

        .main-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px;
            position: relative;
            z-index: 1;
        }

        .content {
            width: 100%;
            max-width: 800px;
            display: flex;
            flex-direction: column;
            gap: 30px;
        }

        .header-section {
            text-align: center;
            animation: fadeInDown 0.6s ease-out;
        }

        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .header-section h1 {
            font-size: 36px;
            font-weight: 500;
            background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.4) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 8px;
        }

        .divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            margin: 12px 0;
        }

        .header-section p {
            font-size: 14px;
            color: rgba(255,255,255,0.4);
        }

        .input-wrapper {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 20px;
            backdrop-filter: blur(40px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }

        .messages-container {
            max-height: 300px;
            overflow-y: auto;
            margin-bottom: 15px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .message {
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 13px;
            line-height: 1.5;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.assistant {
            background: rgba(139, 92, 246, 0.1);
            border-left: 3px solid rgba(139, 92, 246, 0.5);
        }

        .message.user {
            background: rgba(99, 102, 241, 0.2);
            border-left: 3px solid rgba(99, 102, 241, 0.5);
            margin-left: 40px;
        }

        .textarea-container {
            margin-bottom: 15px;
        }

        textarea {
            width: 100%;
            min-height: 60px;
            max-height: 150px;
            background: transparent;
            border: none;
            color: rgba(255, 255, 255, 0.9);
            font-size: 14px;
            resize: none;
            outline: none;
            font-family: inherit;
        }

        textarea::placeholder {
            color: rgba(255, 255, 255, 0.3);
        }

        .input-footer {
            display: flex;
            gap: 15px;
            justify-content: space-between;
            padding-top: 15px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }

        .send-btn {
            padding: 10px 20px;
            background: white;
            color: #0a0a0a;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s;
        }

        .send-btn:hover:not(:disabled) {
            transform: scale(1.02);
        }

        .send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .status-badge {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.6);
            padding: 4px 12px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
        }

        .data-source {
            margin-top: 20px;
            padding: 12px;
            background: rgba(255, 255, 255, 0.02);
            border-left: 2px solid rgba(139, 92, 246, 0.3);
            font-size: 12px;
            color: rgba(255, 255, 255, 0.5);
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="background">
        <div class="bg-blur bg-blur-1"></div>
        <div class="bg-blur bg-blur-2"></div>
        <div class="bg-blur bg-blur-3"></div>
    </div>

    <div class="main-container">
        <div class="content">
            <div class="header-section">
                <h1>CivicPulse AI</h1>
                <div class="divider"></div>
                <p>Trained with 2024 Election Data</p>
            </div>

            <div class="input-wrapper">
                <div class="messages-container" id="messages"></div>

                <div class="textarea-container">
                    <textarea id="userInput" placeholder="Ask about candidates, polls, or voting..." style="display:none;"></textarea>
                </div>

                <div class="input-footer">
                    <div class="status-badge" id="status">Ready</div>
                    <button class="send-btn" id="sendBtn" style="display:none;">
                        Send ➤
                    </button>
                    <button class="send-btn" id="startBtn">Start Chat</button>
                </div>
            </div>

            <div class="data-source">
                📊 Data Sources: Candidates, Polling, Primaries, Delegate Counts
            </div>
        </div>
    </div>

    <script>
        const messages = document.getElementById('messages');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');
        const startBtn = document.getElementById('startBtn');
        const status = document.getElementById('status');
        
        async function start() {
            startBtn.style.display = 'none';
            userInput.style.display = 'block';
            sendBtn.style.display = 'flex';
            status.textContent = 'Connected';
            
            const res = await fetch('/api/start');
            const data = await res.json();
            addMessage(data.message, 'assistant');
            userInput.focus();
        }
        
        async function send() {
            const text = userInput.value.trim();
            if (!text) return;
            
            addMessage(text, 'user');
            userInput.value = '';
            sendBtn.disabled = true;
            status.textContent = 'Processing...';
            
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                
                const data = await res.json();
                addMessage(data.message, 'assistant');
            } finally {
                sendBtn.disabled = false;
                status.textContent = 'Ready';
                userInput.focus();
            }
        }
        
        function addMessage(text, role) {
            const div = document.createElement('div');
            div.className = `message ${role}`;
            div.textContent = text;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }

        userInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 150) + 'px';
        });
        
        startBtn.addEventListener('click', start);
        sendBtn.addEventListener('click', send);
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                send();
            }
        });
    </script>
</body>
</html>'''

# Start server
PORT = 8000
server = HTTPServer(('127.0.0.1', PORT), CivicPulseHandler)
print(f"\n{'='*70}")
print(f"CivicPulse AI - Data-Trained Election Assistant")
print(f"Datasets Loaded:")
print(f"  • Candidates: {len(dataset.candidates)}")
print(f"  • Polling Data: {len(dataset.polls)}")
print(f"  • Primary Results: {len(dataset.primaries)}")
print(f"  • Delegate Counts: {len(dataset.delegate_counts)}")
print(f"\nServer running: http://localhost:{PORT}")
print(f"Press Ctrl+C to stop")
print(f"{'='*70}\n")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\n\nServer stopped. Thank you for using CivicPulse AI!")
