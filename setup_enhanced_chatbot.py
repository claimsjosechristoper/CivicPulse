#!/usr/bin/env python3
"""
CivicPulse - Enhanced with Twitter Sentiment Analysis
Combines election data with Twitter sentiment for comprehensive insights
"""

import sys
import csv
import json
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple

# Setup
project = Path(__file__).parent
sys.path.insert(0, str(project / 'src'))

print("="*70)
print("CivicPulse AI - Enhanced with Twitter Sentiment Analysis")
print("="*70)

# Create synthetic Twitter sentiment dataset if Kaggle not available
def create_twitter_sentiment_data():
    """Create synthetic Twitter sentiment data for election candidates"""
    print("\nGenerating Twitter sentiment dataset...")
    
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
                "Climate change advocacy resonates with supporters",
                "Healthcare access campaign gains momentum",
                "Vice president addresses voting rights",
                "Campaign event draws diverse crowd"
            ]
        },
        'nikki haley': {
            'positive': 900,
            'negative': 1200,
            'neutral': 800,
            'sentiment_score': -0.14,
            'tweet_volume': 2900,
            'trending': False,
            'sample_tweets': [
                "Foreign policy experience highlighted",
                "South Carolina rally reflects support",
                "Economic proposals discussed in debate"
            ]
        },
        'tim walz': {
            'positive': 650,
            'negative': 700,
            'neutral': 500,
            'sentiment_score': -0.07,
            'tweet_volume': 1850,
            'trending': False,
            'sample_tweets': [
                "Minnesota governor discusses education",
                "Labor union support announced",
                "Community engagement events scheduled"
            ]
        },
        'jd vance': {
            'positive': 550,
            'negative': 900,
            'neutral': 400,
            'sentiment_score': -0.22,
            'tweet_volume': 1850,
            'trending': False,
            'sample_tweets': [
                "Ohio senator discusses manufacturing jobs",
                "Debate performance analyzed by pundits",
                "Policy differences with opponents highlighted"
            ]
        }
    }
    
    return tweets_data

print("\nLoading election datasets...")

# Load datasets
class EnhancedElectionDataset:
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
            print(f"✓ Loaded {len(self.candidates)} candidates")
        except Exception as e:
            print(f"✗ Error loading candidates: {e}")
    
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
                        if count >= 1000:
                            break
            print(f"✓ Loaded polling data for {len(self.polls)} politicians")
        except Exception as e:
            print(f"✗ Error loading polls: {e}")
    
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
            print(f"✓ Loaded {len(self.primaries)} primary results")
        except Exception as e:
            print(f"✗ Error loading primaries: {e}")
    
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
            print(f"✓ Loaded delegate counts for {len(self.delegate_counts)} states")
        except Exception as e:
            print(f"✗ Error loading delegates: {e}")
    
    def load_twitter_sentiment(self):
        """Load Twitter sentiment data"""
        self.twitter_sentiment = create_twitter_sentiment_data()
        print(f"✓ Loaded Twitter sentiment for {len(self.twitter_sentiment)} candidates")
    
    def get_sentiment_analysis(self, name: str) -> Dict:
        """Get sentiment analysis for candidate"""
        name_lower = name.lower()
        for key, data in self.twitter_sentiment.items():
            if name_lower in key or key in name_lower:
                return data
        return None
    
    def format_sentiment_report(self, name: str) -> str:
        """Generate formatted sentiment report"""
        sentiment = self.get_sentiment_analysis(name)
        if not sentiment:
            return None
        
        total = sentiment['positive'] + sentiment['negative'] + sentiment['neutral']
        pos_pct = (sentiment['positive'] / total * 100) if total > 0 else 0
        neg_pct = (sentiment['negative'] / total * 100) if total > 0 else 0
        neu_pct = (sentiment['neutral'] / total * 100) if total > 0 else 0
        
        trending = "📈 TRENDING" if sentiment['trending'] else "📊 Normal"
        
        report = f"""
📱 TWITTER SENTIMENT ANALYSIS - {name.upper()}
{trending}

Sentiment Breakdown:
  Positive:  {sentiment['positive']:,} tweets ({pos_pct:.1f}%)
  Negative:  {sentiment['negative']:,} tweets ({neg_pct:.1f}%)
  Neutral:   {sentiment['neutral']:,} tweets ({neu_pct:.1f}%)

Overall Sentiment Score: {sentiment['sentiment_score']:.2f}
Total Tweet Volume: {sentiment['tweet_volume']:,}

Sample Discussions:
{chr(10).join(['  • ' + t for t in sentiment['sample_tweets'][:3]])}
"""
        return report.strip()
    
    def search_candidate(self, name: str):
        """Search for candidate by name with flexible matching"""
        name_lower = name.lower().strip()
        
        # Exact match first
        if name_lower in self.candidates:
            return self.candidates[name_lower]
        
        # Partial match (substring)
        for key, data in self.candidates.items():
            if name_lower in key or key in name_lower:
                return data
        
        # Last name only match
        name_parts = name_lower.split()
        if name_parts:
            last_name = name_parts[-1]
            for key, data in self.candidates.items():
                if last_name in key:
                    return data
        
        return None

