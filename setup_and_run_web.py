#!/usr/bin/env python3
"""
CivicPulse - Setup and Web Server Launcher
Creates all source files with UTF-8 encoding, then starts web server
"""

import sys
from pathlib import Path

# Project root
project = Path(__file__).parent
sys.path.insert(0, str(project / 'src'))

print("Setting up CivicPulse...")

# Create directories
for d in ['src', 'tests', '.agent/skills']:
    (project / d).mkdir(parents=True, exist_ok=True)

# Create __init__ files
(project / 'src' / '__init__.py').write_text('"""CivicPulse"""', encoding='utf-8')
(project / 'tests' / '__init__.py').write_text('"""Tests"""', encoding='utf-8')

# Create logic.py
(project / 'src' / 'logic.py').write_text('''from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import re, logging
logger = logging.getLogger(__name__)

class ConversationState(Enum):
    INITIAL = "initial"
    REGISTRATION_CHECK = "registration_check"
    TIMELINE_GENERATION = "timeline_generation"
    VOTING_DAY_PREP = "voting_day_prep"

class ElectionAssistant:
    STATES = {'AL':'Alabama','AK':'Alaska','AZ':'Arizona','AR':'Arkansas','CA':'California','CO':'Colorado','CT':'Connecticut','DE':'Delaware','FL':'Florida','GA':'Georgia','HI':'Hawaii','ID':'Idaho','IL':'Illinois','IN':'Indiana','IA':'Iowa','KS':'Kansas','KY':'Kentucky','LA':'Louisiana','ME':'Maine','MD':'Maryland','MA':'Massachusetts','MI':'Michigan','MN':'Minnesota','MS':'Mississippi','MO':'Missouri','MT':'Montana','NE':'Nebraska','NV':'Nevada','NH':'New Hampshire','NJ':'New Jersey','NM':'New Mexico','NY':'New York','NC':'North Carolina','ND':'North Dakota','OH':'Ohio','OK':'Oklahoma','OR':'Oregon','PA':'Pennsylvania','RI':'Rhode Island','SC':'South Carolina','SD':'South Dakota','TN':'Tennessee','TX':'Texas','UT':'Utah','VT':'Vermont','VA':'Virginia','WA':'Washington','WV':'West Virginia','WI':'Wisconsin','WY':'Wyoming'}
    
    def __init__(self):
        self.states_reverse = {v.lower(): k for k, v in self.STATES.items()}
    
    @staticmethod
    def parse_yes_no(user_input: str) -> Optional[bool]:
        lower = user_input.lower().strip()
        if any(lower.startswith(p) for p in ['yes','yeah','yep','sure','y','ok']): return True
        if any(lower.startswith(p) for p in ['no','nope','nah','negative','n']): return False
        return None
    
    def generate_election_timeline(self, user_profile: Dict) -> Dict:
        election_date = datetime(2024, 11, 5)
        timeline = {'summary': '', 'calendar_events': [], 'key_dates': []}
        if not user_profile.get('is_registered'):
            rd = election_date - timedelta(days=30)
            timeline['summary'] = f"REGISTRATION TIMELINE:\\n1. {rd.strftime('%B %d, %Y')} - Registration Deadline\\n2. {(election_date - timedelta(days=7)).strftime('%B %d, %Y')} - Verify Registration\\n3. {election_date.strftime('%B %d, %Y')} - Election Day\\n"
        else:
            ev = election_date - timedelta(days=21)
            timeline['summary'] = f"VOTING TIMELINE:\\n1. {ev.strftime('%B %d, %Y')} - Early Voting Starts\\n2. {(election_date - timedelta(days=7)).strftime('%B %d, %Y')} - Mail-in Deadline\\n3. {election_date.strftime('%B %d, %Y')} - Election Day\\n"
        return timeline
''', encoding='utf-8')

