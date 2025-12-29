#!/usr/bin/env python3
"""
Continuous monitoring script to process new review markdown files as they are created.
"""

import time
import os
from pathlib import Path
from extract_metadata import extract_metadata, load_original_comments
import json

def get_processed_files(data_dir):
    """Get set of already processed files based on JSON files in data directory."""
    if not data_dir.exists():
        return set()

    processed = set()
    for json_file in data_dir.glob("*.json"):
        md_name = json_file.stem + '.md'
        processed.add(md_name)
    return processed

def monitor_and_process():
    """Continuously monitor for new markdown files and process them."""
    reviews_dir = Path("/Users/canal/gamelist_manyplayers/reviews")
    data_dir = Path("/Users/canal/gamelist_manyplayers/data")

    # Create data directory if it doesn't exist
    data_dir.mkdir(exist_ok=True)

    # Load original comments and prices once
    print("Loading original comments and prices...")
    original_comments, original_prices = load_original_comments()

    # Track processed files
    processed_files = get_processed_files(data_dir)
    print(f"Starting with {len(processed_files)} already processed files")

    iteration = 0
    while True:
        iteration += 1

        # Get all current markdown files
        current_md_files = set()
        for md_file in reviews_dir.glob("*.md"):
            current_md_files.add(md_file.name)

        # Find new files
        new_files = current_md_files - processed_files

        if new_files:
            print(f"\n[Iteration {iteration}] Found {len(new_files)} new file(s) to process:")

            for md_filename in sorted(new_files):
                md_path = reviews_dir / md_filename
                try:
                    # Extract metadata
                    metadata = extract_metadata(md_path, original_comments, original_prices)

                    # Create JSON filename
                    json_filename = Path(md_filename).stem + '.json'
                    json_path = data_dir / json_filename

                    # Write JSON file
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False)

                    print(f"  ✓ {md_filename} -> {json_filename}")
                    processed_files.add(md_filename)

                except Exception as e:
                    print(f"  ✗ Error processing {md_filename}: {e}")
        else:
            if iteration % 10 == 0:  # Print status every 10 iterations
                print(f"[Iteration {iteration}] No new files. Total processed: {len(processed_files)}")

        # Sleep for 5 seconds before checking again
        time.sleep(5)

if __name__ == "__main__":
    print("=" * 60)
    print("METADATA EXTRACTION MONITORING SERVICE")
    print("=" * 60)
    print("Monitoring /Users/canal/gamelist_manyplayers/reviews/")
    print("Output directory: /Users/canal/gamelist_manyplayers/data/")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    try:
        monitor_and_process()
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user.")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
