#!/usr/bin/env python3
"""
Script to fetch YouVersion moments and save them to JSON
"""
import json
import requests
from datetime import datetime, timezone
import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

class MomentsFetcher:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        self.base_url = "https://moments.youversionapi.com/3.1/items.json"
        self.user_id = "224177359"
        
        # Auto-detect path: if running from scripts/ dir, go up one level; otherwise use current dir
        if os.path.basename(os.getcwd()) == 'scripts':
            self.moments_file = "../moments.json"  # From scripts/ directory
            self.last_update_file = "../last_update.txt"
        else:
            self.moments_file = "moments.json"  # From root directory (GitHub Actions)
            self.last_update_file = "last_update.txt"
            
        self.existing_moments = []
        self.last_note_date = None
        
        # Get bearer token from environment variable
        bearer_token = os.getenv('YOUVERSION_BEARER_TOKEN')
        if not bearer_token:
            raise ValueError("YOUVERSION_BEARER_TOKEN environment variable is required")
        
        # Headers required for API authentication
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'fr-FR,fr;q=0.9',
            'Authorization': f'Bearer {bearer_token}',
            'Connection': 'keep-alive',
            'Host': 'moments.youversionapi.com',
            'Referer': 'https://ios.youversionapi.com',
            'User-Agent': 'Bible 11.9.0 (iPhone 16;iOS 26.0;fr;gzip)',
            'X-Youversion-App-Platform': 'ios',
            'X-Youversion-App-State': 'fg',
            'X-Youversion-App-Version': '2025259',
            'X-Youversion-Client': 'youversion'
        }
        
    def load_existing_data(self):
        """Load existing moments and last update date"""
        try:
            if os.path.exists(self.moments_file):
                with open(self.moments_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.existing_moments = data.get('moments', [])
                    self.last_note_date = data.get('last_update')
                    print(f"Loaded {len(self.existing_moments)} existing moments")
                    if self.last_note_date:
                        print(f"Last note date: {self.last_note_date}")
        except Exception as e:
            print(f"Error loading existing moments: {e}")
            
        # Fallback: try to load from old separate file if JSON doesn't have last_update
        if not self.last_note_date:
            try:
                if os.path.exists(self.last_update_file):
                    with open(self.last_update_file, 'r') as f:
                        self.last_note_date = f.read().strip()
                        print(f"Last note date (from old file): {self.last_note_date}")
            except Exception as e:
                print(f"Error loading last update date: {e}")
            
    def fetch_moments_page(self, page: int = 1) -> Dict:
        """Fetch a specific page of moments from YouVersion API"""
        params = {
            'only_color': 'false',
            'page': page,
            'user_id': self.user_id
        }
        
        try:
            # Disable SSL verification for this specific API due to certificate issues
            response = requests.get(
                self.base_url, 
                headers=self.headers, 
                params=params, 
                timeout=30,
                verify=False  # Disable SSL verification
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.SSLError as e:
            print(f"SSL Error on page {page}: {e}")
            print("Trying with SSL verification disabled...")
            # Fallback with SSL disabled
            response = requests.get(
                self.base_url, 
                headers=self.headers, 
                params=params, 
                timeout=30,
                verify=False
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            return {}
            
    def fetch_verse_text(self, usfm: str, version_id: int = 133) -> Optional[str]:
        """Fetch Bible verse text from YouVersion API - currently disabled due to API limitations"""
        # For now, we'll return None and just prepare the structure
        # This can be implemented later when we find the correct API endpoint
        return None
            
    def format_references_with_text(self, references: List[Dict]) -> List[Dict]:
        """Format references and add Bible text"""
        formatted_refs = []
        
        for ref in references:
            formatted_ref = {
                'usfm': ref.get('usfm', []),
                'version_id': ref.get('version_id', 133),
                'human': ref.get('human', ''),
                'human_text': ''  # Will be filled with Bible text
            }
            
            # Try to fetch the Bible text for the first USFM reference
            if formatted_ref['usfm'] and len(formatted_ref['usfm']) > 0:
                usfm_ref = formatted_ref['usfm'][0]
                verse_text = self.fetch_verse_text(usfm_ref, formatted_ref['version_id'])
                if verse_text:
                    formatted_ref['human_text'] = verse_text
                    print(f"Added text for {formatted_ref['human']}: {verse_text[:50]}...")
                else:
                    formatted_ref['human_text'] = ''  # Empty for now, can be filled later
            
            formatted_refs.append(formatted_ref)
        
        return formatted_refs
            
    def format_moment(self, moment: Dict) -> Dict:
        """Format a moment according to specifications"""
        extras = moment.get('extras', {})
        references = extras.get('references', [])
        
        # Format references with Bible text
        formatted_references = self.format_references_with_text(references)
        
        formatted_moment = {
            'content': extras.get('content', ''),
            'color': extras.get('color', ''),
            'references': formatted_references,
            'tag': ''  # Empty tag field as requested
        }
        
        return formatted_moment
        
    def is_newer_than_last_update(self, created_dt: str) -> bool:
        """Check if a moment is newer than our last saved note"""
        if not self.last_note_date:
            return True
            
        try:
            moment_date = datetime.fromisoformat(created_dt.replace('Z', '+00:00'))
            last_date = datetime.fromisoformat(self.last_note_date.replace('Z', '+00:00'))
            return moment_date > last_date
        except Exception as e:
            print(f"Error comparing dates: {e}")
            return True
            
    def fetch_all_new_moments(self) -> List[Dict]:
        """Fetch all new moments from all pages"""
        new_moments = []
        page = 1
        latest_note_date = self.last_note_date
        
        while page <= 50:  # Safety limit to prevent infinite loops
            page_data = self.fetch_moments_page(page)
            
            if not page_data or page_data.get('response', {}).get('code') != 200:
                print(f"Failed to fetch page {page} or reached end")
                break
                
            moments = page_data.get('response', {}).get('data', {}).get('moments', [])
            
            if not moments:
                print(f"No moments found on page {page}")
                break
                
            page_has_new_moments = False
            
            for moment in moments:
                # Process notes and highlights (kind_id: "note.v1" or "highlight.v1")
                if moment.get('kind_id') not in ['note.v1', 'highlight.v1']:
                    continue
                    
                created_dt = moment.get('created_dt', '')
                
                # Update the latest note date
                if not latest_note_date or self.is_newer_than_last_update(created_dt):
                    if not latest_note_date or created_dt > latest_note_date:
                        latest_note_date = created_dt
                        
                # Only add if it's newer than our last update
                if self.is_newer_than_last_update(created_dt):
                    formatted_moment = self.format_moment(moment)
                    # Add created_dt temporarily for deduplication, will be removed later
                    formatted_moment['_created_dt'] = created_dt
                    new_moments.append(formatted_moment)
                    page_has_new_moments = True
                    print(f"Found new moment: {formatted_moment['content'][:50]}...")
            
            # If this page had no new moments, we might be done
            # but continue to next page to be thorough
            if not page_has_new_moments:
                print(f"No new moments on page {page}")
                
            page += 1
            
        # Update the last note date
        if latest_note_date and latest_note_date != self.last_note_date:
            self.last_note_date = latest_note_date
            
        return new_moments
        
    def save_data(self, new_moments: List[Dict]):
        """Save moments to JSON file and update last update date"""
        # Combine existing and new moments
        all_moments = self.existing_moments + new_moments
        
        # Sort by _created_dt (newest first) - using the temporary field for sorting
        all_moments.sort(key=lambda x: x.get('_created_dt', ''), reverse=True)
        
        # Remove duplicates based on content and created_dt
        unique_moments = []
        seen = set()
        for moment in all_moments:
            key = (moment.get('content', ''), moment.get('_created_dt', ''))
            if key not in seen:
                seen.add(key)
                # Remove the temporary _created_dt field before adding to final list
                clean_moment = {k: v for k, v in moment.items() if k != '_created_dt'}
                unique_moments.append(clean_moment)
        
        # Extract unique colors used
        colors_used = list(set(moment.get('color', '') for moment in unique_moments if moment.get('color', '')))
        colors_used.sort()  # Sort alphabetically for consistency
                
        data = {
            'moments': unique_moments,
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'last_update': self.last_note_date,  # Add last note date in JSON
            'total_moments': len(unique_moments),
            'colors_used': colors_used  # Add list of colors used
        }
        
        # Save moments with last_update included in JSON
        try:
            with open(self.moments_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(unique_moments)} moments to {self.moments_file}")
            if self.last_note_date:
                print(f"Last note date included in JSON: {self.last_note_date}")
        except Exception as e:
            print(f"Error saving moments: {e}")
                
    def run(self):
        """Main execution method"""
        print("Starting YouVersion moments fetch...")
        
        # Load existing data
        self.load_existing_data()
        
        # Fetch new moments
        new_moments = self.fetch_all_new_moments()
        
        if new_moments:
            print(f"Found {len(new_moments)} new moments")
            self.save_data(new_moments)
            
            # Auto-fill Bible texts for new moments
            print("\n🔄 Filling Bible texts for new moments...")
            try:
                from fill_bible_texts import BibleTextFiller
                bible_filler = BibleTextFiller()
                bible_filler.fill_bible_texts()
            except Exception as e:
                print(f"Error filling Bible texts: {e}")
                
            # Generate AI tags for new moments
            print("\n🏷️  Generating AI tags for moments...")
            try:
                from generate_tags import TagsGenerator
                tags_generator = TagsGenerator()
                tags_generator.run()
            except Exception as e:
                print(f"Error generating tags: {e}")
        else:
            print("No new moments found")
            # Still update the data file to show last check time
            self.save_data([])

if __name__ == "__main__":
    fetcher = MomentsFetcher()
    fetcher.run()
