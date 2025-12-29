#!/usr/bin/env python3
"""Extract actual game names from gameslist.txt that need reviews."""
import re
import os

GAMESLIST_FILE = "/Users/canal/gamelist_manyplayers/gameslist.txt"
REVIEWS_DIR = "/Users/canal/gamelist_manyplayers/reviews"

# Games we've already created
created_games = {f[:-3].lower().replace('_', ' ') for f in os.listdir(REVIEWS_DIR) if f.endswith('.md')}

# Read gameslist and extract real game names
with open(GAMESLIST_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Split into sections - games are typically followed by prices or dates
lines = content.split('\n')

games_to_check = []
i = 0
while i < len(lines):
    line = lines[i].strip()
    
    # Skip metadata lines
    if not line or line.startswith('"') or line.startswith('$') or line.startswith('-'):
        i += 1
        continue
    
    # Skip date lines  
    if re.match(r'^[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}', line):
        i += 1
        continue
    
    # Skip Steam UI elements and metadata
    skip_keywords = ['Filter', 'System', 'Store', 'Privacy', 'Legal', 'Accessibility', 'VAT', 
                     'Valve Software', 'hidden items', 'preferences', 'Explore more', 'See all',
                     'reviews by', 'Local Multiplayer List', 'More than', 'a list of', 
                     'to know if', 'would like', 'Useful', 'try something', 'party']
    
    if any(kw.lower() in line.lower() for kw in skip_keywords):
        i += 1
        continue
    
    # Look for likely game names (uppercase start, reasonable length)
    if line and 2 < len(line) < 100 and line[0].isupper():
        # Normalize for comparison
        norm = line.lower().replace('_', ' ').replace("'", '').replace('-', ' ').strip()
        if norm not in created_games and line not in created_games:
            games_to_check.append(line)
    
    i += 1

# Remove duplicates while keeping order
seen = set()
remaining = []
for game in games_to_check:
    norm = game.lower()
    if norm not in seen:
        seen.add(norm)
        remaining.append(game)

print("Real remaining games to create:")
print("=" * 60)
for i, game in enumerate(remaining, 1):
    print(f"{i}. {game}")

print(f"\n✓ Total: {len(remaining)} games remaining")
