#!/usr/bin/env python3
"""
CivicPulse - Complete Setup and Localhost Runner
Automatically creates all files and starts the web server
"""

import os
import sys
from pathlib import Path
import subprocess

def setup_and_run():
    """Complete setup and run function."""
    
    project_root = Path(__file__).parent
    
    print("\n" + "="*70)
    print("🗳️  CivicPulse - Election Assistant - Localhost Setup")
    print("="*70)
    
    # Step 1: Create directories
    print("\n📁 Step 1: Creating directory structure...")
    dirs = ['src', 'tests', '.agent/skills']
    for d in dirs:
        (project_root / d).mkdir(parents=True, exist_ok=True)
    print("   ✓ Directories created")
    
    # Step 2: Create __init__ files
    print("\n📝 Step 2: Creating Python package files...")
    (project_root / 'src' / '__init__.py').write_text('"""CivicPulse Package"""\n')
    (project_root / 'tests' / '__init__.py').write_text('"""Tests Package"""\n')
    print("   ✓ Package files created")
    
    # Step 3: Create main modules
    print("\n📝 Step 3: Creating source modules...")
    
    # Create logic.py
    with open(project_root / 'src' / 'logic.py', 'w') as f:
        f.write('''"""Election Assistant Logic Module"""
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import re
import logging

logger = logging.getLogger(__name__)

class ConversationState(Enum):
    INITIAL = "initial"
    REGISTRATION_CHECK = "registration_check"
    TIMELINE_GENERATION = "timeline_generation"
    VOTING_DAY_PREP = "voting_day_prep"

class ElectionAssistant:
    STATES = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
        'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
        'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
        'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
        'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
        'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
        'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
        'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
        'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
        'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
        'WI': 'Wisconsin', 'WY': 'Wyoming'
    }

    def __init__(self):
        self.states_reverse = {v.lower(): k for k, v in self.STATES.items()}

    @staticmethod
    def parse_yes_no(user_input: str) -> Optional[bool]:
        lower_input = user_input.lower().strip()
        yes_patterns = ['yes', 'yeah', 'yep', 'sure', 'absolutely', 'y', 'ok']
        no_patterns = ['no', 'nope', 'nah', 'negative', 'n']
        if any(lower_input.startswith(p) for p in yes_patterns):
            return True
        if any(lower_input.startswith(p) for p in no_patterns):
            return False
        return None

    def validate_email(self, email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def generate_election_timeline(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        election_date = datetime(2024, 11, 5)
        timeline = {'summary': '', 'calendar_events': [], 'key_dates': []}
        
        if not user_profile.get('is_registered'):
            registration_deadline = election_date - timedelta(days=30)
            timeline['summary'] = f"📅 REGISTRATION TIMELINE:\\n1. {registration_deadline.strftime('%B %d, %Y')} - Registration Deadline\\n2. {(election_date - timedelta(days=7)).strftime('%B %d, %Y')} - Verify Registration\\n3. {election_date.strftime('%B %d, %Y')} - Election Day\\n"
        else:
            early_voting = election_date - timedelta(days=21)
            timeline['summary'] = f"📅 VOTING TIMELINE:\\n1. {early_voting.strftime('%B %d, %Y')} - Early Voting Starts\\n2. {(election_date - timedelta(days=7)).strftime('%B %d, %Y')} - Mail-in Deadline\\n3. {election_date.strftime('%B %d, %Y')} - Election Day\\n"
        
        return timeline
''')
    
    # Create services.py
    with open(project_root / 'src' / 'services.py', 'w') as f:
        f.write('''"""Google Services Integration Module"""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class GoogleServicesClient:
    def __init__(self, api_key: Optional[str] = None, calendar_id: Optional[str] = None):
        self.api_key = api_key
        self.calendar_id = calendar_id
        self.is_configured = bool(api_key and calendar_id)

    def search_registration_deadline(self, state: str) -> Dict[str, Any]:
        mock_deadlines = {
            'CA': {'deadline': '2024-10-07', 'days_remaining': 10},
            'TX': {'deadline': '2024-10-07', 'days_remaining': 10},
            'NY': {'deadline': '2024-10-12', 'days_remaining': 15},
            'FL': {'deadline': '2024-10-07', 'days_remaining': 10},
        }
        state_code = state.upper() if len(state) == 2 else state[:2].upper()
        return mock_deadlines.get(state_code, {'deadline': 'Contact your state', 'days_remaining': 'N/A'})

    def search_polling_location(self, location: str) -> Optional[Dict[str, Any]]:
        return {
            'name': 'City Community Center',
            'address': f'{location}, USA',
            'hours': '7:00 AM - 8:00 PM (Election Day)',
            'accessible': True,
            'parking': 'Free parking available'
        }

    def create_calendar_event(self, event: Dict[str, str], email: str) -> bool:
        logger.info(f"Creating calendar event for {email}")
        return True
''')
    
    # Create main.py
    with open(project_root / 'src' / 'main.py', 'w') as f:
        f.write('''"""CivicPulse Main Module"""
import logging
from typing import Optional
from logic import ElectionAssistant, ConversationState
from services import GoogleServicesClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CivicPulseAssistant:
    def __init__(self, api_key: Optional[str] = None, calendar_id: Optional[str] = None):
        self.logic = ElectionAssistant()
        self.services = GoogleServicesClient(api_key=api_key, calendar_id=calendar_id)
        self.current_state = ConversationState.INITIAL
        self.user_profile = {}
        self.conversation_history = []
        logger.info("CivicPulse Assistant initialized")

    def start_conversation(self) -> str:
        self.current_state = ConversationState.INITIAL
        greeting = "Welcome to CivicPulse! 🗳️\\n\\nI'm here to help you prepare for the upcoming election. Whether you're a first-time voter or a seasoned participant, I'll guide you through every step.\\n\\nLet's start: Are you registered to vote? (yes/no)"
        self.conversation_history.append({"role": "assistant", "content": greeting})
        return greeting

    def process_user_input(self, user_input: str) -> str:
        self.conversation_history.append({"role": "user", "content": user_input})
        
        if self.current_state == ConversationState.INITIAL:
            is_registered = self.logic.parse_yes_no(user_input)
            if is_registered is None:
                return "I didn't quite get that. Could you please answer with 'yes' or 'no'?"
            self.user_profile['is_registered'] = is_registered
            self.current_state = ConversationState.REGISTRATION_CHECK
            
            if is_registered:
                return "Great! You're already registered. 📋\\n\\nNow let's find your polling location. What's your home address or ZIP code?"
            else:
                return "Don't worry—I'll help you get registered! 📝\\n\\nWhat state are you voting in? (e.g., California or CA)"
        
        elif self.current_state == ConversationState.REGISTRATION_CHECK:
            if self.user_profile.get('is_registered'):
                location_data = self.services.search_polling_location(user_input)
                self.user_profile['polling_location'] = location_data
                self.current_state = ConversationState.TIMELINE_GENERATION
                return f"Found your polling location:\\n\\n📍 {location_data['name']}\\n{location_data['address']}\\nHours: {location_data['hours']}\\n\\nWhat's your email for calendar reminders?"
            else:
                deadline_info = self.services.search_registration_deadline(user_input)
                self.current_state = ConversationState.TIMELINE_GENERATION
                return f"Important dates for {user_input}:\\n\\n📅 Registration Deadline: {deadline_info['deadline']}\\nDays remaining: {deadline_info['days_remaining']}\\n\\nWould you like me to set up a reminder? (yes/no)"
        
        elif self.current_state == ConversationState.TIMELINE_GENERATION:
            timeline = self.logic.generate_election_timeline(self.user_profile)
            self.current_state = ConversationState.VOTING_DAY_PREP
            return f"Here's your personalized timeline:\\n\\n{timeline['summary']}\\nDo you need accessible voting accommodations? (yes/no)"
        
        elif self.current_state == ConversationState.VOTING_DAY_PREP:
            needs_accommodation = self.logic.parse_yes_no(user_input)
            if needs_accommodation:
                return "Accommodations available:\\n✓ Curbside voting\\n✓ Accessible machines\\n✓ Ballot assistance\\n✓ Extended time\\n\\nContact your election office 5 days before. You're all set! 🗳️"
            else:
                return "Perfect! Remember to:\\n✓ Bring your ID\\n✓ Arrive early\\n✓ Review candidates\\n\\nThank you for voting! 🗳️"
        
        return "Let's start over. Are you registered to vote?"

    def reset(self):
        self.current_state = ConversationState.INITIAL
        self.user_profile = {}
        self.conversation_history = []
''')
    
    print("   ✓ Source modules created")
    
    # Step 4: Start the web server
    print("\n🌐 Step 4: Starting web server...")
    print("   ✓ Importing web server...")
    
    # Run web_app.py
    web_app_path = project_root / 'web_app.py'
    if not web_app_path.exists():
        print("   ⚠️  web_app.py not found, using terminal interface")
        # Fallback to CLI
        sys.path.insert(0, str(project_root / 'src'))
        from main import CivicPulseAssistant
        assistant = CivicPulseAssistant()
        print(assistant.start_conversation())
        while True:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                break
            print(f"\nAssistant: {assistant.process_user_input(user_input)}")
    else:
        print("   ✓ Starting web interface...")
        try:
            subprocess.run([sys.executable, str(web_app_path)])
        except KeyboardInterrupt:
            print("\n\n✅ Server stopped. Thank you for using CivicPulse! 🗳️\n")

if __name__ == '__main__':
    setup_and_run()
