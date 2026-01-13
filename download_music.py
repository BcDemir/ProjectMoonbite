#!/usr/bin/env python3
"""
Script to download placeholder music files for the zombie survival game.
This script will download royalty-free music from public sources.
"""

import os
import urllib.request
import ssl

# Create a context that doesn't verify SSL certificates
ssl_context = ssl._create_unverified_context()

# Create music directory if it doesn't exist
music_dir = os.path.join("assets", "music")
os.makedirs(music_dir, exist_ok=True)

# URLs for royalty-free music (these are placeholders - replace with actual URLs)
music_urls = {
    "menu": "https://example.com/menu_music.mp3",
    "day": "https://example.com/day_music.mp3",
    "night": "https://example.com/night_music.mp3",
    "shop": "https://example.com/shop_music.mp3",
    "game_over": "https://example.com/game_over_music.mp3",
    "placeholder": "https://example.com/placeholder.mp3"
}

print("Downloading music files...")

# Download each music file
for name, url in music_urls.items():
    file_path = os.path.join(music_dir, f"{name}_music.mp3")
    if name == "placeholder":
        file_path = os.path.join(music_dir, "placeholder.mp3")
    
    # Skip if file already exists
    if os.path.exists(file_path):
        print(f"Skipping {name} music (already exists)")
        continue
    
    try:
        print(f"Downloading {name} music...")
        # In a real implementation, this would download the file
        # For this example, we'll just create a text file
        with open(f"{file_path}.txt", "w") as f:
            f.write(f"This is a placeholder for {name} music.\n")
            f.write(f"In a real implementation, download from: {url}\n")
        print(f"Created placeholder for {name} music")
    except Exception as e:
        print(f"Error downloading {name} music: {e}")

print("Music download complete!")
print("Note: These are just placeholder files.")
print("Replace them with actual .mp3 files with the same names for the music to work.")
