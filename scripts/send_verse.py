#!/usr/bin/env python3
"""
Script to send a random verse from moments.json via ntfy.
"""

import json
import random
import requests
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

def load_moments(moments_path: Path) -> dict:
    """Load moments from JSON file."""
    with open(moments_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def select_random_verse(moments_data: dict) -> dict:
    """Select a random verse from moments."""
    moments = moments_data.get('moments', [])
    
    if not moments:
        raise ValueError("No moments found in the JSON file")
    
    return random.choice(moments)


def format_verse_message(verse: dict) -> tuple[str, str]:
    """Format verse into title and message for ntfy."""
    # Get the content
    content = verse.get('content', '')
    
    # Get the first reference if available
    references = verse.get('references', [])
    reference_text = ''
    verse_text = ''
    
    if references:
        ref = references[0]
        reference_text = ref.get('human', '')
        verse_text = ref.get('human_text', '')
    
    # Build title and message
    title = f"{reference_text}" if reference_text else "📖 Verset du moment"
    
    message_parts = []
    if verse_text:
        message_parts.append(verse_text)
    if content:
        message_parts.append(f"\n💭 {content}")
    
    message = "\n".join(message_parts) if message_parts else "Aucun contenu disponible"
    
    return title, message


def send_to_ntfy(title: str, message: str, ntfy_url: str = "https://ntfy.sh/verset", dry_run: bool = False):
    """Send notification to ntfy."""
    headers = {
        "Title": title.encode('utf-8').decode('latin-1', errors='ignore'),  # Fix encoding issue
        "Priority": "default",
        "Tags": "bible,book"
    }
    
    if dry_run:
        print(f"🔍 DRY RUN MODE - Would send to {ntfy_url}:")
        print(f"Title: {title}")
        print(f"Message: {message}")
        return
    
    response = requests.post(
        ntfy_url,
        data=message.encode('utf-8'),
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"✅ Notification sent successfully to {ntfy_url}")
        print(f"Title: {title}")
        print(f"Message preview: {message[:100]}...")
    else:
        print(f"❌ Failed to send notification. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)


def main():
    """Main function."""
    # Get the moments.json path (one level up from scripts)
    script_dir = Path(__file__).parent
    moments_path = script_dir.parent / 'moments.json'
    
    # Check for dry run mode
    dry_run = '--dry-run' in sys.argv
    
    print(f"📚 Loading moments from: {moments_path}")
    
    try:
        # Load moments
        moments_data = load_moments(moments_path)
        total_moments = len(moments_data.get('moments', []))
        print(f"📊 Found {total_moments} moments")
        
        # Select random verse
        verse = select_random_verse(moments_data)
        print(f"🎲 Selected random verse")
        
        # Format message
        title, message = format_verse_message(verse)
        
        # Send to ntfy
        send_to_ntfy(title, message, dry_run=dry_run)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
