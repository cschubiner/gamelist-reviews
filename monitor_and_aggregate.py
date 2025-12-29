#!/usr/bin/env python3
"""
Monitor review generation and aggregate when ready.
Polls every 30 seconds until 150+ files are available, then aggregates.
"""

import json
import os
import time
from pathlib import Path
import re
import sys

REVIEWS_DIR = Path("/Users/canal/gamelist_manyplayers/reviews")
DATA_DIR = Path("/Users/canal/gamelist_manyplayers/data")
INDEX_HTML = Path("/Users/canal/gamelist_manyplayers/docs/index.html")
TARGET_COUNT = 150

def count_files():
    """Count markdown and JSON files."""
    md_count = len(list(REVIEWS_DIR.glob("*.md")))
    json_count = len(list(DATA_DIR.glob("*.json")))
    return md_count, json_count

def load_all_game_data():
    """Load all JSON files and return as a list of game dictionaries."""
    games = []
    json_files = sorted(DATA_DIR.glob("*.json"))

    print(f"\nLoading {len(json_files)} JSON files...")

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                game_data = json.load(f)
                games.append(game_data)
        except Exception as e:
            print(f"  Error loading {json_file.name}: {e}")

    return games

def generate_js_array(games):
    """Generate JavaScript array string from game data."""
    js_lines = ["let allGames = ["]

    for i, game in enumerate(games):
        # Escape quotes and backslashes in strings
        name = game.get('name', '').replace('\\', '\\\\').replace('"', '\\"')
        comment = game.get('originalComment', '').replace('\\', '\\\\').replace('"', '\\"')
        score = game.get('reviewScore', 0)
        max_players = game.get('maxPlayers', 0)
        platforms = game.get('platforms', [])
        price = game.get('price', '').replace('\\', '\\\\').replace('"', '\\"')

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

def update_index_html(js_array, game_count):
    """Update index.html with new allGames array and update stats."""
    if not INDEX_HTML.exists():
        print(f"Error: {INDEX_HTML} does not exist")
        return False

    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find and replace the allGames array
    pattern = r'let allGames = \[[\s\S]*?\];'

    if not re.search(pattern, content):
        print("Error: Could not find allGames array in index.html")
        return False

    # Replace the array
    updated_content = re.sub(pattern, js_array, content, count=1)

    # Update the total games count in the header
    # <span class="stat-number" id="totalGames">42</span>
    updated_content = re.sub(
        r'<span class="stat-number" id="totalGames">\d+</span>',
        f'<span class="stat-number" id="totalGames">{game_count}</span>',
        updated_content
    )

    # Write back to file
    with open(INDEX_HTML, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print(f"✓ Successfully updated {INDEX_HTML}")
    return True

def monitor_and_wait():
    """Monitor file generation until target is reached."""
    print("=" * 70)
    print("  GAME DATA AGGREGATION - MONITORING MODE")
    print("=" * 70)
    print(f"\nTarget: {TARGET_COUNT}+ markdown review files")
    print("Checking every 30 seconds...\n")

    last_count = 0
    check_num = 0
    start_time = time.time()

    while True:
        check_num += 1
        md_count, json_count = count_files()
        elapsed = int(time.time() - start_time)
        elapsed_min = elapsed // 60
        elapsed_sec = elapsed % 60

        # Calculate rate if we have changes
        if md_count > last_count:
            files_added = md_count - last_count
            rate_info = f" (+{files_added})"
        else:
            rate_info = ""

        print(f"[Check #{check_num:3d}] [{elapsed_min:02d}:{elapsed_sec:02d}] "
              f"MD: {md_count:3d}{rate_info:7s}  JSON: {json_count:3d}  "
              f"Progress: {md_count}/{TARGET_COUNT} ({100*md_count//TARGET_COUNT}%)")

        if md_count >= TARGET_COUNT:
            print(f"\n{'='*70}")
            print(f"  ✓ TARGET REACHED! Found {md_count} markdown files")
            print(f"{'='*70}\n")
            return True

        last_count = md_count
        time.sleep(30)

def aggregate():
    """Perform the aggregation."""
    print("\n" + "=" * 70)
    print("  STARTING AGGREGATION")
    print("=" * 70)

    # Load all game data
    games = load_all_game_data()

    if not games:
        print("✗ Error: No game data found!")
        return False

    print(f"✓ Loaded {len(games)} games")

    # Generate JavaScript array
    print("\nGenerating JavaScript array...")
    js_array = generate_js_array(games)
    print(f"✓ Generated array ({len(js_array):,} characters)")

    # Update index.html
    print("\nUpdating docs/index.html...")

    if update_index_html(js_array, len(games)):
        print("\n" + "=" * 70)
        print("  ✓ AGGREGATION COMPLETE")
        print("=" * 70)
        print(f"\nSummary:")
        print(f"  - Total games aggregated: {len(games)}")
        print(f"  - Updated file: {INDEX_HTML}")
        print(f"  - Array size: {len(js_array):,} characters")
        return True
    else:
        print("\n✗ Failed to update index.html")
        return False

def main():
    """Main process."""
    # Check initial status
    md_count, json_count = count_files()

    if md_count >= TARGET_COUNT:
        print(f"\n✓ Already have {md_count} files (target: {TARGET_COUNT}+)")
        print("  Proceeding directly to aggregation...\n")
    else:
        print(f"\nCurrent status: {md_count} markdown files, {json_count} JSON files")
        print(f"Need {TARGET_COUNT - md_count} more files to reach target.\n")

        # Monitor and wait
        monitor_and_wait()

        # Wait a moment for any final files
        print("\nWaiting 10 seconds for any final files...")
        time.sleep(10)

    # Perform aggregation
    success = aggregate()

    if success:
        print("\n" + "=" * 70)
        print("  NEXT STEPS")
        print("=" * 70)
        print("\n1. Run metadata extraction to ensure all JSON files are up to date:")
        print("   python3 extract_metadata.py")
        print("\n2. Test the visualizer:")
        print("   open docs/index.html")
        print("\n3. Update README.md with final game count")
        print("\n4. Commit and push to GitHub:")
        print("   git add docs/ data/ reviews/")
        print("   git commit -m \"Complete aggregation of all games\"")
        print("   git push origin main")
        print()

    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
