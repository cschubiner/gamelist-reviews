#!/usr/bin/env python3
"""
Check which games from gameslist.txt haven't been created yet.
"""
import re
import os
from pathlib import Path

GAMESLIST_FILE = "/Users/canal/gamelist_manyplayers/gameslist.txt"
REVIEWS_DIR = "/Users/canal/gamelist_manyplayers/reviews"

def extract_game_names_from_list():
    """Extract game names from gameslist.txt"""
    games = []
    
    with open(GAMESLIST_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for patterns like game names before prices/dates
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines and known metadata
        if not line or line.startswith('"') or line.startswith('-') or line.startswith('$'):
            i += 1
            continue
        
        # Skip date patterns
        if re.match(r'^[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}$', line):
            i += 1
            continue
        
        # Skip known metadata keywords
        if any(kw in line for kw in ['Free To Play', 'Recommended', 'Informational', 'In Library', 'On Wishlist', 'Coming soon', 'Not Recommended', 'To be announced', 'Available:', 'New', 'Filter by', 'System']):
            i += 1
            continue
        
        # This is likely a game name
        if line and len(line) > 2 and line[0].isupper():
            games.append(line)
        
        i += 1
    
    return games

def get_created_games():
    """Get list of games that have review files."""
    created = set()
    
    for filename in os.listdir(REVIEWS_DIR):
        if filename.endswith('.md'):
            # Remove .md extension to get game name
            game_name = filename[:-3]
            created.add(game_name.lower().replace('_', ' '))
    
    return created

def normalize_name(name):
    """Normalize game name for comparison."""
    return name.lower().replace('_', ' ').replace("'", '').replace('-', ' ').strip()

def main():
    all_games = extract_game_names_from_list()
    created = get_created_games()
    
    # Find which games haven't been created
    remaining = []
    for game in all_games:
        norm_game = normalize_name(game)
        if norm_game not in created and game.lower() not in created:
            # Check if this might be a duplicate or metadata
            if len(game) > 3 and not any(x in game for x in ['$', ':', '(', ')']):
                remaining.append(game)
    
    # Remove duplicates while preserving order
    remaining = list(dict.fromkeys(remaining))
    
    print(f"📊 Game Inventory Report")
    print(f"=" * 60)
    print(f"Total games in gameslist.txt: {len(all_games)}")
    print(f"Games with review files: {len(created)}")
    print(f"Remaining games to create: {len(remaining)}")
    print(f"=" * 60)
    
    if remaining:
        print(f"\n📋 Remaining {len(remaining)} games:")
        for i, game in enumerate(remaining[:20], 1):
            print(f"  {i}. {game}")
        if len(remaining) > 20:
            print(f"  ... and {len(remaining) - 20} more")
    else:
        print("\n✅ All games from gameslist.txt have been created!")

if __name__ == "__main__":
    main()