# Create services.py
(project / 'src' / 'services.py').write_text('''import logging
from typing import Optional, Dict, Any
logger = logging.getLogger(__name__)

class GoogleServicesClient:
    def __init__(self, api_key: Optional[str] = None, calendar_id: Optional[str] = None):
        self.api_key = api_key
        self.calendar_id = calendar_id
        self.is_configured = bool(api_key and calendar_id)
    
    def search_registration_deadline(self, state: str) -> Dict:
        deadlines = {'CA':{'deadline':'2024-10-07','days_remaining':10},'TX':{'deadline':'2024-10-07','days_remaining':10},'NY':{'deadline':'2024-10-12','days_remaining':15},'FL':{'deadline':'2024-10-07','days_remaining':10}}
        state_code = state.upper() if len(state) == 2 else state[:2].upper()
        return deadlines.get(state_code, {'deadline': 'Contact your state', 'days_remaining': 'N/A'})
    
    def search_polling_location(self, location: str) -> Dict:
        return {'name': 'City Community Center', 'address': f'{location}, USA', 'hours': '7:00 AM - 8:00 PM', 'accessible': True}
    
    def create_calendar_event(self, event, email) -> bool:
        return True
''', encoding='utf-8')

# Create main.py
(project / 'src' / 'main.py').write_text('''import logging
from typing import Optional
from logic import ElectionAssistant, ConversationState
from services import GoogleServicesClient
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CivicPulseAssistant:
    def __init__(self, api_key: Optional[str] = None, calendar_id: Optional[str] = None):
        self.logic = ElectionAssistant()
        self.services = GoogleServicesClient(api_key, calendar_id)
        self.current_state = ConversationState.INITIAL
        self.user_profile = {}
        logger.info("CivicPulse initialized")
    
    def start_conversation(self) -> str:
        self.current_state = ConversationState.INITIAL
        return "Welcome to CivicPulse!\\n\\nI'm here to help you prepare for the upcoming election. Whether you're a first-time voter or seasoned, I'll guide you through every step.\\n\\nLet's start: Are you registered to vote? (yes/no)"
    
    def process_user_input(self, user_input: str) -> str:
        if self.current_state == ConversationState.INITIAL:
            is_registered = self.logic.parse_yes_no(user_input)
            if is_registered is None:
                return "I didn't quite get that. Could you answer with 'yes' or 'no'?"
            self.user_profile['is_registered'] = is_registered
            self.current_state = ConversationState.REGISTRATION_CHECK
            if is_registered:
                return "Great! You're registered.\\n\\nLet's find your polling location. What's your home address or ZIP code?"
            else:
                return "Don't worry—I'll help you register!\\n\\nWhat state are you voting in? (e.g., California or CA)"
        
        elif self.current_state == ConversationState.REGISTRATION_CHECK:
            if self.user_profile.get('is_registered'):
                loc = self.services.search_polling_location(user_input)
                self.current_state = ConversationState.TIMELINE_GENERATION
                return f"Found your polling location:\\n\\n{loc['name']}\\n{loc['address']}\\nHours: {loc['hours']}\\n\\nWhat's your email for reminders?"
            else:
                info = self.services.search_registration_deadline(user_input)
                self.current_state = ConversationState.TIMELINE_GENERATION
                return f"Important dates for {user_input}:\\n\\nDeadline: {info['deadline']}\\nDays left: {info['days_remaining']}\\n\\nWant a reminder? (yes/no)"
        
        elif self.current_state == ConversationState.TIMELINE_GENERATION:
            timeline = self.logic.generate_election_timeline(self.user_profile)
            self.current_state = ConversationState.VOTING_DAY_PREP
            return f"{timeline['summary']}\\nNeed accessible voting accommodations? (yes/no)"
        
        else:
            needs = self.logic.parse_yes_no(user_input)
            if needs:
                return "Accommodations:\\n✓ Curbside\\n✓ Accessible machines\\n✓ Ballot help\\n✓ Extra time\\n\\nContact your election office 5 days before. You're set!"
            else:
                return "Checklist:\\n✓ Bring ID\\n✓ Arrive early\\n✓ Review candidates\\n\\nThank you for voting!"
    
    def reset(self):
        self.current_state = ConversationState.INITIAL
        self.user_profile = {}
''', encoding='utf-8')

