#!/usr/bin/env python3
"""
Script to generate AI-powered tags for moments using 1min.ai API with predefined tags
"""
import json
import requests
from datetime import datetime, timezone
import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

class TagsGenerator:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Auto-detect path: if running from scripts/ dir, go up one level
        if os.path.basename(os.getcwd()) == 'scripts':
            self.moments_file = "../moments.json"
        else:
            self.moments_file = "moments.json"
            
        # API Configuration for 1min.ai
        self.api_url = "https://api.1min.ai/api/features?isStreaming=true"
        
        # Get API key from environment variable
        api_key = os.getenv('ONEMIN_AI_API_KEY')
        if not api_key:
            raise ValueError("ONEMIN_AI_API_KEY environment variable is required")
            
        self.headers = {
            "API-KEY": api_key,
            "Content-Type": "application/json"
        }
        
        self.moments_data = {}
        
        # Predefined tags with descriptions
        self.predefined_tags = [
            {"tag": "priere", "description": "Versets qui enseignent la persévérance dans la prière et la confiance que Dieu répond."},
            {"tag": "courage", "description": "Textes qui encouragent à ne pas avoir peur, à rester fort face aux difficultés."},
            {"tag": "tentation", "description": "Avertissements et conseils pour résister aux attraits du péché."},
            {"tag": "humilite", "description": "Appels à reconnaître ses limites et à rejeter l'orgueil."},
            {"tag": "paroles", "description": "Conseils sur l'usage de la langue : éviter mensonge, médisance, paroles blessantes."},
            {"tag": "richesse", "description": "Mises en garde contre l'amour de l'argent et rappels sur la bonne gestion des biens."},
            {"tag": "travail", "description": "Textes qui valorisent la diligence, la fidélité et condamnent la paresse."},
            {"tag": "justice", "description": "Versets appelant à défendre l'opprimé, juger avec droiture et refuser l'injustice."},
            {"tag": "idolatrie", "description": "Tout ce qui détourne du vrai Dieu : idoles, cultes païens ou obsessions modernes."},
            {"tag": "conflit", "description": "Conseils pour résoudre les disputes, rechercher la paix et pardonner."},
            {"tag": "maladie", "description": "Textes qui apportent espérance et guérison au milieu de la souffrance physique."},
            {"tag": "solitude", "description": "Promesses de la présence de Dieu quand on se sent abandonné."},
            {"tag": "mort", "description": "Réflexions sur la fin de vie terrestre et assurance de la résurrection."},
            {"tag": "discernement", "description": "Encouragements à distinguer le vrai du faux, le bien du mal."},
            {"tag": "discipline", "description": "Versets qui montrent la correction comme un acte d'amour et d'éducation."},
            {"tag": "pauvres", "description": "Commandements d'aimer et soutenir les démunis, orphelins, étrangers, veuves."},
            {"tag": "fausseDoctrine", "description": "Avertissements contre les faux prophètes et enseignements trompeurs."},
            {"tag": "colere", "description": "Mises en garde contre les excès de colère et appels à la maîtrise de soi."},
            {"tag": "mensonge", "description": "Textes qui condamnent le mensonge et valorisent la vérité."},
            {"tag": "jalousie", "description": "Exemples négatifs et avertissements contre l'envie et la rivalité."},
            {"tag": "hypocrisie", "description": "Critiques des pratiques religieuses superficielles et du double visage."},
            {"tag": "perseverance", "description": "Encouragement à rester fidèle malgré les épreuves et la fatigue."},
            {"tag": "gratitude", "description": "Appels à remercier Dieu pour ses bienfaits, même dans l'épreuve."},
            {"tag": "pardon", "description": "Versets sur le pardon reçu de Dieu et celui que l'on doit accorder aux autres."},
            {"tag": "discipulat", "description": "Enseignements sur ce que signifie suivre Jésus au quotidien."},
            {"tag": "sexualite", "description": "Textes qui parlent de pureté, de fidélité et d'éviter l'immoralité sexuelle."},
            {"tag": "orgueil", "description": "Avertissements contre l'élévation de soi et rappels de l'humilité devant Dieu."},
            {"tag": "ivresse", "description": "Conseils contre l'abus d'alcool et la perte de maîtrise de soi."},
            {"tag": "amitie", "description": "Versets sur la fidélité, le soutien et le choix des amis."},
            {"tag": "famille", "description": "Enseignements sur les relations parents-enfants et la vie de foyer."},
            {"tag": "mariage", "description": "Conseils pour l'unité, la fidélité et le respect dans le couple."},
            {"tag": "autorite", "description": "Textes sur l'obéissance aux autorités spirituelles ou civiles."},
            {"tag": "service", "description": "Appels à aider, servir les autres avec humilité et amour."},
            {"tag": "esperance", "description": "Versets concrets qui rappellent la certitude de l'avenir en Christ."},
            {"tag": "trahison", "description": "Exemples de trahison et encouragements à rester fidèle malgré tout."},
            {"tag": "persecution", "description": "Textes qui fortifient face à l'opposition à cause de la foi."},
            {"tag": "avenir", "description": "Promesses et assurances de Dieu sur la direction de la vie."},
            {"tag": "creation", "description": "Textes sur la grandeur de Dieu à travers la nature et la création."},
            {"tag": "organe", "description": "Réflexions sur le corps humain comme temple du Saint-Esprit."},
            {"tag": "convoitise", "description": "Mises en garde contre le désir excessif des biens ou des personnes."},
            {"tag": "vaincreMal", "description": "Appels à répondre au mal par le bien."},
            {"tag": "esperer", "description": "Encouragements à patienter et attendre la délivrance de Dieu."},
            {"tag": "obeissance", "description": "Versets qui rappellent l'importance d'écouter et pratiquer la Parole."}
        ]
        
    def load_existing_data(self):
        """Load existing moments"""
        try:
            if os.path.exists(self.moments_file):
                with open(self.moments_file, 'r', encoding='utf-8') as f:
                    self.moments_data = json.load(f)
                    print(f"Loaded {len(self.moments_data.get('moments', []))} moments")
                    return True
            else:
                print("No moments file found")
                return False
        except Exception as e:
            print(f"Error loading moments: {e}")
            return False
        
    def create_prompt_payload(self, moment_content: str, references_text: str = "") -> Dict:
        """Create the payload for 1min.ai API call"""
        
        # Build tags list for the prompt
        tags_list = "\n".join([f"- {tag['tag']}: {tag['description']}" for tag in self.predefined_tags])
        
        prompt_sys = f"""Tu es un assistant IA spécialisé dans la création de tags pertinents pour des moments spirituels/bibliques.

Analyse le contenu fourni et choisis UNIQUEMENT parmi les tags prédéfinis suivants :

{tags_list}

Règles STRICTES :
- Maximum 2 tags par moment (1 est préférable, 2 seulement si vraiment nécessaire)
- Tu dois choisir UNIQUEMENT parmi les tags ci-dessus
- Ne crée JAMAIS de nouveaux tags
- Si aucun tag ne correspond parfaitement, choisis le plus proche

Réponds UNIQUEMENT avec un JSON dans ce format :
{{
  "tags": ["tag1", "tag2"]
}}

Rien d'autre dans la réponse. Pas de bloc de code."""

        moment_text = moment_content
        if references_text:
            moment_text += f"\n\nTexte biblique associé : {references_text}"
            
        prompt_user = f"Contenu du moment : {moment_text}"

        payload = {
            "type": "CHAT_WITH_AI",
            "model": "gpt-4o-mini",
            "promptObject": {
                "prompt": prompt_sys + "\n\n" + prompt_user,
                "isMixed": False,
                "imageList": [],
                "webSearch": False,
                "numOfSite": 1, 
                "maxWord": 200
            }
        }
        
        return payload
        
    def call_ai_api(self, payload: Dict) -> Optional[List[str]]:
        """Call the 1min.ai API and extract tags"""
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            # The API returns JSON directly
            response_text = response.text.strip()
            
            try:
                # Try to parse the entire response as JSON
                data = json.loads(response_text)
                if 'tags' in data and isinstance(data['tags'], list):
                    return data['tags'][:2]  # Limit to 2 tags maximum
            except json.JSONDecodeError:
                print(f"Failed to parse JSON response: {response_text}")
                return None
                                
            print("Could not extract tags from API response")
            return None
            
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return None
        except Exception as e:
            print(f"Error processing API response: {e}")
            return None
            
    def generate_tags_for_moment(self, moment: Dict) -> List[str]:
        """Generate tags for a single moment"""
        content = moment.get('content', '')
        references = moment.get('references', [])
        
        # Combine reference texts
        references_text = ""
        for ref in references:
            if ref.get('human_text'):
                references_text += ref['human_text'] + " "
                
        if not content and not references_text:
            print("No content to analyze")
            return []
            
        # Create API payload
        payload = self.create_prompt_payload(content, references_text.strip())
        
        # Call AI API
        tag_names = self.call_ai_api(payload)
        
        if not tag_names:
            return []
            
        # Validate tags are in predefined list
        valid_tags = []
        predefined_tag_names = [tag['tag'] for tag in self.predefined_tags]
        
        for tag_name in tag_names:
            tag_name = tag_name.strip().lower()
            if tag_name in predefined_tag_names:
                valid_tags.append(tag_name)
            else:
                print(f"  Warning: Tag '{tag_name}' not in predefined list, skipping")
                
        return valid_tags
        
    def process_all_moments(self):
        """Process all moments and generate tags"""
        moments = self.moments_data.get('moments', [])
        updated_moments = []
        used_tags = set()
        
        print(f"Processing {len(moments)} moments...")
        
        for i, moment in enumerate(moments):
            print(f"Processing moment {i+1}/{len(moments)}...")
            
            # Skip if moment already has tags (optional: you could force regeneration)
            current_tags = moment.get('tag', '')
            if current_tags and current_tags != '':
                if isinstance(current_tags, list):
                    tag_names = [tag.get('name', tag) if isinstance(tag, dict) else tag for tag in current_tags]
                    used_tags.update(tag_names)
                    print(f"  Skipping - already has tags: {tag_names}")
                else:
                    print(f"  Skipping - already has tags: {current_tags}")
                updated_moments.append(moment)
                continue
            
            # Generate tags
            generated_tags = self.generate_tags_for_moment(moment)
            
            if generated_tags:
                # Update moment with generated tags (simple list)
                moment['tag'] = generated_tags
                used_tags.update(generated_tags)
                print(f"  Generated {len(generated_tags)} tags: {generated_tags}")
            else:
                print(f"  No tags generated")
                moment['tag'] = []
                
            updated_moments.append(moment)
            
        return updated_moments, list(used_tags)
        
    def save_data(self, updated_moments: List[Dict], used_tags: List[str]):
        """Save updated moments with tags information"""
        
        # Update moments data
        self.moments_data['moments'] = updated_moments
        self.moments_data['last_tag_update'] = datetime.now(timezone.utc).isoformat()
        self.moments_data['tags_used'] = sorted(used_tags)
        self.moments_data['total_tags_available'] = len(self.predefined_tags)
        
        # Save updated moments
        try:
            with open(self.moments_file, 'w', encoding='utf-8') as f:
                json.dump(self.moments_data, f, indent=2, ensure_ascii=False)
            print(f"Updated moments saved to {self.moments_file}")
            print(f"Tags used: {sorted(used_tags)}")
            print(f"Total tags available: {len(self.predefined_tags)}")
        except Exception as e:
            print(f"Error saving moments: {e}")
            
    def display_available_tags(self):
        """Display all available predefined tags"""
        print("\n📋 Tags disponibles:")
        for i, tag in enumerate(self.predefined_tags, 1):
            print(f"{i:2d}. {tag['tag']:15} - {tag['description']}")
        print(f"\nTotal: {len(self.predefined_tags)} tags disponibles")
            
    def run(self):
        """Main execution method"""
        print("Starting AI tags generation with predefined tags...")
        
        # Load existing data
        if not self.load_existing_data():
            print("Failed to load data")
            return
            
        # Check if this is first run by looking at moments data
        is_first_run = 'tags_used' not in self.moments_data
        
        if is_first_run:
            print("\n🆕 First run detected!")
            self.display_available_tags()
            
        # Process all moments
        updated_moments, used_tags = self.process_all_moments()
        
        # Save results
        self.save_data(updated_moments, used_tags)
        
        print("\n✅ AI tags generation completed!")
        
        if is_first_run:
            print("\n📋 Tags have been saved in the JSON file for future reference.")

if __name__ == "__main__":
    generator = TagsGenerator()
    generator.run()
