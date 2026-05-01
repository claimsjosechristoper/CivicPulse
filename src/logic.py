"""
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
                {'date': (election_date - timedelta(days=7)).strftime('%m/%d/%Y'), 'event': 'Verify Registration Status', 'action': 'Check that you\'re registered to vote'},
                {'date': election_date.strftime('%m/%d/%Y'), 'event': 'Election Day', 'action': 'Vote!'}
            ]
            timeline['summary'] = (f"📅 KEY DATES:\n"
                f"1. {registration_deadline.strftime('%B %d, %Y')} - Registration Deadline\n"
                f"2. {(election_date - timedelta(days=7)).strftime('%B %d, %Y')} - Verify Registration\n"
                f"3. {election_date.strftime('%B %d, %Y')} - Election Day\n")
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
            timeline['summary'] = (f"📅 YOUR VOTING TIMELINE:\n"
                f"1. {early_voting_start.strftime('%B %d, %Y')} - Early Voting Starts\n"
                f"2. {(election_date - timedelta(days=7)).strftime('%B %d, %Y')} - Mail-in Deadline\n"
                f"3. {election_date.strftime('%B %d, %Y')} - Election Day at {location_name}\n")
            timeline['calendar_events'] = [
                {'title': '🗳️ Early Voting Begins', 'date': early_voting_start.strftime('%Y-%m-%d'), 'description': f'Early voting is now available. Visit {location_name}.'},
                {'title': '📬 Mail-in Ballot Deadline', 'date': (election_date - timedelta(days=7)).strftime('%Y-%m-%d'), 'description': 'Last day to request a mail-in ballot.'},
                {'title': '🗳️ Election Day - VOTE!', 'date': election_date.strftime('%Y-%m-%d'), 'description': f'Vote at {location_name}. Bring ID and arrive early!'}
            ]
        return timeline

    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_zip_code(self, zip_code: str) -> bool:
        """Validate US ZIP code format."""
        pattern = r'^\d{5}(-\d{4})?$'
        return re.match(pattern, zip_code) is not None