print("Source files created successfully!")
print("\nStarting Web Server...")

# Now import and run the web server
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from main import CivicPulseAssistant

assistant = CivicPulseAssistant()

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
            greeting = assistant.start_conversation()
            response = json.dumps({'message': greeting, 'state': assistant.current_state.value})
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
                'state': assistant.current_state.value,
                'user_profile': assistant.user_profile
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
    <title>CivicPulse - Election Assistant</title>
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
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
            letter-spacing: -0.5px;
        }

        .divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            margin: 12px 0;
            animation: expandWidth 0.8s ease-out 0.3s backwards;
        }

        @keyframes expandWidth {
            from { width: 0; }
            to { width: 100%; }
        }

        .header-section p {
            font-size: 14px;
            color: rgba(255,255,255,0.4);
            animation: fadeIn 0.6s ease-out 0.2s backwards;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .input-wrapper {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 20px;
            backdrop-filter: blur(40px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            animation: slideUp 0.6s ease-out 0.1s backwards;
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: scale(0.98);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }

        .textarea-container {
            margin-bottom: 15px;
            position: relative;
        }

        textarea {
            width: 100%;
            min-height: 80px;
            max-height: 200px;
            background: transparent;
            border: none;
            color: rgba(255, 255, 255, 0.9);
            font-size: 14px;
            resize: none;
            outline: none;
            font-family: inherit;
            overflow-y: auto;
        }

        textarea::placeholder {
            color: rgba(255, 255, 255, 0.3);
        }

        textarea::-webkit-scrollbar {
            width: 6px;
        }

        textarea::-webkit-scrollbar-track {
            background: transparent;
        }

        textarea::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }

        textarea::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.2);
        }

        .input-footer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 15px;
            padding-top: 15px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }

        .input-buttons {
            display: flex;
            gap: 8px;
        }

        .icon-btn {
            width: 36px;
            height: 36px;
            border: none;
            background: transparent;
            color: rgba(255, 255, 255, 0.4);
            cursor: pointer;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            font-size: 18px;
        }

        .icon-btn:hover {
            color: rgba(255, 255, 255, 0.9);
            background: rgba(255, 255, 255, 0.05);
        }

        .send-btn {
            padding: 10px 20px;
            background: white;
            color: #0a0a0a;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
            box-shadow: 0 10px 20px rgba(255, 255, 255, 0.1);
        }

        .send-btn:hover:not(:disabled) {
            transform: scale(1.02);
            box-shadow: 0 15px 30px rgba(255, 255, 255, 0.15);
        }

        .send-btn:active:not(:disabled) {
            transform: scale(0.98);
        }

        .send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .send-btn.loading {
            background: rgba(255, 255, 255, 0.1);
            color: rgba(255, 255, 255, 0.6);
        }

        .spinner {
            display: inline-block;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .action-buttons {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            animation: fadeIn 0.8s ease-out 0.4s backwards;
        }

        .action-btn {
            padding: 10px 16px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            color: rgba(255, 255, 255, 0.6);
            border-radius: 8px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 500;
        }

        .action-btn:hover {
            background: rgba(255, 255, 255, 0.05);
            color: rgba(255, 255, 255, 0.9);
            border-color: rgba(255, 255, 255, 0.1);
        }

        .action-btn:active {
            transform: scale(0.98);
        }

        .thinking-indicator {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 12px 20px;
            backdrop-filter: blur(40px);
            display: none;
            align-items: center;
            gap: 12px;
            animation: slideUp 0.4s ease-out;
            z-index: 100;
        }

        .thinking-indicator.show {
            display: flex;
        }

        .dots {
            display: flex;
            gap: 4px;
        }

        .dot {
            width: 6px;
            height: 6px;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 50%;
            animation: bounce 1.2s infinite;
        }

        .dot:nth-child(2) { animation-delay: 0.2s; }
        .dot:nth-child(3) { animation-delay: 0.4s; }

        @keyframes bounce {
            0%, 100% {
                opacity: 0.3;
                transform: translateY(0);
            }
            50% {
                opacity: 0.9;
                transform: translateY(-8px);
            }
        }

        @media (max-width: 640px) {
            .header-section h1 {
                font-size: 28px;
            }

            .action-buttons {
                gap: 8px;
            }

            .action-btn {
                font-size: 12px;
                padding: 8px 12px;
            }
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
                <h1>How can I help today?</h1>
                <div class="divider"></div>
                <p>Type a command or ask a question</p>
            </div>

            <div class="input-wrapper">
                <div class="textarea-container">
                    <textarea id="userInput" placeholder="Ask about voting information..." style="display:none;"></textarea>
                </div>

                <div class="input-footer">
                    <div class="input-buttons">
                        <button class="icon-btn" id="attachBtn" style="display:none;" title="Attach file">📎</button>
                        <button class="icon-btn" id="commandBtn" style="display:none;" title="Commands">⌘</button>
                    </div>
                    <button class="send-btn" id="sendBtn" style="display:none;">
                        <span>Send</span>
                        <span style="font-size: 16px;">➤</span>
                    </button>
                    <button class="send-btn" id="startBtn">Start</button>
                </div>
            </div>

            <div class="action-buttons">
                <button class="action-btn" data-action="registration" style="display:none;">📋 Check Registration</button>
                <button class="action-btn" data-action="polling" style="display:none;">📍 Find Polling Location</button>
                <button class="action-btn" data-action="deadline" style="display:none;">📅 Registration Deadline</button>
                <button class="action-btn" data-action="accessibility" style="display:none;">♿ Accessibility Info</button>
            </div>
        </div>
    </div>

    <div class="thinking-indicator" id="thinkingIndicator">
        <span style="font-size: 14px;">CivicPulse thinking</span>
        <div class="dots">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
    </div>

    <script>
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');
        const startBtn = document.getElementById('startBtn');
        const thinkingIndicator = document.getElementById('thinkingIndicator');
        
        async function start() {
            startBtn.style.display = 'none';
            userInput.style.display = 'block';
            sendBtn.style.display = 'flex';
            document.querySelectorAll('.action-btn').forEach(btn => btn.style.display = 'flex');
            
            const res = await fetch('/api/start');
            const data = await res.json();
            userInput.focus();
            showThinking(false);
        }
        
        async function send() {
            const text = userInput.value.trim();
            if (!text) return;
            
            userInput.value = '';
            sendBtn.disabled = true;
            showThinking(true);
            
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                
                const data = await res.json();
                
                // Simulate response delay
                await new Promise(resolve => setTimeout(resolve, 800));
            } catch (error) {
                console.error('Error:', error);
            } finally {
                showThinking(false);
                sendBtn.disabled = false;
                userInput.focus();
            }
        }

        function showThinking(show) {
            if (show) {
                thinkingIndicator.classList.add('show');
            } else {
                thinkingIndicator.classList.remove('show');
            }
        }

        // Auto-resize textarea
        userInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 200) + 'px';
        });
        
        startBtn.addEventListener('click', start);
        sendBtn.addEventListener('click', send);
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                send();
            }
        });

        // Action button handlers
        document.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const action = this.dataset.action;
                userInput.value = {
                    'registration': 'Check if I am registered to vote',
                    'polling': 'Help me find my polling location',
                    'deadline': 'What is the registration deadline?',
                    'accessibility': 'Do you offer accessible voting options?'
                }[action];
                userInput.style.height = 'auto';
                userInput.style.height = Math.min(userInput.scrollHeight, 200) + 'px';
                userInput.focus();
            });
        });
    </script>
</body>
</html>'''

# Start server
PORT = 8000
server = HTTPServer(('127.0.0.1', PORT), CivicPulseHandler)
print(f"\n{'='*70}")
print(f"CivicPulse Web Server is running!")
print(f"Open your browser: http://localhost:{PORT}")
print(f"Press Ctrl+C to stop")
print(f"{'='*70}\n")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\n\nServer stopped. Thank you for using CivicPulse!")
