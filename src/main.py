"""
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
        greeting = ("Welcome to CivicPulse! 🗳️\n\n"
            "I'm here to help you prepare for the upcoming election. "
            "Whether you're a first-time voter or a seasoned participant, "
            "I'll guide you through every step of the process.\n\n"
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
            message = ("Great! You're already registered. 📋\n\nNow let's find your polling location and create a voting plan. What's your home address or ZIP code?")
        else:
            message = ("Don't worry—I'll help you get registered! 📝\n\nWhat state are you voting in? (You can say the state name or abbreviation, e.g., 'California' or 'CA')")
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
                message = (f"Perfect! I found your polling location:\n\n"
                    f"📍 {location_data.get('name', 'Polling Station')}\n"
                    f"   {location_data.get('address', user_input)}\n"
                    f"   Hours: {location_data.get('hours', 'Check with your local election office')}\n\n"
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
                message = (f"Important dates for {state_input}:\n\n"
                    f"📅 Registration Deadline: {deadline_info.get('deadline', 'TBD')}\n"
                    f"   Days remaining: {deadline_info.get('days_remaining', 'N/A')}\n\n"
                    f"Here's what you need to know:\n"
                    f"• You can register online at your state election office\n"
                    f"• Bring valid ID and proof of residency\n\n"
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
                    cal_message = "\n✅ Calendar events created! Check your email for invites."
                else:
                    cal_message = "\n(You can add these dates to your calendar manually)"
                message = (f"Here's your personalized election timeline:\n\n"
                    f"{timeline.get('summary', '')}"
                    f"{cal_message}\n\n"
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
            message = ("Thank you for letting me know. Here are common accommodations available:\n\n"
                "✓ Curbside voting\n"
                "✓ Accessible voting machines\n"
                "✓ Assistance with ballots\n"
                "✓ Extended time for voting\n\n"
                "Contact your local election office at least 5 days before election day to arrange your specific accommodations.\n\n"
                "You're all set! Good luck voting! 🗳️")
        else:
            message = ("Perfect! You're all prepared for election day. Here's a quick reminder:\n\n"
                "✓ Bring your ID and any required documents\n"
                "✓ Arrive early to avoid lines\n"
                "✓ Review candidates beforehand if possible\n\n"
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
        print(f"\nAssistant: {response}\n")

if __name__ == "__main__":
    main()
