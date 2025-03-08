import os
import requests
import json
from dotenv import load_dotenv
from collections import defaultdict
import PyPDF2
from io import BytesIO

# Load environment variables
load_dotenv()

class HealAPI:
    def __init__(self):
        self.api_key = os.getenv('HEAL_API_KEY')
        self.key_id = os.getenv('HEAL_KEY_ID')
        self.base_url = "https://healdata.org/api"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def get_study_info(self, study_id):
        endpoint = f"/study/{study_id}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching study {study_id}: {e}")
            return None

def analyze_studies():
    print("Analyzing studies...")
    
    # Load manifest file
    try:
        with open('manifest.json', 'r') as f:
            files = json.load(f)
    except FileNotFoundError:
        print("Error: manifest.json file not found in current directory")
        return
    
    # Extract study patterns from filenames
    patterns = set()
    for file in files:
        filename = file['file_name'].lower()
        if 'tfus' in filename:
            patterns.add('tFUS')
        if 'nhp' in filename:
            patterns.add('NHP')
        # Add more patterns as needed
            
    print(f"Found study patterns: {patterns}\n")
    
    # Group files by pattern
    for pattern in patterns:
        print("=" * 80)
        print(f"Study Pattern: {pattern}")
        
        # Filter files for this pattern
        pattern_files = [f for f in files if pattern.lower() in f['file_name'].lower()]
        print(f"Number of files: {len(pattern_files)}\n")
        
        # Group by file extension
        file_types = defaultdict(list)
        for file in pattern_files:
            ext = os.path.splitext(file['file_name'])[1].lower().lstrip('.')
            if ext:  # Skip files with no extension
                file_types[ext].append(file)
                
        print("File types summary:\n")
        for ext, type_files in sorted(file_types.items()):
            total_size_mb = sum(f['file_size'] for f in type_files) / (1024 * 1024)
            print(f"{ext.upper()} files ({len(type_files)}):")
            print(f"Total size: {total_size_mb:.2f} MB")
            
            # Sort files by size
            type_files.sort(key=lambda x: x['file_size'], reverse=True)
            for file in type_files:
                size_mb = file['file_size'] / (1024 * 1024)
                print(f"- {file['file_name']} ({size_mb:.2f} MB)")
            print()
            
        # Look for documentation files
        docs = [f for f in pattern_files if 'readme' in f['file_name'].lower() or '.pdf' in f['file_name'].lower()]
        if docs:
            print("\nDocumentation files:")
            for doc in docs:
                size_mb = doc['file_size'] / (1024 * 1024)
                print(f"- {doc['file_name']} ({size_mb:.2f} MB)")
            print()

if __name__ == "__main__":
    analyze_studies()