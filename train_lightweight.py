#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lightweight Training Data Generator
Extracts knowledge from CSV files without heavy dependencies
"""

import json
import csv
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent

class LightweightTrainer:
    """Process datasets without pandas."""
    
    def __init__(self):
        self.knowledge_base = defaultdict(list)
        self.training_data = {
            'elections': [],
            'voting': [],
            'candidates': [],
            'polls': [],
            'india': [],
            'general': []
        }
    
    def load_csv(self, filepath):
        """Load CSV without pandas."""
        try:
            rows = []
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row:
                        rows.append(row)
            return rows[:200]  # Limit rows
        except:
            return []
    
    def process_datasets(self):
        """Process all available datasets."""
        print("\n" + "="*70)
        print("CIVICPULSE - COMPREHENSIVE TRAINING")
        print("="*70)
        
        datasets_processed = 0
        total_records = 0
        
        # Find and process all CSV files
        data_dirs = [
            PROJECT_ROOT / 'polls',
            PROJECT_ROOT / 'approval_ratings',
            PROJECT_ROOT / 'archive',
            PROJECT_ROOT / 'india',
            PROJECT_ROOT / 'may_polls',
            PROJECT_ROOT / 'sep_oct_polls',
        ]
        
        for data_dir in data_dirs:
            if not data_dir.exists():
                continue
            
            print("\nProcessing: {}".format(data_dir.name))
            
            for csv_file in data_dir.rglob('*.csv'):
                rows = self.load_csv(csv_file)
                if rows:
                    datasets_processed += 1
                    total_records += len(rows)
                    print("  [OK] {} ({} records)".format(csv_file.name, len(rows)))
                    
                    # Categorize data
                    filename = csv_file.stem.lower()
                    if 'poll' in filename:
                        self.knowledge_base['polls'].extend(rows[:10])
                    elif 'approval' in filename:
                        self.knowledge_base['approval'].extend(rows[:10])
                    elif 'candidate' in filename:
                        self.knowledge_base['candidates'].extend(rows[:10])
                    elif 'eci' in filename or 'india' in filename:
                        self.knowledge_base['india'].extend(rows[:10])
                    else:
                        self.knowledge_base['other'].extend(rows[:5])
        
        print("\n" + "-"*70)
        print("LOADED: {} files with {} total records".format(datasets_processed, total_records))
        
        # Generate training pairs
        self.generate_qa_pairs()
        
        # Save outputs
        self.save_training_data()
    
    def generate_qa_pairs(self):
        """Generate Q&A pairs for training."""
        
        # Core civics training data
        self.training_data['elections'] = [
            {
                'question': 'What is an election?',
                'answer': 'An election is a formal process where voters choose representatives or decide on policies. Elections are fundamental to democratic governance.'
            },
            {
                'question': 'Why is voting important?',
                'answer': 'Voting is how citizens participate in democracy. Your vote determines elected officials and shapes policies affecting your community and nation.'
            },
            {
                'question': 'How often are elections held?',
                'answer': 'In the US, presidential elections occur every 4 years. Congressional elections are every 2 years. State and local elections vary by jurisdiction.'
            },
            {
                'question': 'What is voter registration?',
                'answer': 'Voter registration is the process of enrolling before you can vote. Requirements vary by state. Most states allow online or in-person registration.'
            },
            {
                'question': 'How do I register to vote?',
                'answer': 'Visit your local election office, use online registration, or register at the DMV. Deadlines vary by state - register early to ensure eligibility.'
            },
            {
                'question': 'What documents do I need to register?',
                'answer': 'You typically need proof of citizenship, residency, and age. Accepted documents include driver\'s license, passport, or state ID.'
            }
        ]
        
        self.training_data['voting'] = [
            {
                'question': 'Where do I vote?',
                'answer': 'You vote at your designated polling place, determined by your voter registration address. Find your polling location at your state\'s election website.'
            },
            {
                'question': 'What do I need to bring to vote?',
                'answer': 'Most states require a government-issued ID. Some accept voter cards, utility bills, or other documents. Check your state\'s specific requirements.'
            },
            {
                'question': 'Can I vote early?',
                'answer': 'Yes! Many states offer early voting periods of 1-3 weeks before election day. You can vote in person or by mail in most jurisdictions.'
            },
            {
                'question': 'How do I vote by mail?',
                'answer': 'Request an absentee or mail-in ballot from your election office. Some states automatically send ballots to all registered voters.'
            },
            {
                'question': 'What if I cannot vote on election day?',
                'answer': 'Use early voting, mail-in ballots, or absentee voting. Most states have at least one option available to all registered voters.'
            },
            {
                'question': 'How long does voting take?',
                'answer': 'Typical voting time is 5-30 minutes depending on your polling place\'s lines. Arrive early on election day or use early voting to avoid crowds.'
            }
        ]
        
        self.training_data['candidates'] = [
            {
                'question': 'Where can I find information about candidates?',
                'answer': 'Visit Vote411.org, candidates\' official websites, or your state election office. Read their policy positions and backgrounds before voting.'
            },
            {
                'question': 'What should I know about candidates?',
                'answer': 'Research their experience, policy positions, voting records, campaign funding, and endorsements. Use nonpartisan sources for objective information.'
            },
            {
                'question': 'How are candidates nominated?',
                'answer': 'Candidates can be nominated through primary elections, party conventions, or petition signatures. Each state has specific nomination procedures.'
            }
        ]
        
        self.training_data['polls'] = [
            {
                'question': 'What are polls?',
                'answer': 'Polls are surveys measuring public opinion on candidates, issues, or approval ratings. They help predict election outcomes but have margins of error.'
            },
            {
                'question': 'How accurate are polls?',
                'answer': 'Polls typically have 2-4% margins of error. Accuracy depends on sample size, methodology, timing, and how questions are asked.'
            },
            {
                'question': 'What is a polling average?',
                'answer': 'A polling average combines results from multiple polls to show overall trends. It\'s generally more reliable than individual polls.'
            }
        ]
        
        self.training_data['india'] = [
            {
                'question': 'Tell me about elections in India',
                'answer': 'India holds elections for national Parliament (Lok Sabha), state assemblies, and local bodies. India is the world\'s largest democracy with over 900 million voters.'
            },
            {
                'question': 'What is the ECI?',
                'answer': 'The Election Commission of India (ECI) is the constitutional body responsible for conducting elections at all government levels across India.'
            },
            {
                'question': 'How often are Indian general elections held?',
                'answer': 'General Elections for the Lok Sabha (lower house) are held every 5 years. India had elections in 2024 with a record turnout.'
            },
            {
                'question': 'How does the Indian voting system work?',
                'answer': 'India uses a first-past-the-post system with universal adult suffrage. Voters directly elect representatives for their constituencies.'
            },
            {
                'question': 'What are state assembly elections?',
                'answer': 'State assembly elections determine representatives for state legislatures. These can be held at different times than national elections.'
            }
        ]
        
        self.training_data['general'] = [
            {
                'question': 'What is civic engagement?',
                'answer': 'Civic engagement includes participating in community activities, voting, volunteering, and staying informed about political issues.'
            },
            {
                'question': 'Why should I stay informed about elections?',
                'answer': 'Being informed helps you make better voting decisions. Follow credible news sources and research candidates\' positions on issues you care about.'
            },
            {
                'question': 'What is the difference between primary and general elections?',
                'answer': 'Primary elections let parties choose candidates. General elections are where voters choose the actual elected officials among party nominees.'
            },
            {
                'question': 'How can I learn more about elections?',
                'answer': 'Visit Vote411.org, your state election website, local election offices, or nonpartisan voter advocacy organizations for reliable information.'
            },
            {
                'question': 'What if I have questions about voting?',
                'answer': 'Contact your local election office, call the voter hotline, or visit your state\'s official election website for official information.'
            }
        ]
    
    def save_training_data(self):
        """Save training data to files."""
        print("\n" + "-"*70)
        print("SAVING TRAINING DATA")
        
        # Save Q&A training data
        training_file = PROJECT_ROOT / 'training_qa_pairs.json'
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(self.training_data, f, indent=2, ensure_ascii=False)
        
        qa_count = sum(len(v) for v in self.training_data.values())
        print("OK: {} ({} Q&A pairs)".format(training_file.name, qa_count))
        
        # Save knowledge base summary
        knowledge_file = PROJECT_ROOT / 'knowledge_summary.json'
        knowledge_summary = {}
        for category, items in self.knowledge_base.items():
            knowledge_summary[category] = {
                'count': len(items),
                'sample': items[0] if items else {}
            }
        
        with open(knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge_summary, f, indent=2, default=str, ensure_ascii=False)
        
        print("OK: {}".format(knowledge_file.name))
        
        print("\n" + "="*70)
        print("TRAINING COMPLETE!")
        print("="*70)
        print("\nGenerated files:")
        print("  - training_qa_pairs.json: Q&A pairs for chatbot")
        print("  - knowledge_summary.json: Data summary")
        print("\nFiles are ready for integration with the chatbot.")
        print("="*70 + "\n")

if __name__ == '__main__':
    trainer = LightweightTrainer()
    trainer.process_datasets()
