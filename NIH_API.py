import requests
import json
import re
from datetime import datetime, timedelta

VERSION_URL = "https://clinicaltrials.gov/api/v2/version"
BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

def extract_instrument_elements(text):
    if not text:
        return []
    
    # Pattern to match "instrument" and what follows until the end of the sentence
    patterns = [
        r'instrument[s]?\s+(?:is|are|includes?|consists? of|measures?|assesses?|evaluates?)\s+([^.!?\n]+)',
        r'using\s+(?:the|an|a)\s+instrument[s]?\s+(?:to|that|which)\s+([^.!?\n]+)',
        r'instrument[s]?:\s+([^.!?\n]+)'
    ]
    
    elements = []
    for pattern in patterns:
        matches = re.finditer(pattern, text.lower())
        for match in matches:
            elements.append(match.group(1).strip())
    
    return elements

def fetch_study_data(search_terms, max_results=2):
    params = {
        "format": "json",
        "pageSize": max_results,
        "countTotal": "true",
        # "query.cond": "Depression OR \"Pain Management\" OR Opioid OR Addiction",
        # "query.term": "AREA[LastUpdatePostDate]RANGE[2023-01-15,MAX]",
        # # "filter.overallStatus": "RECRUITING,NOT_YET_RECRUITING",
        "query.term": "instrument",
        "fields": ",".join([
            "protocolSection.identificationModule.nctId",
            "protocolSection.identificationModule.briefTitle",
            "protocolSection.identificationModule.acronym",
            "protocolSection.statusModule.overallStatus",
            "protocolSection.conditionsModule.conditions",
            "protocolSection.conditionsModule.keywords",
            "protocolSection.designModule.phases",
            "protocolSection.descriptionModule.briefSummary",
            "protocolSection.descriptionModule.detailedDescription",
            "protocolSection.eligibilityModule.eligibilityCriteria",
            "protocolSection.designModule.studyType",
            "protocolSection.designModule.designInfo",
            "protocolSection.sponsorCollaboratorsModule.leadSponsor",
            "protocolSection.sponsorCollaboratorsModule.collaborators",
            "protocolSection.armsInterventionsModule",
            "protocolSection.outcomesModule"
        ]),
        "sort": ["LastUpdatePostDate:desc"]  # Sort by most recent first
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data and 'studies' in data:
            for study in data['studies']:
                # Extract text from relevant sections
                brief_summary = study.get('protocolSection', {}).get('descriptionModule', {}).get('briefSummary', '')
                detailed_desc = study.get('protocolSection', {}).get('descriptionModule', {}).get('detailedDescription', '')
                
                # Find instrument elements
                elements = extract_instrument_elements(brief_summary)
                elements.extend(extract_instrument_elements(detailed_desc))
                
                if elements:
                    print(f"\nStudy: {study['protocolSection']['identificationModule']['briefTitle']}")
                    print("Instrument elements found:")
                    for element in elements:
                        print(f"- {element}")
        
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

search_criteria = {
    "condition": ["Pain", "Addiction", "Depression", "Opioid", "Helping to End Addiction Long-term"]
    # "status": ["RECRUITING", "NOT_YET_RECRUITING"]
}

study_data = fetch_study_data(search_criteria)

if study_data and "studies" in study_data:
    print(f"\nFound {study_data.get('totalCount', 0)} total studies")
    print(f"Displaying first {len(study_data['studies'])} results:\n")
    
    for study in study_data["studies"]:
        protocol = study.get("protocolSection", {})
        identification = protocol.get("identificationModule", {})
        status = protocol.get("statusModule", {})
        conditions = protocol.get("conditionsModule", {})
        design = protocol.get("designModule", {})
        description = protocol.get("descriptionModule", {})
        eligibility = protocol.get("eligibilityModule", {})
        
        print("\nSTUDY DETAILS:")
        print(f"Title: {identification.get('briefTitle', 'N/A')}")
        print(f"NCT ID: {identification.get('nctId', 'N/A')}")
        print(f"Status: {status.get('overallStatus', 'N/A')}")
        print(f"Conditions: {', '.join(conditions.get('conditions', ['N/A']))}")
        print(f"Phase: {', '.join(design.get('phases', ['N/A']))}")
        print("\nPROTOCOL DETAILS:")
        print(f"Study Type: {design.get('studyType', 'N/A')}")
        print("\nBrief Summary:")
        print(description.get('briefSummary', 'N/A'))
        print("\nEligibility Criteria:")
        print(eligibility.get('eligibilityCriteria', 'N/A'))
        print("-" * 80)
else:
    print("No studies found or invalid response format")

def export_to_file(study_data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("CLINICAL TRIALS SEARCH RESULTS\n")
        f.write("=" * 80 + "\n\n")
        
        if study_data and "studies" in study_data:
            f.write(f"Total Studies Found: {study_data.get('totalCount', 0)}\n")
            f.write(f"Results Displayed: {len(study_data['studies'])}\n\n")
            
            for study in study_data["studies"]:
                protocol = study.get("protocolSection", {})
                identification = protocol.get("identificationModule", {})
                status = protocol.get("statusModule", {})
                conditions = protocol.get("conditionsModule", {})
                design = protocol.get("designModule", {})
                description = protocol.get("descriptionModule", {})
                eligibility = protocol.get("eligibilityModule", {})
                
                f.write("\nSTUDY DETAILS:\n")
                f.write(f"Title: {identification.get('briefTitle', 'N/A')}\n")
                f.write(f"NCT ID: {identification.get('nctId', 'N/A')}\n")
                f.write(f"Status: {status.get('overallStatus', 'N/A')}\n")
                f.write(f"Conditions: {', '.join(conditions.get('conditions', ['N/A']))}\n")
                f.write(f"Phase: {', '.join(design.get('phases', ['N/A']))}\n")
                f.write("\nPROTOCOL DETAILS:\n")
                f.write(f"Study Type: {design.get('studyType', 'N/A')}\n")
                f.write("\nBrief Summary:\n")
                f.write(f"{description.get('briefSummary', 'N/A')}\n")
                f.write("\nEligibility Criteria:\n")
                f.write(f"{eligibility.get('eligibilityCriteria', 'N/A')}\n")
                f.write("-" * 80 + "\n")
        else:
            f.write("No studies found or invalid response format\n")

if study_data:
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"clinical_trials_results_{timestamp}.txt"
    export_to_file(study_data, filename)
    print(f"\nResults have been exported to: {filename}")

def search_nih_projects(project_numbers=None, start_date=None, end_date=None):
    """Search NIH Reporter API for projects"""
    
    url = "https://api.reporter.nih.gov/v2/projects/search"
    
    # If no dates provided, use last 5 years
    if not start_date:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5*365)
    
    # Format dates for API
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    # Build criteria
    criteria = {
        "include_active_projects": True,
        "include_terminated_projects": True,
    }
    
    # Add specific project numbers if provided
    if project_numbers:
        criteria["project_nums"] = project_numbers
    else:
        criteria["fiscal_years"] = [year for year in range(start_date.year, end_date.year + 1)]
    
    payload = {
        "criteria": criteria,
        "include_fields": [
            "ProjectTitle",
            "ProjectNum",
            "ContactPiName",
            "OrgName",
            "ProjectStartDate",
            "ProjectEndDate",
            "TotalCost",
            "AbstractText",
            "ProjectTerms",
            "ApplId"
        ],
        "offset": 0,
        "limit": 100
    }
    
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    # Search for the specific HOPE study
    project_numbers = ["1RM1DA055301-01"]
    print(f"\nSearching for specific project: {project_numbers[0]}")
    
    results = search_nih_projects(project_numbers=project_numbers)
    
    if results and 'results' in results:
        print(f"\nFound {len(results['results'])} matching projects")
        
        for project in results['results']:
            print("\nProject Details:")
            print(f"Title: {project.get('ProjectTitle')}")
            print(f"PI: {project.get('ContactPiName')}")
            print(f"Project Number: {project.get('ProjectNum')}")
            print(f"Institution: {project.get('OrgName')}")
            print(f"Start Date: {project.get('ProjectStartDate')}")
            print(f"End Date: {project.get('ProjectEndDate')}")
            print(f"Total Cost: ${project.get('TotalCost', 0):,.2f}")
            print("\nAbstract:")
            print(project.get('AbstractText', 'No abstract available'))
            print("-" * 80)
        
        # Save the results
        with open('hope_study_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        print("\nFull results saved to hope_study_results.json")
    else:
        print("No results found")