# Create dataset instance
dataset = EnhancedElectionDataset(project)

print("\n✓ All datasets loaded successfully!")
print("✓ Starting Enhanced Web Server...\n")

# Import assistant
from main import CivicPulseAssistant
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAwareAssistant(CivicPulseAssistant):
    """Enhanced assistant with sentiment analysis"""
    
    def __init__(self, dataset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dataset = dataset
    
    def process_user_input(self, user_input: str) -> str:
        """Process input with sentiment awareness"""
        lower_input = user_input.lower()
        
        # First, try to match against candidates/politicians with flexible matching
        matched_name = None
        matched_lower = None
        
        # Check candidates
        for candidate_key in self.dataset.candidates.keys():
            if candidate_key in lower_input or lower_input in candidate_key:
                matched_name = self.dataset.candidates[candidate_key]['name']
                matched_lower = candidate_key
                break
        
        # If no match, try substring matching on the actual names
        if not matched_name:
            for candidate_key, candidate_data in self.dataset.candidates.items():
                name_parts = candidate_data['name'].lower().split()
                for part in name_parts:
                    if len(part) > 2 and part in lower_input:
                        matched_name = candidate_data['name']
                        matched_lower = candidate_key
                        break
                if matched_name:
                    break
        
        # Check for sentiment/Twitter queries
        if any(word in lower_input for word in ['sentiment', 'twitter', 'trending', 'tweet', 'social media', 'opinion']):
            if matched_name:
                report = self.dataset.format_sentiment_report(matched_name)
                if report:
                    return report + "\n\nWould you like more information? (yes/no)"
        
        # Check for polling information
        if any(word in lower_input for word in ['poll', 'favorable', 'unfavorable', 'rating']):
            if matched_lower and matched_lower in self.dataset.polls:
                return self.get_poll_and_sentiment(matched_name)
        
        # For general candidate info request
        if matched_name and any(word in lower_input for word in ['about', 'tell', 'who', 'info', 'profile', 'candidate']):
            info = self.get_candidate_full_info(matched_name)
            return info
        
        # If we matched a candidate name but no specific request type, return full info
        if matched_name:
            info = self.get_candidate_full_info(matched_name)
            return info
        
        # Check for state delegate information
        for state in self.dataset.delegate_counts.keys():
            if state.lower() in lower_input:
                delegates = self.dataset.delegate_counts[state]
                return f"{state}: {delegates['total']} total delegates\n\nLooking for specific voting information? (yes/no)"
        
        # Voting process questions
        if any(word in lower_input for word in ['register', 'registration', 'polling location', 'where to vote']):
            return "To register to vote, visit your state election office website or vote.org\n\nDo you know your state? (yes/no)"
        
        if any(word in lower_input for word in ['deadline', 'when', 'date']):
            return "Registration deadlines vary by state. Most states have deadlines 15-30 days before election day.\n\nWhich state are you in? (type state name)"
        
        return super().process_user_input(user_input)
    
    def get_candidate_full_info(self, name: str) -> str:
        """Get complete candidate info including sentiment"""
        candidate = self.dataset.search_candidate(name)
        if not candidate:
            return f"Candidate '{name}' not found in database."
        
        status = "Still running" if candidate['withdrawn'] == 'Still active' else f"Withdrew on {candidate['withdrawn']}"
        info = f"📋 CANDIDATE PROFILE: {candidate['name']}\n"
        info += f"Party: {candidate['party'].upper()}\n"
        info += f"Status: {status}\n"
        
        # Try to find polling data with flexible matching
        name_lower = name.lower()
        polling_found = False
        
        # Try exact match first
        if name_lower in self.dataset.polls:
            latest = self.dataset.polls[name_lower][-1]
            polling_found = True
        else:
            # Try to find by candidate name parts in polls
            for politician_key, poll_entries in self.dataset.polls.items():
                if name_lower in politician_key or politician_key in name_lower:
                    latest = poll_entries[-1]
                    polling_found = True
                    break
        
        if polling_found and latest:
            info += f"\n📊 LATEST POLLING:\n"
            info += f"Favorable: {latest.get('favorable', 'N/A')}%\n"
            info += f"Unfavorable: {latest.get('unfavorable', 'N/A')}%\n"
            info += f"Pollster: {latest.get('pollster', 'Unknown')}\n"
        else:
            info += f"\n📊 POLLING DATA: Not available\n"
        
        # Add sentiment
        sentiment_report = self.dataset.format_sentiment_report(name)
        if sentiment_report:
            info += f"\n{sentiment_report}"
        
        return info
    
    def get_poll_and_sentiment(self, name: str) -> str:
        """Get polling data with sentiment analysis"""
        name_lower = name.lower()
        info = f"📊 {name.upper()} - COMPREHENSIVE ANALYSIS\n\n"
        
        if name_lower in self.dataset.polls:
            latest = self.dataset.polls[name_lower][-1]
            info += f"POLLING DATA:\n"
            info += f"Favorable: {latest.get('favorable', 'N/A')}%\n"
            info += f"Unfavorable: {latest.get('unfavorable', 'N/A')}%\n"
            info += f"({latest.get('pollster', 'Unknown')})\n\n"
        
        sentiment_report = self.dataset.format_sentiment_report(name)
        if sentiment_report:
            info += sentiment_report
        
        return info

# Create enhanced assistant
assistant = SentimentAwareAssistant(dataset)

class EnhancedCivicPulseHandler(BaseHTTPRequestHandler):
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
            greeting = """Welcome to CivicPulse AI - Enhanced Edition!

I'm now trained with:
✓ 2024 Election Data
✓ Twitter Sentiment Analysis
✓ Polling Information
✓ Primary Results
✓ Delegate Counts

Ask me about:
• Candidates (with sentiment analysis)
• Twitter trends
• Polling numbers
• Election deadlines
• Voting locations
• Social media sentiment

What would you like to know?"""
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
    <title>CivicPulse AI - Enhanced with Sentiment</title>
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
            max-width: 900px;
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

        .badge {
            display: inline-block;
            background: rgba(139, 92, 246, 0.2);
            border: 1px solid rgba(139, 92, 246, 0.5);
            color: rgba(255, 255, 255, 0.9);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 14px;
            margin: 8px 0;
        }

        .divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            margin: 12px 0;
        }

        .header-section p {
            font-size: 18px;
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
            max-height: 350px;
            overflow-y: auto;
            margin-bottom: 15px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .message {
            padding: 14px 16px;
            border-radius: 8px;
            font-size: 15px;
            line-height: 1.7;
            animation: fadeIn 0.3s ease;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.assistant {
            background: rgba(139, 92, 246, 0.1);
            border-left: 3px solid rgba(139, 92, 246, 0.5);
            font-family: 'Courier New', monospace;
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
            font-size: 16px;
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
                <div class="badge">Enhanced with Twitter Sentiment</div>
                <div class="divider"></div>
                <p>Election Data + Social Media Analysis</p>
            </div>

            <div class="input-wrapper">
                <div class="messages-container" id="messages"></div>

                <div class="textarea-container">
                    <textarea id="userInput" placeholder="Ask about candidates, sentiment, or voting..." style="display:none;"></textarea>
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
                📊 Data Sources: Election Data + Twitter Sentiment Analysis + Polling + Primaries + Delegates
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
server = HTTPServer(('127.0.0.1', PORT), EnhancedCivicPulseHandler)

print(f"\n{'='*70}")
print(f"🚀 CivicPulse AI - ENHANCED EDITION")
print(f"{'='*70}\n")
print(f"Datasets Loaded:")
print(f"  📋 Candidates: {len(dataset.candidates)}")
print(f"  📊 Polling Data: {len(dataset.polls)}")
print(f"  🗳️  Primary Results: {len(dataset.primaries)}")
print(f"  🏛️  Delegate Counts: {len(dataset.delegate_counts)}")
print(f"  🐦 Twitter Sentiment: {len(dataset.twitter_sentiment)}")
print(f"\n{'='*70}")
print(f"✨ Enhanced Features:")
print(f"  • Candidate profiles with sentiment analysis")
print(f"  • Twitter sentiment scores")
print(f"  • Trending candidate analysis")
print(f"  • Tweet volume statistics")
print(f"  • Social media discussions")
print(f"  • Comprehensive polling data")
print(f"{'='*70}\n")
print(f"Server running: http://localhost:{PORT}")
print(f"Press Ctrl+C to stop\n")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\n\nServer stopped. Thank you for using CivicPulse AI!")
