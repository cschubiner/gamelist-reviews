#!/usr/bin/env python3
"""
Aggregate all game data from reviews and JSON files into a single JavaScript array.
Waits until at least 150 markdown files are available before proceeding.
"""

import json
import os
import time
from pathlib import Path
import re

REVIEWS_DIR = Path("/Users/canal/gamelist_manyplayers/reviews")
DATA_DIR = Path("/Users/canal/gamelist_manyplayers/data")
INDEX_HTML = Path("/Users/canal/gamelist_manyplayers/docs/index.html")

def count_files():
    """Count markdown and JSON files."""
    md_count = len(list(REVIEWS_DIR.glob("*.md")))
    json_count = len(list(DATA_DIR.glob("*.json")))
    return md_count, json_count

def load_all_game_data():
    """Load all JSON files and return as a list of game dictionaries."""
    games = []
    json_files = sorted(DATA_DIR.glob("*.json"))
    
    print(f"Loading {len(json_files)} JSON files...")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                game_data = json.load(f)
                games.append(game_data)
        except Exception as e:
            print(f"Error loading {json_file.name}: {e}")
    
    return games

def generate_js_array(games):
    """Generate JavaScript array string from game data."""
    js_lines = ["let allGames = ["]
    
    for i, game in enumerate(games):
        # Escape quotes in strings
        name = game.get('name', '').replace('"', '\\"')
        comment = game.get('originalComment', '').replace('"', '\\"')
        score = game.get('reviewScore', 0)
        max_players = game.get('maxPlayers', 0)
        platforms = game.get('platforms', [])
        price = game.get('price', '').replace('"', '\\"')
        
        # Format platforms as JSON array
        platforms_str = json.dumps(platforms)
        
        # Create game object line
        game_line = f'  {{"name":"{name}","originalComment":"{comment}","reviewScore":{score},"maxPlayers":{max_players},"platforms":{platforms_str},"price":"{price}"}}'
        
        # Add comma if not last item
        if i < len(games) - 1:
            game_line += ","
        
        js_lines.append(game_line)
    
    js_lines.append("];")
    
    return "\n".join(js_lines)

def update_index_html(js_array):
    """Update index.html with new allGames array."""
    if not INDEX_HTML.exists():
        print(f"Error: {INDEX_HTML} does not exist")
        return False
    
    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the allGames array
    # Pattern: let allGames = [...];
    pattern = r'let allGames = \[[\s\S]*?\];'
    
    if not re.search(pattern, content):
        print("Error: Could not find allGames array in index.html")
        return False
    
    # Replace the array
    updated_content = re.sub(pattern, js_array, content, count=1)
    
    # Write back to file
    with open(INDEX_HTML, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"Successfully updated {INDEX_HTML}")
    return True

def wait_for_files(target_count=150, check_interval=30, max_wait=3600):
    """
    Wait until at least target_count markdown files are available.
    
    Args:
        target_count: Minimum number of markdown files to wait for
        check_interval: Seconds between checks
        max_wait: Maximum seconds to wait (default 1 hour)
    """
    start_time = time.time()
    
    print(f"Waiting for at least {target_count} markdown review files...")
    print(f"Will check every {check_interval} seconds (max wait: {max_wait}s)")
    
    while True:
        md_count, json_count = count_files()
        elapsed = int(time.time() - start_time)
        
        print(f"[{elapsed}s] Current status: {md_count} markdown files, {json_count} JSON files")
        
        if md_count >= target_count:
            print(f"✓ Target reached! Found {md_count} markdown files")
            return True
        
        if elapsed >= max_wait:
            print(f"⚠ Max wait time reached. Proceeding with {md_count} files.")
            return False
        
        time.sleep(check_interval)

def main():
    """Main aggregation process."""
    print("=" * 60)
    print("Game Data Aggregation Script")
    print("=" * 60)
    
    # Check current status
    md_count, json_count = count_files()
    print(f"\nCurrent status:")
    print(f"  - Markdown reviews: {md_count}")
    print(f"  - JSON metadata files: {json_count}")
    
    # Wait for files if needed
    if md_count < 150:
        print(f"\n⚠ Warning: Only {md_count} files found (target: 150+)")
        response = input("Do you want to (w)ait, (p)roceed anyway, or (q)uit? [w/p/q]: ").lower()
        
        if response == 'q':
            print("Exiting...")
            return
        elif response == 'w':
            if not wait_for_files(target_count=150):
                response = input("Continue with current files? [y/n]: ").lower()
                if response != 'y':
                    print("Exiting...")
                    return
    
    # Load all game data
    print("\n" + "=" * 60)
    print("Loading game data...")
    print("=" * 60)
    games = load_all_game_data()
    
    if not games:
        print("Error: No game data found!")
        return
    
    print(f"✓ Loaded {len(games)} games")
    
    # Generate JavaScript array
    print("\n" + "=" * 60)
    print("Generating JavaScript array...")
    print("=" * 60)
    js_array = generate_js_array(games)
    
    print(f"✓ Generated array with {len(games)} games")
    print(f"  Array size: {len(js_array)} characters")
    
    # Update index.html
    print("\n" + "=" * 60)
    print("Updating index.html...")
    print("=" * 60)
    
    if update_index_html(js_array):
        print("✓ Successfully updated index.html")
        print(f"\nSummary:")
        print(f"  - Total games: {len(games)}")
        print(f"  - Updated file: {INDEX_HTML}")
        print(f"\nNext steps:")
        print(f"  1. Review the changes in docs/index.html")
        print(f"  2. Test the visualizer locally")
        print(f"  3. Commit and push changes to GitHub")
    else:
        print("✗ Failed to update index.html")

if __name__ == "__main__":
    main()
