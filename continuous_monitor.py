#!/usr/bin/env python3
"""
Continuous monitoring script for new game files and automatic updates.
Watches for new markdown files and automatically regenerates visualizer.
"""

import os
import time
import json
import subprocess
import sys
from pathlib import Path

REVIEWS_DIR = "/Users/canal/gamelist_manyplayers/reviews"
DATA_DIR = "/Users/canal/gamelist_manyplayers/data"
SCRIPT_DIR = "/Users/canal/gamelist_manyplayers"

def count_files():
    """Count markdown and JSON files."""
    md_files = len([f for f in os.listdir(REVIEWS_DIR) if f.endswith('.md')])
    json_files = len([f for f in os.listdir(DATA_DIR) if f.endswith('.json')])
    return md_files, json_files

def extract_metadata():
    """Run metadata extraction."""
    print("🔄 Extracting metadata from all review files...")
    result = subprocess.run(
        ["python3", "extract_metadata.py"],
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("✓ Metadata extraction complete")
        return True
    else:
        print(f"✗ Metadata extraction failed: {result.stderr}")
        return False

def aggregate_visualizer():
    """Run visualizer aggregation."""
    print("🔄 Regenerating GitHub Pages visualizer...")
    result = subprocess.run(
        ["python3", "aggregate_all_games.py"],
        input="1\n",
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("✓ Visualizer regenerated")
        return True
    else:
        print(f"✗ Visualizer regeneration failed: {result.stderr}")
        return False

def update_readme(game_count):
    """Update README with new game count."""
    print(f"📝 Updating README for {game_count} games...")
    readme_path = "/Users/canal/gamelist_manyplayers/README.md"
    
    with open(readme_path, 'r') as f:
        content = f.read()
    
    # Update title
    content = content.replace(
        f"Complete database with comprehensive reviews for {game_count - 1} local multiplayer games",
        f"Complete database with comprehensive reviews for {game_count} local multiplayer games"
    )
    
    # Update in games included section
    additional = game_count - 16
    content = content.replace(
        f"Plus {additional - 1} additional games covering diverse multiplayer genres",
        f"Plus {additional} additional games covering diverse multiplayer genres"
    )
    content = content.replace(
        f"for the complete, sortable list of all {game_count - 1} games",
        f"for the complete, sortable list of all {game_count} games"
    )
    
    # Update directory structure
    content = content.replace(
        f"├── reviews/              # {game_count - 1} markdown review files",
        f"├── reviews/              # {game_count} markdown review files"
    )
    content = content.replace(
        f"├── data/                 # {game_count - 1} JSON files with structured game data",
        f"├── data/                 # {game_count} JSON files with structured game data"
    )
    
    with open(readme_path, 'w') as f:
        f.write(content)
    
    print(f"✓ README updated for {game_count} games")

def commit_changes(game_count):
    """Commit changes to git."""
    print(f"💾 Committing {game_count} total games...")
    
    # Stage files
    subprocess.run(
        ["git", "add", "reviews/", "data/", "docs/", "README.md"],
        cwd=SCRIPT_DIR,
        capture_output=True
    )
    
    # Commit
    message = f"Update to {game_count} total multiplayer games with complete metadata and visualizer"
    result = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True
    )
    
    if "nothing to commit" in result.stdout.lower():
        print("✓ No changes to commit (visualizer already up to date)")
        return False
    elif result.returncode == 0:
        print(f"✓ Committed {game_count} games to git")
        return True
    else:
        print(f"✗ Commit failed: {result.stderr}")
        return False

def push_changes():
    """Push changes to GitHub."""
    print("🚀 Pushing to GitHub...")
    result = subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✓ Pushed to GitHub")
        return True
    else:
        print(f"✗ Push failed: {result.stderr}")
        return False

def monitor_and_update():
    """Monitor for file changes and update."""
    last_count = 0
    consecutive_stable = 0
    
    print("=" * 60)
    print("🎮 Continuous Game Repository Monitor Started")
    print("=" * 60)
    
    while True:
        try:
            md_count, json_count = count_files()
            
            if md_count != last_count:
                print(f"\n📊 NEW GAMES DETECTED! Now at {md_count} games")
                print("=" * 60)
                
                # Wait a moment for all files to finish writing
                time.sleep(2)
                
                # Extract metadata
                if extract_metadata():
                    # Regenerate visualizer
                    if aggregate_visualizer():
                        # Update README
                        update_readme(md_count)
                        
                        # Commit changes
                        if commit_changes(md_count):
                            # Push to GitHub
                            push_changes()
                        
                        print("=" * 60)
                        print(f"✅ Repository updated with {md_count} games!")
                        print(f"📍 https://github.com/cschubiner/gamelist-reviews")
                        print(f"🌐 https://cschubiner.github.io/gamelist_manyplayers/")
                        print("=" * 60)
                
                last_count = md_count
                consecutive_stable = 0
            else:
                consecutive_stable += 1
                if consecutive_stable % 6 == 0:  # Every 60 seconds
                    print(f"⏱️  Stable at {md_count} games - monitoring...")
            
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Monitor stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    monitor_and_update()
