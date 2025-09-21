#!/usr/bin/env python3
"""
Script to fill Bible verse texts in the moments.json file
Uses the Bible API to fetch verse texts
"""
import json
import os
import requests
import re
import time
from typing import Dict, List

class BibleTextFiller:
    def __init__(self):

        # Auto-detect path: if running from scripts/ dir, go up one level; otherwise use current dir
        if os.path.basename(os.getcwd()) == 'scripts':
            self.moments_file = "../moments.json"  # From scripts/ directory
        else:
            self.moments_file = "moments.json"  # From root directory (GitHub Actions)
            
        # Using Fetch Bible API with French SBL translation
        self.bible_api_base = "https://v1.fetch.bible/bibles/fra_sbl"
        
    def usfm_to_fetch_bible_format(self, usfm: str) -> tuple:
        """Convert USFM format to Fetch Bible API format"""
        # Examples:
        # MAT.4.7 -> ('mat', 4, 7)
        # MRK.3.34 -> ('mrk', 3, 34)
        
        try:
            # Parse USFM: MAT.4.7 -> ['MAT', '4', '7']
            parts = usfm.split('.')
            if len(parts) >= 3:
                book_code = parts[0].lower()  # Convert to lowercase for fetch.bible
                chapter = int(parts[1])
                verse = int(parts[2])
                
                return (book_code, chapter, verse)
        except:
            pass
            
        return None
        
    def fetch_verse_text(self, usfm: str) -> str:
        """Fetch verse text from Fetch Bible API"""
        try:
            api_format = self.usfm_to_fetch_bible_format(usfm)
            if not api_format:
                return ""
                
            book_code, chapter, verse = api_format
            
            # Fetch the whole book in JSON format
            url = f"{self.bible_api_base}/txt/{book_code}.json"
            
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                contents = data.get('contents', [])
                
                # Structure: contents[chapter][verse]
                # Both chapter and verse are 1-indexed in the API structure
                if len(contents) > chapter:
                    chapter_content = contents[chapter]  # Direct chapter index
                    
                    if len(chapter_content) > verse:
                        verse_content = chapter_content[verse]  # Direct verse index
                        
                        # Extract text from the verse content
                        if isinstance(verse_content, list):
                            text_parts = []
                            for item in verse_content:
                                if isinstance(item, str):
                                    text_parts.append(item.strip())
                                elif isinstance(item, dict) and item.get('type') not in ['heading', 'note']:
                                    # Skip headings and notes, but include other text content
                                    if 'text' in item:
                                        text_parts.append(item['text'].strip())
                            
                            if text_parts:
                                verse_text = ' '.join(text_parts)
                                verse_text = re.sub(r'\s+', ' ', verse_text)
                                verse_text = re.sub(r'\n+', ' ', verse_text)
                                # Remove trailing punctuation like periods and newlines
                                verse_text = re.sub(r'\s*\.\s*$', '', verse_text)
                                return verse_text.strip()
                        elif isinstance(verse_content, str):
                            return verse_content.strip()
            
            print(f"  ⚠️ Could not find {usfm} (API response {response.status_code})")
            
        except Exception as e:
            print(f"Error fetching {usfm}: {e}")
            
        return ""
        
    def fill_bible_texts(self):
        """Fill all empty human_text fields in moments.json"""
        try:
            with open(self.moments_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading moments.json: {e}")
            return
            
        moments = data.get('moments', [])
        updated_count = 0
        
        print(f"Processing {len(moments)} moments...")
        
        for i, moment in enumerate(moments):
            references = moment.get('references', [])
            
            for ref in references:
                if ref.get('human_text') == '':  # Only fill empty texts
                    usfm_list = ref.get('usfm', [])
                    if usfm_list and len(usfm_list) > 0:
                        
                        print(f"Fetching text for {ref.get('human', 'verses')}...")
                        
                        # Fetch all verses in the range
                        verse_texts = []
                        for usfm in usfm_list:
                            verse_text = self.fetch_verse_text(usfm)
                            if verse_text:
                                verse_texts.append(verse_text)
                            
                            # Small delay to be respectful to the API
                            time.sleep(0.3)
                        
                        if verse_texts:
                            # Combine all verses with appropriate spacing
                            combined_text = ' '.join(verse_texts)
                            ref['human_text'] = combined_text
                            updated_count += 1
                            print(f"  ✅ Added: {combined_text[:60]}...")
                        else:
                            print(f"  ❌ Could not fetch text for {usfm_list}")
                        
                        # Additional delay between references
                        time.sleep(0.2)
            
            # Progress indicator
            if (i + 1) % 10 == 0:
                print(f"Progress: {i + 1}/{len(moments)} moments processed")
        
        print(f"\\nUpdated {updated_count} verse texts")
        
        # Save updated data
        try:
            with open(self.moments_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Updated moments.json with Bible texts")
        except Exception as e:
            print(f"Error saving updated data: {e}")

def main():
    filler = BibleTextFiller()
    filler.fill_bible_texts()

if __name__ == "__main__":
    main()
