#!/usr/bin/env python3
"""Test dataset loading and matching"""

import csv
from collections import defaultdict
from pathlib import Path

print("Testing dataset loading and candidate matching...\n")

# Load candidates
candidates = {}
try:
    with open('candidates.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('name', '').strip()
            if name:
                candidates[name.lower()] = {
                    'name': name,
                    'party': row.get('party', 'unknown').strip(),
                }
    print(f"✓ Loaded {len(candidates)} candidates")
except Exception as e:
    print(f"✗ Error loading candidates: {e}")

# Test candidate search
def search_candidate(name: str):
    """Search for candidate by name with flexible matching"""
    name_lower = name.lower().strip()
    
    # Exact match first
    if name_lower in candidates:
        return candidates[name_lower]
    
    # Partial match (substring)
    for key, data in candidates.items():
        if name_lower in key or key in name_lower:
            return data
    
    # Last name only match
    name_parts = name_lower.split()
    if name_parts:
        last_name = name_parts[-1]
        for key, data in candidates.items():
            if last_name in key:
                return data
    
    return None

# Test searches
test_names = ["trump", "Trump", "Donald Trump", "harris", "Kamala Harris", "haley", "Nikki Haley", "unknown"]

print("\n📋 Testing candidate search:\n")
for test_name in test_names:
    result = search_candidate(test_name)
    if result:
        print(f"  ✓ '{test_name}' -> Found: {result['name']}")
    else:
        print(f"  ✗ '{test_name}' -> Not found")

# Load polls
polls = defaultdict(list)
try:
    with open('favorability_polls.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            politician = row.get('politician', '').strip()
            if politician:
                polls[politician.lower()].append({
                    'favorable': row.get('favorable', '0'),
                    'unfavorable': row.get('unfavorable', '0'),
                })
                count += 1
                if count >= 20:
                    break
    print(f"\n✓ Loaded polling data for {len(polls)} politicians")
except Exception as e:
    print(f"\n✗ Error loading polls: {e}")

# Test poll matching
print("\n📊 Testing polling data lookup:\n")
for test_name in ["trump", "harris", "biden"]:
    if test_name in polls:
        print(f"  ✓ '{test_name}' -> Has {len(polls[test_name])} poll entries")
    else:
        print(f"  ✗ '{test_name}' -> No polling data")

print("\n✓ All tests completed!")
