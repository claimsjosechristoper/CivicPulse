#!/usr/bin/env python3
"""Quick test of CivicPulse without web server"""
import sys
from pathlib import Path

# Setup
project = Path(__file__).parent
sys.path.insert(0, str(project / 'src'))

# Create files if needed
print("Setting up CivicPulse...")
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
            timeline['summary'] = f"📅 REGISTRATION TIMELINE:\\n1. {rd.strftime('%B %d, %Y')} - Registration Deadline\\n2. {(election_date - timedelta(days=7)).strftime('%B %d, %Y')} - Verify Registration\\n3. {election_date.strftime('%B %d, %Y')} - Election Day\\n"
        else:
            ev = election_date - timedelta(days=21)
            timeline['summary'] = f"📅 VOTING TIMELINE:\\n1. {ev.strftime('%B %d, %Y')} - Early Voting Starts\\n2. {(election_date - timedelta(days=7)).strftime('%B %d, %Y')} - Mail-in Deadline\\n3. {election_date.strftime('%B %d, %Y')} - Election Day\\n"
        return timeline
''')

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
''')

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
        return "Welcome to CivicPulse! 🗳️\\n\\nI'm here to help you prepare for the upcoming election. Whether you're a first-time voter or seasoned, I'll guide you through every step.\\n\\nLet's start: Are you registered to vote? (yes/no)"
    
    def process_user_input(self, user_input: str) -> str:
        if self.current_state == ConversationState.INITIAL:
            is_registered = self.logic.parse_yes_no(user_input)
            if is_registered is None:
                return "I didn't quite get that. Could you answer with 'yes' or 'no'?"
            self.user_profile['is_registered'] = is_registered
            self.current_state = ConversationState.REGISTRATION_CHECK
            if is_registered:
                return "Great! You're registered. 📋\\n\\nLet's find your polling location. What's your home address or ZIP code?"
            else:
                return "Don't worry—I'll help you register! 📝\\n\\nWhat state are you voting in? (e.g., California or CA)"
        
        elif self.current_state == ConversationState.REGISTRATION_CHECK:
            if self.user_profile.get('is_registered'):
                loc = self.services.search_polling_location(user_input)
                self.current_state = ConversationState.TIMELINE_GENERATION
                return f"Found your polling location:\\n\\n📍 {loc['name']}\\n{loc['address']}\\nHours: {loc['hours']}\\n\\nWhat's your email for reminders?"
            else:
                info = self.services.search_registration_deadline(user_input)
                self.current_state = ConversationState.TIMELINE_GENERATION
                return f"Important dates for {user_input}:\\n\\n📅 Deadline: {info['deadline']}\\nDays left: {info['days_remaining']}\\n\\nWant a reminder? (yes/no)"
        
        elif self.current_state == ConversationState.TIMELINE_GENERATION:
            timeline = self.logic.generate_election_timeline(self.user_profile)
            self.current_state = ConversationState.VOTING_DAY_PREP
            return f"{timeline['summary']}\\nNeed accessible voting accommodations? (yes/no)"
        
        else:
            needs = self.logic.parse_yes_no(user_input)
            if needs:
                return "Accommodations:\\n✓ Curbside\\n✓ Accessible machines\\n✓ Ballot help\\n✓ Extra time\\n\\nContact your election office 5 days before. You're set! 🗳️"
            else:
                return "Checklist:\\n✓ Bring ID\\n✓ Arrive early\\n✓ Review candidates\\n\\nThank you for voting! 🗳️"
    
    def reset(self):
        self.current_state = ConversationState.INITIAL
        self.user_profile = {}
''')

# Run it
from main import CivicPulseAssistant
print("\n" + "="*70)
print("🗳️  CIVICPULSE - Election Assistant - Running on Localhost")
print("="*70)
print()

assistant = CivicPulseAssistant()
print("ASSISTANT:", assistant.start_conversation())
print()

while True:
    user_input = input("YOU: ").strip()
    if user_input.lower() in ['exit', 'quit']:
        print("\nAssistant: Thank you for using CivicPulse. See you at the polls! 🗳️")
        break
    if user_input:
        response = assistant.process_user_input(user_input)
        print(f"\nASSISTANT: {response}\n")
