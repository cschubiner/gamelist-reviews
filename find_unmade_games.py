#!/usr/bin/env python3
"""Find games from gameslist that don't have review files."""
import os
import re

REVIEWS_DIR = "/Users/canal/gamelist_manyplayers/reviews"
GAMESLIST = "/Users/canal/gamelist_manyplayers/gameslist.txt"

# Get created games
created = {f[:-3].lower().replace('_', ' ') for f in os.listdir(REVIEWS_DIR) if f.endswith('.md')}

# Read gameslist
with open(GAMESLIST) as f:
    text = f.read()

# Extract games - look for actual game entries (before prices or in clear game sections)
# Parse better by looking at structure
games = []
lines = text.split('\n')

skip_phrases = {
    'steam', 'valve', 'filter', 'system', 'store', 'privacy', 'legal', 'support',
    'about', 'jobs', 'steamworks', 'distribution', 'account', 'help', 'cookies',
    'policy', 'accessibility', 'vat included', 'all prices', 'hidden items',
    'preferences', 'explore more', 'see all', 'reviews by', 'facebook', 'twitter',
    'x:', 'bluesky', 'recycling', 'gift cards', '@steam', 'steampowered'
}

for i, line in enumerate(lines):
    line = line.strip()
    
    # Skip empty/short lines
    if not line or len(line) < 3:
        continue
    
    # Skip known non-game lines
    if any(phrase in line.lower() for phrase in skip_phrases):
        continue
        
    # Skip lines that look like prices, dates, or descriptions
    if line.startswith('$') or line.startswith('"') or line.startswith('-'):
        continue
    if re.match(r'^[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}', line):
        continue
        
    # Check if it looks like a game name
    if line[0].isupper() and len(line) < 150:
        norm = line.lower().replace('_', ' ').replace("'", '')
        if norm not in created and line.lower() not in created:
            games.append(line)

# Deduplicate
games = list(dict.fromkeys(games))

# Filter to remove obvious non-games
real_games = []
for game in games:
    # Should have reasonable length and not be all caps or all lowercase
    if 3 < len(game) < 100 and not game.isupper():
        # Shouldn't start with common metadata
        if not game.startswith(('In ', 'More', 'Free', 'Recommended', 'Not ', 'Coming', 'On ', 'To be', 'Informational', 'A list')):
            real_games.append(game)

print(f"Remaining games to create: {len(real_games)}")
print("=" * 70)
for i, game in enumerate(real_games, 1):
    print(f"{i:3d}. {game}")

