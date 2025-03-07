import requests
import json
import re

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

def fetch_study_data(search_terms, max_results=100):
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
