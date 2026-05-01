#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Training Script
Trains the CivicPulse chatbot with all available datasets:
- US Election Data (polls, candidates, approval ratings)
- India Election Data (ECI 2024)
- Archive historical data
- Additional public datasets
"""

import os
import sys
import json
import csv
import warnings
from pathlib import Path
from collections import defaultdict
import re

warnings.filterwarnings('ignore')

try:
    import pandas as pd
except ImportError:
    pd = None

PROJECT_ROOT = Path(__file__).parent
DATA_DIRS = [
    PROJECT_ROOT / 'polls',
    PROJECT_ROOT / 'approval_ratings',
    PROJECT_ROOT / 'archive',
    PROJECT_ROOT / 'india',
    PROJECT_ROOT / 'may_polls',
    PROJECT_ROOT / 'sep_oct_polls',
    PROJECT_ROOT / 'bipartisan_debates',
    PROJECT_ROOT / 'republican_debates',
    PROJECT_ROOT / 'assassination_attempt'
]

class DatasetProcessor:
    """Process and extract knowledge from datasets."""
    
    def __init__(self):
        self.knowledge_base = defaultdict(list)
        self.stats = {
            'files_processed': 0,
            'rows_processed': 0,
            'knowledge_items': 0
        }
    
    def process_polls(self, df):
        """Extract insights from polling data."""
        insights = []
        
        if 'answer' in df.columns and 'pct' in df.columns:
            for idx, row in df.iterrows():
                if pd.notna(row.get('answer')) and pd.notna(row.get('pct')):
                    insights.append({
                        'type': 'poll_data',
                        'question': row.get('question', 'Poll'),
                        'answer': str(row['answer']),
                        'percentage': float(row.get('pct', 0)),
                        'date': str(row.get('enddate', 'Unknown')),
                        'source': row.get('pollster', 'Poll Data')
                    })
        
        if 'candidate' in df.columns and 'pct' in df.columns:
            for idx, row in df.iterrows():
                insights.append({
                    'type': 'candidate_support',
                    'candidate': str(row.get('candidate', 'Unknown')),
                    'support_percent': float(row.get('pct', 0)),
                    'date': str(row.get('enddate', 'Unknown'))
                })
        
        return insights
    
    def process_approval(self, df):
        """Extract approval ratings data."""
        insights = []
        
        for idx, row in df.iterrows():
            if 'approve_pct' in df.columns:
                insights.append({
                    'type': 'approval_rating',
                    'approve': float(row.get('approve_pct', 0)),
                    'disapprove': float(row.get('disapprove_pct', 0)),
                    'date': str(row.get('modeldate', '')),
                    'president': str(row.get('president', 'Unknown'))
                })
        
        return insights
    
    def process_candidates(self, df):
        """Extract candidate information."""
        insights = []
        
        for idx, row in df.iterrows():
            candidate_info = {
                'type': 'candidate',
                'name': str(row.get('candidate', 'Unknown')),
                'party': str(row.get('party', 'Unknown')),
            }
            
            # Add relevant fields
            for col in ['state', 'total_receipts', 'total_disbursements', 'date']:
                if col in df.columns:
                    candidate_info[col] = str(row.get(col, 'N/A'))
            
            insights.append(candidate_info)
        
        return insights
    
    def process_india_data(self, df):
        """Extract India election data."""
        insights = []
        
        for idx, row in df.iterrows():
            election_info = {
                'type': 'india_election',
                'country': 'India'
            }
            
            # Extract available columns
            for col in df.columns:
                if pd.notna(row.get(col)):
                    election_info[col.lower().replace(' ', '_')] = str(row[col])
            
            insights.append(election_info)
        
        return insights
    
    def process_csv_file(self, filepath):
        """Process a CSV file and extract knowledge."""
        try:
            df = pd.read_csv(filepath, on_bad_lines='skip', encoding='utf-8', low_memory=False)
            
            if df.empty:
                return []
            
            self.stats['rows_processed'] += len(df)
            
            # Determine file type and process accordingly
            filename = filepath.name.lower()
            insights = []
            
            if 'poll' in filename:
                insights = self.process_polls(df)
            elif 'approval' in filename:
                insights = self.process_approval(df)
            elif 'candidate' in filename:
                insights = self.process_candidates(df)
            elif 'eci' in filename or 'india' in filename:
                insights = self.process_india_data(df)
            else:
                # Generic processing
                for idx, row in df.head(100).iterrows():
                    insights.append({
                        'type': 'dataset',
                        'source': filename,
                        'data': dict(row[pd.notna(row)])
                    })
            
            return insights
        
        except Exception as e:
            print(f"⚠️  Error processing {filepath}: {e}")
            return []
    
    def load_datasets(self):
        """Load all available datasets."""
        print("\n" + "="*70)
        print("📊 LOADING DATASETS")
        print("="*70)
        
        for data_dir in DATA_DIRS:
            if not data_dir.exists():
                continue
            
            print(f"\n🔍 Processing: {data_dir.name}")
            
            for csv_file in data_dir.rglob('*.csv'):
                print(f"  📄 {csv_file.relative_to(PROJECT_ROOT)}")
                insights = self.process_csv_file(csv_file)
                
                if insights:
                    category = csv_file.stem
                    self.knowledge_base[category].extend(insights)
                    self.stats['knowledge_items'] += len(insights)
                    self.stats['files_processed'] += 1
        
        print(f"\n✅ Loaded {self.stats['files_processed']} files")
        print(f"📈 Extracted {self.stats['knowledge_items']} knowledge items")
        print(f"🔢 Processed {self.stats['rows_processed']} data rows")
    
    def generate_training_data(self):
        """Generate training data with Q&A pairs."""
        print("\n" + "="*70)
        print("🎓 GENERATING TRAINING DATA")
        print("="*70)
        
        training_data = {
            'elections': self._generate_election_qa(),
            'voting': self._generate_voting_qa(),
            'candidates': self._generate_candidate_qa(),
            'polls': self._generate_poll_qa(),
            'india': self._generate_india_qa(),
            'general': self._generate_general_qa()
        }
        
        return training_data
    
    def _generate_election_qa(self):
        """Generate election-related Q&A."""
        qa_pairs = [
            {
                'question': 'What is an election?',
                'answer': 'An election is a formal process by which voters choose representatives or decide on policies. Elections are fundamental to democratic systems.'
            },
            {
                'question': 'Why is voting important?',
                'answer': 'Voting is how citizens participate in democracy. Your vote determines elected officials and shapes policies that affect your community.'
            },
            {
                'question': 'What is voter registration?',
                'answer': 'Voter registration is the process of enrolling to vote. You must register in your jurisdiction before you can cast a ballot.'
            },
            {
                'question': 'How do I register to vote?',
                'answer': 'Registration requirements vary by location. Visit your local election office or use online registration where available. Most states allow registration on election day.'
            }
        ]
        
        # Add insights from knowledge base
        if 'candidates' in self.knowledge_base:
            qa_pairs.append({
                'question': 'Who are the candidates running?',
                'answer': f'We have data on {len(self.knowledge_base["candidates"])} candidates across various elections.'
            })
        
        return qa_pairs
    
    def _generate_voting_qa(self):
        """Generate voting process Q&A."""
        return [
            {
                'question': 'Where do I vote?',
                'answer': 'You vote at your designated polling place. This is determined by your voter registration address.'
            },
            {
                'question': 'What do I need to bring to vote?',
                'answer': 'Requirements vary by location. Most polling places accept a government-issued ID. Some states also accept voter registration cards or utility bills.'
            },
            {
                'question': 'Can I vote early?',
                'answer': 'Many states offer early voting periods. You can typically vote by mail or in person before election day. Check your state\'s rules.'
            },
            {
                'question': 'What if I cannot vote on election day?',
                'answer': 'You have options! Early voting, mail-in ballots, and absentee voting are available in most states. Check your state election office for details.'
            }
        ]
    
    def _generate_candidate_qa(self):
        """Generate candidate-related Q&A."""
        qa = [
            {
                'question': 'What information is available about candidates?',
                'answer': 'We provide data on candidate backgrounds, campaign finances, party affiliations, and polling performance.'
            }
        ]
        
        if self.knowledge_base.get('candidates'):
            num_candidates = len(self.knowledge_base['candidates'])
            qa.append({
                'question': f'How many candidates are in the database?',
                'answer': f'Our database contains information on {num_candidates} candidates.'
            })
        
        return qa
    
    def _generate_poll_qa(self):
        """Generate polling data Q&A."""
        qa = [
            {
                'question': 'What are polls?',
                'answer': 'Polls are surveys that measure public opinion on candidates, issues, or approval ratings. They help predict election outcomes.'
            },
            {
                'question': 'How accurate are polls?',
                'answer': 'Polls have margins of error, typically 2-4%. Accuracy depends on sample size, methodology, and when the poll was conducted.'
            }
        ]
        
        # Add real stats from data
        poll_count = sum(1 for items in self.knowledge_base.values() if any(item.get('type') == 'poll_data' for item in items))
        if poll_count > 0:
            qa.append({
                'question': 'How many polls are in your database?',
                'answer': f'We have analyzed {poll_count} polling records from various sources.'
            })
        
        return qa
    
    def _generate_india_qa(self):
        """Generate India-specific Q&A."""
        return [
            {
                'question': 'Tell me about elections in India',
                'answer': 'India holds elections for various levels of government including national (Lok Sabha), state assemblies, and local bodies. India is the world\'s largest democracy.'
            },
            {
                'question': 'What is the ECI?',
                'answer': 'The Election Commission of India (ECI) is the constitutional body responsible for conducting elections in India at all levels.'
            },
            {
                'question': 'How do Indian elections work?',
                'answer': 'Indian elections use a first-past-the-post system with universal adult suffrage. General Elections for the Lok Sabha occur every 5 years.'
            }
        ]
    
    def _generate_general_qa(self):
        """Generate general civics Q&A."""
        return [
            {
                'question': 'What is civic engagement?',
                'answer': 'Civic engagement means participating in community and government activities, including voting, volunteering, and staying informed.'
            },
            {
                'question': 'Why should I stay informed about elections?',
                'answer': 'Being informed helps you make better voting decisions. Follow news, read candidate information, and understand issues that matter to you.'
            },
            {
                'question': 'How can I learn more about the election process?',
                'answer': 'Visit your local election office website, use nonpartisan resources like Vote411.org, or contact voter advocacy organizations.'
            }
        ]
    
    def save_training_data(self, training_data, output_file):
        """Save training data to JSON file."""
        print(f"\n💾 Saving training data to {output_file.name}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Training data saved: {len(training_data)} categories")
        
        # Print summary
        total_qa_pairs = sum(len(v) for v in training_data.values() if isinstance(v, list))
        print(f"📚 Total Q&A pairs: {total_qa_pairs}")
    
    def save_knowledge_base(self, output_file):
        """Save extracted knowledge base."""
        print(f"\n💾 Saving knowledge base to {output_file.name}")
        
        knowledge_dict = {}
        for category, items in self.knowledge_base.items():
            knowledge_dict[category] = items[:100]  # Limit to first 100 items per category
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge_dict, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"✅ Knowledge base saved: {len(knowledge_dict)} categories")


def main():
    """Main training pipeline."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + "🗳️  CIVICPULSE - COMPREHENSIVE MODEL TRAINING".center(68) + "║")
    print("║" + "US Elections + India Elections + Archive Data".center(68) + "║")
    print("╚" + "="*68 + "╝")
    
    processor = DatasetProcessor()
    
    # Load all datasets
    processor.load_datasets()
    
    # Generate training data
    training_data = processor.generate_training_data()
    
    # Save outputs
    training_file = PROJECT_ROOT / 'training_data.json'
    knowledge_file = PROJECT_ROOT / 'knowledge_base.json'
    
    processor.save_training_data(training_data, training_file)
    processor.save_knowledge_base(knowledge_file)
    
    # Print final summary
    print("\n" + "="*70)
    print("✨ TRAINING COMPLETE")
    print("="*70)
    print(f"\n📊 Statistics:")
    print(f"   Files processed: {processor.stats['files_processed']}")
    print(f"   Data rows processed: {processor.stats['rows_processed']}")
    print(f"   Knowledge items extracted: {processor.stats['knowledge_items']}")
    print(f"\n📁 Output files:")
    print(f"   ✓ {training_file.name}")
    print(f"   ✓ {knowledge_file.name}")
    print(f"\n🎯 Next steps:")
    print(f"   1. Review generated training data")
    print(f"   2. Integrate with chatbot for enhanced responses")
    print(f"   3. Add custom Q&A pairs as needed")
    print(f"\n" + "="*70 + "\n")


if __name__ == '__main__':
    main()
