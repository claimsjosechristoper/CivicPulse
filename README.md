# CivicPulse 🗳️

## Overview

**CivicPulse** is an intelligent, state-based election assistant designed to help voters navigate the voting process with confidence and clarity. Built within the Google Antigravity environment, this interactive guide focuses on the **Voter Education & Readiness** vertical—helping citizens understand registration requirements, deadlines, polling locations, and voting day preparations.

**Vertical:** Voter Education & Readiness  
**Tech Stack:** Python 3.10+, Google Search API, Google Calendar API, Google Maps API  
**License:** MIT

---

## Problem Statement & Approach

### The Challenge
Many eligible voters face barriers to participation due to:
- Uncertainty about registration deadlines in their state
- Difficulty finding their polling location
- Lack of information about voting options (early voting, mail-in, etc.)
- Accessibility concerns
- Confusion about required documentation

### Our Approach
CivicPulse implements a **conversational, state-based assistant** that:
1. Determines voter registration status
2. Dynamically prioritizes next steps based on user needs
3. Provides real-time deadline information via Google Search API
4. Integrates polling locations using Google Maps API
5. Generates personalized calendar reminders via Google Calendar API
6. Ensures equal access with accessibility-first design

---

## Logic Flow

### Conversation State Machine
```
┌─────────────┐
│   INITIAL   │  ← User starts conversation
└──────┬──────┘
       │ (Are you registered?)
       ▼
┌──────────────────────┐
│ REGISTRATION_CHECK   │
├──────────────────────┤
│ IF Unregistered:     │ → Ask for state → Fetch deadline
│ IF Registered:       │ → Ask for location → Find polling place
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ TIMELINE_GENERATION  │  Generate personalized calendar
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ VOTING_DAY_PREP      │  Final preparations & accessibility
└──────────────────────┘
```

### Decision-Making Logic

**For Unregistered Voters (Priority: Registration)**
1. Identify state
2. Fetch registration deadline via Google Search API
3. Display deadline + days remaining
4. Provide registration instructions
5. Create calendar reminder
6. Transition to voting day preparation

**For Registered Voters (Priority: Polling Location)**
1. Request home address or ZIP code
2. Search polling locations via Google Maps API
3. Display location + hours + accessibility info
4. Create early voting and election day reminders
5. Prepare voting day checklist

### Timeline Generation
- **Unregistered:** Focuses on registration deadline, verification date, election day
- **Registered:** Includes early voting window, mail-in deadline, election day

---

## Project Structure

```
civicpulse/
├── src/
│   ├── main.py           # Entry point, conversation orchestration
│   ├── logic.py          # State machine, decision algorithms
│   └── services.py       # Google API integrations
├── tests/
│   ├── test_logic.py     # Logic unit tests
│   └── test_services.py  # API integration tests
├── .agent/
│   └── skills/
│       ├── deadline_calculation.md      # Registration deadline skill
│       └── calendar_event_generation.md # Calendar event skill
├── requirements.txt      # Dependencies
├── README.md             # This file
└── .gitignore            # Git ignore rules
```

---

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- (Optional) Google API credentials for full functionality

### Step 1: Clone & Navigate
```bash
git clone https://github.com/yourusername/civicpulse.git
cd civicpulse
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: (Optional) Configure Google APIs
To enable real-time deadline lookups and calendar integration:

1. **Create a Google Cloud Project**
   - Visit [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project

2. **Enable APIs**
   - Enable Google Search API
   - Enable Google Calendar API
   - Enable Google Maps API

3. **Create Credentials**
   - Generate API key for Search/Maps
   - Create OAuth 2.0 credentials for Calendar
   - Save credentials to `credentials.json`

4. **Set Environment Variables**
   ```bash
   export GOOGLE_API_KEY="your_api_key"
   export GOOGLE_CALENDAR_ID="your_calendar_id"
   ```

### Step 5: Run the Assistant
```bash
python src/main.py
```

---

## Usage Example

```
Welcome to CivicPulse! 🗳️

I'm here to help you prepare for the upcoming election. 
Let's start: Are you registered to vote? (yes/no)

You: no
```
