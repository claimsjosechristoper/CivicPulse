#!/usr/bin/env python3
"""
CivicPulse - Setup and Localhost Runner

This script:
1. Creates the project directory structure
2. Generates all source files from embedded code
3. Runs the application on localhost
"""

import os
import sys
import subprocess
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent

def create_directories():
    """Create all necessary directories."""
    directories = ['src', 'tests', '.agent/skills', 'docs']
    for d in directories:
        (PROJECT_ROOT / d).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {d}")

def create_source_files():
    """Create all source files."""
    
    # src/__init__.py
    (PROJECT_ROOT / 'src' / '__init__.py').write_text(
        '"""CivicPulse - Election Assistant Package"""\n__version__ = "1.0.0"\n', encoding='utf-8'
    )
    
    # tests/__init__.py
    (PROJECT_ROOT / 'tests' / '__init__.py').write_text(
        '"""Tests for CivicPulse Election Assistant"""\n', encoding='utf-8'
    )
    
    # src/logic.py
    (PROJECT_ROOT / 'src' / 'logic.py').write_text('''"""
Election Assistant Logic Module

Implements decision-making algorithms, state management, and timeline generation
for the CivicPulse election assistant.
"""

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import re
import logging

logger = logging.getLogger(__name__)

class ConversationState(Enum):
    """Enumeration of conversation states."""
    INITIAL = "initial"
    REGISTRATION_CHECK = "registration_check"
    TIMELINE_GENERATION = "timeline_generation"
    VOTING_DAY_PREP = "voting_day_prep"

class ElectionAssistant:
    """Core logic engine for election assistance decisions."""

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
        """Initialize the election assistant logic engine."""
        self.states_reverse = {v.lower(): k for k, v in self.STATES.items()}

    @staticmethod
    def parse_yes_no(user_input: str) -> Optional[bool]:
        """Parse yes/no responses from user input."""
        lower_input = user_input.lower().strip()
        yes_patterns = ['yes', 'yeah', 'yep', 'sure', 'absolutely', 'y', 'true', 'ok']
        no_patterns = ['no', 'nope', 'nah', 'negative', 'n', 'false']
        
        if any(lower_input.startswith(p) for p in yes_patterns):
            return True
        if any(lower_input.startswith(p) for p in no_patterns):
            return False
        return None

    def normalize_state(self, state_input: str) -> Optional[str]:
        """Normalize state input to standard abbreviation."""
        state_upper = state_input.strip().upper()
        if state_upper in self.STATES:
            return state_upper
        normalized = state_input.strip().lower()
        if normalized in self.states_reverse:
            return self.states_reverse[normalized]
        return None

    def generate_election_timeline(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a personalized election timeline based on user profile."""
        election_date = datetime(2024, 11, 5)
        
        timeline = {'summary': '', 'calendar_events': [], 'key_dates': []}

        if not user_profile.get('is_registered'):
            registration_deadline = election_date - timedelta(days=30)
            timeline['key_dates'] = [
                {'date': registration_deadline.strftime('%m/%d/%Y'), 'event': 'Registration Deadline (IMPORTANT!)', 'action': 'Complete your voter registration'},
                {'date': (election_date - timedelta(days=7)).strftime('%m/%d/%Y'), 'event': 'Verify Registration Status', 'action': 'Check that you\\'re registered to vote'},
                {'date': election_date.strftime('%m/%d/%Y'), 'event': 'Election Day', 'action': 'Vote!'}
            ]
            timeline['summary'] = (f"📅 KEY DATES:\\n"
                f"1. {registration_deadline.strftime('%B %d, %Y')} - Registration Deadline\\n"
                f"2. {(election_date - timedelta(days=7)).strftime('%B %d, %Y')} - Verify Registration\\n"
                f"3. {election_date.strftime('%B %d, %Y')} - Election Day\\n")
            timeline['calendar_events'] = [
                {'title': '⏰ Voter Registration Deadline - Act Now!', 'date': registration_deadline.strftime('%Y-%m-%d'), 'description': 'Last day to register to vote. Visit your state election office.'},
                {'title': '✓ Verify Your Voter Registration', 'date': (election_date - timedelta(days=7)).strftime('%Y-%m-%d'), 'description': 'Confirm your registration status before election day.'},
                {'title': '🗳️ Election Day', 'date': election_date.strftime('%Y-%m-%d'), 'description': 'Go vote! Remember to bring your ID and arrive early.'}
            ]
        else:
            early_voting_start = election_date - timedelta(days=21)
            timeline['key_dates'] = [
                {'date': early_voting_start.strftime('%m/%d/%Y'), 'event': 'Early Voting Begins', 'action': 'You can vote in person at designated locations'},
                {'date': (election_date - timedelta(days=7)).strftime('%m/%d/%Y'), 'event': 'Mail-in Ballot Request Deadline', 'action': 'Request your mail-in ballot'},
                {'date': election_date.strftime('%m/%d/%Y'), 'event': 'Election Day', 'action': 'Vote at your polling location'}
            ]
            location_info = user_profile.get('polling_location', {})
            location_name = location_info.get('name', 'your designated polling location')
            timeline['summary'] = (f"📅 YOUR VOTING TIMELINE:\\n"
                f"1. {early_voting_start.strftime('%B %d, %Y')} - Early Voting Starts\\n"
                f"2. {(election_date - timedelta(days=7)).strftime('%B %d, %Y')} - Mail-in Deadline\\n"
                f"3. {election_date.strftime('%B %d, %Y')} - Election Day at {location_name}\\n")
            timeline['calendar_events'] = [
                {'title': '🗳️ Early Voting Begins', 'date': early_voting_start.strftime('%Y-%m-%d'), 'description': f'Early voting is now available. Visit {location_name}.'},
                {'title': '📬 Mail-in Ballot Deadline', 'date': (election_date - timedelta(days=7)).strftime('%Y-%m-%d'), 'description': 'Last day to request a mail-in ballot.'},
                {'title': '🗳️ Election Day - VOTE!', 'date': election_date.strftime('%Y-%m-%d'), 'description': f'Vote at {location_name}. Bring ID and arrive early!'}
            ]
        return timeline

    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_zip_code(self, zip_code: str) -> bool:
        """Validate US ZIP code format."""
        pattern = r'^\\d{5}(-\\d{4})?$'
        return re.match(pattern, zip_code) is not None
''', encoding='utf-8')
    
    # src/services.py
    (PROJECT_ROOT / 'src' / 'services.py').write_text('''"""
Google Services Integration Module

Handles interactions with Google APIs for deadline lookups and polling location searches.
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class GoogleServicesClient:
    """Client for Google Services API interactions."""

    def __init__(self, api_key: Optional[str] = None, calendar_id: Optional[str] = None):
        """Initialize Google Services client."""
        self.api_key = api_key
        self.calendar_id = calendar_id
        self.is_configured = bool(api_key and calendar_id)
        if not self.is_configured:
            logger.warning("Google Services not fully configured. Using mock data.")

    def search_registration_deadline(self, state: str) -> Dict[str, Any]:
        """Search for voter registration deadlines in a specific state."""
        return self._get_mock_registration_deadline(state)

    @staticmethod
    def _get_mock_registration_deadline(state: str) -> Dict[str, Any]:
        """Return mock registration deadline data."""
        mock_deadlines = {
            'CA': {'deadline': '2024-10-07', 'days_remaining': 10},
            'TX': {'deadline': '2024-10-07', 'days_remaining': 10},
            'NY': {'deadline': '2024-10-12', 'days_remaining': 15},
            'FL': {'deadline': '2024-10-07', 'days_remaining': 10},
        }
        state_code = state.upper() if len(state) == 2 else state[:2].upper()
        return mock_deadlines.get(state_code, {'deadline': 'Contact your state', 'days_remaining': 'N/A'})

    def search_polling_location(self, location: str) -> Optional[Dict[str, Any]]:
        """Search for polling locations using Google Maps."""
        return self._get_mock_polling_location(location)

    @staticmethod
    def _get_mock_polling_location(location: str) -> Dict[str, Any]:
        """Return mock polling location data."""
        return {
            'name': 'City Community Center',
            'address': f'{location}, USA',
            'hours': '7:00 AM - 8:00 PM (Election Day)',
            'accessible': True,
            'parking': 'Free parking available',
            'phone': '(555) 000-0000'
        }

    def create_calendar_event(self, event: Dict[str, str], email: str) -> bool:
        """Create a Google Calendar event for election reminders."""
        logger.info(f"Creating calendar event '{event.get('title')}' for {email}")
        return True

    def get_election_information(self, state: str) -> Dict[str, Any]:
        """Retrieve comprehensive election information for a state."""
        return {
            'registration_deadline': self.search_registration_deadline(state),
            'early_voting_info': {'available': True, 'start_date': '2024-10-15', 'end_date': '2024-11-04', 'details': 'Early voting is available at designated locations.'},
            'mail_in_voting_info': {'available': True, 'deadline': '2024-11-01', 'method': 'Request online or by mail'},
            'accessible_voting': {'accommodations': ['Curbside voting', 'Accessible voting machines', 'Assistance with ballot', 'Extended voting time', 'Language assistance'], 'contact': 'Contact your local election office'}
        }
''', encoding='utf-8')
    
    # src/main.py
    (PROJECT_ROOT / 'src' / 'main.py').write_text('''"""
CivicPulse: Interactive Election Assistant for Voter Education & Readiness
"""

import logging
from typing import Optional
from logic import ElectionAssistant, ConversationState
from services import GoogleServicesClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CivicPulseAssistant:
    """Main class for the CivicPulse election assistant."""

    def __init__(self, api_key: Optional[str] = None, calendar_id: Optional[str] = None):
        """Initialize the CivicPulse assistant."""
        self.logic = ElectionAssistant()
        self.services = GoogleServicesClient(api_key=api_key, calendar_id=calendar_id)
        self.current_state = ConversationState.INITIAL
        self.user_profile = {}
        self.conversation_history = []
        logger.info("CivicPulse Assistant initialized")

    def start_conversation(self) -> str:
        """Initiate the election assistance conversation."""
        self.current_state = ConversationState.INITIAL
        greeting = ("Welcome to CivicPulse! 🗳️\\n\\n"
            "I'm here to help you prepare for the upcoming election. "
            "Whether you're a first-time voter or a seasoned participant, "
            "I'll guide you through every step of the process.\\n\\n"
            "Let's start: Are you registered to vote? (yes/no)")
        self.conversation_history.append({"role": "assistant", "content": greeting})
        logger.info("Conversation started")
        return greeting

    def process_user_input(self, user_input: str) -> str:
        """Process user input and transition state accordingly."""
        self.conversation_history.append({"role": "user", "content": user_input})
        logger.info(f"Processing input: {user_input} | Current state: {self.current_state.name}")

        if self.current_state == ConversationState.INITIAL:
            response = self._handle_registration_check(user_input)
        elif self.current_state == ConversationState.REGISTRATION_CHECK:
            response = self._handle_registration_details(user_input)
        elif self.current_state == ConversationState.TIMELINE_GENERATION:
            response = self._handle_timeline_generation(user_input)
        elif self.current_state == ConversationState.VOTING_DAY_PREP:
            response = self._handle_voting_day_prep(user_input)
        else:
            response = "I'm not sure how to proceed. Let's start over. Are you registered to vote?"
            self.current_state = ConversationState.INITIAL

        self.conversation_history.append({"role": "assistant", "content": response})
        return response

    def _handle_registration_check(self, user_input: str) -> str:
        """Handle the registration check state."""
        is_registered = self.logic.parse_yes_no(user_input)
        if is_registered is None:
            return "I didn't quite get that. Could you please answer with 'yes' or 'no'?"
        self.user_profile['is_registered'] = is_registered
        self.current_state = ConversationState.REGISTRATION_CHECK
        if is_registered:
            message = ("Great! You're already registered. 📋\\n\\nNow let's find your polling location and create a voting plan. What's your home address or ZIP code?")
        else:
            message = ("Don't worry—I'll help you get registered! 📝\\n\\nWhat state are you voting in? (You can say the state name or abbreviation, e.g., 'California' or 'CA')")
        return message

    def _handle_registration_details(self, user_input: str) -> str:
        """Handle registration details based on registration status."""
        if self.user_profile.get('is_registered'):
            return self._handle_polling_location(user_input)
        else:
            return self._handle_registration_deadline(user_input)

    def _handle_polling_location(self, user_input: str) -> str:
        """Handle polling location lookup for registered voters."""
        try:
            location_data = self.services.search_polling_location(user_input)
            if location_data:
                self.user_profile['location'] = user_input
                self.user_profile['polling_location'] = location_data
                self.current_state = ConversationState.TIMELINE_GENERATION
                message = (f"Perfect! I found your polling location:\\n\\n"
                    f"📍 {location_data.get('name', 'Polling Station')}\\n"
                    f"   {location_data.get('address', user_input)}\\n"
                    f"   Hours: {location_data.get('hours', 'Check with your local election office')}\\n\\n"
                    f"Now, let's set up election day reminders. What email should I use for calendar invites?")
                return message
            else:
                return "I couldn't find that location. Could you provide more details? (e.g., full address or ZIP code)"
        except Exception as e:
            logger.error(f"Error searching polling location: {e}")
            return "Sorry, I had trouble looking that up. Please try again or contact your local election office."

    def _handle_registration_deadline(self, state_input: str) -> str:
        """Handle registration deadline for unregistered voters."""
        try:
            deadline_info = self.services.search_registration_deadline(state_input)
            if deadline_info:
                self.user_profile['state'] = state_input
                self.user_profile['registration_deadline'] = deadline_info
                self.current_state = ConversationState.TIMELINE_GENERATION
                message = (f"Important dates for {state_input}:\\n\\n"
                    f"📅 Registration Deadline: {deadline_info.get('deadline', 'TBD')}\\n"
                    f"   Days remaining: {deadline_info.get('days_remaining', 'N/A')}\\n\\n"
                    f"Here's what you need to know:\\n"
                    f"• You can register online at your state election office\\n"
                    f"• Bring valid ID and proof of residency\\n\\n"
                    f"Would you like me to help you register or set up a reminder? (yes/no)")
                return message
            else:
                return f"I couldn't find information for that state. Please visit your state's election office website or reply with a different state."
        except Exception as e:
            logger.error(f"Error searching registration deadline: {e}")
            return "Sorry, I had trouble retrieving that information. Please try again."

    def _handle_timeline_generation(self, user_input: str) -> str:
        """Handle timeline generation and calendar setup."""
        try:
            should_create_event = self.logic.parse_yes_no(user_input)
            if should_create_event is None and '@' not in user_input:
                return "Could you provide your email address for calendar invites? (or 'skip')"
            email = user_input if '@' in user_input else None
            if email or (should_create_event is not None):
                self.user_profile['email'] = email
                self.current_state = ConversationState.VOTING_DAY_PREP
                timeline = self.logic.generate_election_timeline(self.user_profile)
                if email:
                    for event in timeline.get('calendar_events', []):
                        self.services.create_calendar_event(event, email)
                    cal_message = "\\n✅ Calendar events created! Check your email for invites."
                else:
                    cal_message = "\\n(You can add these dates to your calendar manually)"
                message = (f"Here's your personalized election timeline:\\n\\n"
                    f"{timeline.get('summary', '')}"
                    f"{cal_message}\\n\\n"
                    f"Last question: Do you need any accessible voting accommodations? (yes/no)")
                return message
        except Exception as e:
            logger.error(f"Error generating timeline: {e}")
            return "I had trouble generating your timeline. Could you try again?"
        return "I need a bit more information. What's your email?"

    def _handle_voting_day_prep(self, user_input: str) -> str:
        """Handle voting day preparation and accessibility needs."""
        needs_accommodation = self.logic.parse_yes_no(user_input)
        if needs_accommodation is None:
            return "I didn't catch that. Do you need accessible voting accommodations? (yes/no)"
        self.user_profile['needs_accommodation'] = needs_accommodation
        self.current_state = ConversationState.VOTING_DAY_PREP
        if needs_accommodation:
            message = ("Thank you for letting me know. Here are common accommodations available:\\n\\n"
                "✓ Curbside voting\\n"
                "✓ Accessible voting machines\\n"
                "✓ Assistance with ballots\\n"
                "✓ Extended time for voting\\n\\n"
                "Contact your local election office at least 5 days before election day to arrange your specific accommodations.\\n\\n"
                "You're all set! Good luck voting! 🗳️")
        else:
            message = ("Perfect! You're all prepared for election day. Here's a quick reminder:\\n\\n"
                "✓ Bring your ID and any required documents\\n"
                "✓ Arrive early to avoid lines\\n"
                "✓ Review candidates beforehand if possible\\n\\n"
                "Thank you for participating in democracy! 🗳️")
        return message

    def get_conversation_history(self):
        """Return the full conversation history."""
        return self.conversation_history

    def reset(self):
        """Reset the assistant to initial state."""
        self.current_state = ConversationState.INITIAL
        self.user_profile = {}
        self.conversation_history = []
        logger.info("Assistant reset to initial state")

def main():
    """Main entry point for the CivicPulse assistant."""
    assistant = CivicPulseAssistant()
    print(assistant.start_conversation())
    print()
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Assistant: Thank you for using CivicPulse. See you at the polls! 🗳️")
            break
        if not user_input:
            continue
        response = assistant.process_user_input(user_input)
        print(f"\\nAssistant: {response}\\n")

if __name__ == "__main__":
    main()
''', encoding='utf-8')
    
    print("✓ Created all source files")

def main():
    """Main setup function."""
    print("🗳️  CivicPulse Localhost Setup & Run")
    print("=" * 60)
    
    print("\n1. Creating directory structure...")
    create_directories()
    
    print("\n2. Creating source files...")
    create_source_files()
    
    print("\n3. Starting web interface...")
    print("=" * 60)
    
    # Run the web app
    try:
        subprocess.run([sys.executable, str(PROJECT_ROOT / 'web_app.py')])
    except KeyboardInterrupt:
        print("\n\n✅ Shutting down CivicPulse. Thank you!")

if __name__ == '__main__':
    main()
