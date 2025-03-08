import requests
import json
from datetime import datetime

def test_nih_api():
    """Search NIH Reporter API for chronic pain and opioid use disorder studies"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'pain_opioid_studies_{timestamp}.txt'
    
    with open(output_file, 'w') as f:
        url = "https://api.reporter.nih.gov/v2/projects/search"
        
        test_payload = {
            "criteria": {
                "advanced_text_search": {
                    "operator": "and",
                    "search_field": "all",
                    "search_text": "chronic pain opioid use disorder"
                },
                "include_active_projects": True
            },
            "include_fields": [
                "ProjectTitle",
                "ProjectNum",
                "AbstractText"
            ],
            "offset": 0,
            "limit": 100,
            "sort_field": "project_start_date",
            "sort_order": "desc"
        }
        
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        
        try:
            f.write("Chronic Pain and Opioid Use Disorder Studies\n")
            f.write("=" * 80 + "\n\n")
            
            response = requests.post(url, json=test_payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('results'):
                    total_found = data.get('meta', {}).get('total', 0)
                    f.write(f"Total Studies Found: {total_found}\n\n")
                    
                    for project in data['results']:
                        f.write("-" * 80 + "\n")
                        f.write(f"Title: {project.get('project_title', 'N/A')}\n")
                        f.write(f"Project Number: {project.get('project_num', 'N/A')}\n\n")
                        f.write("Abstract:\n")
                        f.write(f"{project.get('abstract_text', 'No abstract available')}\n\n")
                        
                else:
                    f.write("No results found\n")
                
                # Save raw results
                with open(f'pain_opioid_raw_{timestamp}.json', 'w') as json_file:
                    json.dump(data, json_file, indent=2)
                
            else:
                f.write(f"Error accessing NIH Reporter API: {response.status_code}\n")
                
        except Exception as e:
            f.write(f"Error occurred: {str(e)}\n")
            print(f"Error: {str(e)}")
        
        print(f"\nStudy details have been saved to {output_file}")
        print(f"Raw JSON data saved to pain_opioid_raw_{timestamp}.json")

if __name__ == "__main__":
    test_nih_api()