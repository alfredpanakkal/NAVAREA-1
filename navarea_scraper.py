import sys
import os
import requests
import urllib3
from scrapling.parser import Selector

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_navarea_warnings():
    print("Setting up a persistent session to maintain verification token validity...")
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    session.verify = False # Ignore SSL verification issues

    print("Fetching the main Radio Navigation Warnings page...")
    url = "https://msi.admiralty.co.uk/RadioNavigationalWarnings"
    
    response = session.get(url)
    if response.status_code != 200:
        print(f"Error fetching main page, status code: {response.status_code}")
        return

    # Use Scrapling Selector to parse the page
    page = Selector(response.text)
    
    print("Extracting verification token...")
    token = page.css('input[name="__RequestVerificationToken"]::attr(value)').get()
    
    if not token:
        print("Error: Could not find __RequestVerificationToken!")
        return

    print("Extracting warning IDs for NAVAREA I...")
    # Find all checkboxes that have "NAVAREA I" in their aria-label
    navarea_checkboxes = page.css('input.checkbox_warning[aria-label*="NAVAREA I"]')
    
    warning_ids = []
    for cb in navarea_checkboxes:
        w_id = cb.attrib.get('warning-id')
        if w_id:
            warning_ids.append(w_id)
            
    if not warning_ids:
        print("No NAVAREA I warnings found.")
        return
        
    print(f"Found {len(warning_ids)} NAVAREA I warnings. Submitting selection...")
    
    post_url = "https://msi.admiralty.co.uk/RadioNavigationalWarnings/ShowSelection"
    
    payload = {
        "showSelectionId": ",".join(warning_ids),
        "__RequestVerificationToken": token
    }

    # Submit the POST request
    post_response = session.post(post_url, data=payload)
    if post_response.status_code != 200:
        print(f"Error submitting selection, status code: {post_response.status_code}")
        return
        
    print("Parsing the Show Selection page...")
    result_page = Selector(post_response.text)
    
    # Typically, the resulting page has warning elements
    references = result_page.css('.warning-reference::text').getall()
    descriptions = result_page.css('.warning-description::text').getall()
    
    if not references and not descriptions:
        # Fallback: dump text
        print("Warning: Could not find structured elements. Dumping raw text...")
        with open("navarea_1_warnings.txt", "w", encoding="utf-8") as f:
            f.write(result_page.css('body').get())
        print("Saved raw HTML to navarea_1_warnings.txt")
        return
        
    print(f"Successfully parsed {len(references)} warning details.")
    
    output_filename = "navarea_1_warnings.txt"
    with open(output_filename, "w", encoding="utf-8") as f:
        for ref, desc in zip(references, descriptions):
            ref_clean = ref.strip()
            desc_clean = desc.strip()
            f.write(f"--- {ref_clean} ---\n")
            f.write(f"{desc_clean}\n\n")
            
    print(f"Saved {len(references)} warnings to {output_filename}")

if __name__ == "__main__":
    scrape_navarea_warnings()
