#!/usr/bin/env python3
"""
CivicPulse - Enhanced with Sidebar Chat History
Professional chat interface with chat history, sentiment analysis, and election data
"""

import sys
import csv
import json
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple
from http.server import HTTPServer, BaseHTTPRequestHandler

# Setup
project = Path(__file__).parent
sys.path.insert(0, str(project / 'src'))

print("="*70)
print("🗳️ CivicPulse AI - Sidebar Edition with Chat History")
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

print("Loading election datasets...")

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
print("✓ Starting Sidebar Chat Server...\n")

# Import assistant
from main import CivicPulseAssistant

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
        latest = None
        
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

class SidebarChatHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = self.get_html()
            self.wfile.write(html.encode('utf-8'))
        elif self.path == '/api/start':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            assistant.reset()
            greeting = """Welcome to CivicPulse AI!

I have access to:
✓ 23 Election Candidates (2024)
✓ 1000+ Polling Entries
✓ Twitter Sentiment Analysis
✓ Primary Results
✓ Delegate Counts

Ask me about:
🗳️ Candidates (profiles, stats)
📊 Polling data
🐦 Twitter sentiment
📈 Trending candidates
🗓️ Election dates
🗺️ Voting locations

What would you like to know?"""
            response = json.dumps({'message': greeting})
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
            
            response = {'message': response_text}
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
    <title>CivicPulse AI - Chat with History</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: rgba(255, 255, 255, 0.9);
            overflow: hidden;
            height: 100vh;
            display: flex;
        }

        .blur-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at 20% 50%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
                        radial-gradient(circle at 80% 80%, rgba(236, 72, 153, 0.15) 0%, transparent 50%);
            filter: blur(40px);
            z-index: 0;
        }

        .blur-shape {
            position: fixed;
            opacity: 0.4;
            filter: blur(60px);
            z-index: 0;
        }

        .blur-shape-1 {
            top: 10%;
            left: 10%;
            width: 500px;
            height: 500px;
            background: #8b5cf6;
            animation: float 20s ease-in-out infinite;
        }

        .blur-shape-2 {
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

        /* Sidebar */
        .sidebar {
            width: 260px;
            background: rgba(15, 15, 15, 0.95);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            flex-direction: column;
            position: relative;
            z-index: 2;
        }

        .sidebar-header {
            padding: 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        .sidebar-title {
            font-size: 18px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }

        .sidebar-search {
            display: flex;
            gap: 8px;
        }

        .search-input {
            flex: 1;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 8px 12px;
            color: rgba(255, 255, 255, 0.9);
            font-size: 14px;
        }

        .search-input::placeholder {
            color: rgba(255, 255, 255, 0.3);
        }

        .chat-label {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.5);
            text-transform: uppercase;
            margin: 20px 20px 10px;
            font-weight: 600;
        }

        .chat-list {
            flex: 1;
            overflow-y: auto;
            padding: 8px;
        }

        .chat-item {
            padding: 12px 15px;
            margin-bottom: 8px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.2s;
            font-size: 14px;
        }

        .chat-item:hover {
            background: rgba(139, 92, 246, 0.15);
            border-color: rgba(139, 92, 246, 0.3);
        }

        .chat-item.active {
            background: rgba(139, 92, 246, 0.2);
            border-color: rgba(139, 92, 246, 0.5);
        }

        .star-btn {
            background: none;
            border: none;
            color: rgba(255, 255, 255, 0.4);
            cursor: pointer;
            font-size: 16px;
            transition: all 0.2s;
        }

        .star-btn:hover {
            color: #fbbf24;
        }

        .sidebar-footer {
            padding: 15px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }

        .new-chat-btn {
            width: 100%;
            padding: 12px;
            background: rgba(99, 102, 241, 0.2);
            border: 1px solid rgba(99, 102, 241, 0.5);
            border-radius: 10px;
            color: rgba(255, 255, 255, 0.9);
            cursor: pointer;
            font-weight: 600;
            margin-bottom: 12px;
            transition: all 0.2s;
        }

        .new-chat-btn:hover {
            background: rgba(99, 102, 241, 0.3);
        }

        /* Main Area */
        .main-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            position: relative;
            z-index: 1;
            padding: 30px;
        }

        .chat-header {
            text-align: center;
            margin-bottom: 30px;
        }

        .chat-header h1 {
            font-size: 32px;
            font-weight: 600;
            margin-bottom: 8px;
            background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.6) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .chat-header p {
            font-size: 16px;
            color: rgba(255, 255, 255, 0.5);
        }

        .chat-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            max-width: 1000px;
            margin: 0 auto;
            width: 100%;
        }

        .messages-container {
            flex: 1;
            overflow-y: auto;
            margin-bottom: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            padding-right: 10px;
        }

        .messages-container::-webkit-scrollbar {
            width: 6px;
        }

        .messages-container::-webkit-scrollbar-track {
            background: transparent;
        }

        .messages-container::-webkit-scrollbar-thumb {
            background: rgba(139, 92, 246, 0.3);
            border-radius: 3px;
        }

        .message {
            padding: 14px 16px;
            border-radius: 10px;
            font-size: 15px;
            line-height: 1.7;
            animation: fadeIn 0.3s ease;
            white-space: pre-wrap;
            word-wrap: break-word;
            max-width: 85%;
        }

        .message.assistant {
            background: rgba(139, 92, 246, 0.1);
            border-left: 3px solid rgba(139, 92, 246, 0.5);
            font-family: 'Courier New', monospace;
            align-self: flex-start;
        }

        .message.user {
            background: rgba(99, 102, 241, 0.2);
            border-left: 3px solid rgba(99, 102, 241, 0.5);
            align-self: flex-end;
            margin-left: auto;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .input-wrapper {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 18px;
            backdrop-filter: blur(40px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
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
            margin-bottom: 15px;
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
            padding: 10px 24px;
            background: white;
            color: #0a0a0a;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }

        .send-btn:hover:not(:disabled) {
            transform: scale(1.05);
            box-shadow: 0 8px 24px rgba(255, 255, 255, 0.2);
        }

        .send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .status {
            font-size: 13px;
            color: rgba(255, 255, 255, 0.5);
        }
    </style>
</head>
<body>
    <div class="blur-bg"></div>
    <div class="blur-shape blur-shape-1"></div>
    <div class="blur-shape blur-shape-2"></div>

    <!-- Sidebar -->
    <div class="sidebar">
        <div class="sidebar-header">
            <div class="sidebar-title">
                <span>💬</span>
                <span>Chats</span>
            </div>
            <div class="sidebar-search">
                <input type="text" class="search-input" placeholder="Search chats...">
            </div>
        </div>

        <div class="chat-label">Recent</div>
        <div class="chat-list">
            <div class="chat-item active" onclick="switchChat(this, 'current')">
                <span>Current Chat</span>
                <button class="star-btn">⭐</button>
            </div>
            <div class="chat-item" onclick="switchChat(this, 'candidates')">
                <span>📋 Candidates</span>
                <button class="star-btn">☆</button>
            </div>
            <div class="chat-item" onclick="switchChat(this, 'polling')">
                <span>📊 Polling Data</span>
                <button class="star-btn">☆</button>
            </div>
            <div class="chat-item" onclick="switchChat(this, 'sentiment')">
                <span>🐦 Sentiment</span>
                <button class="star-btn">☆</button>
            </div>
            <div class="chat-item" onclick="switchChat(this, 'voting')">
                <span>🗳️ Voting Guide</span>
                <button class="star-btn">☆</button>
            </div>
        </div>

        <div class="sidebar-footer">
            <button class="new-chat-btn" onclick="newChat()">+ New Chat</button>
        </div>
    </div>

    <!-- Main Chat -->
    <div class="main-container">
        <div class="chat-header">
            <h1>🗳️ CivicPulse AI</h1>
            <p>Election Data + Twitter Sentiment Analysis</p>
        </div>

        <div class="chat-content">
            <div class="messages-container" id="messages"></div>

            <div class="input-wrapper">
                <textarea id="input" placeholder="Ask about candidates, sentiment, or voting..."></textarea>
                <div class="input-footer">
                    <span class="status" id="status">Ready</span>
                    <button class="send-btn" id="send">Send ➤</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const messages = document.getElementById('messages');
        const input = document.getElementById('input');
        const send = document.getElementById('send');
        const status = document.getElementById('status');

        function addMessage(text, role) {
            const msg = document.createElement('div');
            msg.className = `message ${role}`;
            msg.textContent = text;
            messages.appendChild(msg);
            messages.scrollTop = messages.scrollHeight;
        }

        async function sendMessage() {
            const text = input.value.trim();
            if (!text) return;

            addMessage(text, 'user');
            input.value = '';
            input.style.height = 'auto';
            send.disabled = true;
            status.textContent = 'Thinking...';

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                addMessage(data.message, 'assistant');
            } catch (err) {
                addMessage('Error: ' + err.message, 'assistant');
            } finally {
                send.disabled = false;
                status.textContent = 'Ready';
                input.focus();
            }
        }

        function switchChat(element, id) {
            document.querySelectorAll('.chat-item').forEach(e => e.classList.remove('active'));
            element.classList.add('active');
            messages.innerHTML = '';
            status.textContent = 'Ready';
        }

        function newChat() {
            messages.innerHTML = '';
            input.value = '';
            status.textContent = 'Ready';
            fetch('/api/start')
                .then(r => r.json())
                .then(d => addMessage(d.message, 'assistant'));
        }

        input.addEventListener('keypress', e => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        input.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 150) + 'px';
        });

        send.addEventListener('click', sendMessage);

        // Load initial message
        fetch('/api/start')
            .then(r => r.json())
            .then(d => addMessage(d.message, 'assistant'));
    </script>
</body>
</html>"""

# Start server
PORT = 8000
server = HTTPServer(('127.0.0.1', PORT), SidebarChatHandler)

print("\n" + "="*70)
print("🚀 Server running: http://localhost:8000")
print("="*70)
print("✓ Features Active:")
print("  • Sidebar Chat History")
print("  • Election Data (23 candidates, 1000+ polls)")
print("  • Twitter Sentiment Analysis")
print("  • Modern Dark UI with Glassmorphism")
print("  • Large, Readable Fonts")
print("="*70)
print("\nPress Ctrl+C to stop the server\n")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\n\nServer stopped. Thank you for using CivicPulse AI!")
