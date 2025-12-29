#!/usr/bin/env python3
"""
Extract metadata from review markdown files and create JSON files.
"""

import os
import re
import json
from pathlib import Path

# Read the gameslist.txt to extract original comments and prices
def load_original_comments():
    comments = {}
    prices = {}
    gameslist_path = Path("/Users/canal/gamelist_manyplayers/gameslist.txt")

    if gameslist_path.exists():
        with open(gameslist_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_game = None
        current_price = None
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Look for game names (lines that aren't prices, dates, or descriptions)
            if line and not line.startswith('"') and not line.startswith('$') and not line.startswith('-') and not re.match(r'^[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}$', line):
                # Check if it's a potential game name
                if not any(keyword in line for keyword in ['Free To Play', 'Recommended', 'Informational', 'In Library', 'On Wishlist', 'Coming soon', 'Not Recommended', 'To be announced', 'Available:', 'New']):
                    current_game = line
                    current_price = None

                    # Look ahead for price (next 1-3 lines)
                    for j in range(1, min(4, len(lines) - i)):
                        next_line = lines[i + j].strip()
                        if next_line.startswith('$'):
                            # Extract the main price (not the discounted one)
                            price_match = re.search(r'\$(\d+\.\d+)', next_line)
                            if price_match:
                                current_price = f"${price_match.group(1)}"
                            break
                        elif next_line.startswith('"'):
                            break

            # Look for descriptions (lines in quotes)
            elif line.startswith('"') and line.endswith('"') and current_game:
                comments[current_game] = line.strip('"')
                if current_price and current_game:
                    prices[current_game] = current_price

            i += 1

    return comments, prices

# Extract metadata from a single markdown file
def extract_metadata(filepath, original_comments, original_prices):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    metadata = {}

    # Extract game name from filename
    filename = os.path.basename(filepath)
    game_name = filename.replace('.md', '').replace('_', ' ')
    metadata['name'] = game_name

    # Try to find the game name in original comments (fuzzy match)
    original_comment = None
    original_price = None

    # Normalize function for better matching
    def normalize_name(name):
        return name.lower().replace('_', ' ').replace("'", '').replace('-', ' ').replace(':', '').strip()

    normalized_game_name = normalize_name(game_name)

    for key in original_comments:
        normalized_key = normalize_name(key)
        if normalized_key == normalized_game_name:
            original_comment = original_comments[key]
            original_price = original_prices.get(key)
            break

    metadata['originalComment'] = original_comment if original_comment else ""

    # Extract review score (look for X/100, X out of 100, Score: X, etc.)
    score_patterns = [
        r'(\d+)/100',  # Direct 70/100 format
        r'(\d+\.\d+)/10.*?\((\d+)/100\)',  # 7.0/10 (70/100) format
        r'(?:score|rating)[:\s]+(\d+)(?:/100|\s*out\s+of\s+100)?',
        r'(\d+)\s*out\s+of\s+100',
        r'##?\s*(?:score|rating)[:\s]+(\d+)',
        r'\*\*(?:score|rating)\*\*[:\s]+(\d+)',
        r'Average\s+(?:Critical\s+)?Assessment[:\s]+.*?(\d+)%',  # Average Assessment: ~40%
        r'Metacritic.*?(\d+)%',  # Metacritic percentage
    ]

    review_score = None
    scores_found = []

    # Try to extract all scores from the Review Sources section
    review_sources_match = re.search(r'## Review Sources.*?---', content, re.DOTALL)
    if review_sources_match:
        review_section = review_sources_match.group(0)
        # Extract all X/100 scores from review sources
        for match in re.finditer(r'\((\d+)/100\)', review_section):
            scores_found.append(int(match.group(1)))
        # Extract X/10 scores and convert to 100 scale
        for match in re.finditer(r'(\d+(?:\.\d+)?)/10(?!\d)', review_section):
            score = float(match.group(1)) * 10
            scores_found.append(int(score))

    # If we found scores in the review sources, average them
    if scores_found:
        review_score = int(sum(scores_found) / len(scores_found))
    else:
        # Fall back to pattern matching in the entire content
        for pattern in score_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # Get the score value (might be in group 1 or 2)
                score_str = match.group(2) if match.lastindex >= 2 and match.group(2) else match.group(1)
                try:
                    score = int(score_str)
                    if 0 <= score <= 100:
                        scores_found.append(score)
                except (ValueError, AttributeError):
                    continue

        if scores_found:
            review_score = int(sum(scores_found) / len(scores_found))

    metadata['reviewScore'] = review_score if review_score is not None else 0

    # Extract max players (look for various patterns)
    player_patterns = [
        r'(?:max(?:imum)?|up to)\s+(\d+)\s+(?:local\s+)?players',
        r'(\d+)\s+(?:local\s+)?players',
        r'(\d+)-player',
        r'supports?\s+(\d+)\s+players',
        r'for\s+(\d+)\s+players',
    ]

    max_players = None
    max_found = 0
    for pattern in player_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            num = int(match.group(1))
            if num > max_found and num <= 100:  # Reasonable upper limit
                max_found = num

    metadata['maxPlayers'] = max_found if max_found > 0 else 0

    # Extract platforms
    platforms = set()
    platform_keywords = {
        'PC': r'\bPC\b',
        'Steam': r'\bSteam\b',
        'Windows': r'\bWindows\b',
        'PS4': r'\bPS4\b',
        'PS5': r'\bPS5\b',
        'PlayStation': r'\bPlayStation\b',
        'Xbox': r'\bXbox\b',
        'Nintendo Switch': r'\bNintendo\s+Switch\b|\bSwitch\b',
        'Mac': r'\b(?:Mac|macOS)\b',
        'Linux': r'\bLinux\b',
        'iOS': r'\biOS\b',
        'Android': r'\bAndroid\b',
        'VR': r'\bVR\b',
        'Oculus': r'\bOculus\b',
        'HTC Vive': r'\bHTC\s+Vive\b|\bVive\b',
        'Meta Quest': r'\bMeta\s+Quest\b|\bQuest\b',
    }

    for platform, pattern in platform_keywords.items():
        if re.search(pattern, content, re.IGNORECASE):
            platforms.add(platform)

    # If no platforms found, default to PC/Steam
    if not platforms:
        platforms.add('PC')
        platforms.add('Steam')

    metadata['platforms'] = sorted(list(platforms))

    # Extract price - prefer original price from gameslist.txt
    if original_price:
        metadata['price'] = original_price
    else:
        price_patterns = [
            r'\$(\d+\.?\d*)',
            r'(?:price|cost)[:\s]+\$?(\d+\.?\d*)',
        ]

        price = None
        for pattern in price_patterns:
            match = re.search(pattern, content)
            if match:
                price_value = match.group(1)
                price = f"${price_value}"
                break

        metadata['price'] = price if price else ""

    return metadata

# Main processing function
def process_all_reviews():
    reviews_dir = Path("/Users/canal/gamelist_manyplayers/reviews")
    data_dir = Path("/Users/canal/gamelist_manyplayers/data")

    # Create data directory if it doesn't exist
    data_dir.mkdir(exist_ok=True)

    # Load original comments and prices
    original_comments, original_prices = load_original_comments()

    # Process all markdown files
    md_files = list(reviews_dir.glob("*.md"))
    print(f"Found {len(md_files)} markdown files to process")

    processed = 0
    for md_file in md_files:
        try:
            metadata = extract_metadata(md_file, original_comments, original_prices)

            # Create JSON filename
            json_filename = md_file.stem + '.json'
            json_path = data_dir / json_filename

            # Write JSON file
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            processed += 1
            print(f"Processed: {md_file.name} -> {json_filename}")
        except Exception as e:
            print(f"Error processing {md_file.name}: {e}")

    print(f"\nTotal processed: {processed}/{len(md_files)}")

if __name__ == "__main__":
    process_all_reviews()
